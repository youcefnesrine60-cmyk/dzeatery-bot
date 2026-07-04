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
        
        *,

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

        chat_id = chat_id,

        answer = captcha["answer"]
    )

    logger.info(

        "Stored captcha answer for user",

        extra={

            "chat_id": chat_id
        }
    )

    await UIManager.update(

        chat_id = chat_id,

        text = captcha["question"],

        reply_markup = captcha["keyboard"]
    )


# ==============================================
# 🚀 HANDLE CAPTCHA RESPONSE
# ==============================================

async def handle_captcha(
        
    *,

    chat_id: int,

    text: str
) -> bool:

    if not text.isdigit():

        logger.warning(
            
            "User provided non-numeric captcha response",

            extra={

                "chat_id": chat_id,

                "text_length": len(text)
            }
        )

        await UIManager.update(

            chat_id = chat_id,

            text = "⚠️ الرجاء إدخال الرقم الصحيح فقط.",

            reply_markup = None
        )

        return False

    valid = await CaptchaManager.verify(

        chat_id = chat_id,

        user_answer = text
    )

    if not valid:

        logger.warning(

            "User provided incorrect captcha response",
            
            extra={

                "chat_id": chat_id,

                "text_length": len(text)
            }
        )

        await UIManager.update(

            chat_id = chat_id,

            text = "❌ إجابة خاطئة.\nحاول مرة أخرى.",

            reply_markup = None
        )

        return False
    
    await CaptchaManager.clear(

        chat_id = chat_id
    )

    logger.info(

        "User provided correct captcha response",

        extra={

            "chat_id": chat_id,

            "text_length": len(text)
        }
    )

    await UIManager.update(

        chat_id = chat_id,

        text = "✅ تم التحقق بنجاح.",

        reply_markup = None
    )

    logger.info(

        "User completed captcha verification",

        extra={
            
            "chat_id": chat_id
        }
    )
    return True