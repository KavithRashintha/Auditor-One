import socket
import ipaddress
from urllib.parse import urlparse
from fastapi import HTTPException

def validate_url(url: str) -> str:
    """
    Validates a URL to prevent Server-Side Request Forgery (SSRF).
    Raises FastAPI HTTPException if the URL is invalid or points to a restricted IP.
    """
    try:
        parsed = urlparse(url)
    except Exception:
        raise HTTPException(status_code=403, detail="SSRF Guard Triggered: Invalid target destination.")

    if parsed.scheme not in ("http", "https"):
        raise HTTPException(status_code=403, detail="SSRF Guard Triggered: Invalid target destination.")

    hostname = parsed.hostname
    if not hostname:
        raise HTTPException(status_code=403, detail="SSRF Guard Triggered: Invalid target destination.")

    try:
        resolved_ip = socket.gethostbyname(hostname)
        ip = ipaddress.ip_address(resolved_ip)
    except Exception:
        raise HTTPException(status_code=403, detail="SSRF Guard Triggered: Invalid target destination.")

    if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_multicast:
        raise HTTPException(status_code=403, detail="SSRF Guard Triggered: Invalid target destination.")

    if str(ip) == "169.254.169.254":
        raise HTTPException(status_code=403, detail="SSRF Guard Triggered: Invalid target destination.")

    return url
