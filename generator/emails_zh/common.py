"""Shared address book + helpers for the emails_zh group (SHA01, BJS01, CDU01, HKG01, TPE01).

Bodies are hand-authored in bodies_<STORE>.py; this module only provides addresses.
"""

DOMAIN = "valentino-retail.example"

# distribution lists / shared people
DL = {
    "ops_cn": f"retail-ops-china@{DOMAIN}",
    "ops_hktw": f"retail-ops-hktw@{DOMAIN}",
    "merch": f"merch-planning@{DOMAIN}",
    "merch_apac": f"merch-planning-apac@{DOMAIN}",
    "vm": f"vm-team@{DOMAIN}",
    "crm_cn": f"crm-china@{DOMAIN}",
    "logistics_apac": f"logistics-apac@{DOMAIN}",
    "aftersales_cn": f"aftersales-china@{DOMAIN}",
    "hr_cn": f"hr-china@{DOMAIN}",
    "it_helpdesk": f"it-helpdesk@{DOMAIN}",
}

SHARED_PEOPLE = {
    # area managers
    "zhaolei": ("赵磊", f"lei.zhao@{DOMAIN}"),
    "zhaolei_en": ("Zhao Lei", f"lei.zhao@{DOMAIN}"),
    "vivian": ("Vivian Lau", f"vivian.lau@{DOMAIN}"),
    # merch planner China (invented)
    "merch_cn": ("Sun Yiwen 孙怡雯", f"yiwen.sun@{DOMAIN}"),
    # HK/TW merch planner (invented)
    "merch_hktw": ("Jason Tsang", f"jason.tsang@{DOMAIN}"),
}


def addr(people: dict, key_or_addr: str) -> str:
    """Resolve a persona key (store-local or shared), a DL key, or a literal address."""
    if key_or_addr in people:
        n, a = people[key_or_addr]
        return f"{n} <{a}>" if n else a
    if key_or_addr in SHARED_PEOPLE:
        n, a = SHARED_PEOPLE[key_or_addr]
        return f"{n} <{a}>"
    if key_or_addr in DL:
        return DL[key_or_addr]
    return key_or_addr
