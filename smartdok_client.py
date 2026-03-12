"""
Convenience wrapper around SmartDokClient.

Provides module-level functions used by hms_report/ so that the package
can simply ``from smartdok_client import get_rue_summaries, ...``.

The singleton client is lazily initialised from environment variables
(SMARTDOK_API_TOKEN / SMARTDOK_BASE_URL) or from the .env.local file
in the project root.
"""

from __future__ import annotations

import importlib.util
import os
from pathlib import Path
from typing import Optional

# Load the original SmartDokClient class by file path to avoid circular import
_ORIG_PATH = (
    Path(__file__).resolve().parent
    / "ÅH - SmartDok API-pakke"
    / "AH - SmartDok API-pakke"
    / "smartdok_client.py"
)
_spec = importlib.util.spec_from_file_location("_smartdok_orig", str(_ORIG_PATH))
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
_SmartDokClient = _mod.SmartDokClient

_client: Optional[_SmartDokClient] = None


def _get_client():
    global _client
    if _client is not None:
        return _client

    token = os.environ.get("SMARTDOK_API_TOKEN", "")
    base_url = os.environ.get("SMARTDOK_BASE_URL", "https://api.smartdok.no")

    # Fallback: try .env.local in project root
    if not token:
        env_path = Path(__file__).resolve().parent / ".env.local"
        if env_path.exists():
            for line in env_path.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" in line:
                    key, _, value = line.partition("=")
                    os.environ.setdefault(key.strip(), value.strip())
            token = os.environ.get("SMARTDOK_API_TOKEN", "")
            base_url = os.environ.get("SMARTDOK_BASE_URL", base_url)

    if not token:
        raise RuntimeError(
            "SMARTDOK_API_TOKEN ikke satt. Sett miljovariabel eller opprett .env.local"
        )

    _client = _SmartDokClient(api_token=token, base_url=base_url)
    return _client


# ---- Convenience functions ----

def get_projects(**kw):
    return _get_client().get_projects(**kw)


def get_users(**kw):
    return _get_client().get_users(**kw)


def get_rue_summaries(**kw):
    return _get_client().get_rue_summaries(**kw)


def get_rue_detail(rue_id: int):
    return _get_client().get_rue_detail(rue_id)


def get_qd_list_v2(**kw):
    return _get_client().get_qd_v2(**kw)


def get_sja_overview(from_date: str, to_date: str):
    return _get_client().get_sja_overview(from_date, to_date)


def get_forms(from_date: str, to_date: str):
    return _get_client().get_forms_v2(last_updated_since=from_date)
