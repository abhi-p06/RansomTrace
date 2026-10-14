import re
import hashlib
import logging
from typing import Dict, Any, List, Optional
import httpx
from backend.app.core.config import settings

logger = logging.getLogger(__name__)

# Base58 character set for Bitcoin
B58_CHARS = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"

def decode_base58(s: str) -> Optional[bytes]:
    """Decodes a Base58 string into bytes."""
    n = 0
    for char in s:
        p = B58_CHARS.find(char)
        if p == -1:
            return None
        n = n * 58 + p
    raw = n.to_bytes((n.bit_length() + 7) // 8 or 1, byteorder="big")
    pad = 0
    for char in s:
        if char == "1":
            pad += 1
        else:
            break
    return b"\x00" * pad + raw

def validate_bitcoin_address(address: str) -> Dict[str, Any]:
    """
    Validates a Bitcoin address (Mainnet & Testnet formats):
    - P2PKH (Legacy): starts with 1
    - P2SH: starts with 3
    - Native SegWit (Bech32): starts with bc1q
    - Taproot (Bech32m): starts with bc1p
    """
    addr = address.strip()
    if not addr:
        return {"valid": False, "reason": "Address cannot be empty"}

    # 0. Demonstration / Synthetic Addresses for Academic Viva
    if addr.startswith(("1Demo", "3Demo", "bc1demo")):
        return {"valid": True, "type": "Demonstration Synthetic (Educational)", "address": addr}

    # 1. Native SegWit / Taproot (Bech32/Bech32m)
    if addr.startswith("bc1"):
        if re.match(r"^bc1[a-z0-9]{39,59}$", addr):
            addr_type = "Taproot (P2TR)" if addr.startswith("bc1p") else "Native SegWit (P2WPKH/P2WSH)"
            return {"valid": True, "type": addr_type, "address": addr}
        return {"valid": False, "reason": "Malformed Bech32 SegWit/Taproot address format"}

    # 2. Legacy P2PKH & P2SH (Base58Check)
    if addr[0] in ("1", "3"):
        if not re.match(r"^[1-9A-HJ-NP-za-km-z]{26,35}$", addr):
            return {"valid": False, "reason": "Invalid Base58 characters or length for Legacy/P2SH address"}
        decoded = decode_base58(addr)
        if not decoded or len(decoded) != 25:
            return {"valid": False, "reason": "Invalid Base58 byte length"}
        payload, checksum = decoded[:-4], decoded[-4:]
        expected_checksum = hashlib.sha256(hashlib.sha256(payload).digest()).digest()[:4]
        if checksum != expected_checksum:
            return {"valid": False, "reason": "Invalid Base58Check checksum"}
        addr_type = "Legacy (P2PKH)" if addr[0] == "1" else "Script Hash (P2SH)"
        return {"valid": True, "type": addr_type, "address": addr}

    # 3. Testnet addresses (m or n Base58, or tb1 Bech32)
    if addr.startswith(("m", "n", "2")):
        if re.match(r"^[mn2][1-9A-HJ-NP-za-km-z]{25,34}$", addr):
            return {"valid": True, "type": "Testnet (Legacy/P2SH)", "address": addr}
        return {"valid": False, "reason": "Malformed Testnet address format"}
    if addr.startswith("tb1"):
        if re.match(r"^tb1[a-z0-9]{39,59}$", addr):
            return {"valid": True, "type": "Testnet (Bech32)", "address": addr}
        return {"valid": False, "reason": "Malformed Testnet Bech32 address format"}

    return {"valid": False, "reason": "Unrecognized Bitcoin address format prefix"}


class MempoolClient:
    """
    Robust HTTP client for retrieving publicly available Bitcoin ledger data
    from the Mempool API with timeout and rate-limit safeguards.
    """

    def __init__(self, base_url: Optional[str] = None, timeout: Optional[int] = None):
        self.base_url = (base_url or settings.MEMPOOL_API_BASE).rstrip("/")
        self.timeout = timeout or settings.HTTP_TIMEOUT_SECONDS

    def _get_headers(self) -> Dict[str, str]:
        return {
            "Accept": "application/json",
            "User-Agent": "RansomTrace-Forensic-Client/1.0",
        }

    async def get_address_summary(self, address: str) -> Dict[str, Any]:
        """Queries public balance and transaction count summary for an address."""
        url = f"{self.base_url}/address/{address}"
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                resp = await client.get(url, headers=self._get_headers())
                if resp.status_code == 404:
                    return {
                        "address": address,
                        "chain_stats": {
                            "funded_txo_count": 0,
                            "funded_txo_sum": 0,
                            "spent_txo_count": 0,
                            "spent_txo_sum": 0,
                            "tx_count": 0,
                        },
                        "mempool_stats": {
                            "funded_txo_count": 0,
                            "funded_txo_sum": 0,
                            "spent_txo_count": 0,
                            "spent_txo_sum": 0,
                            "tx_count": 0,
                        }
                    }
                elif resp.status_code == 429:
                    raise httpx.HTTPStatusError("Public blockchain API rate limit reached. Please wait a moment.", request=resp.request, response=resp)
                resp.raise_for_status()
                return resp.json()
            except httpx.TimeoutException:
                logger.error(f"Timeout querying Mempool API for address: {address}")
                raise RuntimeError("Blockchain network timeout while retrieving public address data.")
            except httpx.HTTPStatusError as e:
                logger.error(f"HTTP error querying address {address}: {e.response.status_code}")
                if e.response.status_code == 429:
                    raise RuntimeError("Upstream blockchain rate limit exceeded. Please retry shortly.")
                raise RuntimeError(f"Blockchain data provider error: {e.response.status_code}")
            except Exception as e:
                logger.error(f"Unexpected error communicating with Mempool API: {e}")
                raise RuntimeError("Unable to communicate with public blockchain data provider.")

    async def get_address_transactions(self, address: str) -> List[Dict[str, Any]]:
        """Queries publicly available transaction history for an address."""
        url = f"{self.base_url}/address/{address}/txs"
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                resp = await client.get(url, headers=self._get_headers())
                if resp.status_code == 404:
                    return []
                elif resp.status_code == 429:
                    raise httpx.HTTPStatusError("Public blockchain API rate limit reached.", request=resp.request, response=resp)
                resp.raise_for_status()
                return resp.json()
            except httpx.TimeoutException:
                logger.error(f"Timeout querying Mempool API transactions for address: {address}")
                raise RuntimeError("Blockchain network timeout while retrieving transaction history.")
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 429:
                    raise RuntimeError("Upstream blockchain rate limit exceeded. Please retry shortly.")
                raise RuntimeError(f"Blockchain data provider error: {e.response.status_code}")
            except Exception as e:
                logger.error(f"Error querying address txs: {e}")
                raise RuntimeError("Unable to retrieve public transactions from blockchain provider.")

    async def get_transaction(self, txid: str) -> Dict[str, Any]:
        """Queries single transaction details by txid."""
        url = f"{self.base_url}/tx/{txid}"
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                resp = await client.get(url, headers=self._get_headers())
                if resp.status_code == 404:
                    raise FileNotFoundError(f"Transaction '{txid}' not found on public blockchain.")
                elif resp.status_code == 429:
                    raise httpx.HTTPStatusError("Rate limit exceeded.", request=resp.request, response=resp)
                resp.raise_for_status()
                return resp.json()
            except httpx.TimeoutException:
                raise RuntimeError(f"Timeout retrieving transaction {txid}")
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 404:
                    raise FileNotFoundError(f"Transaction '{txid}' not found on public blockchain.")
                raise RuntimeError(f"Blockchain data provider error: {e.response.status_code}")

mempool_client = MempoolClient()
