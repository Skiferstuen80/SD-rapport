# EN->NO translation tables for RUE classification values
# Source: smartdok-api-reference.md, live API response data

EVENT_TYPE: dict[str, str] = {
    "Unwanted event": "Uoensket hendelse",
    "Machine damage": "Skade paa maskin/utstyr",
    "Dangerous action": "Farlig handling",
    "Dangerous conditions/state": "Farlige forhold",
    "Observation": "Observasjon",
    "Other": "Annet",
    "Mishap": "Uhell",
    "Injury to person": "Skade paa person",
    "RUE_EventType_Traffic_Safety": "Trafikkfarlig hendelse",
    "RUE_EventType_Damage_Person": "Skade paa person",
    "RUE_EventType_Customer_Complaint": "Klage fra kunde",
    "RUE_EventType_Accident": "Uhell",
}

EVENT_INVOLVED: dict[str, str] = {
    "Equipment/material": "Utstyr/materiell",
    "Machine/car": "Maskin/bil",
    "Person(s)": "Person(er)",
    "Environment/surroundings": "Miljo/omgivelser",
    "Third party": "Tredjepart",
    "Outer environment": "Ytre miljo",
    "Other": "Annet",
    "RUE_EventInvolved_Working_Time": "Arbeidstid",
    "RUE_EventInvolved_External_Environment": "Ytre miljo",
    "RUE_EventInvolved_Third_Parties": "Tredjepart",
}

CAUSE_OF_EVENT: dict[str, str] = {
    "Human error": "Menneskelig svikt",
    "Bad order/tidiness": "Daarlig orden og ryddighet",
    "Fault in machinery/equipment": "Feil paa utstyr/maskin",
    "Error in procedure": "Prosedyrebrudd",
    "Incorrect work execution": "Feil utfoerelse",
    "Loss of concentration/inattention": "Uoppmerksomhet",
    "Operator error": "Operatoerfeil",
    "Unclear procedures/routines": "Uklare prosedyrer",
    "Weather conditions": "Vaerforhold",
    "External force": "Ytre paavirkning",
    "Slippery surface": "Glatt underlag",
    "Difficult access/tight spaces": "Vanskelig adkomst",
    "Equipment/tool failure": "Feil eller mangler paa utstyr",
    "Overload": "Overbelastning",
    "RUE_CauseOfEvent_Collision": "Kollisjon",
    "RUE_CauseOfEvent_Falling_Object": "Fallende gjenstand",
    "RUE_CauseOfEvent_Wear": "Slitasje",
    "RUE_CauseOfEvent_Overload": "Overbelastning",
    "RUE_CauseOfEvent_Difficult_Access": "Vanskelig adkomst",
    "RUE_CauseOfEvent_Vandalism": "Haerverk",
    "RUE_CauseOfEvent_Missing_Marking": "Manglende merking",
    "RUE_CauseOfEvent_Insufficient_Information": "Mangelfull informasjon",
    "RUE_CauseOfEvent_Detection_Lack": "Manglende paavisning",
    "RUE_CauseOfEvent_Missing_Ties": "Manglende sikring",
}

_MAPS = {
    "EventType": EVENT_TYPE,
    "EventInvolved": EVENT_INVOLVED,
    "CauseOfEvent": CAUSE_OF_EVENT,
}

RUE_STATUS: dict[str, str] = {
    "Close": "Lukket",
    "Open": "Aapen",
    "New": "Ny",
    "Unprocessed": "Ubehandlet",
    "Discarded": "Forkastet",
}


def translate_classification(cls_type: str, value: str) -> str:
    m = _MAPS.get(cls_type, {})
    return m.get(value, value)


def translate_rue_status(status: str) -> str:
    return RUE_STATUS.get(status, status)
