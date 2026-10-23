"""Tiny helper so store modules can declare emails compactly."""


def E(id, dt, frm, subj, body, **kw):
    d = dict(id=id, dt=dt, frm=frm, subj=subj, body=body)
    d.update(kw)
    return d


DOM = "valentino-retail.example"


def addr(name):
    first, *rest = name.lower().replace("ø", "o").replace("æ", "ae").replace("å", "a").split()
    return f"{first}.{''.join(rest)}@{DOM}"
