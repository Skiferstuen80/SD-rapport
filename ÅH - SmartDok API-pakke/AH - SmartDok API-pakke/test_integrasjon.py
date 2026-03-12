"""
Test av SmartDok API-integrasjon for Aage Haverstad AS
Kjoer: python test_integrasjon.py
"""
import os, sys
from datetime import date, timedelta
sys.path.insert(0, os.path.dirname(__file__))
from smartdok_client import SmartDokClient

CREDENTIALS = os.path.join(os.path.dirname(__file__), "credentials.env")
OK = "[OK]"
FEIL = "[FEIL]"
ADVARSEL = "[ADVARSEL]"
resultater = []

def test(navn, fn, *args, **kwargs):
    try:
        resultat = fn(*args, **kwargs)
        antall = len(resultat) if isinstance(resultat, (list, dict)) else "n/a"
        print(f"  {OK} {navn} ({antall})")
        resultater.append((navn, True, None))
        return resultat
    except Exception as e:
        print(f"  {FEIL} {navn}: {e}")
        resultater.append((navn, False, str(e)))
        return None

def main():
    print("=" * 60)
    print("  SmartDok API-integrasjonstest")
    print("=" * 60)
    print()
    print("[1] Autentisering")
    try:
        client = SmartDokClient.from_env(CREDENTIALS)
        token = client.authenticate()
        print(f"  {OK} authenticate() -> token ({len(token)} tegn)")
        resultater.append(("authenticate", True, None))
    except Exception as e:
        print(f"  {FEIL} authenticate(): {e}")
        resultater.append(("authenticate", False, str(e)))
        print("Kan ikke fortsette uten autentisering.")
        sys.exit(1)

    print()
    print("[2] Selskapsinfo")
    bruker = test("get_current_user", client.get_current_user)
    if bruker:
        print(f"      API-bruker: {bruker.get('Name')} (CompanyId: {bruker.get('CompanyId')})")
    test("get_license_info", client.get_license_info)

    print()
    print("[3] Prosjekter")
    prosjekter = test("get_projects", client.get_projects)
    test("get_projects (all=True)", client.get_projects, all=True)
    neste_nr = test("get_next_project_number", client.get_next_project_number)
    if neste_nr:
        print(f"      Neste prosjektnummer: {neste_nr}")
    test("get_subprojects", client.get_subprojects)
    if prosjekter and isinstance(prosjekter, list) and prosjekter:
        pid = prosjekter[0]["Id"]
        test(f"get_project({pid})", client.get_project, pid)
        test(f"get_subprojects(project_id={pid})", client.get_subprojects, project_id=pid)

    print()
    print("[4] Brukere og organisasjon")
    test("get_users", client.get_users)
    test("get_users (include_ended)", client.get_users, include_ended=True)
    test("get_departments", client.get_departments)
    test("get_groups", client.get_groups)

    print()
    print("[5] Lonnssystem")
    test("get_wages", client.get_wages)
    test("get_additions", client.get_additions)
    test("get_allowances", client.get_allowances)
    test("get_work_descriptions", client.get_work_descriptions)

    print()
    print("[6] Timeregistreringer")
    fra = (date.today() - timedelta(days=7)).isoformat()
    til = date.today().isoformat()
    timer_resp = test("get_work_hours (7d, ikke all)", client.get_work_hours,
                 from_date=fra, to_date=til, fetch_all=False, page_size=10)
    if timer_resp and isinstance(timer_resp, dict):
        print(f"      TotalCount: {timer_resp.get('TotalCount', 0)}")
        items = timer_resp.get("Items", [])
        if items:
            paakrevde = ["Id", "UserId", "Date", "TimeFrom", "TimeTo", "ProjectId", "WageId"]
            mangler = [f for f in paakrevde if f not in items[0]]
            if mangler:
                print(f"  {ADVARSEL} Manglende felt: {mangler}")
            else:
                print(f"  {OK} WorkHours-struktur validert")

    print()
    print("[7] Maskiner")
    test("get_machines", client.get_machines)
    test("get_machines (all=True)", client.get_machines, all=True)

    print()
    print("[8] Varer og materialer")
    test("get_goods_categories", client.get_goods_categories)
    test("get_goods", client.get_goods)
    fra_mnd = (date.today() - timedelta(days=30)).isoformat()
    til_dag = date.today().isoformat()
    test("get_goods_consumption (30d)", client.get_goods_consumption, from_date=fra_mnd, to_date=til_dag)
    test("get_goods_transportation (30d)", client.get_goods_transportation, from_date=fra_mnd, to_date=til_dag)

    print()
    print("[9] RUE (HMS-hendelser)")
    rue = test("get_rue_summaries", client.get_rue_summaries)
    if rue and isinstance(rue, list) and rue:
        rue_id = rue[0]["Id"]
        test(f"get_rue_detail({rue_id})", client.get_rue_detail, rue_id)
        test(f"get_rue_messages({rue_id})", client.get_rue_messages, rue_id)

    print()
    print("[10] QD (kvalitetsavvik)")
    test("get_qd_v2", client.get_qd_v2)
    test("get_qd_v2 (status=Close)", client.get_qd_v2, status="Close")

    print()
    print("[11] SJA")
    sja_fra = (date.today() - timedelta(days=90)).isoformat()
    sja_til = date.today().isoformat()
    test("get_sja_overview (90d)", client.get_sja_overview, from_date=sja_fra, to_date=sja_til)
    test("get_sja_reasons", client.get_sja_reasons)
    test("get_sja_potential_hazards", client.get_sja_potential_hazards)

    print()
    print("[12] Skjemaer")
    test("get_forms_v2", client.get_forms_v2)
    siste_maned = (date.today() - timedelta(days=30)).isoformat()
    skjemaer = test("get_forms_v2 (siste 30d)", client.get_forms_v2, last_updated_since=siste_maned)
    if skjemaer and isinstance(skjemaer, list) and skjemaer:
        form_id = skjemaer[0]["Id"]
        test(f"get_form_elements({form_id})", client.get_form_elements, form_id)

    print()
    print("[13] Faktura")
    test("get_invoices (90d)", client.get_invoices,
         from_date=(date.today() - timedelta(days=90)).isoformat(),
         to_date=date.today().isoformat())

    print()
    print("[14] Re-autentisering")
    try:
        token2 = client.authenticate()
        print(f"  {OK} Re-autentisering ({len(token2)} tegn)")
        resultater.append(("re-authenticate", True, None))
    except Exception as e:
        print(f"  {FEIL} Re-autentisering: {e}")
        resultater.append(("re-authenticate", False, str(e)))

    print()
    print("[15] Hjelpemetoder")
    test("build_user_map", client.build_user_map)
    test("build_project_map", client.build_project_map)
    test("build_machine_map", client.build_machine_map)

    print()
    print("=" * 60)
    print("  TESTRESULTAT")
    print("=" * 60)
    ok_n = sum(1 for _, s, _ in resultater if s)
    feil_n = sum(1 for _, s, _ in resultater if not s)
    print(f"  OK   : {ok_n}")
    print(f"  FEIL : {feil_n}")
    print(f"  Total: {len(resultater)}")
    print()
    if feil_n > 0:
        print("Feilede tester:")
        for navn, ok, msg in resultater:
            if not ok:
                print(f"  - {navn}: {msg}")
        sys.exit(1)
    else:
        print("Alle tester bestatt!")
        sys.exit(0)

if __name__ == "__main__":
    main()
