"""
Credential fetch + decrypt.
Key moved to .env: CRED_ENCRYPT_KEY (required), CRED_API_URL (optional).
"""

import hashlib
import os

import httpx
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


_CRED_ENCRYPT_KEY = os.getenv("CRED_ENCRYPT_KEY")
if not _CRED_ENCRYPT_KEY:
    import warnings
    warnings.warn("CRED_ENCRYPT_KEY not set — credential commands will fail at runtime", stacklevel=2)

_CRED_SALT = b"amethyst-salt"
_CRED_API = os.getenv("CRED_API_URL", "http://103.107.205.86:3000/api/config/credential")


def _cred_derive_key(secret: str) -> bytes:
    if not secret:
        raise RuntimeError("CRED_ENCRYPT_KEY is not set. Add it to .env")
    return hashlib.scrypt(
        secret.encode(), salt=_CRED_SALT, n=16384, r=8, p=1, dklen=32
    )


def _cred_decrypt(packed_hex: str) -> str:
    key = _cred_derive_key(_CRED_ENCRYPT_KEY)
    raw = bytes.fromhex(packed_hex)
    iv = raw[:16]
    auth_tag = raw[16:32]
    ciphertext = raw[32:]
    aesgcm = AESGCM(key)
    plaintext = aesgcm.decrypt(iv, ciphertext + auth_tag, None)
    return plaintext.decode("utf-8")


def get_credential(name: str) -> dict:
    """Synchronous version — use only outside async context (e.g. scripts)."""
    import requests
    resp = requests.get(f"{_CRED_API}?name={name}", timeout=10)
    resp.raise_for_status()
    data = resp.json()["data"]
    return {
        "username": data["username"],
        "password": _cred_decrypt(data["password"]),
    }


async def get_credential_async(name: str) -> dict:
    """Async version — used by cmd_get_credentials to avoid blocking the event loop."""
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(f"{_CRED_API}?name={name}")
        resp.raise_for_status()
        data = resp.json()["data"]
        return {
            "username": data["username"],
            "password": _cred_decrypt(data["password"]),
        }
