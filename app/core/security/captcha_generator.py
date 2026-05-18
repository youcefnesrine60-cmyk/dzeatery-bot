#=================================
# يولد سؤال التحقق
#=================================

import random


class CaptchaGenerator:

    @classmethod
    def generate(
        cls: type
    ) -> dict:

        a = random.randint(1, 9)

        b = random.randint(1, 9)

        answer = a + b

        question = f"🤖 تحقق أمني\n\nما نتيجة:\n\n{a} + {b} = ؟"

        return {

            "question": question,

            "answer": str(answer)
        }