"""TPE01 Taipei 101 (台北101) - closing emails. Bodies hand-authored in tpe01_p1.py / tpe01_p2.py."""
from tpe01_p1 import E1
from tpe01_p2 import E2

STORE = "TPE01"
PEOPLE = {
    "lyj": ("林怡君 Jenny Lin", "yijun.lin@moncler-retail.example"),
    "wce": ("吳承恩", "chengen.wu@moncler-retail.example"),
    "vicky": ("王筱涵 Vicky", "vicky.wang@moncler-retail.example"),
    "box": ("", "tpe01.store@moncler-retail.example"),
}
PEOPLE_MAILER = {
    "lyj": "Microsoft Outlook 16.0",
    "wce": "Microsoft Outlook 16.0",
    "vicky": "iPhone Mail (22A3354)",
}
DEFAULT_TO = ["ops_hktw"]
DEFAULT_CC = ["vivian"]
ALLOWED_REPEATS = ["怡君", "承恩", "大家好～", "Vivian、大家好～", "Vivian 好～", "怡君 Jenny", "筱涵 Vicky"]
EMAILS = E1 + E2
