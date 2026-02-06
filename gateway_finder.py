#!/usr/bin/env python3
"""
Modem Gateway Finder
- Default gateway IP'yi bulmaya çalışır (Windows/macOS/Linux)
- Yaygın modem arayüz IP'lerini test eder
- Erişilebilen admin sayfalarını listeler

Not: Sadece kendi ağınızda kullanın.
"""

from __future__ import annotations
import os
import re
import socket
import subprocess
import sys
import urllib.request
import urllib.error
from typing import List, Optional, Tuple

COMMON_IPS = [
    "192.168.1.1",
    "192.168.0.1",
    "192.168.1.254",
    "192.168.0.254",
    "192.168.100.1",
    "10.0.0.1",
    "10.0.1.1",
    "172.16.0.1",
]

USER_AGENT = "ModemGatewayFinder/1.0 (+https://github.com/yourname/modem-gateway-finder)"


def run(cmd: List[str]) -> str:
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, check=False)
        return (p.stdout or "") + "\n" + (p.stderr or "")
    except Exception:
        return ""


def detect_gateway() -> Optional[str]:
    plat = sys.platform.lower()

    # Windows
    if plat.startswith("win"):
        out = run(["ipconfig"])
        # "Default Gateway . . . . . . . . . : 192.168.1.1"
        m = re.search(r"Default Gateway[^\n:]*:\s*([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)", out)
        if m:
            return m.group(1).strip()

    # macOS
    if plat == "darwin":
        out = run(["route", "-n", "get", "default"])
        m = re.search(r"gateway:\s*([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)", out)
        if m:
            return m.group(1).strip()

    # Linux (ip route)
    if "linux" in plat:
        out = run(["ip", "route"])
        # "default via 192.168.1.1 dev wlan0 ..."
        m = re.search(r"default\s+via\s+([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)", out)
        if m:
            return m.group(1).strip()

        # Fallback: netstat -rn
        out = run(["netstat", "-rn"])
        m = re.search(r"^0\.0\.0\.0\s+([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)\s+", out, re.M)
        if m:
            return m.group(1).strip()

    return None


def is_port_open(host: str, port: int, timeout: float = 0.4) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except Exception:
        return False


def http_probe(url: str, timeout: float = 1.2) -> Tuple[bool, str]:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            code = getattr(resp, "status", 200)
            # Bazı modemler 401/403 de dönse "canlı" demektir; ama urllib bunu exception'a atabilir.
            return True, f"HTTP {code}"
    except urllib.error.HTTPError as e:
        # 401/403/404 bile cihazın cevap verdiğini gösterir
        return True, f"HTTP {e.code}"
    except Exception as e:
        return False, str(e)


def main() -> int:
    print("== Modem Gateway Finder ==")

    gw = detect_gateway()
    if gw:
        print(f"[+] Default gateway bulundu: {gw}")
    else:
        print("[!] Default gateway bulunamadı (yine de yaygın IP'ler deneniyor).")

    # Aday listesi: gateway + common
    candidates = []
    if gw:
        candidates.append(gw)
    for ip in COMMON_IPS:
        if ip not in candidates:
            candidates.append(ip)

    alive = []
    print("\n== Port taraması (80/443) ==")
    for ip in candidates:
        p80 = is_port_open(ip, 80)
        p443 = is_port_open(ip, 443)
        if p80 or p443:
            alive.append((ip, p80, p443))
            ports = []
            if p80: ports.append("80")
            if p443: ports.append("443")
            print(f"[+] {ip} açık port: {', '.join(ports)}")
        else:
            print(f"[-] {ip} (80/443 kapalı ya da erişilemiyor)")

    if not alive:
        print("\n[!] Hiçbir aday IP 80/443 üzerinden cevap vermedi.")
        print("    - Aynı Wi-Fi/LAN'de misin?")
        print("    - VPN/proxy kapalı mı?")
        print("    - Farklı subnet olabilir (örn: 192.168.2.1)")
        return 1

    print("\n== HTTP probe (admin arayüz linkleri) ==")
    found = []
    for ip, p80, p443 in alive:
        urls = []
        if p80:
            urls.append(f"http://{ip}/")
        if p443:
            urls.append(f"https://{ip}/")

        for url in urls:
            ok, info = http_probe(url)
            if ok:
                found.append((url, info))

    if found:
        print("\nErişilebilir arayüzler:")
        for url, info in found:
            print(f"  - {url}  ({info})")
        print("\nİpucu: 192.168.l.l yazma; oradaki 'l' değil '1' olmalı 🙂")
    else:
        print("\n[!] Port açık göründü ama HTTP probe başarısız (bazı modemler farklı path/port kullanır).")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
