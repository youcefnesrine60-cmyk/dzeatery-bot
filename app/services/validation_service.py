import re

# =========================
# 🟢 VALIDATION
# =========================
def valid_phone(text):
    text = text.replace(" ", "")
    return re.match(r"0[5-7]\d{8}$", text)