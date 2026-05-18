from app.helpers.ui_manager import (
    UIManager
)

from app.core.security.captcha_manager import (
    CaptchaManager
)

from app.core.security.captcha_generator import (
    CaptchaGenerator
)

from app.core.logger import (
    logger
)

# ==============================================
# 🚀 SEND CAPTCHA CHALLENGE
# ==============================================

async def send_captcha(
        chat_id: int
) -> None:

    logger.info(

        "Initiating captcha challenge for user",
        
        extra={
            "chat_id": chat_id
        }
    )

    captcha = CaptchaGenerator.generate()

    logger.debug(

        "Generated captcha for user",
        
        extra={
            "chat_id": chat_id,
            "captcha": captcha
        }
    )

    await CaptchaManager.require(

        chat_id,

        captcha["answer"]
    )

    logger.info(

        "Stored captcha answer for user",

        extra={
            "chat_id": chat_id
        }
    )

    await UIManager.update(

        chat_id,

        captcha["question"]
    )


# ==============================================
# 🚀 HANDLE CAPTCHA RESPONSE
# ==============================================

async def handle_captcha(

    chat_id: int,

    text: str
) -> bool:

    if not text.isdigit():

        logger.warning(
            
            "User provided non-numeric captcha response",

            extra={
                "chat_id": chat_id,
                "text": text
            }
        )

        await UIManager.update(

            chat_id,

            "⚠️ الرجاء إدخال الرقم الصحيح فقط."
        )

        return False

    valid = await CaptchaManager.verify(

        chat_id,

        text
    )

    if not valid:

        logger.warning(

            "User provided incorrect captcha response",
            
            extra={
                "chat_id": chat_id,
                "text": text
            }
        )

        await UIManager.update(

            chat_id,

            "❌ إجابة خاطئة.\nحاول مرة أخرى."
        )

        return False

    await CaptchaManager.clear(chat_id)

    logger.info(

        "User provided correct captcha response",

        extra={
            "chat_id": chat_id,
            "text": text
        }
    )

    await UIManager.update(

        chat_id,

        "✅ تم التحقق بنجاح."
    )

    logger.info(

        "User completed captcha verification",

        extra={
            "chat_id": chat_id
        }
    )
    return True