"""Wrapper tipis untuk macOS Keychain via package ``keyring``.

Lihat .agents/rules/security-and-data.md — nilai secret
TIDAK BOLEH disimpan di SQLite atau file plaintext mana pun.
"""

from __future__ import annotations

import keyring

_SERVICE_NAME = "DevCodex"


def store_secret(key_name: str, value: str) -> None:
    """Simpan secret ke macOS Keychain.

    Args:
        key_name: nama unik untuk secret ini (cocokkan dengan
                  ``ApiRef.keychain_key_name``).
        value: nilai secret yang akan disimpan.
    """
    keyring.set_password(_SERVICE_NAME, key_name, value)


def get_secret(key_name: str) -> str | None:
    """Ambil secret dari macOS Keychain.

    Args:
        key_name: nama unik secret.

    Returns:
        Nilai secret, atau None kalau belum diisi.
    """
    return keyring.get_password(_SERVICE_NAME, key_name)


def delete_secret(key_name: str) -> None:
    """Hapus secret dari macOS Keychain.

    Args:
        key_name: nama unik secret.

    Raises:
        keyring.errors.PasswordDeleteError: kalau key tidak ditemukan.
    """
    keyring.delete_password(_SERVICE_NAME, key_name)


def has_secret(key_name: str) -> bool:
    """Cek apakah secret sudah tersimpan di Keychain.

    Args:
        key_name: nama unik secret.

    Returns:
        True kalau secret ada, False kalau belum diisi.
    """
    return get_secret(key_name) is not None
