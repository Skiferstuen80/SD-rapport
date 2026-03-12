"""
SmartDok integrasjon for Aage Haverstad AS
Kjoer: python kjor_integrasjon.py
"""
import os, sys
from datetime import date, timedelta
sys.path.insert(0, os.path.dirname(__file__))
from smartdok_client import SmartDokClient

CREDENTIALS = os.path.join(os.path.dirname(__file__), "credentials.env")

def hdr(tekst):
    print()
    print("=" * 60)
    print(f"  {tekst}")
    print("=" * 60)

def main():
    print("Kobler til SmartDok API...")
    client = SmartDokClient.from_env(CREDENTIALS)
    client.authenticate()
    print("Autentisert OK")

    hdr("SELSKAPSINFO")
    bruker = client.get_current_user()
    print(f"API-bruker : {bruker.get('Name')} ({bruker.get('Role')})")
    print(f"Selskap ID : {bruker.get('CompanyId')}")
    lisens = client.get_license_info()
    print(f"Lisenser   : {lisens.get('TotalLicenses')} totalt, {lisens.get('AvailableLicenses')} ledig")

    hdr("PROSJEKTER")
    prosjekter = client.get_projects()
    aktive = sorted(
        [p for p in prosjekter if p.get("IsActive")],
        key=lambda p: p.get("ProjectNumber", "").strip()
    )
    print(f"Aktive prosjekter: {len(aktive)}")
    print(f"{'Nr.':<12} {'Navn':<45} {'Timer':>8}")
    print("-" * 68)
    for p in aktive[:20]:
        nr = p.get("ProjectNumber", "").strip()
        navn = p.get("ProjectName", "")[:44]
        timer = p.get("TimeConsumption", 0)
        print(f"{nr:<12} {navn:<45} {timer:>8.1f}")
    if len(aktive) > 20:
        print(f"  ... og {len(aktive)-20} til")
    neste_nr = client.get_next_project_number()
    print(f"Neste prosjektnummer: {neste_nr}")

    hdr("DELPROSJEKTER")
    delprosjekter = client.get_subprojects()
    aktive_del = [d for d in delprosjekter if d.get("IsActive")]
    print(f"Totalt: {len(delprosjekter)}, aktive: {len(aktive_del)}")
    for d in aktive_del[:5]:
        proj = d.get("Project", {})
        print(f"  {proj.get('ProjectNumber','').strip()} | {d.get('SubProjectName')}")
    if len(aktive_del) > 5:
        print(f"  ... og {len(aktive_del)-5} til")

    hdr("BRUKERE OG ORGANISASJON")
    brukere = client.get_users()
    aktive_brukere = [b for b in brukere if not b.get("IsEnded") and not b.get("IsDeleted")]
    print(f"Brukere totalt: {len(brukere)}, aktive: {len(aktive_brukere)}")
    avdelinger = client.get_departments()
    print(f"Avdelinger: {len(avdelinger)}")
    for avd in avdelinger:
        status = "aktiv" if avd.get("IsActive") else "inaktiv"
        print(f"  {avd.get('Id'):>6} | {avd.get('Name'):<30} ({status})")
    grupper = client.get_groups()
    print(f"Brukergrupper: {len(grupper)}")
    for g in grupper:
        print(f"  {g.get('Id'):>6} | {g.get('Name')}")

    hdr("LONNSSYSTEM")
    lonnsarter = client.get_wages()
    print(f"Lonnsarter: {len(lonnsarter)}")
    for w in lonnsarter[:8]:
        fravr = " [FRAVR]" if w.get("IsAbsence") else ""
        print(f"  {w.get('Number'):<6} {w.get('Name')}{fravr}")
    tillegg = client.get_additions()
    print(f"Tillegg: {len(tillegg)}")
    for t in tillegg[:5]:
        ttype = "fast" if t.get("Addition") else "enhet"
        print(f"  {t.get('Number'):<6} {t.get('Name'):<30} [{ttype}]")
    godtgjorelser = client.get_allowances()
    print(f"Godtgjorelsestyper: {len(godtgjorelser)}")
    aktiviteter = client.get_work_descriptions()
    print(f"Arbeidsbeskrivelser: {len(aktiviteter)}")

    hdr("TIMEREGISTRERINGER (siste 30 dager)")
    til_dato = date.today().isoformat()
    fra_dato = (date.today() - timedelta(days=30)).isoformat()
    print(f"Periode: {fra_dato} til {til_dato}")
    print("Henter timer (kan ta litt tid)...")
    timer = client.get_work_hours(from_date=fra_dato, to_date=til_dato)
    print(f"Timeregistreringer: {len(timer)}")
    if timer:
        total_timer = 0.0
        prosjekt_timer = {}
        maskin_timer_count = 0
        def hms(s):
            if not s:
                return 0.0
            d = s.split(":")
            return int(d[0]) + int(d[1])/60 + int(d[2])/3600
        for t in timer:
            t_sum = hms(t.get("TimeTo","0:0:0")) - hms(t.get("TimeFrom","0:0:0")) - hms(t.get("BreakTime","0:0:0"))
            if t_sum < 0:
                t_sum = 0
            total_timer += t_sum
            pid = t.get("ProjectId")
            prosjekt_timer[pid] = prosjekt_timer.get(pid, 0) + t_sum
            if t.get("MachineHourRegistrations"):
                maskin_timer_count += 1
        print(f"Timer totalt: {total_timer:.1f}h")
        print(f"Registreringer med maskintimer: {maskin_timer_count}")
        print(f"Prosjekter med timer: {len(prosjekt_timer)}")
        proj_map = client.build_project_map()
        topp = sorted(prosjekt_timer.items(), key=lambda x: x[1], reverse=True)[:5]
        print("Topp 5 prosjekter etter timer:")
        for pid, t_sum in topp:
            p = proj_map.get(pid)
            navn = f"{p['ProjectNumber'].strip()} {p['ProjectName']}" if p else str(pid)
            print(f"  {navn[:50]:<50} {t_sum:>6.1f}h")

    hdr("MASKINER OG UTSTYR")
    maskiner = client.get_machines()
    alle_maskiner = client.get_machines(all=True)
    print(f"Aktive: {len(maskiner)}, totalt: {len(alle_maskiner)}")
    for m in maskiner[:8]:
        print(f"  {m.get('InternalNumber',''):<8} {m.get('Name'):<30} {m.get('HoursUsed',0):>6}h")
    if len(maskiner) > 8:
        print(f"  ... og {len(maskiner)-8} til")

    hdr("VARER OG MATERIALER")
    kategorier = client.get_goods_categories()
    print(f"Varekategorier: {len(kategorier)}")
    for kat in kategorier[:6]:
        print(f"  {kat.get('Id'):>6} | {kat.get('Name')}")
    varer = client.get_goods()
    print(f"Varer (aktive): {len(varer)}")

    hdr("HMS - RUE (uonsket hendelser)")
    rue_liste = client.get_rue_summaries()
    print(f"RUE totalt: {len(rue_liste)}")
    status_teller = {}
    alvorlighet_teller = {}
    for r in rue_liste:
        s = r.get("Status", "Ukjent")
        a = r.get("Severity", "Ukjent")
        status_teller[s] = status_teller.get(s, 0) + 1
        alvorlighet_teller[a] = alvorlighet_teller.get(a, 0) + 1
    print("Status-fordeling:")
    for s, n in sorted(status_teller.items()):
        print(f"  {s:<15} {n:>4}")
    print("Alvorlighetsgrad:")
    for a, n in sorted(alvorlighet_teller.items()):
        print(f"  {a:<15} {n:>4}")
    apne_rue = [r for r in rue_liste if r.get("Status") in ("Open", "New", "Unprocessed")]
    print(f"Apne/nye RUE: {len(apne_rue)}")
    for r in sorted(apne_rue, key=lambda x: x.get("SubmitDate",""), reverse=True)[:5]:
        print(f"  #{r.get('EventId'):<5} {r.get('Title','')[:45]:<45} [{r.get('Severity','')}]")

    hdr("HMS - QD (kvalitetsavvik)")
    qd_liste = client.get_qd_v2()
    print(f"QD totalt: {len(qd_liste)}")
    qd_status = {}
    for q in qd_liste:
        s = q.get("Status", "Ukjent")
        qd_status[s] = qd_status.get(s, 0) + 1
    for s, n in sorted(qd_status.items()):
        print(f"  {s:<15} {n:>4}")

    hdr("SJA (siste 90 dager)")
    sja_fra = (date.today() - timedelta(days=90)).isoformat()
    sja_til = date.today().isoformat()
    sja_liste = client.get_sja_overview(from_date=sja_fra, to_date=sja_til)
    print(f"SJA-analyser: {len(sja_liste)}")
    for s in sja_liste[:5]:
        status_tekst = "Godkjent" if s.get("Status") == 1 else "Ubehandlet"
        print(f"  {s.get('SerialNumber',''):<8} {s.get('Title','')[:40]:<40} [{status_tekst}]")
    if len(sja_liste) > 5:
        print(f"  ... og {len(sja_liste)-5} til")

    hdr("SKJEMAER")
    skjemaer = client.get_forms_v2()
    print(f"Skjemaer totalt: {len(skjemaer)}")
    skjema_typer = {}
    for s in skjemaer:
        navn = s.get("Subject") or "(ingen tittel)"
        skjema_typer[navn] = skjema_typer.get(navn, 0) + 1
    topp_skjema = sorted(skjema_typer.items(), key=lambda x: x[1], reverse=True)[:5]
    print("Vanligste skjemaer:")
    for navn, antall in topp_skjema:
        print(f"  {antall:>5}x {navn[:50]}")

    hdr("OPPSUMMERING")
    print(f"  Prosjekter (aktive)   : {len(aktive)}")
    print(f"  Delprosjekter (aktive): {len(aktive_del)}")
    print(f"  Brukere (aktive)      : {len(aktive_brukere)}")
    print(f"  Maskiner (aktive)     : {len(maskiner)}")
    print(f"  Varer                 : {len(varer)}")
    print(f"  RUE totalt            : {len(rue_liste)}")
    print(f"  QD totalt             : {len(qd_liste)}")
    print(f"  SJA siste 90 dager    : {len(sja_liste)}")
    print(f"  Skjemaer totalt       : {len(skjemaer)}")
    print()
    print("Integrasjon fullfort.")

if __name__ == "__main__":
    main()
