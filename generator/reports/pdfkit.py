"""reportlab / matplotlib helpers shared by the PDF reports."""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from reportlab.lib import colors  # noqa: E402
from reportlab.lib.styles import ParagraphStyle  # noqa: E402
from reportlab.pdfbase import pdfmetrics  # noqa: E402
from reportlab.pdfbase.ttfonts import TTFont  # noqa: E402
from reportlab.platypus import Table, TableStyle  # noqa: E402

FONTS = {
    "LibSans": "/usr/share/fonts/liberation/LiberationSans-Regular.ttf",
    "LibSans-B": "/usr/share/fonts/liberation/LiberationSans-Bold.ttf",
    "LibSans-I": "/usr/share/fonts/liberation/LiberationSans-Italic.ttf",
    "LibSerif": "/usr/share/fonts/liberation/LiberationSerif-Regular.ttf",
    "LibSerif-B": "/usr/share/fonts/liberation/LiberationSerif-Bold.ttf",
    "LibSerif-I": "/usr/share/fonts/liberation/LiberationSerif-Italic.ttf",
    "NSerif": "/usr/share/fonts/noto/NotoSerif-Regular.ttf",
    "NSerif-B": "/usr/share/fonts/noto/NotoSerif-Bold.ttf",
    "NSerif-L": "/usr/share/fonts/noto/NotoSerif-Light.ttf",
    "NSerif-I": "/usr/share/fonts/noto/NotoSerif-Italic.ttf",
    "NSans": "/usr/share/fonts/noto/NotoSans-Regular.ttf",
    "NSans-B": "/usr/share/fonts/noto/NotoSans-Bold.ttf",
    "NSans-L": "/usr/share/fonts/noto/NotoSans-Light.ttf",
    "NSans-I": "/usr/share/fonts/noto/NotoSans-Italic.ttf",
}
_done = False


def register_fonts():
    global _done
    if _done:
        return
    for name, path in FONTS.items():
        if Path(path).exists():
            pdfmetrics.registerFont(TTFont(name, path))
    _done = True


def style(name, font="LibSans", size=9, leading=None, color=colors.black, **kw):
    return ParagraphStyle(name, fontName=font, fontSize=size, leading=leading or size * 1.3, textColor=color, **kw)


def table(data, col_widths, header_bg, font="LibSans", size=7.5, zebra=None, bold_last=False, align_right_from=1,
          header_fg=colors.white, grid=colors.HexColor("#CCCCCC"), header_font=None):
    t = Table(data, colWidths=col_widths, repeatRows=1)
    st = [("FONT", (0, 0), (-1, -1), font, size),
          ("FONT", (0, 0), (-1, 0), header_font or font + "-B", size),
          ("BACKGROUND", (0, 0), (-1, 0), header_bg), ("TEXTCOLOR", (0, 0), (-1, 0), header_fg),
          ("ALIGN", (align_right_from, 0), (-1, -1), "RIGHT"), ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
          ("LINEBELOW", (0, 0), (-1, -1), 0.25, grid), ("TOPPADDING", (0, 0), (-1, -1), 2),
          ("BOTTOMPADDING", (0, 0), (-1, -1), 2)]
    if zebra:
        for i in range(1, len(data)):
            if i % 2 == 0:
                st.append(("BACKGROUND", (0, i), (-1, i), zebra))
    if bold_last:
        st.append(("FONT", (0, -1), (-1, -1), (header_font or font + "-B"), size))
        st.append(("LINEABOVE", (0, -1), (-1, -1), 0.8, colors.black))
    t.setStyle(TableStyle(st))
    return t


def fmt_k(x, dec=0):
    return f"{x / 1e3:,.{dec}f}"


def fmt_pct(x, dec=1, sign=True):
    if x is None or x != x:
        return "n.a."
    return f"{x:+.{dec}f}%" if sign else f"{x:.{dec}f}%"


def savefig(fig, path, dpi=170):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=dpi, bbox_inches="tight")
    plt.close(fig)
    return str(path)
