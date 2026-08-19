import socket
import ipaddress
import threading
from urllib.parse import urlparse, urljoin
from contextlib import contextmanager
import httpx
import logging

_dns_patch_lock = threading.RLock()

def resolve_and_validate_ip(hostname: str) -> str:
    """
    Resolves hostname via socket.getaddrinfo and verifies that all resolved IPs
    are public addresses (rejects private, loopback, link-local, and 0.0.0.0).
    Returns the first validated IP string.
    """
    if not hostname:
        raise ValueError("Invalid hostname: empty")

    try:
        addr_info = socket.getaddrinfo(hostname, None)
    except socket.gaierror as e:
        raise ValueError(f"Could not resolve hostname '{hostname}': {e}")

    if not addr_info:
        raise ValueError(f"No IP addresses found for hostname '{hostname}'")

    validated_ip = None
    for family, _, _, _, sockaddr in addr_info:
        ip_str = sockaddr[0]
        try:
            ip = ipaddress.ip_address(ip_str)
        except ValueError as parse_err:
            logging.warning(f"Could not parse IP address string '{ip_str}' for hostname '{hostname}': {parse_err}")
            continue

        if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_unspecified:
            raise ValueError(f"Blocked private/restricted IP target '{ip_str}' for hostname '{hostname}'")

        if validated_ip is None:
            validated_ip = ip_str

    if not validated_ip:
        raise ValueError(f"Could not validate a public IP for hostname '{hostname}'")

    return validated_ip


@contextmanager
def pinned_dns_context(target_host: str, target_ip: str):
    """
    Monkeypatches socket.getaddrinfo for the duration of the context block
    so that requests to `target_host` resolve strictly to `target_ip`.
    This preserves TLS/SNI and Host header behavior while eliminating
    the TOCTOU DNS rebinding vulnerability.

    Thread-safe: uses _dns_patch_lock to prevent concurrent requests from racing.
    """
    with _dns_patch_lock:
        original_getaddrinfo = socket.getaddrinfo

        def patched_getaddrinfo(host, port, family=0, type=0, proto=0, flags=0):
            if host == target_host:
                # Force resolution to target_ip
                return original_getaddrinfo(target_ip, port, family, type, proto, flags)
            return original_getaddrinfo(host, port, family, type, proto, flags)

        socket.getaddrinfo = patched_getaddrinfo
        try:
            yield
        finally:
            socket.getaddrinfo = original_getaddrinfo


def safe_fetch_html(url: str, max_redirects: int = 3, timeout: float = 15.0, max_bytes: int = 5 * 1024 * 1024) -> str:
    """
    Fetches web content securely:
    - Parses scheme (must be http/https) and hostname.
    - Performs atomic DNS resolution & SSRF IP validation per hop.
    - Uses pinned_dns_context so httpx connects to the pre-validated IP while preserving TLS/SNI.
    - Manually follows redirects (up to max_redirects), re-validating each Location header using urljoin.
    - Enforces a response body size limit (max_bytes, default 5MB) via byte streaming.
    """
    current_url = url

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    }

    for redirect_count in range(max_redirects + 1):
        parsed = urlparse(current_url)
        if parsed.scheme not in ("http", "https"):
            raise ValueError(f"Invalid URL scheme '{parsed.scheme}'. Only http and https are allowed.")

        hostname = parsed.hostname
        if not hostname:
            raise ValueError("URL is missing a valid hostname.")

        # 1. Resolve & validate IP
        validated_ip = resolve_and_validate_ip(hostname)

        # 2. Perform request with pinned DNS context & streaming byte cap
        with pinned_dns_context(hostname, validated_ip):
            with httpx.Client(follow_redirects=False, timeout=timeout, verify=True) as client:
                try:
                    with client.stream("GET", current_url, headers=headers) as response:
                        # Check for redirects
                        if response.status_code in (301, 302, 303, 307, 308):
                            location = response.headers.get("Location")
                            if not location:
                                raise ValueError(f"Received redirect status {response.status_code} without Location header.")
                            
                            # Use urljoin for RFC 3986 compliant resolution
                            current_url = urljoin(current_url, location)
                            logging.info(f"Following safe redirect ({redirect_count + 1}/{max_redirects}): -> {current_url}")
                            continue

                        if response.status_code >= 400:
                            raise RuntimeError(f"HTTP {response.status_code} error response from target URL.")

                        content_bytes = bytearray()
                        for chunk in response.iter_bytes(chunk_size=8192):
                            content_bytes.extend(chunk)
                            if len(content_bytes) > max_bytes:
                                logging.warning(f"Response body for '{current_url}' exceeded max limit of {max_bytes} bytes. Truncating.")
                                break

                        encoding = response.encoding or "utf-8"
                        try:
                            return content_bytes.decode(encoding, errors="replace")
                        except Exception:
                            return content_bytes.decode("utf-8", errors="replace")
                except httpx.RequestError as exc:
                    raise RuntimeError(f"HTTP request error fetching '{current_url}': {exc}")

    raise ValueError(f"Exceeded maximum redirect limit of {max_redirects} hops.")

