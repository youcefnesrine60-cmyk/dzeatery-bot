import re

# =========================
# 🟢 VALIDATION
# =========================
def valid_phone(text: str) -> bool:
    text = text.replace(" ", "")
    return bool(re.match(r"0[5-7]\d{8}$", text))