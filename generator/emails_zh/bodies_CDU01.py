"""CDU01 Chengdu Taikoo Li (成都远洋太古里) - closing emails. Bodies hand-authored in cdu01_p1.py / cdu01_p2.py."""
from cdu01_p1 import E1
from cdu01_p2 import E2

STORE = "CDU01"
PEOPLE = {
    "ln": ("李娜", "na.li@valentino-retail.example"),
    "yf": ("杨帆", "fan.yang@valentino-retail.example"),
    "hyt": ("何雨桐", "yutong.he@valentino-retail.example"),
    "box": ("", "cdu01.store@valentino-retail.example"),
}
PEOPLE_MAILER = {
    "ln": "iPhone Mail (22A3354)",
    "yf": "Microsoft Outlook 16.0",
}
DEFAULT_TO = ["ops_cn"]
DEFAULT_CC = ["zhaolei"]
ALLOWED_REPEATS = ["李娜", "Fan", "Fan / 杨帆", "赵总好～", "赵总、各位好～", "各位好～", "赵总好，", "各位好，", "雨桐", "杨帆"]
EMAILS = E1 + E2
