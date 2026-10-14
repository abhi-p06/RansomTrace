import type { Metadata } from "next";
import "./globals.css";
import SOCShell from "@/components/layout/SOCShell";

export const metadata: Metadata = {
  title: "RansomTrace — Cryptocurrency Forensics & Ransomware Analysis Platform",
  description:
    "Cybercrime Investigation, Cryptocurrency Forensics & AI-Based Ransomware Payment Analysis Platform",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className="bg-[#070a13] text-slate-100 antialiased font-sans">
        <SOCShell>{children}</SOCShell>
      </body>
    </html>
  );
}
