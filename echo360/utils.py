def naive_versiontuple(v):
    """
    This only works for version tuple with the same number of parts.
    Expects naive_versiontuple('xx.yy.zz') < naive_versiontuple('aa.bb.cc').
    """
    return tuple(map(int, (v.split("."))))


def strip_illegal_path(path: str) -> str:
    illegal_chars = '<>:"/\\|?*' + "".join(chr(c) for c in range(0, 32))
    for ch in illegal_chars:
        path = path.replace(ch, "_")

    reserved_names = {
        "CON",
        "PRN",
        "AUX",
        "NUL",
        "COM1",
        "COM2",
        "COM3",
        "COM4",
        "COM5",
        "COM6",
        "COM7",
        "COM8",
        "COM9",
        "LPT1",
        "LPT2",
        "LPT3",
        "LPT4",
        "LPT5",
        "LPT6",
        "LPT7",
        "LPT8",
        "LPT9",
    }
    name, *ext = path.rsplit(".", 1)
    if name.upper() in reserved_names:
        path = f"_{path}"

    path = path.rstrip(" .")

    if path in {".", ".."}:
        path = "_"

    return path


PERSISTENT_SESSION_FOLDER = "_browser_persistent_session"
