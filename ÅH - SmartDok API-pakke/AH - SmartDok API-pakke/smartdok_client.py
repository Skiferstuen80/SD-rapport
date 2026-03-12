"""
SmartDok API-klient for Aage Haverstad AS (CompanyId: 225)

Autentisering: POST /Authorize/ApiToken -> session-token (~1 time)
Session-token brukes som Bearer token pa alle kall.
Ved 401: autentiser pa nytt automatisk.
"""

import os
import time
import requests
from typing import Any, Optional


BASE_URL = "https://api.smartdok.no"
TIMEOUT = 30


def _load_env(env_path: str) -> dict:
    env = {}
    if not os.path.exists(env_path):
        return env
    with open(env_path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                key, _, value = line.partition("=")
                env[key.strip()] = value.strip()
    return env


class SmartDokClient:

    def __init__(self, api_token: str, base_url: str = BASE_URL):
        self.api_token = api_token
        self.base_url = base_url.rstrip("/")
        self.session_token: Optional[str] = None
        self._token_fetched_at: Optional[float] = None
        self._session = requests.Session()

    @classmethod
    def from_env(cls, env_path: str) -> "SmartDokClient":
        env = _load_env(env_path)
        api_token = env.get("SMARTDOK_API_TOKEN", "")
        base_url = env.get("SMARTDOK_BASE_URL", BASE_URL)
        if not api_token:
            raise ValueError(f"SMARTDOK_API_TOKEN mangler i {env_path}")
        return cls(api_token=api_token, base_url=base_url)

    def authenticate(self) -> str:
        url = f"{self.base_url}/Authorize/ApiToken"
        resp = self._session.post(
            url,
            json={"Token": self.api_token},
            headers={"Content-Type": "application/json"},
            timeout=TIMEOUT,
        )
        resp.raise_for_status()
        token = resp.json()
        if not isinstance(token, str):
            raise RuntimeError(f"Uventet respons: {token!r}")
        self.session_token = token
        self._token_fetched_at = time.time()
        return token

    def _is_token_valid(self) -> bool:
        if not self.session_token or self._token_fetched_at is None:
            return False
        return (time.time() - self._token_fetched_at) < (55 * 60)

    def _ensure_authenticated(self):
        if not self._is_token_valid():
            self.authenticate()

    def _auth_headers(self) -> dict:
        return {"Authorization": f"Bearer {self.session_token}"}

    def _get(self, endpoint: str, params: Optional[dict] = None) -> Any:
        self._ensure_authenticated()
        url = f"{self.base_url}/" + endpoint.lstrip("/")
        resp = self._session.get(url, headers=self._auth_headers(), params=params, timeout=TIMEOUT)
        if resp.status_code == 401:
            self.authenticate()
            resp = self._session.get(url, headers=self._auth_headers(), params=params, timeout=TIMEOUT)
        resp.raise_for_status()
        return resp.json()

    def _post(self, endpoint: str, data: Any = None, params: Optional[dict] = None) -> Any:
        self._ensure_authenticated()
        url = f"{self.base_url}/" + endpoint.lstrip("/")
        headers = {**self._auth_headers(), "Content-Type": "application/json"}
        resp = self._session.post(url, headers=headers, json=data, params=params, timeout=TIMEOUT)
        if resp.status_code == 401:
            self.authenticate()
            headers = {**self._auth_headers(), "Content-Type": "application/json"}
            resp = self._session.post(url, headers=headers, json=data, params=params, timeout=TIMEOUT)
        resp.raise_for_status()
        if resp.text.strip():
            return resp.json()
        return None

    def _get_all_pages(self, endpoint: str, params: Optional[dict] = None, page_size: int = 100) -> list:
        params = dict(params or {})
        params["count"] = page_size
        params["offset"] = 0
        all_items = []
        while True:
            data = self._get(endpoint, params)
            if not isinstance(data, dict) or "Items" not in data:
                return data if isinstance(data, list) else [data]
            items = data.get("Items", [])
            all_items.extend(items)
            total = data.get("TotalCount", len(all_items))
            if len(all_items) >= total:
                break
            params["offset"] += page_size
        return all_items

    # --- Selskapsinfo ---

    def get_current_user(self) -> dict:
        return self._get("/Users/current")

    def get_license_info(self) -> dict:
        return self._get("/LicenseInfo")

    # --- Prosjekter ---

    def get_projects(self, all: bool = False) -> list:
        params = {"all": "true"} if all else {}
        return self._get_all_pages("/Projects", params)

    def get_project(self, project_id: int) -> dict:
        return self._get(f"/Projects/{project_id}")

    def get_next_project_number(self) -> str:
        return self._get("/Projects/NextProjectNumber")

    def get_subprojects(self, project_id: Optional[int] = None, all: bool = False,
                        updated_since: Optional[str] = None) -> list:
        params = {}
        if all:
            params["all"] = "true"
        if updated_since:
            params["updatedSince"] = updated_since
        if project_id:
            return self._get_all_pages(f"/Projects/{project_id}/SubProjects", params)
        return self._get_all_pages("/SubProjects", params)

    # --- Brukere og organisasjon ---

    def get_users(self, include_ended: bool = False) -> list:
        params = {"includeIsEndedUsers": "true"} if include_ended else {}
        return self._get_all_pages("/Users", params)

    def get_departments(self, all: bool = True) -> list:
        params = {"all": "true"} if all else {}
        return self._get_all_pages("/Departments", params)

    def get_groups(self) -> list:
        return self._get("/Group")

    # --- Lonnssystem ---

    def get_wages(self, all: bool = True) -> list:
        params = {"all": "true"} if all else {}
        return self._get("/Wages", params)

    def get_additions(self, all: bool = True) -> list:
        params = {"all": "true"} if all else {}
        return self._get("/Additions", params)

    def get_allowances(self) -> list:
        return self._get_all_pages("/Allowance")

    def get_work_descriptions(self, all: bool = True) -> list:
        params = {"all": "true"} if all else {}
        return self._get("/WorkDescriptions", params)

    # --- Timeregistrering ---

    def get_work_hours(self, from_date: Optional[str] = None, to_date: Optional[str] = None,
                       project_id: Optional[int] = None, sub_project_id: Optional[int] = None,
                       approved: Optional[bool] = None, absence: Optional[bool] = None,
                       last_updated: Optional[str] = None, fetch_all: bool = True,
                       page_size: int = 100) -> list:
        params = {}
        if from_date:
            params["fromDate"] = from_date
        if to_date:
            params["toDate"] = to_date
        if project_id:
            params["projectId"] = project_id
        if sub_project_id:
            params["subProjectId"] = sub_project_id
        if approved is not None:
            params["approved"] = str(approved).lower()
        if absence is not None:
            params["absence"] = str(absence).lower()
        if last_updated:
            params["lastUpdated"] = last_updated
        if fetch_all:
            return self._get_all_pages("/WorkHours/v2", params, page_size=page_size)
        params.update({"count": page_size, "offset": 0})
        return self._get("/WorkHours/v2", params)

    # --- Maskiner ---

    def get_machines(self, all: bool = False) -> list:
        params = {"all": "true"} if all else {}
        return self._get_all_pages("/Machines", params)

    # --- Varer og materialer ---

    def get_goods(self, all: bool = False) -> list:
        params = {"all": "true"} if all else {}
        return self._get_all_pages("/Goods", params)

    def get_goods_categories(self) -> list:
        return self._get("/GoodsCategories")

    def get_goods_consumption(self, from_date: Optional[str] = None, to_date: Optional[str] = None,
                              project_id: Optional[int] = None) -> list:
        params = {}
        if from_date:
            params["fromDate"] = from_date
        if to_date:
            params["toDate"] = to_date
        if project_id:
            params["projectId"] = project_id
        return self._get_all_pages("/GoodsConsumption", params)

    def get_goods_transportation(self, from_date: Optional[str] = None, to_date: Optional[str] = None,
                                 project_id: Optional[int] = None) -> list:
        params = {}
        if from_date:
            params["fromDate"] = from_date
        if to_date:
            params["toDate"] = to_date
        if project_id:
            params["projectId"] = project_id
        return self._get_all_pages("/GoodsTransportation", params)

    # --- RUE (HMS-hendelser) ---

    def get_rue_summaries(self, project_id: Optional[int] = None, status: Optional[str] = None,
                          last_updated_since: Optional[str] = None) -> list:
        """Status: New, Open, Close, Discarded, Unprocessed"""
        params = {}
        if project_id:
            params["ProjectId"] = project_id
        if status:
            params["RueStatus"] = status
        if last_updated_since:
            params["LastUpdatedSince"] = last_updated_since
        return self._get_all_pages("/rue/summaries", params)

    def get_rue_detail(self, rue_id: int) -> dict:
        return self._get(f"/rue/{rue_id}")

    def get_rue_messages(self, rue_id: int) -> list:
        return self._get(f"/rue/{rue_id}/messages")

    # --- QD (Kvalitetsavvik) ---

    def get_qd_v2(self, project_id: Optional[int] = None, status: Optional[str] = None,
                  last_updated_since: Optional[str] = None) -> list:
        """Status: Unprocessed, Open, Close, Discarded"""
        params = {}
        if project_id:
            params["projectId"] = project_id
        if status:
            params["qdStatus"] = status
        if last_updated_since:
            params["lastUpdatedSince"] = last_updated_since
        return self._get_all_pages("/qd/v2", params)

    # --- SJA (Sikker Jobb Analyse) ---

    def get_sja_overview(self, from_date: str, to_date: str) -> list:
        """POST-endepunkt. Returnerer listen fra .NET backing field."""
        data = self._post("/sja/overview", data={"fromDate": from_date, "toDate": to_date})
        if isinstance(data, dict):
            for value in data.values():
                if isinstance(value, list):
                    return value
        return data if isinstance(data, list) else []

    def get_sja_reasons(self) -> list:
        return self._get("/sja/reasons")

    def get_sja_potential_hazards(self) -> list:
        return self._get("/sja/potential_hazards")

    # --- Skjemaer (Forms) ---

    def get_forms_v2(self, last_updated_since: Optional[str] = None,
                     project_id: Optional[int] = None) -> list:
        """Anbefalt skjema-endepunkt. Ingen 32-dagers grense."""
        params = {}
        if last_updated_since:
            params["lastUpdatedSince"] = last_updated_since
        endpoint = "/Forms/v2"
        if project_id:
            endpoint = "/Forms/v2/Project"
            params["projectId"] = project_id
        return self._get_all_pages(endpoint, params)

    def get_form_elements(self, form_id: int) -> list:
        return self._get(f"/Forms/v2/{form_id}/elements")

    # --- Faktura ---

    def get_invoices(self, from_date: Optional[str] = None, to_date: Optional[str] = None) -> list:
        params = {}
        if from_date:
            params["fromDate"] = from_date
        if to_date:
            params["toDate"] = to_date
        result = self._get("/Invoices", params)
        return result if isinstance(result, list) else result.get("Items", [])

    # --- Hjelpemetoder for mapping ---

    def build_user_map(self) -> dict:
        return {u["Id"]: u for u in self.get_users(include_ended=True)}

    def build_project_map(self) -> dict:
        return {p["Id"]: p for p in self.get_projects(all=True)}

    def build_machine_map(self) -> dict:
        return {m["Id"]: m for m in self.get_machines(all=True)}
