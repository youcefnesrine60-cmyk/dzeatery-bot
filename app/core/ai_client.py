# ==============================================
# 🤖 AI CLIENT
# مسؤول عن التواصل مع نماذج الذكاء الاصطناعي
# يدعم OpenAI و DeepSeek
# ==============================================

import json
import re
from typing import (
    Any, 
    Dict, 
    Optional
)

from openai import OpenAI

from app.core.config import settings
from app.core.logger import logger

# ==============================================
# 🧩 TYPES
# ==============================================

AIMessage = Dict[str, str]
AIMessages = list[AIMessage]
AIResponse = Dict[str, Any]

# ==============================================
# 🤖 AI CLIENT
# ==============================================

class AIClient:
    """
    عميل موحد للذكاء الاصطناعي
    
    يدعم:
        - OpenAI (GPT-4, GPT-4o-mini, etc.)
        - DeepSeek (deepseek-chat, deepseek-reasoner)
    
    Attributes:
        client: عميل OpenAI
        model: اسم النموذج المستخدم
    """

    def __init__(
        self,
    ) -> None:
        """
        تهيئة العميل مع الإعدادات من .env
        """
        self.client = OpenAI(
            api_key=settings.OPENAI_API_KEY,
            base_url=settings.OPENAI_BASE_URL,
        )
        self.model = settings.AI_MODEL

        logger.info(
            "ai_client_initialized",
            extra={
                "model": self.model,
                "base_url": settings.OPENAI_BASE_URL,
            },
        )

    # ==========================================
    # 🗣️ CHAT
    # ==========================================

    async def chat(
        *,
        self,
        message: str,
        system_prompt: Optional[str] = None,
    ) -> str:
        """
        إرسال رسالة والحصول على رد من الذكاء الاصطناعي

        Args:
            message: رسالة المستخدم
            system_prompt: تعليمات النظام (اختياري)

        Returns:
            رد الذكاء الاصطناعي
        """
        try:
            messages: AIMessages = []

            # إضافة تعليمات النظام
            if system_prompt:
                messages.append({
                    "role": "system",
                    "content": system_prompt,
                })
            else:
                messages.append({
                    "role": "system",
                    "content": "أنت مساعد ذكي للمطاعم، تتحدث العربية والفرنسية والإنجليزية.",
                })

            # إضافة رسالة المستخدم
            messages.append({
                "role": "user",
                "content": message,
            })

            # إرسال الطلب
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=1000,
            )

            # استخراج الرد
            reply = response.choices[0].message.content

            logger.debug(
                "ai_chat_success",
                extra={
                    "message_length": len(message),
                    "reply_length": len(reply),
                },
            )

            return reply

        except Exception as e:
            logger.exception(
                "ai_chat_failed",
                extra={
                    "error": str(e),
                    "message": message[:100],
                },
            )
            return "عذراً، حدث خطأ في معالجة طلبك. يرجى المحاولة مرة أخرى."

    # ==========================================
    # 📊 ANALYZE ORDER
    # ==========================================

    async def analyze_order(
        *,
        self,
        order_text: str,
    ) -> AIResponse:
        """
        تحليل طلب العميل واستخراج المنتجات

        Args:
            order_text: نص الطلب

        Returns:
            قاموس يحتوي على المنتجات والملاحظات
        """
        system_prompt = """
        أنت مساعد مطعم ذكي. مهمتك تحليل طلبات العملاء واستخراج:
        1. المنتجات المطلوبة
        2. الكميات
        3. الملاحظات (مثل: بدون زيتون، إضافة جبن)
        4. الاقتراحات (Upselling)

        أخرج النتيجة بصيغة JSON.
        """

        response = await self.chat(
            message=order_text,
            system_prompt=system_prompt,
        )

        # محاولة تحويل الرد إلى JSON
        try:
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except (json.JSONDecodeError, AttributeError):
            pass

        # إذا فشل التحويل، أرجع النص كامل
        return {
            "raw_response": response,
            "products": [],
            "notes": order_text,
        }


# ==============================================
# 🌍 GLOBAL INSTANCE
# ==============================================

ai_client = AIClient()