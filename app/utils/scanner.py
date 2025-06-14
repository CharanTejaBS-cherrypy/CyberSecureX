import socket
import ssl
import httpx


async def scan_website(target):
    report = {
        "target": target,
        "ip_address": None,
        "https_valid": None,
        "http_headers": {},
        "errors": [],
    }

    # DNS Resolution
    try:
        ip = socket.gethostbyname(target)
        report["ip_address"] = ip
    except Exception as e:
        report["errors"].append(f"DNS error: {e}")
        return report

    # SSL Certificate Check
    try:
        context = ssl.create_default_context()
        with socket.create_connection((target, 443), timeout=3) as sock:
            with context.wrap_socket(sock, server_hostname=target) as ssock:
                cert = ssock.getpeercert()
                report["https_valid"] = True if cert else False
    except Exception as e:
        report["https_valid"] = False
        report["errors"].append(f"SSL error: {e}")

    # Fetch HTTP Headers
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"https://{target}", timeout=5)
            report["http_headers"] = dict(resp.headers)
    except Exception as e:
        report["errors"].append(f"HTTP fetch error: {e}")

    return report
