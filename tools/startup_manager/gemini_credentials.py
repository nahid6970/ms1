"""Windows Credential Manager storage for the Gemini API key."""
from __future__ import annotations

import ctypes
from ctypes import wintypes


_TARGET_NAME = "StartupManager/GeminiApiKey"
_CRED_TYPE_GENERIC = 1
_CRED_PERSIST_LOCAL_MACHINE = 2


class _FileTime(ctypes.Structure):
    _fields_ = [("dwLowDateTime", wintypes.DWORD), ("dwHighDateTime", wintypes.DWORD)]


class _Credential(ctypes.Structure):
    _fields_ = [
        ("Flags", wintypes.DWORD),
        ("Type", wintypes.DWORD),
        ("TargetName", wintypes.LPWSTR),
        ("Comment", wintypes.LPWSTR),
        ("LastWritten", _FileTime),
        ("CredentialBlobSize", wintypes.DWORD),
        ("CredentialBlob", ctypes.POINTER(ctypes.c_ubyte)),
        ("Persist", wintypes.DWORD),
        ("AttributeCount", wintypes.DWORD),
        ("Attributes", ctypes.c_void_p),
        ("TargetAlias", wintypes.LPWSTR),
        ("UserName", wintypes.LPWSTR),
    ]


_advapi = ctypes.WinDLL("Advapi32.dll", use_last_error=True)
_cred_write = _advapi.CredWriteW
_cred_write.argtypes = [ctypes.POINTER(_Credential), wintypes.DWORD]
_cred_write.restype = wintypes.BOOL
_cred_read = _advapi.CredReadW
_cred_read.argtypes = [wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD, ctypes.POINTER(ctypes.POINTER(_Credential))]
_cred_read.restype = wintypes.BOOL
_cred_delete = _advapi.CredDeleteW
_cred_delete.argtypes = [wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD]
_cred_delete.restype = wintypes.BOOL
_cred_free = _advapi.CredFree
_cred_free.argtypes = [ctypes.c_void_p]
_cred_free.restype = None


def save_gemini_api_key(api_key: str) -> None:
    key_bytes = api_key.strip().encode("utf-8")
    if not key_bytes:
        raise ValueError("The API key is empty.")
    blob = ctypes.create_string_buffer(key_bytes)
    credential = _Credential(
        Flags=0,
        Type=_CRED_TYPE_GENERIC,
        TargetName=_TARGET_NAME,
        Comment="Startup Manager Gemini API key",
        LastWritten=_FileTime(0, 0),
        CredentialBlobSize=len(key_bytes),
        CredentialBlob=ctypes.cast(blob, ctypes.POINTER(ctypes.c_ubyte)),
        Persist=_CRED_PERSIST_LOCAL_MACHINE,
        AttributeCount=0,
        Attributes=None,
        TargetAlias=None,
        UserName="Gemini API",
    )
    if not _cred_write(ctypes.byref(credential), 0):
        raise ctypes.WinError(ctypes.get_last_error())


def load_gemini_api_key() -> str:
    credential_pointer = ctypes.POINTER(_Credential)()
    if not _cred_read(_TARGET_NAME, _CRED_TYPE_GENERIC, 0, ctypes.byref(credential_pointer)):
        return ""
    try:
        credential = credential_pointer.contents
        key_bytes = ctypes.string_at(credential.CredentialBlob, credential.CredentialBlobSize)
        return key_bytes.decode("utf-8")
    finally:
        _cred_free(credential_pointer)


def delete_gemini_api_key() -> None:
    if not _cred_delete(_TARGET_NAME, _CRED_TYPE_GENERIC, 0):
        error = ctypes.get_last_error()
        if error != 1168:  # ERROR_NOT_FOUND
            raise ctypes.WinError(error)
