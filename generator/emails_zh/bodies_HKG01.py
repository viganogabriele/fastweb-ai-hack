"""HKG01 Hong Kong Canton Road (廣東道) - closing emails. Bodies hand-authored in hkg01_p1.py / hkg01_p2.py."""
from hkg01_p1 import E1
from hkg01_p2 import E2

STORE = "HKG01"
PEOPLE = {
    "karen": ("Karen Chan 陳嘉欣", "karen.chan@moncler-retail.example"),
    "ming": ("Ming Wong", "ming.wong@moncler-retail.example"),
    "sammi": ("Sammi Lee", "sammi.lee@moncler-retail.example"),
    "box": ("", "hkg01.store@moncler-retail.example"),
}
PEOPLE_MAILER = {
    "karen": "Microsoft Outlook 16.0",
    "ming": "iPhone Mail (22A3354)",
    "sammi": "iPhone Mail (21H16)",
}
DEFAULT_TO = ["ops_hktw"]
DEFAULT_CC = ["vivian"]
ALLOWED_REPEATS = ["Karen", "Ming", "Hi all,", "Hi Vivian, all,", "Sent from my iPhone", "Thx", "Sammi",
                   "This e-mail and any attachments are confidential and may be privileged. If you are not the intended recipient, please notify the sender immediately and delete it. Moncler Hong Kong Limited"]
EMAILS = E1 + E2
