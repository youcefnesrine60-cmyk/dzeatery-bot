import re

def sanitize_text(
        text: str, 
        max_length: int = 50
) -> str | None:
    if not text:
        return None

    # حذف المسافات الزائدة
    text = text.strip()

    # تحديد الطول
    text = text[:max_length]

    # السماح فقط بالحروف العربية والانجليزية والأرقام والمسافة
    text = re.sub(r"[^a-zA-Z0-9\u0600-\u06FF\s\-&']", "", text)

    # حذف المسافات المتكررة
    text = re.sub(r"\s+", " ", text)

    if len(text) < 2:
        return None

    return text