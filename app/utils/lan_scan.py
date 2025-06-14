import socket
import subprocess
import platform
import concurrent.futures
import re
import time


def get_local_ip():
    """Get local IP address."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "Unknown"


def ping(ip):
    """Ping an IP address and return (is_alive, latency_ms)."""
    param = "-n" if platform.system().lower() == "windows" else "-c"
    time_param = "-w" if platform.system().lower() == "windows" else "-W"
    try:
        start = time.time()
        result = subprocess.run(
            ["ping", param, "1", time_param, "1000", ip],
            stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, timeout=2
        )
        latency = int((time.time() - start) * 1000)
        return (result.returncode == 0, latency if result.returncode == 0 else None)
    except:
        return (False, None)


def scan_ports(ip, ports=None):
    """Scan specified ports on the given IP."""
    if ports is None:
        ports = [21, 22, 23, 25, 53, 80, 110, 139, 143, 443, 445, 3389]

    open_ports = []
    for port in ports:
        try:
            with socket.create_connection((ip, port), timeout=0.5):
                open_ports.append(port)
        except:
            continue
    return open_ports



def get_mac(ip):
    """Fetch MAC address from ARP table."""
    try:
        if platform.system().lower() == "windows":
            output = subprocess.check_output("arp -a", shell=True).decode()
            pattern = re.compile(rf"{re.escape(ip)}\s+([a-fA-F0-9\-]+)")
        else:
            output = subprocess.check_output(["arp", "-n", ip]).decode()
            pattern = re.compile(r"(([a-fA-F0-9]{2}:){{5}}[a-fA-F0-9]{{2}})")

        match = pattern.search(output)
        if match:
            return match.group(1)
        else:
            return "Unavailable"
    except:
        return "Unavailable"


def discover_devices():
    """Scan local subnet and get active devices with open ports and MACs."""
    local_ip = get_local_ip()
    if local_ip == "Unknown":
        return {"error": "Could not detect local IP"}

    ip_base = ".".join(local_ip.split(".")[:3]) + "."

    active_ips = []

    def check_ip(i):
        ip = ip_base + str(i)
        if ip != local_ip:
            alive, latency = ping(ip)
            if alive:
                active_ips.append((ip, latency))

    # Concurrent ping sweep
    with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
        executor.map(check_ip, range(1, 255))

    devices = []
    for ip, latency in active_ips:
        try:
            hostname = socket.gethostbyaddr(ip)[0]
        except:
            hostname = "Unknown"

        open_ports = scan_ports(ip)
        mac = get_mac(ip)

        devices.append({
            "ip": ip,
            "hostname": hostname,
            "mac": mac,
            "latency_ms": latency,
            "open_ports": open_ports or []
        })

    return devices


def scan_lan():
    """Trigger LAN scan and return results."""
    local_ip = get_local_ip()

    # Local device info
    try:
        local_hostname = socket.gethostname()
        local_ports = scan_ports(local_ip)
        local_mac = get_mac(local_ip)
    except:
        local_hostname = "Unknown"
        local_ports = []
        local_mac = "Unavailable"

    return {
        "local_device": {
            "ip": local_ip,
            "hostname": local_hostname,
            "mac": local_mac,
            "open_ports": local_ports
        },
        "devices": discover_devices()
    }
