# ==============================================
# 🤖 CAPTCHA GENERATOR
# ==============================================

import random
from app.core.logger import logger

# ==============================================
# 🧩 CAPTCHA GENERATOR
# ==============================================

class CaptchaGenerator:

    # ==========================================
    # ➕ GENERATE CAPTCHA
    # ==========================================

    @classmethod
    def generate(
        cls,
    ) -> dict[str, object]:

        a = random.randint(1, 9)
        b = random.randint(1, 9)

        answer = a + b

        question = (
            "🤖 تحقق أمني\n\n"
            "ما نتيجة:\n\n"
            f"{a} + {b} = ؟"
        )

        logger.info(
            "captcha_generated",
            extra={
                "question": question, 
                "answer": str(answer)
            }
        )

        return {
            "question": question,
            "answer": str(answer),
        }