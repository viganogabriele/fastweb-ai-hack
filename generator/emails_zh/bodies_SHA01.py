"""SHA01 Shanghai Plaza 66 (上海恒隆广场) - closing emails. Bodies hand-authored in sha01_p1.py / sha01_p2.py."""
from sha01_p1 import E1
from sha01_p2 import E2

STORE = "SHA01"
PEOPLE = {
    "wj": ("王静", "jing.wang@moncler-retail.example"),
    "ch": ("陈浩", "hao.chen@moncler-retail.example"),
    "tina": ("周婷婷 Tina", "tina.zhou@moncler-retail.example"),
    "box": ("", "sha01.store@moncler-retail.example"),
}
PEOPLE_MAILER = {
    "wj": "iPhone Mail (22A3354)",
    "ch": "Microsoft Outlook 16.0",
    "tina": "WeChat Work Mail 4.1",
}
DEFAULT_TO = ["ops_cn"]
DEFAULT_CC = ["zhaolei"]
ALLOWED_REPEATS = ["【SHA01 恒隆 每日营业报告】", "重点事项：", "需要支持：", "无", "王静 Jing", "王静", "浩",
                   "发自我的iPhone", "Moncler 上海恒隆广场店", "需要支持：无", "Tina"]
EMAILS = E1 + E2
