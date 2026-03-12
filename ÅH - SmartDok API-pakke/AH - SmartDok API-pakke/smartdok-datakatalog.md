# SmartDok API — Datakatalog

Oversikt over hvilke data som kan hentes fra SmartDok for Aage Haverstad AS. Ingen tekniske detaljer — kun hva som er tilgjengelig, i hvilke formater, og hva det betyr.

**Sist oppdatert:** Februar 2026 | **Antall datakategorier:** 29 | **API-endepunkter totalt:** 181


---

## 1. Autentisering (Authorize)

Autentisering mot SmartDok API-et.

| Data | Format | Eksempel |
|------|--------|----------|
| API-token innveksling | POST med Token-streng, returnerer session-token som ren tekst | `POST /Authorize/ApiToken` |
| Token-fornyelse | POST for aa fornye session-token | `POST /Authorize/ApiToken/Renew` |
| Offentlige noekler | Liste med RSA-noekler (Exponent + Modulus) | `GET /Authorize/PublicKeys` |

**Praktisk info:**
- Session-token varer ca. 1 time. Ved 401 maa du autentisere paa nytt.
- API-token (i .env-filen) varer ca. 1 aar.
- Responsen fra `/Authorize/ApiToken` er en **ren tekststreng**, ikke et JSON-objekt.


---

## 2. Prosjekter (Projects)

Alle aktive prosjekter i firmaet. Pr. februar 2026: **43 prosjekter**.

| Data | Format | Eksempel |
|------|--------|----------|
| Intern ID | Heltall | 2050085 |
| Prosjektnummer | Tekst (kan ha trailing space!) | 202600 |
| Prosjektnavn | Tekst | 202600 Administasjon 2026 |
| Lokasjon | Tekst | Vinstra, Div |
| Prosjektleder | Navn, epost, mobil | Carl Terje Haug |
| HMS-ansvarlig | UUID (kobles mot bruker) | 08e93173-... |
| KS-ansvarlig | UUID (kobles mot bruker) | 08e93173-... |
| Avdelinger | Liste med ID-er | [398, 395, 18124, 447] |
| Startdato | Dato | 2026-01-01 |
| Sluttdato | Dato eller tom | null |
| Er aktiv | Boolean | true |
| Er fravarsprosjekt | Boolean | false |
| Er ordre | Boolean | false |
| Ordretype-ID | Heltall eller null | null |
| Eksternreferanse | Tekst eller null | null |
| Kunde-ID | Heltall eller null | null |
| Beskrivelse | Tekst | (ofte tom) |
| Opprettet/oppdatert | Dato og tid | 2026-01-05T08:30:51 |
| Tidsforbruk | Desimaltall, timer | 1658.0 |
| CalcuatedTimeConsumption | Desimaltall (alltid 0 — kjent feil, skrivefeil i API) | 0 |
| Internkostnad per time | Desimaltall | 0.0 |
| Timepris | Desimaltall | 0.0 |
| Ferdigstilt | Boolean | false |
| Skal faktureres | Boolean | false |
| GeoLocation | Koordinater eller null | null |
| Tilknyttede brukere | Liste med UUID-er | ["26cb2f01-..."] |
| Fakturaberegningsnotat | Tekst | (ofte tom) |
| Kundeinfo | Firmanavn, kontakt, epost, mobil | (ofte tom) |
| Dokumentlenke | URL eller tom | (ofte tom) |

**Praktisk info:**
- `/Projects` returnerer kun naavarende aktive prosjekter. Historiske RUE/QD-hendelser kan referere til prosjekt-IDer som ikke lenger finnes.
- `ProjectNumber` har ofte **trailing spaces** — alltid `.trim()`.
- `CalcuatedTimeConsumption` og `CalculatedTimeConsumption` finnes begge, begge returnerer 0. Bruk `TimeConsumption` i stedet.
- Ingen server-side filtrering — alle prosjekter returneres. Filtrer i koden.


---

## 3. Delprosjekter (SubProjects)

Delprosjekter knyttet til hovedprosjekter. Pr. februar 2026: **84 delprosjekter**.

| Data | Format | Eksempel |
|------|--------|----------|
| Intern ID | Heltall | 1945306 |
| Prosjekt-ID | Heltall | 1686756 |
| Delprosjektnavn | Tekst | 1 Venabygdsvegen |
| Delprosjektnummer | Tekst | 1 |
| Er aktiv | Boolean | true |
| Startdato | Dato eller null | null |
| Sluttdato | Dato eller null | null |
| Beskrivelse | Tekst | (ofte tom) |
| Kundefirma | Tekst | Gjerdrum Kommune |
| Dokumentlenke | Tekst | (ofte tom) |
| Beregnet timeforbruk | Desimaltall | 0.0 |
| Faktisk tidsforbruk | Desimaltall, timer | 1310.5 |
| Lokasjon | Tekst | (ofte tom) |
| GeoLocation | Koordinater eller null | null |
| Overordnet prosjekt | Objekt med ProjectId, ProjectName, ProjectNumber | {1686756, "240050 Utbedr.tiltak...", "240050"} |
| Oppdatert | Dato og tid | 2024-07-11T13:48:50 |
| Fakturaberegningsnotat | Tekst | Arbeidspakke 1 |
| HMS-ansvarlig | UUID eller null | 08e93173-... |
| KS-ansvarlig | UUID eller null | 08e93173-... |

**Praktisk info:**
- Hvert delprosjekt har et nestet `Project`-objekt med informasjon om hovedprosjektet.
- `CalculatedHourUse` er alltid 0 — bruk `TimeConsumption` for faktisk timeforbruk.
- Filtrering: `subProjectNumber`, `subProjectName`, `all`, `active`, `projectId`, `updatedSince`.
- Kan ogsaa hentes per prosjekt via `/Projects/{projectId}/SubProjects`.


---

## 4. Brukere (Users)

Alle registrerte brukere i SmartDok for firmaet. Pr. februar 2026: **64 brukere**.

| Data | Format | Eksempel |
|------|--------|----------|
| Bruker-ID | UUID | abb1fdd9-be74-42b7-... |
| Navn | Tekst | Lars Erik Bjoerke |
| Brukernavn | Tekst (ofte telefonnummer) | 95925740 |
| Epost | Tekst | larserik.bjorke@gmail.com |
| Telefon | Landskode + nummer | 47 / 95925740 |
| Foedselsdato | Tekst (dd.MM.yyyy) | 01.08.1991 |
| Rolle | Tekst | User, Foreman, ProjectAdministrator, Administrator |
| Tilgangsnivaa-ID | UUID | 63068a29-... |
| Avdeling | ID + navn | 447 / Timeloenn maaned |
| Ansattnummer | Tekst | 120 |
| Eksternt ansattnummer | Tekst | (ofte tom) |
| Gruppe | ID + navn | 11928 / Ansatte Aage Haverstad AS |
| Spraakkode | Tekst | nb-no |
| Er avsluttet | Boolean | false |
| Er utestengt | Boolean | false |
| Er slettet | Boolean | false |
| Er kontaktperson | Boolean | false |
| Ansattkostnad | Desimaltall eller null | null |
| Ressurstype | Tekst eller null | null |
| Kompetanse | Tekst eller null | null |
| Paaroerende 1 | Navn, telefon privat/jobb, relasjon | Gunn Helen Tvete / Samboer |
| Paaroerende 2 | Navn, telefon privat/jobb, relasjon | (valgfritt) |
| Siste aktivitet | Dato og tid | 2026-02-24T15:40:04 |
| Opprettet | Dato og tid | 2012-02-27T17:44:26 |

**Brukere er sentralt for kobling:** UUID-en dukker opp som innmelder, eier, HMS-ansvarlig osv. i alle andre endepunkter.

**Praktisk info:**
- Ingen server-side filtrering — alle brukere returneres. Filtrer i koden.
- Brukere som er merket `IsEnded: true` har sluttet, men er fortsatt i listen.
- Filtrering: `userName`, `name`, `email`, `employeeNo`, `groupId`, `all`, `active`, `includeIsEndedUsers`, `updatedSince`.


---

## 5. Grupper (Groups)

Brukergrupper i SmartDok. Pr. februar 2026: **6 grupper**.

| Data | Format | Eksempel |
|------|--------|----------|
| Intern ID | Heltall | 11928 |
| Navn | Tekst | Ansatte Aage Haverstad AS |

**Grupper i bruk:**
- ADK - Ansatte AH AS
- Ansatte Aage Haverstad AS
- Diett hoey ansatte AH AS
- Groeftarb. - Ansatte AH AS
- Innleide AH AS
- Testgruppe

**Praktisk info:**
- Stoetter `AddUser` og `RemoveUser` for aa legge til/fjerne brukere fra grupper.
- Brukes for aa gruppere ansatte til loennsrelatert logikk (f.eks. diett-grupper).


---

## 6. Avdelinger (Departments)

Avdelingsstruktur i firmaet. Pr. februar 2026: **11 avdelinger**.

| Data | Format | Eksempel |
|------|--------|----------|
| Intern ID | Heltall | 447 |
| Navn | Tekst | Timeloenn maaned |
| Nummer | Tekst | 1 |
| Er aktiv | Boolean | true |
| Oppdatert | Dato og tid eller null | 2024-07-12T08:49:54 |

**Avdelinger i bruk (aktive):**
- 398 / Adm.-Fastloennede (nr. 10)
- 395 / Innleid (nr. 4)
- 18124 / Praksis (nr. 6)
- 447 / Timeloenn maaned (nr. 1)
- 396 / Toemrer (nr. 6)
- 397 / Verksted (nr. 7)

**Praktisk info:**
- Avdelings-ID-er brukes i prosjekter, brukere og timeregistreringer.
- Filtrering: `departmentNumber`, `departmentName`, `all`, `active`.


---

## 7. Roller (Roles) — Deprecated

Tilgjengelige brukerroller i SmartDok. **Endepunktet er markert som Deprecated.**

| Rolle | Beskrivelse |
|-------|-------------|
| User | Vanlig bruker |
| Foreman | Formann/bas |
| ProjectAdministrator | Prosjektadministrator |
| Administrator | Systemadministrator |
| Guest | Gjest |
| EmployeeWithoutAccess | Ansatt uten tilgang |
| SubContractor | Underentreprisoer |

**Praktisk info:**
- Returnerer en enkel liste med roller som tekststrenger (ikke objekter).
- Rollen er ogsaa tilgjengelig per bruker i `/Users`-responsen.


---

## 8. Uoenskede hendelser (RUH/RUE)

Rapporterte HMS-hendelser. Pr. februar 2026: **300 hendelser** totalt.

### Listedata — ny versjon (`/rue/summaries`)

**ANBEFALT:** `/rue/summaries` er det nye (ikke-deprecated) endepunktet for aa hente RUE-lister. Bruker UUID-er i stedet for navn, og inkluderer alvorlighetsgrad og tidsfrist.

| Data | Format | Eksempel |
|------|--------|----------|
| Intern ID | Heltall | 1857498 |
| Hendelsesnummer (EventId) | Heltall | 1299 |
| Tittel | Tekst | "Farlig hoey fart forbi arbeidsplassen" |
| Status | Tekst | Close, Open, New, Unprocessed, Discarded |
| Alvorlighetsgrad | Tekst | High, Medium, Low |
| Innmeldingsdato | Dato og tid | 2026-02-19T10:43:51 |
| Hendelsestidspunkt | Dato og tid | 2026-02-19T10:39:39 |
| Tidsfrist | Dato og tid eller null | null |
| Prosjekt-ID | Heltall | 2040345 |
| Delprosjekt-ID | Heltall eller null | null |
| Eier (UUID) | UUID | 08e93173-... |
| Innmelder (UUID) | UUID | a4e2283d-... |

### Listedata — gammel versjon (`/rue`)

Deprecated, men fungerer fortsatt. Returnerer navn i stedet for UUID-er.

| Data | Format | Eksempel |
|------|--------|----------|
| Intern ID | Heltall | 1464174 |
| Hendelsesnummer (EventId) | Heltall | 1004 |
| Tittel | Tekst | "Uhell" |
| Status | Tekst | Close, Open, New, Unprocessed, Discarded |
| Innmelder | Tekst (navn) | Geir Haansnar |
| Saksbehandler | Tekst (navn) | Therese Silliloekken |
| Innmeldingsdato | Dato og tid | 2024-10-09T10:11:02 |
| Prosjekt | Intern ID (kobles mot Prosjekter) | 1664628 |
| GPS-posisjon | Bredde-/lengdegrad, noeyaktighet | Ofte null |

**Visning:** Hendelse #1004 i UI = EventId 1004 i API.

### Detaljdata (per hendelse)

Hentes via `/rue/{id}` med gyldig ID.

| Data | Format | Eksempel | Merknad |
|------|--------|----------|---------|
| Beskrivelse | Fritekst | "Maskinforer skulle skyve..." | Kan vaere lang og detaljert |
| Alvorlighetsgrad | Tekst | High, Medium, Low | Severity-feltet |
| Hendelsestidspunkt | Dato og tid | 2024-09-16T07:30:00 | Kan avvike fra innmeldingsdato |
| Strakstiltak | Fritekst | "Maa ha kvalifiserte maskinfoerere" | ImmediateMeasuresDescription |
| Permanente tiltak | Fritekst | "" | PermanentMeasuresDescription |
| Konsekvensanalyse | Fritekst | "" | ConsequenceAnalysis |
| Konklusjon | Fritekst | "Soerge for kvalifisert mannskap" | Conclusion |
| Estimert kostnad | Tall eller null | null | |
| Faktisk kostnad | Tall eller null | null | |
| Fravaersdager | Tall eller null | null | |
| Fravaer gjelder | Tekst | NotRelevant | |
| Rapportert av underentreprenor | Boolean | false | |
| Innmelder (UUID) | UUID | 9ca04ec6-... | Kobles mot Users |
| Eier (UUID) | UUID | 08e93173-... | Kobles mot Users |

### Tilleggsendepunkter for RUE

- `/rue/{id}/eventlog` — Hendelseslogg for en RUE
- `/rue/{id}/messages` — Meldinger knyttet til en RUE
- `/rue/{reportId}/pdf` — PDF-rapport for en RUE (stoetter `includeDetails=true`)

### Klassifisering (per hendelse)

Hver hendelse har fire klassifiseringsdimensjoner:

**Type hendelse (EventType):**
- Uoensket hendelse
- Skade paa maskin/utstyr
- Farlig handling
- Farlige forhold
- Observasjon
- Uhell
- Skade paa person
- Trafikkfarlig hendelse
- Klage fra kunde
- Annet

**Hendelsen omfattet (EventInvolved):**
- Utstyr/materiell
- Maskin/bil
- Person(er)
- Miljoe/omgivelser
- Tredjepart
- Arbeidstid
- Ytre miljoe
- Annet

**Aarsak (CauseOfEvent):**
- Menneskelig svikt
- Daarlig orden og ryddighet
- Feil paa utstyr/maskin
- Prosedyrebrudd
- Feil utfoerelse
- Uoppmerksomhet
- Operatoerfeil
- Uklare prosedyrer
- Vaerforhold
- Kollisjon
- Fallende gjenstand
- Slitasje
- Overbelastning
- Vanskelig adkomst
- Haerverk
- Manglende merking
- Mangelfull informasjon
- Manglende paavisning
- Manglende sikring
- Ytre paavirkning
- Glatt underlag
- Feil eller mangler paa utstyr

**Arbeidsoperasjon (WorkOperation):**
- Bruk av anleggsmaskin (Use of construction machinery)
- Arbeid langs vei (WorkOnAlongTheWay)
- (andre verdier avhenger av bedriftens konfigurasjon i SmartDok)

**MERK:** API-et returnerer engelske verdier. Norske oversettelser er dokumentert i den tekniske referansen.


---

## 9. Kvalitetsavvik (QD)

Registrerte kvalitetsavvik. Pr. februar 2026: **26 avvik** totalt.

### Listedata (`/qd`)

| Data | Format | Eksempel |
|------|--------|----------|
| Intern ID | Heltall | 137654 |
| Avviksnummer (EventId) | Heltall | 1002 |
| Tittel | Tekst | "Feil roerdeler" |
| Status | Tekst | Close, Open, Discarded |
| Innmelder | Tekst (navn) | Anders Nord |
| Saksbehandler | Tekst (navn) | Therese Silliloekken |
| Innmeldingsdato | Dato og tid | 2024-11-05T19:19:10 |
| Prosjekt-ID | Heltall | 1674364 |
| Delprosjekt-ID | Heltall eller null | null |
| GPS-posisjon | Bredde-/lengdegrad, noeyaktighet | Ofte null |

**Visning:** Avvik Q-1002 i UI = EventId 1002 i API (uten Q-prefix).

### Detaljdata via v2 (`/qd/v2`)

**NYTT:** `/qd/v2` gir tilgang til detaljdata som tidligere kun var tilgjengelig via PDF. Inkluderer beskrivelse og klassifisering.

| Data | Format | Eksempel |
|------|--------|----------|
| Intern ID | Heltall | 137654 |
| Avviksnummer (EventId) | Heltall | 1002 |
| Tittel | Tekst | "Feil roerdeler" |
| Beskrivelse | Fritekst | "Togfri helg. Feil dimensjon paa Fleksi-Seal..." |
| Status | Tekst | Close, Open, Discarded |
| Innmeldingsdato | Dato og tid | 2024-11-05T19:19:10 |
| Prosjekt-ID | Heltall | 1674364 |
| Delprosjekt-ID | Heltall eller null | null |
| Innmelder | Tekst (navn) | Anders Nord |
| Saksbehandler | Tekst (navn) | Therese Silliloekken |
| GPS-posisjon | Bredde-/lengdegrad, noeyaktighet | Ofte null |
| Aarsak (Cause) | Tekst (norsk) | Feil i leveranse, Feil utfoerelse, Annet |
| Gjelder (Concerning) | Tekst (norsk) | Leverandoer, Egne arbeidere, Utfoerelse |
| Relatert til (RelatesTo) | Tekst (norsk) | Kvalitetssikring, Fremdrift, Kontrakt/standard |

**Praktisk info:**
- `/qd/{id}` returnerer **fortsatt 404** — dette er en kjent API-begrensning. Bruk `/qd/v2` for detaljdata med klassifisering.
- Full QD-rapport kan ogsaa hentes som PDF via `/qd/{id}/pdf`.
- Klassifiseringsverdiene i v2 er paa **norsk** (i motsetning til RUE som bruker engelsk).


---

## 10. SJA (Sikker Jobb Analyse)

SJA-er er en del av Skjemaer (Forms), men har egne endepunkter for oppslagsdata.

### Potensielle farer (`/sja/potential_hazards`)

23 predefinerte faretyper:

| ID | Fare |
|----|------|
| 1 | Sammenstoet/paakjoersel |
| 2 | Konstruksjonssvikt |
| 3 | Brann/eksplosjon |
| 4 | Bevegelige gjenstander/klemfare |
| 5 | Skarp gjenstand (kutt/stikk) |
| 6 | Fallende gjenstand |
| 7 | Fall |
| 8 | Tunge loeft/tunge materialer |
| 9 | Overflater med hoey/lav temperatur |
| 10 | Fare for elektriske stoet |
| 11 | Hoeyt trykk/sprutfare |
| 12 | Stoey/vibrasjon |
| 13 | Straaling |
| 14 | Stoev, roeyk, gasser, giftige stoffer |
| 15 | Mangelfull belysning |
| 16 | Vaerforhold (vind/kulde/taake) |
| 17 | Naturhendelser (flom/ras) |
| 18 | Arbeid i tanker/oksygenmangel |
| 19 | Drukningsfare |
| 20 | Lekkasje |
| 21 | Ytre miljoe |
| 22 | Avsporing |
| 9999 | Annet (spesifiser) |

### Begrunnelser for SJA (`/sja/reasons`)

7 predefinerte begrunnelser:

| ID | Begrunnelse |
|----|-------------|
| 1 | Arbeidet medfoerer avvik fra beskrivelser i prosedyrer og planer |
| 2 | Aktiviteten er ny og ukjent |
| 3 | Folk som ikke kjenner hverandre skal jobbe sammen |
| 4 | Utstyr som arbeidstakerne ikke har erfaring med skal benyttes |
| 5 | Forutsetningene er endret (f.eks. vaerforhold, tilgjengelig tid, rekkefoelje av oppgaver) |
| 6 | Ulykker/uoenskede hendelser har skjedd tidligere ved tilsvarende aktiviteter |
| 9999 | Annet (spesifiser) |

**Praktisk info:**
- Fare- og begrunnelsesdata har Id, Key og Name. Key er en maskinlesbar noekkel (f.eks. `SJA.hazard.fall`).
- Selve SJA-skjemaene hentes via `/Forms` eller `/Forms/v2`.


---

## 11. Skjemaer (Forms)

Utfylte skjemaer fra SmartDok-appen. Dekker SJA, vernerunder, daglige kontroller, egenerklaeringer og mer. Pr. februar 2026: **3993 skjemaer** totalt.

### Versjon 1 (`/Forms`) — Deprecated

**OBS: Endepunktet `GET /Forms` er markert som Deprecated i SmartDoks Swagger-spec (pr. februar 2026).** Det fungerer fortsatt, men bruk helst v2 for nye integrasjoner.

#### Filtreringsmuligheter (v1)

I motsetning til andre endepunkter stoetter Forms server-side filtrering:

| Filter | Beskrivelse | Eksempel |
|--------|-------------|----------|
| Datointervall | Paakreved, maks 32 dager | startDate/endDate |
| Modultype | Prosjekt (1) eller Maskin (2) | moduleId=1 |
| Prosjekt/maskin | Filtrer paa ett prosjekt eller maskin | moduleInstanceId=2037327 |
| Delprosjekt | Filtrer paa delprosjekt | moduleSubInstanceId=123 |
| Skjematype | Filtrer paa en bestemt skjemadefinisjon | formDefinitionId=7521602279564840 |
| Kategori | Filtrer paa skjemakategori | categoryId=1978 |
| Midlertidige | Inkluder midlertidig lagrede skjemaer | temporaryForms=true |

#### Data per skjema (v1)

| Data | Format | Eksempel |
|------|--------|----------|
| Skjema-ID (FormId) | Heltall | 2676649 |
| Skjematype | Tekst | Avviksskjema ledelsessystemer |
| Definisjons-ID (DefFormId) | Stort heltall | 3625216538568122 |
| Utfylt av | Tekst (navn) | Ola Ruststuen |
| Utfylt av (UUID) | UUID | f9f0f776-... |
| Utfyllingsdato | Dato og tid | 2023-11-28T15:13:23 |
| Modultype (ModuleId) | Heltall | 1 (prosjekt) / 2 (maskin) |
| Prosjekt-ID | Heltall | 1590108 |
| Delprosjekt-ID | Heltall eller null | null |
| Maskin-ID | Heltall eller null | null |
| Emne | Tekst | "Virksomhetens kompetansebehov" |
| Loepenummer | Heltall | 9 |
| Midlertidig lagret | Boolean | false |
| Foelg opp senere | Boolean | false |
| Signatur | Navn, epost, bilde-ID | (valgfritt) |
| Skjemastatus-ID | Heltall eller null | null |
| Felter (Elements) | Liste med utfylte felter | Se under |

### Versjon 2 (`/Forms/v2`) — Anbefalt

**NYTT:** Ikke deprecated. Lettere respons (ingen Elements), bedre for listevisning. Pr. februar 2026: **3993 skjemaer** totalt (same som v1).

| Data | Format | Eksempel |
|------|--------|----------|
| Skjema-ID | Heltall | 2676649 |
| Utfylt av | Tekst (navn) | Ola Ruststuen |
| Utfylt av (UUID) | UUID | f9f0f776-... |
| Utfyllingsdato | Dato og tid | 2023-11-28T15:13:23 |
| Emne | Tekst | "Virksomhetens kompetansebehov" |
| Loepenummer | Heltall | 9 |
| Skjemamal-ID (FormTemplateId) | Stort heltall | 3625216538568122 |
| Modultype | Tekst | "Project" eller "Machine" |
| Hovednummer (MainSerialNumber) | Tekst | 47-1683-001522 |
| Prosjekt-ID | Heltall eller null | 1590108 |
| Delprosjekt-ID | Heltall eller null | null |
| Maskin-ID | Heltall eller null | null |
| Sist oppdatert | Dato og tid | 2023-11-28T15:13:23 |

#### Spesialiserte v2-endepunkter

| Endepunkt | Beskrivelse | Antall |
|-----------|-------------|--------|
| `/Forms/v2` | Alle skjemaer | 3993 |
| `/Forms/v2/Project` | Kun prosjektskjemaer | 3480 |
| `/Forms/v2/Machine` | Kun maskinskjemaer | 513 |

**Filtreringsmuligheter (v2):** `lastUpdatedSince`, `offset`, `count`.

### Skjematyper i bruk hos Aage Haverstad AS

| Skjematype | Typisk bruk |
|------------|-------------|
| Daglig kontroll av anleggsmaskin | Daglig sjekkliste foer maskinstart |
| Daglig rapport paa prosjekt | Daglig fremdriftsrapport |
| Egenerklaeering ved sykdom | Sykmeldings-egenerklaeering |
| Sjekkliste komprimering | Kvalitetskontroll komprimering |
| Mottakskontroll | Varemottak |
| Vernerunde | HMS-inspeksjon paa anlegg |
| Dokumentert opplaering graving | Opplaeringsdokumentasjon |
| Grave- og groefteplan | Planlegging gravearbeid |
| Dokumentert sikkerhetsopplaering | Opplaeringsdokumentasjon |
| Sjekkliste Stikkrenne | Kvalitetskontroll VA |
| Ukerapport | Ukentlig prosjektrapport |
| Sjekkliste VA- og stikkledning | Kvalitetskontroll VA |
| Sjekkliste for kum/fundament | Kvalitetskontroll |
| Avviksskjema ledelsessystemer | Internt avvik |
| Avviksrapport Kvalitet | Kvalitetsavvik |

### Utfylte felter per skjema (kun v1)

Hvert skjema i v1 inneholder en liste med utfylte felter (`Elements`):

| Felttype | Dataformat | Eksempel |
|----------|-----------|----------|
| Tekstfelt | Streng | "God fremdrift" |
| Avkrysning | CheckboxValues-liste med booleans | [false, true] = nei/ja |
| Dato | DateValue-streng | "2023-11-14T00:00:00" |
| Tall | Streng | "4" |
| Bilde | Liste med bilde-IDer | [] |
| Signatur | Settings med Name, Email, Url, SignatureId | {Name: "Ola", Url: "https://s3..."} |
| Tabell | Rows-liste med rader | [["P110-P160", "0,20m", "2"]] |
| Nedtrekksmeny | SelectedValue-streng | "2" |

For aa forstaa HVA et felt betyr (hvilken label det har), maa du hente skjemadefinisjonen (`/FormDefinitions/{DefFormId}`).

**Praktisk info:**
- v1 har 32-dagers grense paa datointervall — loop i blokker for lengre perioder.
- v2 har **ingen datogrense**, men stoetter `lastUpdatedSince` for inkrementelle oppdateringer.
- v2 returnerer IKKE skjemafeltene (Elements) — kun metadata. For feltdata, bruk v1 eller hent enkeltskjema.


---

## 12. Skjemadefinisjoner (FormDefinitions)

Maler/definisjoner som beskriver feltene i et skjema.

| Data | Format | Eksempel |
|------|--------|----------|
| Definisjons-ID | Stort heltall | 7589980306400505 |
| Navn | Tekst | Egenerklaeering ved sykdom |
| Dokumentnummer | Tekst | HR-001 |
| Versjon | Tekst | 3.0 |
| Kategori | Tekst | Personal/HR |
| Utarbeidet av | Tekst | Carl-Terje |
| Godkjent av | Tekst | Carl-Terje |

### Feltdefinisjoner

| Data | Format | Eksempel |
|------|--------|----------|
| Felt-ID | Heltall | 4166071 |
| Label | Tekst | "Kan fravaeret skyldes forhold paa arbeidsplassen?" |
| Type | Tekst | TextBox, Checkbox, HeadLine, Picture, Signature, Date, Number, DropDown |
| Paakreved | Boolean | false |
| Rekkefoelje | Heltall | 5 |
| Avkrysningsalternativer | Liste | ["JA", "NEI"] |

**Praktisk info:**
- Hentes med `/FormDefinitions/{DefFormId}` — DefFormId kommer fra skjemaets `DefFormId` (v1) eller `FormTemplateId` (v2).
- Kobling: `FormControlId` i et skjemas Elements → `Id` i FormDefinitions' Elements → gir `Label`.


---

## 13. Maskiner (Machines)

Maskinparken til firmaet. Pr. februar 2026: **185 maskiner**.

| Data | Format | Eksempel |
|------|--------|----------|
| Intern ID | Heltall | 231746 |
| Navn | Tekst | Haandtimer |
| Internnummer | Tekst | H100 |
| Kategori-ID | Heltall | 0 |
| Kategorinavn | Tekst | (ofte tom) |
| Registreringsnummer | Tekst | AE 64850 |
| Beskrivelse | Tekst | (ofte tom) |
| Timer brukt | Heltall | 3408 |
| Kilometerstand | Heltall | 0 |
| Modellaar | Heltall | 0 |
| Lokasjon | Tekst (prosjektnavn) | 202602 Internt arbeid 2026 |
| Lokasjonsdato | Dato og tid | 2026-02-24T00:00:00 |
| Innkjoepsdato | Dato eller null | null |
| Er aktiv | Boolean | true |
| Kommentar | Tekst | (ofte tom) |
| Pris per time | Desimaltall eller null | null |
| Serienummer | Tekst | (ofte tom) |
| Internkostnad | Desimaltall eller null | null |
| Kode | Tekst | (ofte tom) |
| Skjul i transport | Boolean | true |
| Maks tonn | Desimaltall | 0.0 |
| Maks m3 | Desimaltall | 0.0 |
| Bilde-URL | Tekst | (ofte tom) |
| Ansvarlige brukere | Liste med UUID-er | [] |
| Henger | Boolean | false |
| Vis i registreringer | Boolean | true |
| Avdelings-IDer | Liste med heltall | [395, 398, 447, 18124] |

**Praktisk info:**
- `Location` viser **navnet paa prosjektet** maskinen sist var registrert paa, med `LocationDateTime` som dato.
- `CategoryId: 0` betyr ingen kategori (se Maskinkategorier).
- Filtrering: `internalNumber`, `machineName`, `registrationNumber`, `all`, `active`.
- Maskiner kobles til timeregistreringer via `MachineHourRegistrations` i WorkHours.


---

## 14. Maskinkategorier (MachineCategories) — IKKE TILGJENGELIG

**Status: 401 Unauthorized** — Manglende rettighet: `MachineCategoriesRead`.

Endepunktet finnes, men tokenet har ikke tilgang. Stoetter filtrering paa `machineCategoryName`, `all`, `active`, samt CRUD-operasjoner.


---

## 15. Timer v1 og v2 (WorkHours)

Timeregistreringer for alle ansatte. Pr. februar 2026: **157 125 registreringer** totalt.

### Versjon 1 (`/WorkHours`) — Krever datofilter

| Filter | Paakreved | Beskrivelse |
|--------|-----------|-------------|
| fromDate | Ja | Startdato |
| toDate | Ja | Sluttdato |

### Versjon 2 (`/WorkHours/v2`) — Anbefalt

Stoetter paginering (`offset`/`count`) og flere filtre. Gir hele datasettet uten obligatorisk datofilter.

| Data | Format | Eksempel |
|------|--------|----------|
| Intern ID | Heltall | 130176537 |
| Bruker-ID | UUID | 568d8a01-... |
| Dato | Dato (YYYY-MM-DD) | 2026-02-24 |
| Tid fra | Tid (HH:mm:ss) | 13:00:00 |
| Tid til | Tid (HH:mm:ss) | 14:30:00 |
| Pausetid | Tid (HH:mm:ss) | 00:00:00 |
| Pausestart | Tid eller null | null |
| Timebankinnsetning | Tid (HH:mm:ss) | 00:00:00 |
| Prosjekt-ID | Heltall | 2050094 |
| Delprosjekt-ID | Heltall eller null | null |
| Aktivitets-ID (ActivityId) | Heltall | 6367 |
| Aktivitetskategori-ID | Heltall eller null | null |
| Loennsart-ID (WageId) | Heltall | 2844 |
| Loennsartkommentar | Tekst | (ofte tom) |
| Avdelings-ID | Heltall | 447 |
| Omraade-ID | Heltall eller null | null |
| Element-ID | Heltall eller null | null |
| Kommentar | Tekst | "Testing av Hitachi" |
| Admin-kommentar | Tekst eller null | null |
| Tilgjengelighetsvarighet | Tid eller null | null |
| Dagtid-ID | Heltall eller null | null |
| Godtgjoerelses-ID | Heltall eller null | null |
| Godtgjoerelseskommentar | Tekst | (ofte tom) |
| Registreringstype | Tekst | Ordinary |
| Registreringsnummer | Tekst | (ofte tom) |
| Tilleggsregistreringer | Liste med {WageId, Amount, Comment} | [{WageId: 93976, Amount: 0.0}] |
| Maskintimeregistreringer | Liste med {MachineId, Hours} | [{MachineId: 231746, Hours: "01:30:00"}] |
| Sist oppdatert | Dato og tid | 2026-02-24T18:30:17 |

**Praktisk info:**
- v1 krever `fromDate`/`toDate` — gir 400 uten disse.
- v2 stoetter `offset`, `count`, `fromDate`, `toDate`, `userId`, `projectId`, `subProjectId`, `departmentId`, `updatedSince`.
- `MachineHourRegistrations` kobler timer til maskiner — viser hvilken maskin som ble brukt og hvor lenge.
- `AdditionRegistrations` viser tillegg (groeftetillegg, overtid osv.) knyttet til timen.
- `WageId` kobles mot `/Wages` for aa finne loennsartnavn.
- `ActivityId` kobles mot `/WorkDescriptions` for aa finne arbeidsbeskrivelsen.


---

## 16. Loennsarter (Wages)

Loennsarter brukt i timeregistreringer. Pr. februar 2026: **12 loennsarter**.

| Data | Format | Eksempel |
|------|--------|----------|
| Intern ID | Heltall | 2844 |
| Navn | Tekst | Timer loenn |
| Nummer | Tekst | 100 |
| Er fravaer | Boolean | false |
| Er dagtid | Boolean | false |
| Er aktiv | Boolean | true |
| Eksport | Boolean | true |
| Sats | Desimaltall | 0.0 |
| Timekostnad | Desimaltall | 0.0 |
| Internpris | Desimaltall | 0.0 |
| Rekkefoelje | Heltall | 1 |
| Krever kommentar | Boolean | false |

**Loennsarter i bruk (utvalg):**
- 2844 / Timer loenn (nr. 100)
- 2855 / Maskinkost innleide (nr. 155)
- 86023 / Velferdspermisjon (nr. 130) — krever kommentar
- 102285 / Test loennsart (nr. 999)

**Praktisk info:**
- `IsAbsence: true` betyr at loennsarten representerer fravaer.
- `WageId` i WorkHours kobles mot `Id` her for aa finne type registrering.
- Filtrering: `wageNumber`, `wageName`, `all`, `active`.


---

## 17. Tillegg (Additions)

Loennstillegg for timeregistreringer. Pr. februar 2026: **13 tillegg**.

| Data | Format | Eksempel |
|------|--------|----------|
| Intern ID | Heltall | 102333 |
| Nummer | Tekst | 142 |
| Navn | Tekst | Groeftarbeidstillegg |
| Er tillegg (per dag) | Boolean | true |
| Er enhetstillegg (per time) | Boolean | false |
| Er aktiv | Boolean | true |
| Eksport | Boolean | true |
| Sats | Desimaltall | 0.0 |
| Timekostnad | Desimaltall | 15.0 |
| Rekkefoelje | Heltall | 0 |
| Krever kommentar | Boolean | false |
| Er overtid | Boolean | false |

**Tillegg i bruk (utvalg):**
- Groeftarbeidstillegg (kr 15/t)
- ADK-tillegg (kr 15/t)
- Fagorganiseringstillegg (kr 3/t)
- Formannstillegg (kr 15/t)
- Pendler-/skifttillegg (kr 30/t)
- Overtid 50% (kr 144/t) — enhetstillegg
- Overtid 100% (kr 288/t) — enhetstillegg
- Nattillegg (kr 70,35/t) — enhetstillegg
- Tunelltillegg (kr 20/t) — enhetstillegg
- Kloakktillegg (kr 30/t) — enhetstillegg
- Broeyteberedskapshelg (kr 1000/stk) — enhetstillegg

**Praktisk info:**
- `Addition: true` = dagstillegg, `UnitAddition: true` = timetillegg.
- Refereres fra `AdditionRegistrations` i WorkHours via `WageId`.
- Filtrering: `additionNumber`, `additionName`, `onlyAddition`, `onlyUnitAddition`, `all`, `active`.


---

## 18. Godtgjoerelser (Allowance)

Godtgjoerelser (diett o.l.). Pr. februar 2026: **2 godtgjoerelser**.

| Data | Format | Eksempel |
|------|--------|----------|
| Intern ID | Heltall | 238 |
| Navn | Tekst | Brakkediett |
| Nummer | Tekst | 115 |
| Firma-ID | Heltall | 225 |
| Er aktiv | Boolean | true |
| Sats | Desimaltall | 250.0 |
| Rekkefoelje | Heltall | 0 |
| Krever kommentar | Boolean | false |
| Eksport | Boolean | true |

**Godtgjoerelser:**
- 238 / Brakkediett (kr 250)
- 6302 / Diett (kr 400)

**Praktisk info:**
- Refereres fra `AllowanceId` i WorkHours.
- Filtrering: `number`, `name`, `all`, `active`.
- `PUT /Allowance/{id}` er markert som **Deprecated**.


---

## 19. Arbeidsbeskrivelser (WorkDescriptions)

Aktivitetstyper/arbeidsbeskrivelser for timeregistreringer. Pr. februar 2026: **minst 10 aktive arbeidsbeskrivelser**.

| Data | Format | Eksempel |
|------|--------|----------|
| Intern ID | Heltall | 3253 |
| Navn | Tekst | Rigging |
| Nummer | Tekst | 01.1 |
| Er aktiv | Boolean | true |
| Pris | Desimaltall | 0.0 |
| Internsats | Desimaltall | 0.0 |

**Arbeidsbeskrivelser i bruk (utvalg):**
- 1 / Ikke definert (std) (nr. 999)
- 57 / Fravaer (std) (nr. 888)
- 3253 / Rigging (nr. 01.1)
- 3254 / Vegetasjonsrydding (nr. 05.1)
- 3255 / Groeftearbeider (nr. 04)
- 3318 / Graving av groeft (nr. 02.1)
- 6069 / Nedrigging (nr. 01.2)
- 6070 / Graving av trau (nr. 02.2)
- 6071 / Grunnarbeid groeft (nr. 04.1)
- 6072 / Legging av roer (nr. 04.2)

**Praktisk info:**
- `ActivityId` i WorkHours kobles mot `Id` her.
- Filtrering: `workDescriptionNumber`, `workDescriptionName`, `all`, `active`.
- `/WorkDescriptionCategory` returnerer **401** (mangler rettighet: `ActivityCategoriesRead`).


---

## 20. Varer (Goods)

Varelager og materialer. Pr. februar 2026: **225 varer**.

| Data | Format | Eksempel |
|------|--------|----------|
| Intern ID | Heltall | 9030 |
| Navn | Tekst | Pukk 10/16 |
| Nummer | Tekst | 1 |
| Beholdning | Desimaltall | -1680.01 |
| Enhets-ID | Heltall | 5 |
| Enhet | Objekt {Id, Name} | {5, "tonn"} |
| Er aktiv | Boolean | true |
| Er produksjon | Boolean | false |
| Pris | Desimaltall | 135.0 |
| Internkostnad | Desimaltall eller null | null |
| Kategori-ID | Heltall | 1061 |
| Kategori | Objekt {Id, Name, IsProduction, IsActive} | {1061, "Pukk", false, true} |
| Strekkoder | Liste eller null | null |

**Praktisk info:**
- `Amount` kan vaere **negativt** — representerer forbruk/uttak fra lager.
- Kategorier er nestet i hvert vareobjekt, men kan ogsaa hentes separat via `/GoodsCategories`.
- Enheter (Units) hentes via `/Goods/Units`.
- Filtrering: `goodsNumber`, `goodsName`, `all`, `active`.


---

## 21. Varekategorier (GoodsCategories)

Kategorier for varelager. Pr. februar 2026: **17 kategorier**.

| Data | Format | Eksempel |
|------|--------|----------|
| Intern ID | Heltall | 1061 |
| Navn | Tekst | Pukk |
| Er produksjon | Boolean | false |
| Er aktiv | Boolean | true |

**Kategorier i bruk (aktive):**
- Pukk, Forsterkningslag, Grus, Sand, Jord, Baerelag, Stein, Asfalt, Diverse, Blokk, Lagervare, Sams masse, Betong

**Praktisk info:**
- Kan ogsaa hente varer per kategori via `/GoodsCategories/{categoryId}/Goods`.


---

## 22. Vareforbruk (GoodsConsumption)

Registrert vareforbruk paa prosjekter. Pr. februar 2026: **0 registreringer**.

**Praktisk info:**
- Stoetter dato- og prosjektfiltrering (`fromDate`, `toDate`, `projectId`).
- CRUD-operasjoner og `MarkAsExported`.
- Ingen data registrert i systemet pr. naa.


---

## 23. Vareproduksjon (GoodsProduction)

Registrert vareproduksjon. Pr. februar 2026: **0 registreringer**.

**Praktisk info:**
- Stoetter dato- og prosjektfiltrering.
- Har `MarkAsExported`-endepunkt.


---

## 24. Varetransport (GoodsTransportation)

Registrert varetransport. Pr. februar 2026: **0 registreringer**.

**Praktisk info:**
- Stoetter dato- og prosjektfiltrering.
- Har `MarkAsExported`-endepunkt.


---

## 25. Varelokasjoner (GoodsLocations) — IKKE TILGJENGELIG

**Status: 401 Unauthorized** — Manglende rettighet: `GoodsLocationsRead`.

Endepunktet finnes, men tokenet har ikke tilgang. Har ogsaa et `/GoodsLocations/Flows`-endepunkt (ogsaa 401).


---

## 26. Verktoy (Tools) — IKKE TILGJENGELIG

**Status: 401 Unauthorized** — Manglende rettigheter: `ToolsRead`, `ToolCategoriesRead`, `ToolLocationsRead`.

Endepunktene finnes:
- `/Tools` — Hent/opprett verktoy
- `/Tools/{id}` — Hent/oppdater/slett verktoy
- `/Tools/Categories` — Kategorier
- `/Tools/Locations` — Lokasjoner

Men tokenet har ikke tilgang til noen av dem.


---

## 27. Fakturaer (Invoices)

Utgaaende fakturaer. Pr. februar 2026: **0 fakturaer** (tomt resultat).

| Filter | Beskrivelse |
|--------|-------------|
| fromDate | Startdato for fakturadato |
| toDate | Sluttdato for fakturadato |

**Praktisk info:**
- Paginert endepunkt.
- Kan hente enkeltfaktura via `/Invoices/{id}`.
- Ingen data i systemet pr. naa (fakturering haandteres trolig i annet system).


---

## 28. Leverandoerfakturaer (SupplierInvoices)

Inngaaende fakturaer fra leverandoerer.

| Endepunkt | Metode | Beskrivelse |
|-----------|--------|-------------|
| `/SupplierInvoices` | POST | Opprett leverandoerfaktura |
| `/SupplierInvoices` | PUT | Oppdater leverandoerfaktura |
| `/SupplierInvoices/{id}` | GET | Hent leverandoerfaktura |
| `/SupplierInvoices/document/upload` | POST | Last opp fakturadokument |

**Praktisk info:**
- Ingen GET-liste-endepunkt — kun opprett/oppdater/hent-en.
- Dokumentopplasting tar `externalInvoiceNumber` som parameter.
- Det eldre endepunktet `/SupplierInvoices/{externalInvoiceNumber}/document/upload` er **Deprecated**.


---

## 29. Bilder (Pictures)

Bilder knyttet til prosjekter.

| Filter | Beskrivelse |
|--------|-------------|
| projectId | Prosjekt-ID (paakreved, i URL-path) |
| subProjectId | Delprosjekt-ID (valgfritt) |
| fromDate | Startdato (valgfritt) |
| toDate | Sluttdato (valgfritt) |

**Praktisk info:**
- Hentes via `/Pictures/project/{projectId}`.
- Paginert respons.
- Returnerer bildemetadata inkludert nedlastingslenker.


---

## 30. Lisensinfo (LicenseInfo)

Lisensbruk for firmaet.

| Data | Format | Eksempel |
|------|--------|----------|
| Ledige lisenser | Heltall | 1 |
| Totale lisenser | Heltall | 65 |

**Praktisk info:**
- Kun lesing (GET). Viser hvor mange SmartDok-lisenser firmaet har og hvor mange som er ledige.


---

## 31. PDF-rapporter

Tilgjengelig for baade QD og RUE. Stoetter valgfri `includeDetails=true` parameter for aa inkludere ekstra detaljer i rapporten.

| Data | Format | Eksempel |
|------|--------|----------|
| Filstoerrelse | Bytes | 75353 |
| Fildato | Dato og tid | 2025-12-12T14:38:07 |
| Filnavn | Tekst | QD-1027.pdf |
| Nedlastingslenke | Pre-signert S3-URL | https://s3.amazonaws.com/... |

Lenken er gyldig i 24 timer. Ingen autentisering noedvendig for selve nedlastingen.


---

## Endepunkter med begrenset tilgang (401)

Foegende endepunkter returnerer 401 med vaar naavarende API-token. Disse krever ekstra rettigheter som maa aktiveres i SmartDok-administrasjonen:

| Endepunkt | Manglende rettighet | Beskrivelse |
|-----------|---------------------|-------------|
| `/Areas` | AreaRead | Omraader knyttet til delprosjekter |
| `/Customers` | CustomersRead | Kunderegister (CRUD, filtrering) |
| `/GoodsLocations` | GoodsLocationsRead | Varelagerlokasjoner og -flyt |
| `/MachineCategories` | MachineCategoriesRead | Maskinkategorier |
| `/News` | (POST/GET kun) | Nyhetsinnlegg |
| `/Orders` | OrdersRead | Ordrer (ogsaa **Deprecated**) |
| `/OrderTypes` | OrderTypeRead | Ordretyper |
| `/ResourcePlanning/Plans` | ResourcePlanningRead | Ressursplanleggingsblokker |
| `/ResourcePlanning/Resources` | ResourcePlanningRead | Ressurser for planlegging |
| `/Tools` | ToolsRead | Verktoyregister |
| `/Tools/Categories` | ToolCategoriesRead | Verktoykategorier |
| `/Tools/Locations` | ToolLocationsRead | Verktoylokasjoner |
| `/TripToFromWorkAddition` | TripToFromWorkAdditionRead | Reise til/fra jobb-tillegg |
| `/WorkDescriptionCategory` | ActivityCategoriesRead | Arbeidsbeskrivelseskategorier |
| `/v2/orders/{projectId}/workers` | OrderWorkersRead | Ordrearbeidere per prosjekt |


---

## Webhooks

SmartDok stoetter webhooks for hendelsesdrevet integrasjon. Pr. februar 2026: **0 webhooks** konfigurert.


---

## Begrensninger og praktisk info

- **Gamle prosjekter mangler** — `/Projects` returnerer kun naavarende prosjekter. Historiske RUE/QD-hendelser kan referere til prosjekt-IDer som ikke lenger finnes i listen. Haandter manglende match i koden.
- **Begrenset server-side filtrering** — `/Projects`, `/Users`, `/rue` og `/qd` returnerer ALT (filtrer i koden). `/Forms` stoetter derimot filtrering paa modul, prosjekt, skjematype og kategori. `/WorkHours/v2` stoetter dato-, bruker- og prosjektfiltrering.
- **Forms v1 har 32-dagers grense** — Maks datointervall per API-kall er 32 dager. Loop i blokker for lengre perioder. Forms v2 har ingen slik grense.
- **QD detalj via v2** — `/qd/{id}` gir fortsatt 404, men `/qd/v2` gir detaljdata inkludert beskrivelse og klassifisering.
- **RUE bruk summaries** — `/rue/summaries` er det nye endepunktet med UUID-er og alvorlighetsgrad. `/rue` (gammel versjon) bruker navn.
- **Klassifisering kun paa RUE-detalj** — Hendelsestype, aarsak, etc. finnes bare naar du henter `/rue/{id}` (ikke i listen).
- **GPS sjelden tilgjengelig** — De fleste hendelser har null paa Lat/Lon.
- **Skjemadata er ustrukturert** — Feltene i Forms er generiske (TextBoxValue). Du maa koble mot FormDefinitions for aa forstaa hva feltet betyr.
- **Engelske verdier i RUE-API** — Klassifiseringsnavn (EventType, CauseOfEvent etc.) er paa engelsk, mens UI viser norsk. QD v2 bruker derimot norske verdier.
- **Data sendes IKKE i sanntid** — SmartDok er ikke et sanntidssystem. Data oppdateres naar brukere fyller ut skjemaer eller registrerer hendelser.
- **CompanyId 225** — Tokenet er bundet til Aage Haverstad AS. Ingen tilgang til andre firmaers data.
- **Token-levetid** — API-token (i .env) varer 1 aar. Session-token varer ca. 1 time.
- **Forms v1 er Deprecated** — `GET /Forms` er markert som Deprecated i Swagger-spec. Bruk `/Forms/v2` for nye integrasjoner.
- **CalcuatedTimeConsumption** — Skrivefeil i API (mangler 'l'). Begge varianter finnes, begge returnerer 0. Bruk `TimeConsumption`.
- **157 000+ timeregistreringer** — WorkHours v2 returnerer alt. Bruk `offset`/`count` for paginering og filtre for aa begrense data.
- **15 endepunkter returnerer 401** — Se egen tabell over. Krever ekstra rettigheter som kan aktiveres i SmartDok.
