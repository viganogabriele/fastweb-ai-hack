"""BJS01 Beijing SKP (北京SKP) - closing emails. Bodies hand-authored in bjs01_p1.py / bjs01_p2.py."""
from bjs01_p1 import E1
from bjs01_p2 import E2

STORE = "BJS01"
PEOPLE = {
    "ly": ("刘洋", "yang.liu@valentino-retail.example"),
    "zm": ("张敏", "min.zhang@valentino-retail.example"),
    "mx": ("马骁", "xiao.ma@valentino-retail.example"),
    "box": ("", "bjs01.store@valentino-retail.example"),
}
PEOPLE_MAILER = {
    "ly": "iPhone Mail (22A3354)",
    "zm": "Foxmail 7.2.25.375[cn]",
    "mx": "NetEase Mail Master 7.18",
}
DEFAULT_TO = ["ops_cn"]
DEFAULT_CC = ["zhaolei"]
ALLOWED_REPEATS = ["[抱拳]", "张敏", "Valentino 北京SKP店", "马骁", "领导好", "各位好：", "赵总、各位好：", "赵总好："]
EMAILS = E1 + E2
