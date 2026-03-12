# SmartDok API — Teknisk referanse

Denne filen inneholder alt en utvikler eller AI trenger for aa bygge en integrasjon mot SmartDok API for Aage Haverstad AS (CompanyId: 225) fra scratch.

## Autentisering — Proprietaer token-bytte

SmartDok bruker en enkel 2-stegs autentisering: send et langtlevende API-token, faa tilbake et kortlevende session-token.

### Steg 1: Hent session-token

```
POST https://api.smartdok.no/Authorize/ApiToken
Content-Type: application/json

{"Token": "<SMARTDOK_API_TOKEN fra .env>"}
```

Respons:
```json
"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**VIKTIG:** Responsen er en **ren streng** (JSON string), ikke et JSON-objekt. Mange JSON-parsere haandterer dette automatisk, men viss du parser manuelt, husk at det er en streng i anfoeselstegn.

### Steg 2: Bruk session-token paa alle kall

```
GET https://api.smartdok.no/<endepunkt>
Authorization: Bearer <session-token>
```

### Token-levetid

- **API-token** (i .env): Gyldig 1 aar. Genereres i SmartDok-administrasjon.
- **Session-token**: Ca. 1 time. Ingen refresh-mekanisme — hent nytt ved utloep.

### Feilhaandtering auth

Ved 401 paa et API-kall: session-token er utloept. Autentiser paa nytt med API-tokenet.

---

## API-kall

Alle kall bruker Bearer token:

```
GET https://api.smartdok.no/<endepunkt>
Authorization: Bearer <session-token>
```

Timeout: 30 sekunder anbefalt.

---

## Paginering

Alle listeendepunkter returnerer:

```json
{
  "Count": 43,
  "Offset": 0,
  "TotalCount": 43,
  "Items": [...]
}
```

- `Count`: Antall Items i denne responsen
- `Offset`: Gjeldende offset
- `TotalCount`: Totalt antall poster (bruk for aa sjekke om det finnes mer data)
- Bruk `?offset=N&count=M` for aa paginere

Eksempel paa pagineringslogikk:
```javascript
let offset = 0;
const count = 100;
let all = [];
while (true) {
  const data = await api(session, `/rue?offset=${offset}&count=${count}`);
  all = all.concat(data.Items);
  if (all.length >= data.TotalCount) break;
  offset += count;
}
```

**MERK:** Noen endepunkter returnerer rene arrays (ikke paginert wrapper), f.eks. `/Additions`, `/Wages`, `/WorkDescriptions`, `/GoodsCategories`, `/Group`, `/Goods/Units`, `/Roles`, `/Authorize/PublicKeys`, `/sja/reasons`, `/sja/potential_hazards`, `/GoodsProduction`. Disse returnerer alle poster i en enkelt respons uten `Count`/`Offset`/`TotalCount`-wrapping.

---

## Responseksempler (live data, hentet 2026-02-24)

### /Projects

```json
{
  "Count": 43,
  "Offset": 0,
  "TotalCount": 43,
  "Items": [
    {
      "Id": 2050085,
      "ProjectName": "202600 Administasjon 2026",
      "ProjectNumber": "202600",
      "Departments": [398, 395, 18124, 447],
      "IsAbsenceProject": false,
      "IsActive": true,
      "IsOrder": false,
      "OrderTypeId": null,
      "ExternalReference": null,
      "CustomerId": null,
      "StartDate": "2026-01-01T00:00:00",
      "EndDate": null,
      "Location": "Vinstra",
      "ProjectOwnerName": "Carl Terje Haug",
      "ProjectOwnerEmail": "carl-te@aage-haverstad.no",
      "ProjectOwnerMobile": "+4790101685",
      "ClientCompanyName": "",
      "ClientCompanyContact": "",
      "ClientCompanyEmail": "",
      "ClientCompanyMobile": "",
      "DescriptionText": "",
      "DocumentUrl": "",
      "CalcuatedTimeConsumption": 0,
      "CalculatedTimeConsumption": 0,
      "InternalCostPerHour": 0,
      "HourlyRate": 0,
      "Finished": false,
      "ToBeInvoiced": false,
      "GeoLocation": null,
      "UserIds": ["26cb2f01-756d-422c-b0c1-1af6803776cd"],
      "Updated": "2026-01-05T08:32:55.293",
      "Created": "2026-01-05T08:30:51.98",
      "InvoiceCalculationNote": "",
      "HSEResponsibleId": "08e93173-2601-4420-984d-87e837275588",
      "QAResponsibleId": "08e93173-2601-4420-984d-87e837275588",
      "TimeConsumption": 1578.5
    }
  ]
}
```

### /Projects/NextProjectNumber

Returnerer neste ledige prosjektnummer som en ren streng:

```json
"260009"
```

Nyttig for automatisk nummerering ved opprettelse av nye prosjekter.

### /SubProjects (delprosjekter)

**84 delprosjekter** paa tvers av alle prosjekter.

**Server-side filtreringsparametere:**

| Parameter | Type | Beskrivelse |
|-----------|------|-------------|
| `subProjectNumber` | string | Filtrer paa delprosjektnummer |
| `subProjectName` | string | Filtrer paa delprosjektnavn |
| `all` | boolean | Inkluder inaktive (default: kun aktive) |
| `active` | boolean | Filtrer paa aktiv-status |
| `updatedSince` | string (ISO 8601) | Kun delprosjekter oppdatert etter denne datoen |

Delprosjekter kan ogsaa hentes per prosjekt via `GET /Projects/{projectId}/SubProjects` med samme filtreringsparametere.

```json
{
  "Count": 84,
  "Offset": 0,
  "TotalCount": 84,
  "Items": [
    {
      "Id": 1945306,
      "ProjectId": 1686756,
      "SubProjectName": "1 Venabygdsvegen",
      "SubProjectNumber": "1",
      "IsActive": true,
      "StartDate": null,
      "EndDate": null,
      "DescriptionText": "",
      "ClientCompanyName": "",
      "DocumentUrl": "",
      "CalculatedHourUse": 0.0,
      "Location": "",
      "GeoLocation": null,
      "Project": {
        "ProjectId": 1686756,
        "ProjectName": "240050 Utbedr.tiltak Midt-Gudbr.dal",
        "ProjectNumber": "240050"
      },
      "Updated": "2024-07-11T13:48:50.703",
      "InvoiceCalculationNote": "",
      "HSEResponsibleId": null,
      "QAResponsibleId": null,
      "TimeConsumption": 1310.5
    }
  ]
}
```

**MERK:** SubProjects inkluderer et nested `Project`-objekt med `ProjectId`, `ProjectName` og `ProjectNumber`, saa man slipper aa gjore et ekstra oppslag mot `/Projects` for aa vise prosjekttilhoerighet.

### 11. Gamle prosjekter finnes ikke i /Projects

`/Projects` returnerer kun naavarende/aktive prosjekter. RUE- og QD-hendelser kan referere til `ProjectId`-er som ikke lenger finnes i listen (slettede eller avsluttede prosjekter). Haandter dette i koden:

```javascript
const projName = (id) => {
  const p = projMap[id];
  return p ? `${p.ProjectNumber.trim()} ${p.ProjectName}` : String(id);
};
```

### 12. WorkOperation-verdier er ikke komplett dokumentert

`WorkOperation` i Values-arrayen kan inneholde verdier utover det som er dokumentert her, f.eks. `WorkOnAlongTheWay` (arbeid langs vei). Disse verdiene avhenger av bedriftens konfigurasjon i SmartDok og kan endres uten API-endring.

### 13. /Forms er markert som Deprecated — bruk /Forms/v2

`GET /Forms` er markert som **Deprecated** i SmartDoks Swagger-spec. Endepunktet fungerer fortsatt (pr. februar 2026). **Bruk `/Forms/v2` i stedet** — ingen 32-dagers begrensning, men har et lettere listeformat uten inline Elements (hent via `/Forms/v2/{id}/elements`).

### 15. SJA er et eget API — ikke del av Forms

SJA (Sikker Jobb Analyse) har **egne endepunkter** (`/sja/overview`, `/sja/reasons`, `/sja/potential_hazards`). SJA dukker IKKE opp i `/Forms` eller `/Forms/v2`. For HMS-rapportering maa SJA hentes separat.

### 16. /sja/overview bruker POST og har uvanlig respons-wrapping

SJA-oversikten bruker POST (ikke GET) med dato-filter i request body. Responsen er wrappet i et .NET backing field: `data["<Data>k__BackingField"]`. Dette er en serialiseringsartefakt og maa haandteres i klienten.

### 17. /qd/v2 klassifisering er paa norsk med kommaseparerte verdier

I motsetning til RUE (engelsk klassifisering), bruker QD v2 **norske verdier**. Feltene `Cause`, `Concerning` og `RelatesTo` kan inneholde **flere kommaseparerte verdier** (f.eks. `"Feil utfoerelse, Mangel paa informasjon/kunnskap"`). Split paa `, ` for aa faa individuelle verdier.

### 14. CalcuatedTimeConsumption — skrivefeil i API

**Casing-felle:** `CalcuatedTimeConsumption` er en skrivefeil i APIet (mangler 'l'). Det riktige feltet `CalculatedTimeConsumption` finnes ogsaa. Begge returnerer alltid 0 i praksis.

**ProjectNumber med trailing space:** `"ProjectNumber": "202601 "` — bruk `.trim()` ved sammenligning!

### /Users

```json
{
  "Count": 64,
  "Offset": 0,
  "TotalCount": 64,
  "Items": [
    {
      "Id": "abb1fdd9-be74-42b7-a979-003cc01f2b57",
      "UserName": "95925740",
      "Name": "Lars Erik Bjoerke",
      "Email": "larserik.bjorke@gmail.com",
      "PhonePrefix": "47",
      "PhoneNumber": "95925740",
      "BirthDate": "01.08.1991",
      "Role": "User",
      "AccessLevelId": "63068a29-54e9-4814-9c09-adf48a924d30",
      "IsEnded": false,
      "CompanyId": 225,
      "DepartmentId": 447,
      "EmployeeNo": "120",
      "ExternalEmployeeNo": "",
      "GroupId": 11928,
      "GroupName": "Ansatte Aage Haverstad AS",
      "LanguageCode": "nb-no",
      "NextOfKinName": "Gunn Helen Tvete",
      "NextOfKinPhonePrivate": "95925740",
      "NextOfKinPhoneWork": "90261690",
      "NextOfKinRelation": "Samboer",
      "NextOfKin2Name": "",
      "NextOfKin2PhonePrivate": "",
      "NextOfKin2PhoneWork": "",
      "NextOfKin2Relation": "",
      "ResourceType": null,
      "DepartmentName": "Timeloenn maaned",
      "Expertise": null,
      "IsLockedOut": false,
      "IsDeleted": false,
      "IsContactPerson": false,
      "EmployeeCost": null,
      "LastActivityTime": "2026-02-21T07:12:14.203",
      "CreatedDate": "2012-02-27T17:44:26"
    }
  ]
}
```

**VIKTIG:** User `Id` er en UUID (f.eks. `"abb1fdd9-be74-42b7-a979-003cc01f2b57"`). Denne UUID-en dukker opp som `SubmitterId`, `OwnerId`, `HSEResponsibleId`, `QAResponsibleId` og `FilledOutById` i andre endepunkter. Bruk Users-endepunktet for aa mappe UUID til navn/epost/telefon.

**Roller:** `User`, `Foreman`, `ProjectAdministrator`, `Administrator`, `Guest`, `EmployeeWithoutAccess`, `SubContractor`

### /Users/current (naavarende bruker)

Returnerer brukerobjektet for den autentiserte API-brukeren (samme felt som /Users-item):

```json
{
  "Id": "6632f631-94b7-4501-bcb0-a95bd653d8a3",
  "UserName": "smartdok225",
  "Name": "SmartDok",
  "Email": "post@smartdok.com",
  "PhonePrefix": "47",
  "PhoneNumber": "41044962",
  "BirthDate": null,
  "Role": "Administrator",
  "AccessLevelId": "996ffe05-bef0-4c46-8930-9089c86015bd",
  "IsEnded": false,
  "CompanyId": 225,
  "DepartmentId": 1,
  "EmployeeNo": "",
  "ExternalEmployeeNo": null,
  "GroupId": 0,
  "GroupName": "",
  "LanguageCode": "nb-no",
  "DepartmentName": "ingen",
  "IsLockedOut": false,
  "IsDeleted": false,
  "IsContactPerson": false,
  "LastActivityTime": "2018-10-25T03:21:04",
  "CreatedDate": "2018-10-25T03:21:04"
}
```

Nyttig for aa verifisere korrekt autentisering og sjekke hvilken rolle API-tokenet har.

### /LicenseInfo

Returnerer lisensinformasjon for selskapet:

```json
{
  "AvailableLicenses": 1,
  "TotalLicenses": 65
}
```

### /Authorize/PublicKeys

Returnerer offentlige noekler for JWT-verifisering:

```json
[
  {
    "Exponent": "AQAB",
    "Modulus": "xIa1dRFqzZ1/h6Y3cvaJZaG2pR8g1qwZ..."
  }
]
```

### /Roles — DEPRECATED

Returnerer en enkel array av rollestrenger:

```json
["User", "Foreman", "ProjectAdministrator", "Administrator", "Guest", "EmployeeWithoutAccess", "SubContractor"]
```

Markert som **Deprecated**. Brukerroller er allerede inkludert i `/Users`-responsen (`Role`-feltet).

### /Group (brukergrupper)

Returnerer alle grupper som en ren array (ikke paginert):

```json
[
  {"Id": 13374, "Name": "ADK - Ansatte AH AS"},
  {"Id": 11928, "Name": "Ansatte Aage Haverstad AS"},
  {"Id": 13440, "Name": "Diett hoey ansatte AH AS"},
  {"Id": 13375, "Name": "Groeftarb. - Ansatte AH AS"},
  {"Id": 11929, "Name": "Innleide AH AS"},
  {"Id": 13373, "Name": "Testgruppe"}
]
```

Grupper brukes for aa organisere brukere. `GroupId` i `/Users`-responsen refererer til disse gruppe-ID-ene. Stoetter ogsaa `POST /Group/AddUser` og `DELETE /Group/RemoveUser?userId=<uuid>` for brukeradministrasjon.

### /Departments (avdelinger)

**11 avdelinger totalt**, 6 aktive.

**Server-side filtreringsparametere:**

| Parameter | Type | Beskrivelse |
|-----------|------|-------------|
| `departmentNumber` | string | Filtrer paa avdelingsnummer |
| `departmentName` | string | Filtrer paa avdelingsnavn |
| `all` | boolean | Inkluder inaktive (default: kun aktive) |
| `active` | boolean | Filtrer paa aktiv-status |
| `updatedSince` | string (ISO 8601) | Kun avdelinger oppdatert etter denne datoen |

```json
{
  "Count": 11,
  "Offset": 0,
  "TotalCount": 11,
  "Items": [
    {
      "Id": 398,
      "Name": "Adm.-Fastloennede",
      "Number": "10",
      "IsActive": true,
      "Updated": "2025-11-25T13:48:59.237"
    },
    {
      "Id": 395,
      "Name": "Innleid",
      "Number": "4",
      "IsActive": true,
      "Updated": null
    },
    {
      "Id": 447,
      "Name": "Timeloenn maaned",
      "Number": "1",
      "IsActive": true,
      "Updated": "2024-07-12T08:49:54.197"
    }
  ]
}
```

`DepartmentId` i `/Users`-responsen refererer til disse avdelings-ID-ene. `Updated` kan vaere `null` for avdelinger som ikke er endret siden opprettelse.

### /Additions (tillegg)

**13 tillegg** konfigurert. Returnerer en ren array (ikke paginert).

**Server-side filtreringsparametere:**

| Parameter | Type | Beskrivelse |
|-----------|------|-------------|
| `additionNumber` | string | Filtrer paa tilleggsnummer |
| `additionName` | string | Filtrer paa tilleggsnavn |
| `onlyAddition` | boolean | Kun faste tillegg (Addition=true) |
| `onlyUnitAddition` | boolean | Kun enhetstillegg (UnitAddition=true) |
| `all` | boolean | Inkluder inaktive |
| `active` | boolean | Filtrer paa aktiv-status |

```json
[
  {
    "Id": 102333,
    "Number": "142",
    "Name": "Groeftarbeidstillegg",
    "Addition": true,
    "UnitAddition": false,
    "IsActive": true,
    "Export": true,
    "Rate": 0.0,
    "HourlyCost": 15.0,
    "Order": 0,
    "IsCommentRequired": false,
    "IsOvertime": false
  },
  {
    "Id": 102325,
    "Number": "108",
    "Name": "Overtid 50 %",
    "Addition": false,
    "UnitAddition": true,
    "IsActive": true,
    "Export": true,
    "Rate": 0.0,
    "HourlyCost": 144.0,
    "Order": 24,
    "IsCommentRequired": false,
    "IsOvertime": false
  }
]
```

**To typer tillegg:**
- `Addition = true` — fast tillegg per time (f.eks. groeftarbeidstillegg, ADK-tillegg)
- `UnitAddition = true` — enhetstillegg (f.eks. overtid 50%, nattillegg, broeyteberedskapshelg)

Tilleggsregistreringer dukker opp i `WorkHours/v2` som `AdditionRegistrations[]`-array med `WageId` som refererer til `Id` i denne listen.

### /Allowance (godtgjoerelse)

**2 godtgjoerelsetyper** konfigurert.

**Server-side filtreringsparametere:**

| Parameter | Type | Beskrivelse |
|-----------|------|-------------|
| `number` | string | Filtrer paa godtgjoerelsesnummer |
| `name` | string | Filtrer paa godtgjoerelsesnavn |
| `all` | boolean | Inkluder inaktive |
| `active` | boolean | Filtrer paa aktiv-status |

```json
{
  "Count": 2,
  "Offset": 0,
  "TotalCount": 2,
  "Items": [
    {
      "Id": 238,
      "Name": "Brakkediett",
      "Number": "115",
      "CompanyId": 225,
      "IsActive": true,
      "Rate": 250.0,
      "Order": 0,
      "IsCommentRequired": false,
      "IsExport": true
    },
    {
      "Id": 6302,
      "Name": "Diett",
      "Number": "116",
      "CompanyId": 225,
      "IsActive": true,
      "Rate": 400.0,
      "Order": 0,
      "IsCommentRequired": false,
      "IsExport": true
    }
  ]
}
```

`AllowanceId` i `/WorkHours/v2` refererer til disse ID-ene.

### /Wages (loennsarter)

**12 loennsarter** konfigurert. Returnerer en ren array (ikke paginert).

**Server-side filtreringsparametere:**

| Parameter | Type | Beskrivelse |
|-----------|------|-------------|
| `wageNumber` | string | Filtrer paa loennsnummer |
| `wageName` | string | Filtrer paa loennsnavn |
| `all` | boolean | Inkluder inaktive |
| `active` | boolean | Filtrer paa aktiv-status |

```json
[
  {
    "Id": 2844,
    "Name": "Timer loenn",
    "IsAbsence": false,
    "IsDaytime": false,
    "Number": "100",
    "IsActive": true,
    "Export": true,
    "Rate": 0.0,
    "HourlyCost": 0.0,
    "InternalPrice": 0.0,
    "Order": 1,
    "IsCommentRequired": false
  },
  {
    "Id": 85892,
    "Name": "Velferdspermisjon",
    "IsAbsence": true,
    "IsDaytime": false,
    "Number": "130",
    "IsActive": false,
    "Export": true,
    "Rate": 0.0,
    "HourlyCost": 0.0,
    "InternalPrice": 0.0,
    "Order": 0,
    "IsCommentRequired": true
  },
  {
    "Id": 2855,
    "Name": "Maskinkost innleide",
    "IsAbsence": false,
    "IsDaytime": false,
    "Number": "155",
    "IsActive": true,
    "Export": true,
    "Rate": 0.0,
    "HourlyCost": 0.0,
    "InternalPrice": 0.0,
    "Order": 8,
    "IsCommentRequired": false
  }
]
```

**MERK:** `IsAbsence = true` markerer loennsarten som fravaer (ferie, sykdom, permisjon). `WageId` i `/WorkHours/v2` refererer til disse ID-ene.

### /WorkDescriptions (arbeidsbeskrivelser/aktiviteter)

**82 arbeidsbeskrivelser** konfigurert. Returnerer en ren array (ikke paginert).

**Server-side filtreringsparametere:**

| Parameter | Type | Beskrivelse |
|-----------|------|-------------|
| `workDescriptionNumber` | string | Filtrer paa aktivitetsnummer |
| `workDescriptionName` | string | Filtrer paa aktivitetsnavn |
| `all` | boolean | Inkluder inaktive |
| `active` | boolean | Filtrer paa aktiv-status |

```json
[
  {
    "Id": 1,
    "Name": "Ikke definert(std)",
    "Number": "999",
    "IsActive": true,
    "Price": 0.0,
    "InternalRate": 0.0
  },
  {
    "Id": 57,
    "Name": "Fravaer(std)",
    "Number": "888",
    "IsActive": true,
    "Price": 0.0,
    "InternalRate": 0.0
  },
  {
    "Id": 3253,
    "Name": "Rigging",
    "Number": "01.1",
    "IsActive": true,
    "Price": 0.0,
    "InternalRate": 0.0
  },
  {
    "Id": 3255,
    "Name": "Groeftearbeider",
    "Number": "04",
    "IsActive": true,
    "Price": 0.0,
    "InternalRate": 0.0
  }
]
```

`ActivityId` i `/WorkHours/v2` refererer til disse ID-ene. Typiske aktiviteter for anleggsentreprenoer: rigging, vegetasjonsrydding, groeftearbeider, veiarbeid, komprimering, legging av roer, betong, etc.

### /WorkHours/v2 (arbeidstimer — anbefalt)

**157 125 timeregistreringer** totalt. Stoetter paginering.

**Server-side filtreringsparametere:**

| Parameter | Type | Beskrivelse |
|-----------|------|-------------|
| `offset` | int32 | Paginering offset |
| `count` | int32 | Paginering antall |
| `fromDate` | string (ISO 8601) | Timer fra og med dato |
| `toDate` | string (ISO 8601) | Timer til og med dato |
| `projectId` | int32 | Filtrer paa prosjekt |
| `subProjectId` | int32 | Filtrer paa delprosjekt |
| `areaId` | int32 | Filtrer paa omraade |
| `lastUpdated` | string (ISO 8601) | Kun timer oppdatert etter denne datoen |
| `approved` | boolean | Filtrer paa godkjent-status |
| `absence` | boolean | Filtrer paa fravaer |

```json
{
  "Count": 1,
  "Offset": 0,
  "TotalCount": 157125,
  "Items": [
    {
      "Id": 130176537,
      "UserId": "568d8a01-608e-4c94-86c3-020b35824374",
      "Date": "2026-02-24",
      "TimeFrom": "13:00:00",
      "TimeTo": "14:30:00",
      "BreakTime": "00:00:00",
      "BreakStart": null,
      "HourBankDeposit": "00:00:00",
      "ProjectId": 2050094,
      "SubProjectId": null,
      "ActivityId": 6367,
      "ActivityCategoryId": null,
      "WageId": 2844,
      "WageComment": "",
      "DepartmentId": 447,
      "AreaId": null,
      "ElementId": null,
      "Comment": "Testing av Hitachi",
      "AdminComment": null,
      "AvailabilityTime": null,
      "DaytimeId": null,
      "AllowanceId": null,
      "AllowanceComment": "",
      "RegistrationType": "Ordinary",
      "RegistrationNumber": "",
      "AdditionRegistrations": [
        {
          "WageId": 93976,
          "Amount": 0.0,
          "Comment": null
        },
        {
          "WageId": 102317,
          "Amount": 0.0,
          "Comment": null
        }
      ],
      "MachineHourRegistrations": [
        {
          "MachineId": 231746,
          "Hours": "01:30:00"
        }
      ],
      "LastUpdated": "2026-02-24T18:30:17.51"
    }
  ]
}
```

**Referansenoekler:**
- `UserId` → `/Users` (UUID)
- `ProjectId` → `/Projects`
- `SubProjectId` → `/SubProjects`
- `ActivityId` → `/WorkDescriptions`
- `WageId` → `/Wages`
- `DepartmentId` → `/Departments`
- `AllowanceId` → `/Allowance`
- `AdditionRegistrations[].WageId` → `/Additions`
- `MachineHourRegistrations[].MachineId` → `/Machines`

**Nested arrays:**
- `AdditionRegistrations` — tilleggsregistreringer per timefoering (WageId, Amount, Comment)
- `MachineHourRegistrations` — maskintimer per timefoering (MachineId, Hours)

**Tidsformat:** `TimeFrom`, `TimeTo`, `BreakTime`, `HourBankDeposit` og `MachineHourRegistrations[].Hours` bruker `HH:mm:ss`-format (ikke ISO 8601).

### /WorkHours (v1 — krever datofiltre)

V1-endepunktet krever `fromDate` og `toDate` (begge paakreved). Uten disse faar du 400 Bad Request:

```json
{"errors":{"toDate":["The toDate field is required."],"fromDate":["The fromDate field is required."]}}
```

**Server-side filtreringsparametere (v1):**

| Parameter | Type | Paakrevd | Beskrivelse |
|-----------|------|----------|-------------|
| `fromDate` | string | **Ja** | Fra dato |
| `toDate` | string | **Ja** | Til dato |
| `includeExported` | boolean | Nei | Inkluder eksporterte timer |
| `onlyAttested` | boolean | Nei | Kun attesterte timer |
| `includeMachineHours` | boolean | Nei | Inkluder maskintimer |
| `includeWagesMarkedNoExport` | boolean | Nei | Inkluder loennsarter merket for ikke-eksport |
| `projectId` | int32 | Nei | Filtrer paa prosjekt |
| `subProjectId` | int32 | Nei | Filtrer paa delprosjekt |
| `areaId` | int32 | Nei | Filtrer paa omraade |
| `exportedExternal` | boolean | Nei | Filtrer paa ekstern eksportstatus |
| `exportedExternalId` | string | Nei | Filtrer paa ekstern eksport-ID |
| `absence` | boolean | Nei | Filtrer paa fravaer |
| `includeHourBankHours` | boolean | Nei | Inkluder timebankregistreringer |
| `includeAllowanceMarkedNoExport` | boolean | Nei | Inkluder godtgjoerelse merket for ikke-eksport |
| `lastUpdated` | string (ISO 8601) | Nei | Kun timer oppdatert etter denne datoen |

**Anbefaling:** Bruk `/WorkHours/v2` i stedet — stoetter paginering og krever ikke datofiltre.

### /Goods (varer)

**225 varer** konfigurert.

**Server-side filtreringsparametere:**

| Parameter | Type | Beskrivelse |
|-----------|------|-------------|
| `goodsNumber` | string | Filtrer paa varenummer |
| `goodsName` | string | Filtrer paa varenavn |
| `all` | boolean | Inkluder inaktive |
| `active` | boolean | Filtrer paa aktiv-status |

```json
{
  "Count": 225,
  "Offset": 0,
  "TotalCount": 225,
  "Items": [
    {
      "Id": 9030,
      "Name": "Pukk 10/16",
      "Number": "1",
      "Amount": -1680.01,
      "UnitId": 5,
      "Unit": {
        "Id": 5,
        "Name": "tonn"
      },
      "IsActive": true,
      "IsProduction": false,
      "Price": 135.0,
      "InternalCost": null,
      "CategoryId": 1061,
      "Category": {
        "Id": 1061,
        "Name": "Pukk",
        "IsProduction": false,
        "IsActive": true
      },
      "Barcodes": null
    }
  ]
}
```

**MERK:** Goods inkluderer **nested objekter**: `Unit` (med Id og Name) og `Category` (med Id, Name, IsProduction, IsActive). Man trenger ikke aa gjore ekstra oppslag mot `/Goods/Units` eller `/GoodsCategories` for grunnleggende informasjon.

`Amount` er et loepende saldo-felt og kan vaere negativt (brukt mer enn tilfoert).

### /Goods/Units (enhetstyper)

Returnerer alle mulige enhetstyper som en ren array (40 enheter):

```json
[
  {"UnitId": 0, "Name": "stk"},
  {"UnitId": 1, "Name": "meter"},
  {"UnitId": 2, "Name": "kubikkmeter"},
  {"UnitId": 3, "Name": "kvadratmeter"},
  {"UnitId": 4, "Name": "kilo"},
  {"UnitId": 5, "Name": "tonn"},
  {"UnitId": 6, "Name": "kilometer"},
  {"UnitId": 7, "Name": "doegn"},
  {"UnitId": 8, "Name": "timer"},
  {"UnitId": 9, "Name": "pakke"},
  {"UnitId": 10, "Name": "lass"},
  {"UnitId": 16, "Name": "liter"}
]
```

**MERK:** ID-ene er ikke sammenhengende (hopper fra 36 til 61).

### /GoodsCategories (varekategorier)

Returnerer alle varekategorier som en ren array (17 kategorier):

```json
[
  {"Id": 1061, "Name": "Pukk", "IsProduction": false, "IsActive": true},
  {"Id": 1569, "Name": "Forsterkningslag", "IsProduction": false, "IsActive": true},
  {"Id": 1571, "Name": "Grus", "IsProduction": false, "IsActive": true},
  {"Id": 1573, "Name": "Sand", "IsProduction": false, "IsActive": true},
  {"Id": 1574, "Name": "Jord", "IsProduction": false, "IsActive": true},
  {"Id": 3031, "Name": "Baerelag", "IsProduction": false, "IsActive": true},
  {"Id": 3326, "Name": "Stein", "IsProduction": false, "IsActive": true},
  {"Id": 3361, "Name": "Asfalt", "IsProduction": false, "IsActive": true},
  {"Id": 3514, "Name": "Diverse", "IsProduction": false, "IsActive": true},
  {"Id": 42370, "Name": "Betong", "IsProduction": false, "IsActive": true}
]
```

**Server-side filtreringsparametere:**

| Parameter | Type | Beskrivelse |
|-----------|------|-------------|
| `goodsCategoryName` | string | Filtrer paa kategorinavn |
| `production` | boolean | Filtrer paa produksjonskategori |
| `all` | boolean | Inkluder inaktive |
| `active` | boolean | Filtrer paa aktiv-status |

Stoetter ogsaa `GET /GoodsCategories/{categoryId}/Goods` for aa hente varer i en spesifikk kategori.

### /GoodsConsumption (vareforbruk)

Vareforbruk — registreringer av materialer brukt paa prosjekter.

**Server-side filtreringsparametere:**

| Parameter | Type | Beskrivelse |
|-----------|------|-------------|
| `fromDate` | string (ISO 8601) | Fra dato |
| `toDate` | string (ISO 8601) | Til dato |
| `goodsCategoryId` | int32 | Filtrer paa varekategori |
| `projectId` | int32 | Filtrer paa prosjekt |
| `subProjectId` | int32 | Filtrer paa delprosjekt |
| `Selection` | int32 | Utvalg |
| `markedToBeInvoiced` | boolean | Kun merket for fakturering |
| `invoiced` | boolean | Kun fakturerte |

```json
{
  "Count": 0,
  "Offset": 0,
  "TotalCount": 0,
  "Items": []
}
```

**MERK:** Uten datofiltre returnerer endepunktet tom liste. Spesifiser `fromDate`/`toDate` for aa hente data. Stoetter ogsaa POST (opprett), PUT (oppdater), DELETE og MarkAsExported-operasjoner.

### /GoodsProduction (vareproduksjon)

Vareproduksjon — registreringer av produserte varer. Samme filtreringsparametere som `/GoodsConsumption`.

```json
[]
```

Returnerer tom array uten datofiltre.

### /GoodsTransportation (varetransport)

Varetransport — registreringer av transporterte varer. Samme filtreringsparametere som `/GoodsConsumption`.

```json
{
  "Count": 0,
  "Offset": 0,
  "TotalCount": 0,
  "Items": []
}
```

Returnerer tom liste uten datofiltre.

### /Invoices (fakturaer)

**Server-side filtreringsparametere:**

| Parameter | Type | Beskrivelse |
|-----------|------|-------------|
| `fromDate` | string (ISO 8601) | Fra dato |
| `toDate` | string (ISO 8601) | Til dato |

```json
[]
```

Returnerer tom array uten datofiltre. Stoetter ogsaa `GET /Invoices/{id}` for enkeltfaktura.

### /rue (liste) — DEPRECATED

```json
{
  "Count": 300,
  "Offset": 0,
  "TotalCount": 300,
  "Items": [
    {
      "Id": 1464174,
      "ProjectId": 1664628,
      "SubProjectId": null,
      "SubmitDate": "2024-10-09T10:11:02.8",
      "SubmitterName": "Geir Haansnar",
      "CaseWorkerName": "Therese Silliloekken",
      "Status": "Close",
      "Title": "Uhell",
      "Lat": null,
      "Lon": null,
      "Accuracy": null,
      "EventId": 1004
    }
  ]
}
```

**ID-moenster:**
- `Id` (1464174) — intern database-ID, brukes i URL-er (`/rue/1464174`)
- `EventId` (1004) — brukersynlig loepenummer, vises som `#1004` i UI
- `ProjectId` — intern prosjekt-ID, maa mappes mot `/Projects` for aa faa prosjektnummer/navn. **NB:** Gamle/avsluttede prosjekter finnes ikke i `/Projects`-listen — ProjectId kan vaere uten match.

**Statusverdier:** `Close`, `Open`, `New`, `Discarded`, `Unprocessed`

### /rue/{id} (detalj)

```json
{
  "Id": 1464174,
  "EventId": 1004,
  "Title": "Uhell",
  "Description": "Soere Feforvegen. Maskinforer skulle skyve brukte 800 roer ut av vegen...",
  "Status": "Close",
  "Severity": "High",
  "SubmitDate": "2024-10-09T10:11:02.8",
  "EventTime": "2024-09-16T07:30:00",
  "DeadlineDateTime": null,
  "ProjectId": 1664628,
  "SubProjectId": null,
  "SubmitterId": "9ca04ec6-b2b3-4795-84c6-e49c032815d9",
  "OwnerId": "08e93173-2601-4420-984d-87e837275588",
  "ImmediateMeasuresDescription": "Maa ha (kvalifiserte) maskinfoerere paa vaare oppdrag.",
  "PermanentMeasuresDescription": "",
  "ConsequenceAnalysis": "",
  "Conclusion": "Soerge for at vi har kvalifisert mannskap med riktig kompetanse til en hver tid.",
  "ConclusionVisibleToSubmitter": false,
  "EstimatedCost": null,
  "ActualCost": null,
  "AbsenceDays": null,
  "AbsenceAppliesTo": "NotRelevant",
  "GeoLocation": null,
  "LocationAccuracy": null,
  "ReportedBySubcontractor": false,
  "Values": [
    {
      "Id": 49405,
      "Type": "EventType",
      "Values": [
        {
          "Id": 91,
          "Name": "Dangerous action",
          "Key": "Dangerous action",
          "Type": "EventType",
          "Sequence": 5
        }
      ]
    },
    {
      "Id": 49406,
      "Type": "EventInvolved",
      "Values": [
        {
          "Id": 6,
          "Name": "Person(s)",
          "Key": "Person(s)",
          "Type": "EventInvolved",
          "Sequence": 0
        }
      ]
    },
    {
      "Id": 49407,
      "Type": "CauseOfEvent",
      "Values": [
        {
          "Id": 47,
          "Name": "Loss of concentration/inattention",
          "Key": "Loss of concentration/inattention",
          "Type": "CauseOfEvent",
          "Sequence": 0
        }
      ]
    },
    {
      "Id": 49408,
      "Type": "WorkOperation",
      "Values": [
        {
          "Id": 45,
          "Name": "Use of construction machinery",
          "Key": "Use of construction machinery",
          "Type": "WorkOperation",
          "Sequence": 0
        }
      ]
    }
  ],
  "DefinitionId": 18355
}
```

**Values-strukturen** er en array av klassifiseringsgrupper:
- `EventType` — type hendelse (Unwanted event, Machine damage, Dangerous action, Observation, etc.)
- `EventInvolved` — hva hendelsen omfattet (Equipment/material, Machine/car, Person(s), etc.)
- `CauseOfEvent` — aarsak (Human error, Fault in machinery/equipment, etc.)
- `WorkOperation` — type arbeid (Use of construction machinery, etc.)

**MERK:** Klassifiseringsnavnene er paa **engelsk** i APIet selv om SmartDok-UI-et viser norsk. Se oversettelsestabell lenger ned.

### /qd (liste) — DEPRECATED

```json
{
  "Count": 26,
  "Offset": 0,
  "TotalCount": 26,
  "Items": [
    {
      "Id": 175668,
      "ProjectId": 2031633,
      "SubProjectId": null,
      "SubmitDate": "2025-12-12T14:38:07.823",
      "SubmitterName": "Joern Espen Traeet",
      "CaseWorkerName": "Therese Silliloekken",
      "Status": "Close",
      "Title": "Feil informasjon",
      "Lat": null,
      "Lon": null,
      "Accuracy": null,
      "EventId": 1027
    }
  ]
}
```

Samme struktur som RUE-listen. QD vises som **"Q-{EventId}"** (f.eks. Q-1027) i PDF/UI, men `Q-`-prefix finnes IKKE i API-data.

### /qd/{id} — FUNGERER IKKE

```
GET /qd/175668
→ HTTP 404 Not Found
```

Kjent API-begrensning. Detaljendepunktet er aldri implementert. Bruk `/qd/v2` for utvidet data eller `/qd/{id}/pdf` for full rapport.

### /qd/v2 (utvidet QD-liste med klassifisering)

**Foretrukket endepunkt.** Returnerer alle felter fra `/qd` pluss Description, Cause, Concerning og RelatesTo.

**Server-side filtreringsparametere (gjelder ogsaa `/qd`):**

| Parameter | Type | Beskrivelse |
|-----------|------|-------------|
| `lastUpdatedSince` | string (ISO 8601) | Kun QD oppdatert etter denne datoen |
| `projectId` | int32 | Filtrer paa prosjekt |
| `subprojectId` | int32 | Filtrer paa delprosjekt |
| `qdStatus` | string | Filtrer paa status: `Unprocessed`, `Open`, `Close`, `Discarded` |

```json
{
  "Count": 26,
  "Offset": 0,
  "TotalCount": 26,
  "Items": [
    {
      "Id": 175668,
      "Status": "Close",
      "SubmitDate": "2025-12-12T14:38:07.823",
      "Title": "Feil informasjon",
      "Description": "Under befaring med Saferoad i forbindelse med graving av fundamenter for bommer til Vevig, ble det oppfattet at loesningen besto av 2 stk. 6 m bommer og 1 stk. 4 m bom...",
      "EventId": 1027,
      "ProjectId": 2031633,
      "SubProjectId": null,
      "SubmitterName": "Joern Espen Traeet",
      "CaseWorkerName": "Therese Silliloekken",
      "Lat": null,
      "Lon": null,
      "Accuracy": null,
      "Cause": "Mangel paa informasjon/kunnskap, Manglende dokumentasjon",
      "Concerning": "Annet",
      "RelatesTo": "Kvalitetssikring"
    }
  ]
}
```

**Klassifiseringsfeltene (Cause, Concerning, RelatesTo):**
- Verdiene er paa **norsk** (i motsetning til RUE-klassifisering som er paa engelsk)
- Kan inneholde **flere kommaseparerte verdier** (f.eks. `"Feil utfoerelse, Mangel paa informasjon/kunnskap"`)
- `Cause` = Aarsak (tilsvarer CauseOfEvent i RUE)
- `Concerning` = Angaar (f.eks. Egne arbeidere, Leverandoer, Underentreprenoer/innleide, Teknisk, Utfoerelse, Oppdragsgiver, Annet)
- `RelatesTo` = I forhold til (f.eks. Kvalitetssikring, Fremdrift, Godkjenninger/tillatelser, Kontrakt/standard, Leveranser, Lover og forskrifter, Annet)

### /sja/overview (SJA — Sikker Jobb Analyse)

**MERK:** SJA bruker **POST**, ikke GET. Dato-filter sendes i request body.

```
POST https://api.smartdok.no/sja/overview
Content-Type: application/json
Authorization: Bearer <session-token>

{"fromDate": "2025-10-01", "toDate": "2025-12-31"}
```

**VIKTIG:** Responsen wrapper dataene i et .NET backing field:

```json
{
  "<Data>k__BackingField": [
    {
      "Id": 550148,
      "ProjectName": "250055 Bryggavika VA-BaneNor Eiendom",
      "ProjectId": 2037327,
      "SubProjectName": "",
      "SubProjectId": null,
      "Title": "Borring ved siden av jernbane.",
      "SerialNumber": "S-1047",
      "SubmittedByName": "Joern Espen Traeet",
      "SubmitterId": "e607d705-7867-4d8e-acc2-66f5f74bb71a",
      "SubmittedDate": "2026-02-18T07:19:09.34",
      "DiscardReason": null,
      "SubTasksCount": 1,
      "ParticipantsCount": 4,
      "Reasons": [
        {"Id": 9999, "Name": "Annet (spesifiser)"}
      ],
      "OtherReasonDescription": "Fare for aa komme i kontakt med KL.",
      "Status": 1,
      "LastUpdatedDate": "2026-02-18T07:19:09.34"
    }
  ]
}
```

**SJA-felter:**
- `SerialNumber` — brukersynlig nummer (f.eks. "S-1047")
- `ProjectName` — prosjektnavn er inkludert direkte (ingen mapping noedvendig)
- `Reasons` — array av grunner til at SJA ble utfoert
- `SubTasksCount` — antall deloppgaver/risikovurderinger
- `ParticipantsCount` — antall deltakere
- `Status` — numerisk: 0 = Ubehandlet, 1 = Godkjent/Lukket

**SJA er IKKE del av Forms.** SJA har egne endepunkter og dukker ikke opp i `/Forms` eller `/Forms/v2`.

### /sja/reasons (referansedata)

Statisk liste over SJA-grunner:

```json
[
  {"Id": 1, "Key": "SJA.reason.deviates-from-description", "Name": "Arbeidet medfører avvik fra beskrivelser i prosedyrer og planer"},
  {"Id": 2, "Key": "SJA.reason.unfamiliar-activity", "Name": "Aktiviteten er ny og ukjent"},
  {"Id": 3, "Key": "SJA.reason.unfamiliar-coworkers", "Name": "Folk som ikke kjenner hverandre skal jobbe sammen"},
  {"Id": 4, "Key": "SJA.reason.unfamiliar-equipment", "Name": "Utstyr som arbeidstakerne ikke har erfaring med skal benyttes"},
  {"Id": 5, "Key": "SJA.reason.changed-assumptions", "Name": "Forutsetningene er endret"},
  {"Id": 6, "Key": "SJA.reason.earlier-incidents", "Name": "Ulykker/uoenskede hendelser har skjedd tidligere ved tilsvarende aktiviteter"},
  {"Id": 9999, "Key": "SJA.reason.other", "Name": "Annet (spesifiser)"}
]
```

### /sja/potential_hazards (referansedata)

Statisk liste over farepotensial (23 verdier):

```json
[
  {"Id": 1, "Key": "SJA.hazard.impact-collision", "Name": "Sammenstoet/paakjoersel"},
  {"Id": 2, "Key": "SJA.hazard.structural-failure", "Name": "Konstruksjonssvikt"},
  {"Id": 3, "Key": "SJA.hazard.fire-explosion", "Name": "Brann/eksplosjon"},
  {"Id": 7, "Key": "SJA.hazard.fall", "Name": "Fall"},
  {"Id": 8, "Key": "SJA.hazard.heavy-materials", "Name": "Tunge loeft/tunge materialer"},
  {"Id": 10, "Key": "SJA.hazard.electric-shock", "Name": "Fare for elektriske stoet"},
  "..."
]
```

### /Machines

```json
{
  "Count": 185,
  "Offset": 0,
  "TotalCount": 185,
  "Items": [
    {
      "Id": 231746,
      "Name": "Haandtimer",
      "InternalNumber": "H100",
      "CategoryId": 0,
      "RegistrationNumber": "",
      "Description": "",
      "HoursUsed": 2991,
      "MilageKm": 0,
      "ModelYear": 0,
      "Location": "202602 Internt arbeid 2026",
      "LocationDateTime": "2026-02-19T00:00:00",
      "DateAcquired": null,
      "IsActive": true,
      "Comment": "",
      "PricePerHour": null,
      "SerialNumber": "",
      "CategoryName": "",
      "InternalCost": null,
      "Code": "",
      "HideInTransportation": true,
      "MaxTons": 0.0,
      "MaxM3": 0.0,
      "ImageUrl": "",
      "ResponsibleUsers": [],
      "Trailer": false,
      "ShowInRegistrations": true,
      "DepartmentIds": [395, 398, 447, 18124]
    }
  ]
}
```

**Server-side filtreringsparametere:**

| Parameter | Type | Beskrivelse |
|-----------|------|-------------|
| `internalNumber` | string | Filtrer paa internnummer |
| `machineName` | string | Filtrer paa maskinnavn |
| `all` | boolean | Inkluder inaktive (default: kun aktive) |
| `active` | boolean | Filtrer paa aktiv-status |

**185 maskiner totalt, 59 aktive** (pr. februar 2026). Inkluderer gravemaskiner, lastebiler, haandtimer, og annet utstyr.

### /rue/summaries (RUE-oppsummeringer)

Lettere versjon av RUE-listen med Severity og EventTime, men uten Description/Values:

**Server-side filtreringsparametere:**

| Parameter | Type | Beskrivelse |
|-----------|------|-------------|
| `LastUpdatedSince` | string (ISO 8601) | Kun RUE oppdatert etter denne datoen |
| `ProjectId` | int32 | Filtrer paa prosjekt |
| `SubprojectId` | int32 | Filtrer paa delprosjekt |
| `RueStatus` | string | Filtrer paa status |
| `Offset` | int32 | Paginering offset |
| `Count` | int32 | Paginering antall |

```json
{
  "Count": 300,
  "Offset": 0,
  "TotalCount": 300,
  "Items": [
    {
      "Id": 1857498,
      "EventId": 1299,
      "Title": "Farlig hoey fart forbi arbeidsplassen",
      "Status": "Unprocessed",
      "Severity": "High",
      "SubmitDate": "2026-02-19T10:43:51.967",
      "EventTime": "2026-02-19T10:39:39",
      "DeadlineDateTime": null,
      "ProjectId": 2040345,
      "SubProjectId": null,
      "OwnerId": "08e93173-2601-4420-984d-87e837275588",
      "SubmitterId": "a4e2283d-7280-4b86-a723-1f243c242155"
    }
  ]
}
```

**Fordel over `/rue`:** Inkluderer `Severity` og `EventTime` uten aa maatte hente detalj for hvert enkelt RUE.

### /rue/{id}/eventlog og /rue/{id}/messages

To ekstra endepunkter for RUE-detaljer:
- `GET /rue/{id}/eventlog` — hendelseslogg (statusendringer, tildelinger)
- `GET /rue/{id}/messages` — meldinger/kommentarer paa hendelsen

### /Forms/v2 (erstatter deprecated /Forms)

**Anbefalt endepunkt for skjemaer.** Ingen 32-dagers begrensning. Lettere listeformat (uten inline Elements).

**Varianter:**

| Endepunkt | Beskrivelse | Ekstra parametere |
|-----------|-------------|-------------------|
| `GET /Forms/v2` | Alle skjemaer | `lastUpdatedSince`, `categoryId` |
| `GET /Forms/v2/Project` | Skjemaer per prosjekt | + `projectId`, `subProjectId` |
| `GET /Forms/v2/Machine` | Skjemaer per maskin | + `machineId` |
| `GET /Forms/v2/{id}` | Enkeltskjema | |
| `GET /Forms/v2/{id}/elements` | Skjemafelt-data | `ordinals`, `offset`, `count` |
| `POST /Forms/v2/elements` | Felt-data for flere skjemaer | Array av form-IDer i body |
| `GET /Forms/v2/{id}/pdf` | Skjema-PDF | |

```json
{
  "Count": 3993,
  "Offset": 0,
  "TotalCount": 3993,
  "Items": [
    {
      "Id": 2676649,
      "FilledOutDate": "2023-11-28T15:13:23.293",
      "FilledOutBy": "Ola Ruststuen",
      "FilledOutById": "f9f0f776-8947-49dc-8c70-8b2ef15b895a",
      "Subject": "Virksomhetens generelle kompetansebehov",
      "SerialNumber": 9,
      "FormTemplateId": 3625216538568122,
      "ModuleType": "Project",
      "MainSerialNumber": "47-1683-001522",
      "ProjectId": 1590108,
      "SubProjectId": null,
      "MachineId": null,
      "LastUpdated": "2023-11-28T15:13:23.9733333"
    }
  ]
}
```

**Forskjeller fra /Forms v1:**
- `Id` i stedet for `FormId`
- `FormTemplateId` i stedet for `DefFormId` (men peker paa samme FormDefinition)
- `ModuleType` (streng: "Project", "Machine") i stedet for `ModuleId` (tall)
- `MainSerialNumber` — unik identifikator paa tvers av moduler
- `LastUpdated` — tidspunkt for siste endring
- **Ingen inline `Elements[]`** — hent via `/Forms/v2/{id}/elements`
- **Ingen `DefFormName`** — maa hentes via `/FormDefinitions/{FormTemplateId}` om noedvendig

### /Forms (med startDate/endDate) — DEPRECATED

**OBS:** Dette endepunktet er markert som **Deprecated** i SmartDoks Swagger-spec (pr. februar 2026). Det fungerer fortsatt, men kan bli erstattet i en fremtidig API-versjon. Monitorér Swagger-spec for endringer.

**Valgfrie filtreringsparametere (fra Swagger-spec):**

| Parameter | Type | Beskrivelse |
|-----------|------|-------------|
| `moduleId` | int32 | 1 = Prosjekt, 2 = Maskin |
| `moduleInstanceId` | int32 | Prosjekt- eller maskin-ID (filtrerer paa ett prosjekt/maskin) |
| `moduleSubInstanceId` | int32 | Delprosjekt-ID |
| `formDefinitionId` | int64 | DefFormId — filtrer paa bestemt skjematype |
| `categoryId` | int32 | Skjemakategori-ID |
| `temporaryForms` | boolean | Inkluder midlertidig lagrede skjemaer |

Eksempel med filtrering paa skjematype og prosjekt:
```
GET /Forms?startDate=2026-01-01&endDate=2026-01-31&formDefinitionId=7521602279564840&moduleInstanceId=2037327
```

```json
{
  "Count": 40,
  "Offset": 0,
  "TotalCount": 40,
  "Items": [
    {
      "FormId": 7529123,
      "FilledOutDate": "2026-01-23T09:49:14.272359",
      "FollowUpLater": false,
      "FilledOutBy": "Jonas Ekern",
      "Subject": "",
      "Serialnumber": 1,
      "TemporarilySaved": false,
      "ModuleId": 1,
      "ModuleInstanceId": 2037327,
      "ModuleSubInstanceId": null,
      "DefFormId": 7521602279564840,
      "DefFormName": "Ukerapport",
      "FilledOutById": "2f021b1f-a1d6-4758-847e-f5d647721f49",
      "SignaturePictureId": null,
      "SignatureName": "",
      "SignatureEmail": "",
      "FormStatusId": null,
      "MachineId": null,
      "ProjectId": 2037327,
      "Elements": [
        {
          "Id": 89293958,
          "FormControlId": 4170661,
          "FormDataId": 7529123,
          "Pictures": [],
          "TextBoxValue": "4",
          "Settings": {
            "TextValue": "4"
          }
        }
      ]
    }
  ]
}
```

**VIKTIG — 32-dagers grense:** `startDate` og `endDate` er **paakreved**, og maks intervall er 32 dager. For lengre perioder maa du loope i 32-dagers blokker. De valgfrie filtreringsparameterne (`moduleId`, `formDefinitionId` etc.) kan kombineres med datointervallet for aa redusere datamengden:

```javascript
let current = new Date(startDate);
const end = new Date(endDate);
while (current < end) {
  const blockEnd = new Date(Math.min(
    current.getTime() + 31 * 24 * 60 * 60 * 1000,
    end.getTime()
  ));
  const forms = await api(session,
    `/Forms?startDate=${current.toISOString()}&endDate=${blockEnd.toISOString()}`
  );
  // ... prosesser forms ...
  current = new Date(blockEnd.getTime() + 1);
}
```

**Elements-arrayen** inneholder de utfylte feltene. Hvert element har:
- `FormControlId` — kobler til feltet i FormDefinitions
- `TextBoxValue` — utfylt verdi (alltid streng)
- `Settings.TextValue` — samme verdi (for tekstfelter)
- `Settings.CheckboxValues` — array av booleans (for avkrysningsfelt)
- `Pictures` — array av bilde-IDer (for foto-felter)

### /FormDefinitions/{id}

```json
{
  "Id": 7589980306400505,
  "Name": "Egenerklæring ved sykdom",
  "Headline": "Egenerklæring ved sykdom",
  "Description": "",
  "Date": "2015-02-10T08:06:17.133",
  "DocumentNumber": "HR-001",
  "PreparedBy": "Carl-Terje",
  "ApprovedBy": "Carl-Terje",
  "ApprovedDate": "10.02.2015",
  "IsArchived": false,
  "Version": "3.0",
  "ShowToAll": false,
  "AllowGPStracking": false,
  "IsDraft": false,
  "IsAvailableOffline": false,
  "ShowSubjectField": true,
  "SendEmailToProjectManager": false,
  "SendEmailToEmployer": false,
  "FollowUpLater": false,
  "FormDefinitionCategoryId": 1978,
  "Revision": 0,
  "FormDefinitionCategory": {
    "ID": 1978,
    "Label": "Personal/HR",
    "CompanyId": 225,
    "ModuleId": 1,
    "ModuleName": "Prosjekt",
    "Root": true,
    "Visible": true,
    "OriginatorId": null
  },
  "Elements": [
    {
      "Id": 4166071,
      "FormId": 7589980306400505,
      "Label": "- Kan fraværet skyldes forhold paa arbeidsplassen?",
      "Information": "",
      "InformationImage": null,
      "Ordinal": 5,
      "Required": false,
      "Type": "Checkbox",
      "Settings": {
        "ShowComment": false,
        "Checkboxes": ["JA", "NEI"]
      }
    },
    {
      "Id": 4166073,
      "FormId": 7589980306400505,
      "Label": "Undertegnede bekrefter aa ha vaert fravarende paa grunn av sykdom",
      "Information": "",
      "InformationImage": null,
      "Ordinal": 2,
      "Required": false,
      "Type": "HeadLine",
      "Settings": {}
    }
  ]
}
```

**Element-typer:** `TextBox`, `Checkbox`, `HeadLine`, `Picture`, `Signature`, `Date`, `Number`, `DropDown`

For aa tolke et utfylt skjema: map `Elements[].FormControlId` fra Forms-responsen mot `Elements[].Id` i FormDefinitions for aa faa feltnavn (`Label`).

### /webhooks

```json
{
  "Count": 0,
  "Offset": 0,
  "TotalCount": 0,
  "Items": []
}
```

Webhook-endepunktet finnes og gir 200, men ingen abonnementer er satt opp.

---

## Endepunkter med begrenset tilgang (401)

Foelgende endepunkter returnerer 401 med "Missing claims"-feil. Disse krever ekstra API-rettigheter (claims) som ikke er tildelt vaart API-token.

### /Areas — Krever `AreaRead`

Omraader (arbeidsomraader innenfor delprosjekter).

| Endepunkt | Metode | Beskrivelse |
|-----------|--------|-------------|
| `/Areas` | GET | Hent omraader |
| `/Areas/{id}` | GET | Hent enkeltomraade |
| `/Areas/{id}` | PUT | Oppdater omraade |
| `/SubProjects/{subProjectId}/Areas` | GET | Hent omraader per delprosjekt |
| `/SubProjects/{subProjectId}/Areas` | POST | Opprett omraade |
| `/SubProjects/{subProjectId}/Areas/NextNumber` | GET | Neste ledige omraadenummer |

**Filtreringsparametere:** `areaNumber`, `areaName`, `all`, `active`, `updatedSince`

### /Customers — Krever `CustomersRead`

Kunder/oppdragsgivere.

| Endepunkt | Metode | Beskrivelse |
|-----------|--------|-------------|
| `/Customers` | GET | Hent kunder |
| `/Customers` | POST | Opprett kunde |
| `/Customers/{id}` | GET | Hent enkeltkunde |
| `/Customers/{id}` | PUT | Oppdater kunde (deprecated) |
| `/v2/Customers/{id}` | PUT | Oppdater kunde (anbefalt) |

**Filtreringsparametere:** `customerNumber`, `customerName`, `all`, `active`, `updatedSince`

### /GoodsLocations — Krever `GoodsLocationsRead`

Varelokasjoner (lager, utleveringssteder).

| Endepunkt | Metode | Beskrivelse |
|-----------|--------|-------------|
| `/GoodsLocations` | GET | Hent lokasjoner |
| `/GoodsLocations` | POST | Opprett lokasjon |
| `/GoodsLocations/Flows` | GET | Hent flytretninger |
| `/GoodsLocations/{id}` | GET | Hent enkeltlokasjon |
| `/GoodsLocations/{id}` | PUT | Oppdater lokasjon |

**Filtreringsparametere:** `active`

### /MachineCategories — Krever `MachineCategoriesRead`

Maskinkategorier (gravemaskin, lastebil, etc.).

| Endepunkt | Metode | Beskrivelse |
|-----------|--------|-------------|
| `/MachineCategories` | GET | Hent kategorier |
| `/MachineCategories` | POST | Opprett kategori |
| `/MachineCategories/{id}` | GET | Hent enkeltkategori |
| `/MachineCategories/{id}` | PUT | Oppdater kategori |

**Filtreringsparametere:** `machineCategoryName`, `all`, `active`

### /News — Krever tilleggsrettigheter

Nyheter/meldinger til ansatte.

| Endepunkt | Metode | Beskrivelse |
|-----------|--------|-------------|
| `/News` | POST | Opprett nyhetsinnlegg |
| `/News/{id}` | GET | Hent nyhetsinnlegg |

Ingen liste-endepunkt tilgjengelig (kun POST og GET/{id}).

### /OrderTypes — Krever `OrderTypeRead`

Ordretyper.

| Endepunkt | Metode | Beskrivelse |
|-----------|--------|-------------|
| `/OrderTypes` | GET | Hent ordretyper |
| `/OrderTypes` | POST | Opprett ordretype |
| `/OrderTypes/{id}` | GET | Hent enkelordretype |
| `/OrderTypes/{id}` | PUT | Oppdater ordretype |

### /Orders — Krever `OrdersRead` (alle deprecated)

Ordrestyring. **Alle endepunkter under /Orders er markert som deprecated.**

| Endepunkt | Metode | Beskrivelse |
|-----------|--------|-------------|
| `/Orders` | GET | Hent ordrer |
| `/Orders` | POST | Opprett ordre |
| `/Orders/{id}` | GET | Hent enkeltordre |
| `/Orders/{id}` | PUT | Oppdater ordre |
| `/Orders/GetAvailableByUser` | GET | Hent tilgjengelige ordrer per bruker |
| `/Orders/GetByUser` | GET | Hent ordrer per bruker |
| `/Orders/NextNumber` | GET | Neste ledige ordrenummer |
| `/Orders/types` | GET | Hent ordretyper |

**Filtreringsparametere (GET /Orders):** `orderNumber`, `orderName`, `all`, `active`, `modifiedSince`, `createdSince`

### /ResourcePlanning — Krever `ResourcePlanningRead`

Ressursplanlegging.

| Endepunkt | Metode | Beskrivelse |
|-----------|--------|-------------|
| `/ResourcePlanning/Plans` | GET | Hent planleggingsblokker |
| `/ResourcePlanning/Resources` | GET | Hent alle ressurser |
| `/ResourcePlanning/Resources/{resourceId}` | GET | Hent enkeltressurs |

**Filtreringsparametere (Plans):** `offset`, `count`, `from`, `to`, `resourceType`, `resourceGroupId`, `resourceId`, `projectId`
**Filtreringsparametere (Resources):** `offset`, `count`, `resourceType`, `all`, `active`

### /Tools — Krever `ToolsRead`

Verktoeystyring.

| Endepunkt | Metode | Beskrivelse | Claim |
|-----------|--------|-------------|-------|
| `/Tools` | GET | Hent verkoey | `ToolsRead` |
| `/Tools` | POST | Opprett verktoey | |
| `/Tools/{id}` | GET | Hent enkeltverktoey | `ToolsRead` |
| `/Tools/{id}` | PUT | Oppdater verktoey | |
| `/Tools/Categories` | GET | Hent verktoeykategorier | `ToolCategoriesRead` |
| `/Tools/Categories` | POST | Opprett kategori | |
| `/Tools/Categories/{id}` | GET | Hent enkeltkategori | `ToolCategoriesRead` |
| `/Tools/Categories/{id}` | PUT | Oppdater kategori | |
| `/Tools/Locations` | GET | Hent verktoeylokasjoner | `ToolLocationsRead` |
| `/Tools/Locations` | POST | Opprett lokasjon | |
| `/Tools/Locations/{id}` | GET | Hent enkeltlokasjon | `ToolLocationsRead` |
| `/Tools/Locations/{id}` | PUT | Oppdater lokasjon | |

**Filtreringsparametere (Tools/Locations):** `activeOnly`

### /TripToFromWorkAddition — Krever `TripToFromWorkAdditionRead`

Reise til/fra arbeid-tillegg.

| Endepunkt | Metode | Beskrivelse |
|-----------|--------|-------------|
| `/TripToFromWorkAddition` | GET | Hent reisetillegg |
| `/TripToFromWorkAddition` | POST | Opprett reisetillegg |
| `/TripToFromWorkAddition/{id}` | GET | Hent enkeltreisetillegg |
| `/TripToFromWorkAddition/{id}` | PUT | Oppdater reisetillegg |

**Filtreringsparametere:** `additionNumber`, `additionName`, `all`, `active`

### /WorkDescriptionCategory — Krever `ActivityCategoriesRead`

Aktivitetskategorier (overordnet gruppering av arbeidsbeskrivelser).

| Endepunkt | Metode | Beskrivelse |
|-----------|--------|-------------|
| `/WorkDescriptionCategory` | GET | Hent aktivitetskategorier |
| `/WorkDescriptionCategory/{id}` | GET | Hent enkeltkategori |

**Filtreringsparametere:** `workDescriptionCategoryName`, `all`, `active`, `updatedSince`

### /v2/orders/{projectId}/workers — Krever `OrderWorkersRead`

Arbeidere paa ordrer.

| Endepunkt | Metode | Beskrivelse |
|-----------|--------|-------------|
| `/v2/orders/{projectId}/workers` | GET | Hent arbeidere |
| `/v2/orders/{projectId}/workers` | PUT | Oppdater arbeidere |

---

## Fallgruver fra praksis (verifisert mot live API 2026-02-24)

### 1. QD detalj-endepunkt gir 404 — men /qd/v2 har klassifisering

`/qd/{id}` returnerer alltid 404 (controlleren er aldri implementert). Men `/qd/v2` returnerer utvidet data med Description, Cause, Concerning og RelatesTo — nok til klassifisering uten PDF-parsing. RUE-detaljer fungerer fint (`/rue/{id}`).

### 2. ProjectNumber har trailing spaces

```json
"ProjectNumber": "202601 "
```

Bruk alltid `.trim()` naar du sammenligner prosjektnummer.

### 3. Forms krever datointervall — maks 32 dager

Uten `startDate` og `endDate` faar du feil. Med mer enn 32 dagers intervall faar du ogsaa feil. Loop i blokker.

### 4. Server-side filtrering — mer tilgjengelig enn foerst antatt

Flere endepunkter stoetter server-side filtrering via query-parametere:

| Endepunkt | Server-side filtre |
|-----------|-------------------|
| `/rue` | `rueStatus`, `projectId`, `subprojectId`, `lastUpdatedSince` |
| `/rue/summaries` | Samme + `Offset`, `Count` |
| `/qd` og `/qd/v2` | `qdStatus`, `projectId`, `subprojectId`, `lastUpdatedSince` |
| `/Projects` | `projectNumber`, `projectName`, `active`, `updatedSince`, `createdSince`, `includeOrders` |
| `/Users` | `all`, `active` |
| `/Machines` | `internalNumber`, `machineName`, `all`, `active` |
| `/Forms` (v1) | `startDate`/`endDate` (paakreved), `moduleId`, `formDefinitionId`, `categoryId` |
| `/Forms/v2` | `lastUpdatedSince`, `categoryId` |
| `/Forms/v2/Project` | + `projectId`, `subProjectId` |
| `/sja/overview` | `fromDate`/`toDate` i POST body |
| `/Additions` | `additionNumber`, `additionName`, `onlyAddition`, `onlyUnitAddition`, `all`, `active` |
| `/Allowance` | `number`, `name`, `all`, `active` |
| `/Departments` | `departmentNumber`, `departmentName`, `all`, `active`, `updatedSince` |
| `/Goods` | `goodsNumber`, `goodsName`, `all`, `active` |
| `/GoodsCategories` | `goodsCategoryName`, `production`, `all`, `active` |
| `/GoodsConsumption` | `fromDate`, `toDate`, `goodsCategoryId`, `projectId`, `subProjectId`, `Selection`, `markedToBeInvoiced`, `invoiced` |
| `/GoodsProduction` | Samme filtre som `/GoodsConsumption` |
| `/GoodsTransportation` | Samme filtre som `/GoodsConsumption` |
| `/Invoices` | `fromDate`, `toDate` |
| `/SubProjects` | `subProjectNumber`, `subProjectName`, `all`, `active`, `updatedSince` |
| `/Wages` | `wageNumber`, `wageName`, `all`, `active` |
| `/WorkDescriptions` | `workDescriptionNumber`, `workDescriptionName`, `all`, `active` |
| `/WorkHours` (v1) | `fromDate` (paakreved), `toDate` (paakreved), `includeExported`, `onlyAttested`, `includeMachineHours`, `projectId`, `subProjectId`, `areaId`, `absence`, `lastUpdated` m.fl. |
| `/WorkHours/v2` | `offset`, `count`, `fromDate`, `toDate`, `projectId`, `subProjectId`, `areaId`, `lastUpdated`, `approved`, `absence` |

For klient-side filtrering naar server-side ikke er nok:
```javascript
const rueForProject = allRue.filter(r => r.ProjectId === projectId);
const rueInPeriod = allRue.filter(r => new Date(r.SubmitDate) >= startDate);
```

### 5. ID-forvirring: Id vs EventId

- `Id` = intern database-ID (brukes i URL-er)
- `EventId` = brukersynlig loepenummer (vises i UI)
- `/rue/{Id}` — bruk intern Id, IKKE EventId

### 6. UUID-er for brukere

`SubmitterId`, `OwnerId` etc. er UUID-er. For aa faa navn maa du hente `/Users` og bygge en mapping:

```javascript
const userMap = Object.fromEntries(users.map(u => [u.Id, u]));
const name = userMap[rueDetail.SubmitterId]?.Name;
```

### 7. Klassifiseringsverdier er paa engelsk

API-et returnerer engelske navn (`Dangerous action`, `Person(s)`, `Human error`), mens UI-et viser norsk. Se oversettelsestabell under.

### 8. SubmitDate vs EventTime

- `SubmitDate` = naar hendelsen ble registrert i SmartDok
- `EventTime` = naar hendelsen faktisk skjedde (kan vaere dager/uker foer registrering)
- Noen hendelser har kun `SubmitDate` (EventTime kan vaere null)

### 9. CalcuatedTimeConsumption — skrivefeil i API

Feltet `CalcuatedTimeConsumption` (mangler 'l') eksisterer i Projects-responsen ved siden av det korrekte `CalculatedTimeConsumption`. Begge returnerer alltid 0.

### 10. Status-verdier er inkonsistente

RUE bruker `Close` (ikke `Closed`), og nye hendelser kan ha `Unprocessed` (foer saksbehandler har tatt tak). For robust filtrering:

```javascript
const isClosed = ['Close', 'Closed', 'Lukket'].includes(r.Status);
const isOpen = ['Open', 'New', 'Unprocessed'].includes(r.Status);
```

### 18. WorkHours v1 krever fromDate/toDate, v2 stoetter paginering

`GET /WorkHours` (v1) krever baaade `fromDate` og `toDate` — uten disse faar du `400 Bad Request`. V2-endepunktet (`/WorkHours/v2`) stoetter standard paginering med `offset`/`count` og **krever ikke** datofiltre. For store datasett (157 000+ rader) bruk alltid v2 med paginering.

### 19. /rue er deprecated — bruk /rue/summaries

`GET /rue` er markert som **deprecated** i Swagger-specen. Bruk `/rue/summaries` i stedet — den inkluderer `Severity`, `EventTime`, `OwnerId` og `SubmitterId` som den gamle listen mangler, pluss stoetter server-side filtrering paa status og prosjekt.

### 20. /qd er deprecated — bruk /qd/v2

`GET /qd` er markert som **deprecated**. Bruk `/qd/v2` som inkluderer `Description`, `Cause`, `Concerning` og `RelatesTo` — nok til klassifisering uten PDF-parsing.

### 21. 15 endepunktkategorier returnerer 401 (krever ekstra API-claims)

Foelgende endepunkter krever claims som vaart API-token ikke har:

| Claim | Endepunkter |
|-------|-------------|
| `AreaRead` | /Areas, /SubProjects/{id}/Areas |
| `CustomersRead` | /Customers |
| `GoodsLocationsRead` | /GoodsLocations, /GoodsLocations/Flows |
| `MachineCategoriesRead` | /MachineCategories |
| `OrderTypeRead` | /OrderTypes |
| `OrdersRead` | /Orders (alle varianter) |
| `OrderWorkersRead` | /v2/orders/{projectId}/workers |
| `ResourcePlanningRead` | /ResourcePlanning/Plans, /ResourcePlanning/Resources |
| `ToolsRead` | /Tools |
| `ToolCategoriesRead` | /Tools/Categories |
| `ToolLocationsRead` | /Tools/Locations |
| `TripToFromWorkAdditionRead` | /TripToFromWorkAddition |
| `ActivityCategoriesRead` | /WorkDescriptionCategory |

For aa faa tilgang maa claims legges til API-tokenet i SmartDok-administrasjonen.

### 22. Goods-endepunkter inkluderer nested Unit og Category objekter

`/Goods` returnerer hvert item med inline `Unit`-objekt (`{Id, Name}`) og `Category`-objekt (`{Id, Name, IsProduction, IsActive}`). Du trenger ikke gjore separate oppslag mot `/Goods/Units` eller `/GoodsCategories` for aa vise varenavn med enhet og kategori.

### 23. WorkHours/v2 AdditionRegistrations og MachineHourRegistrations er nested arrays

Hver timeregistrering i `/WorkHours/v2` kan inneholde:
- `AdditionRegistrations[]` — tilleggsregistreringer med `WageId` (refererer til `/Additions`), `Amount` og `Comment`
- `MachineHourRegistrations[]` — maskintimer med `MachineId` (refererer til `/Machines`) og `Hours` (format `HH:mm:ss`)

Begge arrays kan vaere tomme `[]`. Husk aa sjekke for dette foer du prosesserer.

### 24. /Forms/v2/{id}/elements stoetter ordinals-parameter

Bruk `ordinals`-parameteren (array) for aa hente kun spesifikke felt etter posisjon: `GET /Forms/v2/{id}/elements?ordinals=1&ordinals=3&ordinals=5`. Stoetter ogsaa `offset` og `count` for paginering av feltdata.

### 25. POST /Forms/v2/elements for bulk-henting av skjemafelt

For aa hente feltdata for flere skjemaer i ett kall, bruk `POST /Forms/v2/elements` med en array av form-IDer i request body. Mye mer effektivt enn aa gjore individuelle GET-kall for hvert skjema.

### 26. SupplierInvoices har to upload-endepunkter (v1 deprecated, v2 anbefalt)

- `POST /SupplierInvoices/{externalInvoiceNumber}/document/upload` — **deprecated**, tar ekstern fakturanummer i URL
- `POST /SupplierInvoices/document/upload?externalInvoiceNumber=X` — anbefalt, tar fakturanummer som query-parameter

Stoetter ogsaa `POST /SupplierInvoices` (opprett), `PUT /SupplierInvoices` (oppdater) og `GET /SupplierInvoices/{id}` (hent).

### 27. Versjonerte update-endepunkter (/v2/Allowance, /v2/Customers, /v2/Projects, /v3/Projects)

Flere endepunkter har versjonerte oppdateringsvarianter:

| Deprecated | Anbefalt | Merknad |
|------------|----------|---------|
| `PUT /Allowance/{id}` | `PUT /v2/Allowance/{id}` | |
| `PUT /Customers/{id}` | `PUT /v2/Customers/{id}` | |
| `PUT /Projects/{id}` | `PUT /v3/Projects/{id}` | v2 er ogsaa deprecated |

Bruk alltid den nyeste versjonen for PUT-operasjoner.

---

## Oversettelsestabell: API (engelsk) → Norsk

### EventType (type hendelse)

| API-verdi | Norsk |
|-----------|-------|
| Unwanted event | Uoensket hendelse |
| Machine damage | Skade paa maskin/utstyr |
| Dangerous action | Farlig handling |
| Dangerous conditions/state | Farlige forhold |
| Observation | Observasjon |
| Other | Annet |
| Mishap | Uhell |
| Injury to person | Skade paa person |
| RUE_EventType_Traffic_Safety | Trafikkfarlig hendelse |
| RUE_EventType_Damage_Person | Skade paa person |
| RUE_EventType_Customer_Complaint | Klage fra kunde |
| RUE_EventType_Accident | Uhell |

### EventInvolved (hendelsen omfattet)

| API-verdi | Norsk |
|-----------|-------|
| Equipment/material | Utstyr/materiell |
| Machine/car | Maskin/bil |
| Person(s) | Person(er) |
| Environment/surroundings | Miljoe/omgivelser |
| Third party | Tredjepart |
| Outer environment | Ytre miljoe |
| Other | Annet |
| RUE_EventInvolved_Working_Time | Arbeidstid |
| RUE_EventInvolved_External_Environment | Ytre miljoe |
| RUE_EventInvolved_Third_Parties | Tredjepart |

### CauseOfEvent (aarsak)

| API-verdi | Norsk |
|-----------|-------|
| Human error | Menneskelig svikt |
| Bad order/tidiness | Daarlig orden og ryddighet |
| Fault in machinery/equipment | Feil paa utstyr/maskin |
| Error in procedure | Prosedyrebrudd |
| Incorrect work execution | Feil utfoerelse |
| Loss of concentration/inattention | Uoppmerksomhet |
| Operator error | Operatoerfeil |
| Unclear procedures/routines | Uklare prosedyrer |
| Weather conditions | Vaerforhold |
| External force | Ytre paavirkning |
| Slippery surface | Glatt underlag |
| Difficult access/tight spaces | Vanskelig adkomst |
| Equipment/tool failure | Feil eller mangler paa utstyr |
| Overload | Overbelastning |
| RUE_CauseOfEvent_Collision | Kollisjon |
| RUE_CauseOfEvent_Falling_Object | Fallende gjenstand |
| RUE_CauseOfEvent_Wear | Slitasje |
| RUE_CauseOfEvent_Overload | Overbelastning |
| RUE_CauseOfEvent_Difficult_Access | Vanskelig adkomst |
| RUE_CauseOfEvent_Vandalism | Haerverk |
| RUE_CauseOfEvent_Missing_Marking | Manglende merking |
| RUE_CauseOfEvent_Insufficient_Information | Mangelfull informasjon |
| RUE_CauseOfEvent_Detection_Lack | Manglende paavisning |
| RUE_CauseOfEvent_Missing_Ties | Manglende sikring |

### WorkOperation (arbeidsoperasjon)

| API-verdi | Norsk |
|-----------|-------|
| Use of construction machinery | Bruk av anleggsmaskin |
| WorkOnAlongTheWay | Arbeid langs vei |

**NB:** WorkOperation-verdiene er bedriftskonfigurerte og kan utvides uten API-endring. Listen over er ikke uttoeemmende.

---

## Komplett endepunktoversikt (181 endepunkter, 127 paths)

Hentet fra OpenAPI-spec (`/docs/v1`) 2026-02-24:

### Tilgjengelige endepunkter (200 OK)

| Kategori | GET liste | GET/{id} | POST | PUT | Andre |
|----------|-----------|----------|------|-----|-------|
| Additions | `/Additions` | `/Additions/{id}` (404) | `/Additions` | `/Additions/{id}` | |
| Allowance | `/Allowance` | `/Allowance/{id}` (404) | `/Allowance` | `/v2/Allowance/{id}` | |
| Authorize | `/Authorize/PublicKeys` | | `/Authorize/ApiToken` | | `/Authorize/ApiToken/Renew` |
| Departments | `/Departments` | `/Departments/{id}` (404) | `/Departments` | `/Departments/{id}` | |
| Forms | `/Forms/v2`, `/Forms` (dep.) | `/Forms/v2/{id}` | `POST /Forms/v2/elements` | | `/Forms/v2/{id}/elements`, `/Forms/v2/{id}/pdf` |
| FormDefinitions | | `/FormDefinitions/{id}` | | | |
| Goods | `/Goods`, `/Goods/Units` | `/Goods/{id}` (404) | `/Goods` | `/Goods/{id}` | |
| GoodsCategories | `/GoodsCategories` | `/GoodsCategories/{id}` (404) | `/GoodsCategories` | `/GoodsCategories/{id}` | `/GoodsCategories/{id}/Goods` |
| GoodsConsumption | `/GoodsConsumption` | `/GoodsConsumption/{id}` (404) | `/GoodsConsumption` | `/GoodsConsumption/{id}` | DELETE, MarkAsExported |
| GoodsProduction | `/GoodsProduction` | `/GoodsProduction/{id}` (404) | | | MarkAsExported |
| GoodsTransportation | `/GoodsTransportation` | `/GoodsTransportation/{id}` (404) | | | MarkAsExported |
| Group | `/Group` | `/Group/{id}` (404) | `AddUser` | | `DELETE RemoveUser` |
| Invoices | `/Invoices` | `/Invoices/{id}` (404) | | | |
| LicenseInfo | `/LicenseInfo` | | | | |
| Machines | `/Machines` | `/Machines/{id}` | `/Machines` | `/Machines/{id}` | |
| Pictures | | | | | `/Pictures/project/{id}` |
| Projects | `/Projects`, `NextProjectNumber` | `/Projects/{id}` | `/Projects` | `/v3/Projects/{id}` | `/Projects/{id}/Location`, `/Projects/{id}/Prices` |
| QD | `/qd` (dep.), `/qd/v2` | `/qd/{id}` (404) | | | `/qd/{id}/pdf` |
| Roles | `/Roles` (dep.) | | | | |
| RUE | `/rue` (dep.), `/rue/summaries` | `/rue/{id}` | | | `/rue/{id}/pdf`, `/rue/{id}/eventlog`, `/rue/{id}/messages` |
| SJA | | | `POST /sja/overview` | | `/sja/reasons`, `/sja/potential_hazards` |
| SubProjects | `/SubProjects` | `/SubProjects/{id}` | `/Projects/{id}/SubProjects` | `/SubProjects/{id}` | Location, NextNumber |
| SupplierInvoices | | `/SupplierInvoices/{id}` | `/SupplierInvoices` | `/SupplierInvoices` | document/upload (v1 dep., v2) |
| Users | `/Users`, `/Users/current` | `/Users/{id}` | `/Users` | `/Users/{id}` | `DELETE /Users/{id}` |
| Wages | `/Wages` | `/Wages/{id}` (404) | `/Wages` | `/Wages/{id}` | |
| Webhooks | `/Webhooks` | | `/Webhooks` | `/Webhooks/{id}` | `DELETE /Webhooks/{id}` |
| WorkDescriptions | `/WorkDescriptions` | `/WorkDescriptions/{id}` | `/WorkDescriptions` | `/WorkDescriptions/{id}` | |
| WorkHours | `/WorkHours` (v1), `/WorkHours/v2` | `/WorkHours/{id}` (404) | `/WorkHours` | | MarkAsExported, SetExportedExternal |

### Endepunkter med 401 (krever ekstra claims)

| Kategori | Claim | Endepunkter |
|----------|-------|-------------|
| Areas | `AreaRead` | GET/PUT /Areas, /SubProjects/{id}/Areas |
| Customers | `CustomersRead` | GET/POST/PUT /Customers |
| GoodsLocations | `GoodsLocationsRead` | GET/POST/PUT /GoodsLocations, /GoodsLocations/Flows |
| MachineCategories | `MachineCategoriesRead` | GET/POST/PUT /MachineCategories |
| News | (ukjent) | POST /News, GET /News/{id} |
| OrderTypes | `OrderTypeRead` | GET/POST/PUT /OrderTypes |
| Orders | `OrdersRead` | GET/POST/PUT /Orders (alle dep.) |
| OrderWorkers | `OrderWorkersRead` | GET/PUT /v2/orders/{id}/workers |
| ResourcePlanning | `ResourcePlanningRead` | GET /ResourcePlanning/Plans, /Resources |
| Tools | `ToolsRead` | GET/POST/PUT /Tools |
| ToolCategories | `ToolCategoriesRead` | GET/POST/PUT /Tools/Categories |
| ToolLocations | `ToolLocationsRead` | GET/POST/PUT /Tools/Locations |
| TripToFromWorkAddition | `TripToFromWorkAdditionRead` | GET/POST/PUT /TripToFromWorkAddition |
| WorkDescriptionCategory | `ActivityCategoriesRead` | GET /WorkDescriptionCategory |

---

## Andre tekniske detaljer

### Swagger-spesifikasjon og API-dokumentasjon

| URL | Beskrivelse |
|-----|-------------|
| `https://api.smartdok.no/api-docs/` | Interaktiv API-dokumentasjon (Scalar UI) |
| `https://api.smartdok.no/docs/v1` | OpenAPI/Swagger JSON-spec (oppdatert, inkluderer v2-endepunkter) |
| `https://api.smartdok.no/swagger/docs/v1` | Gammel Swagger-spec (ufullstendig) |

**VIKTIG:** `/docs/v1` er mer komplett enn `/swagger/docs/v1`. Den gamle specen mangler mange endepunkter (bl.a. `/qd/v2`, `/sja/*`, `/Forms/v2/*`, `/Machines`).

### Data-typer

- Alle datoer er ISO 8601 uten tidssone (antas norsk tid / UTC+1/+2)
- Id-er for prosjekter/RUE/QD er heltall
- Id-er for brukere er UUID-strenger
- DefFormId (skjemadefinisjoner) er store tall (f.eks. 7589980306400505)
- GeoLocation er `null` i de fleste tilfeller (GPS-tracking er sjelden aktivert)
- Tidsfelter i WorkHours bruker `HH:mm:ss`-format (ikke ISO 8601)

### PDF-nedlasting

PDF-endepunktene (`/qd/{id}/pdf` og `/rue/{id}/pdf`) stoetter en valgfri `includeDetails`-parameter (boolean, query) for aa inkludere ekstra detaljer i rapporten:

```
GET /rue/{id}/pdf?includeDetails=true
GET /qd/{id}/pdf?includeDetails=true
```

Begge returnerer:

```json
{
  "FileSize": 75353,
  "FileDate": "2025-12-12T14:38:07",
  "Filename": "QD-1027.pdf",
  "DownloadUrl": "https://s3.amazonaws.com/..."
}
```

`DownloadUrl` er en pre-signert S3-URL, gyldig i 24 timer. Last ned med en vanlig GET-forespoersel (ingen auth-header noedvendig).

### CompanyId

Aage Haverstad AS har CompanyId 225. Denne er bakt inn i API-tokenet og begrenser tilgangen til firmaets data.

### Feilkoder

| Kode | Beskrivelse | Tiltak |
|------|-------------|--------|
| 401 | Ugyldig eller utloept session-token, eller manglende claims | Re-autentiser med API-token. Sjekk om endepunktet krever ekstra claims. |
| 404 | Endepunkt/ressurs finnes ikke (inkl. `/qd/{id}`) | Sjekk URL og Id |
| 400 | Ugyldige parametere (f.eks. Forms uten datoer, WorkHours v1 uten datoer) | Sjekk paakreved parametere |
| 500 | Serverfeil | Proev igjen senere |
