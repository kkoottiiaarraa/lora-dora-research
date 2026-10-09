#!/usr/bin/env python3
"""Install on the user's relay VM, never on the shared GPU server.

Standalone stdlib-only Ubuntu/Debian helper. --print-unit is read-only.
Checks the local Tailscale IP before performing any installation.
"""
import argparse
import ipaddress
import json
import os
import pwd
import socket
import subprocess
import sys
import time
from pathlib import Path

SERVICE = "lora-dora-ssh-relay.service"
MARKER = "# Managed by lora-dora-research/scripts/setup_ssh_relay.py"


def checked_endpoints(listen_ip, target_ip, listen_port, target_port):
    listen = ipaddress.IPv4Address(listen_ip)
    target = ipaddress.IPv4Address(target_ip)
    if listen not in ipaddress.IPv4Network("100.64.0.0/10"):
        raise ValueError("Listener must use a Tailscale IPv4 address")
    if target.is_unspecified or target.is_multicast or target.is_loopback:
        raise ValueError("Target must identify the remote SSH server")
    if any(type(port) is not int or not 1 <= port <= 65535
           for port in (listen_port, target_port)):
        raise ValueError("Ports must be integers from 1 to 65535")
    if listen_port < 1024:
        raise ValueError("Relay uses an unprivileged port, >=1024")
    return str(listen), str(target)


def render_unit(listen_ip, target_ip, listen_port=2222, target_port=22):
    listen, target = checked_endpoints(listen_ip, target_ip, listen_port, target_port)
    return f"""{MARKER}
[Unit]
Description=SSH relay for the LoRA/DoRA checkpoint study
After=network-online.target tailscaled.service
Wants=network-online.target tailscaled.service

[Service]
Type=simple
User=nobody
ExecStart=/usr/bin/socat TCP4-LISTEN:{listen_port},bind={listen},reuseaddr,fork TCP4:{target}:{target_port},connect-timeout=10
Restart=on-failure
RestartSec=5
NoNewPrivileges=yes
PrivateTmp=yes
ProtectSystem=strict
ProtectHome=yes

[Install]
WantedBy=multi-user.target
"""


def run(command, timeout=30, capture=False):
    return subprocess.run(command, check=True, timeout=timeout,
                          text=True, capture_output=capture)


def ssh_banner(listen_ip, listen_port):
    last_error = None
    for _ in range(4):
        try:
            with socket.create_connection((listen_ip, listen_port), timeout=3) as connection:
                connection.settimeout(5)
                data = connection.recv(256)
            banner = data.decode("ascii", errors="replace").strip()
            if not banner.startswith("SSH-"):
                raise RuntimeError("Relay did not return an SSH banner")
            return banner
        except (OSError, RuntimeError) as error:
            last_error = error
            time.sleep(0.5)
    raise RuntimeError("Relay SSH banner check failed: " + str(last_error))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--listen-ip", required=True)
    parser.add_argument("--target-ip", required=True)
    parser.add_argument("--listen-port", type=int, default=2222)
    parser.add_argument("--target-port", type=int, default=22)
    parser.add_argument("--print-unit", action="store_true")
    args = parser.parse_args()
    unit = render_unit(args.listen_ip, args.target_ip, args.listen_port, args.target_port)
    if args.print_unit:
        print(unit, end="")
        return
    if os.geteuid() != 0:
        raise RuntimeError("Run this helper with sudo on the Finland VM")
    # Fail before apt or service changes on a different machine.
    local_ips = run(["tailscale", "ip", "-4"], capture=True).stdout.split()
    if args.listen_ip not in local_ips:
        raise RuntimeError("This machine does not have the requested Tailscale IP")
    pwd.getpwnam("nobody")
    unit_path = Path("/etc/systemd/system") / SERVICE
    if unit_path.exists() and not unit_path.read_text().startswith(MARKER + "\n"):
        raise RuntimeError("A service with this name exists and is not managed by this helper")
    # These package changes are only on the user's own relay VM.
    if not Path("/usr/bin/socat").is_file():
        run(["apt-get", "update"], timeout=300)
        run(["apt-get", "install", "-y", "socat"], timeout=300)
    unit_path.write_text(unit)
    unit_path.chmod(0o644)
    run(["systemctl", "daemon-reload"])
    run(["systemctl", "enable", SERVICE])
    run(["systemctl", "restart", SERVICE])
    run(["systemctl", "is-active", SERVICE], capture=True)
    banner = ssh_banner(args.listen_ip, args.listen_port)
    print(json.dumps(dict(service=SERVICE, listen_ip=args.listen_ip,
        listen_port=args.listen_port, target_ip=args.target_ip,
        target_port=args.target_port, ssh_banner=banner,
        verified="VM-local TCP relay only; cloud VPN and SSH authentication still unchecked"),
        ensure_ascii=False, indent=2))


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print(str(error), file=sys.stderr)
        sys.exit(1)
