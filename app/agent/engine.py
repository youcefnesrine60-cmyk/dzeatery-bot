# ==============================================
# MoulAI Platform - Agent-as-a-Service
# Author: Youcef Nesrine
# License: CC BY-NC-ND 4.0
# Copyright (c) 2026 Youcef Nesrine
# ==============================================

# ==============================================
# 🤖 AGENT ENGINE
# المحرك الرئيسي للوكيل الذكي
# ==============================================

from typing import (
    Any,
    Dict,
    Optional,
    Tuple,
)

from app.agent.config import (
    AgentConfig,
    LanguageCode,
    default_config,
)
from app.agent.executor.action_executor import (
    ActionContext,
    ActionExecutor,
    ExecutionResult,
)
from app.agent.language.detector import detect_language
from app.agent.memory.memory_manager import (
    MemoryManager,
    SessionData,
    memory_manager as default_memory,
)
from app.agent.nlu.entity_extractor import (
    EntityExtractor,
    ExtractionResult,
)
from app.agent.nlu.intent_classifier import (
    IntentClassifier,
    IntentResult,
)
from app.agent.prompts.translations import (
    ERROR_RESPONSES,
    GOODBYE_RESPONSES,
    GREETING_RESPONSES,
    HELP_RESPONSES,
)
from app.core.logger import logger

# ==============================================
# 🧩 TYPES
# ==============================================

AgentResponse = Dict[str, Any]
ProcessResult = Dict[str, Any]

# ==============================================
# 🤖 AGENT ENGINE
# ==============================================


class AgentEngine:
    """
    المحرك الرئيسي للوكيل الذكي.
    
    يجمع جميع المكونات:
        - كاشف اللغة
        - مصنف النوايا
        - مستخرج الكيانات
        - منفذ الإجراءات
        - مدير الذاكرة
    
    Attributes:
        config: إعدادات الوكيل
        intent_classifier: مصنف النوايا
        entity_extractor: مستخرج الكيانات
        action_executor: منفذ الإجراءات
        memory_manager: مدير الذاكرة
    """

    def __init__(
        self,
        *,
        config: Optional[AgentConfig] = None,
        intent_classifier: Optional[IntentClassifier] = None,
        entity_extractor: Optional[EntityExtractor] = None,
        action_executor: Optional[ActionExecutor] = None,
        memory_manager: Optional[MemoryManager] = None,
    ) -> None:
        """
        تهيئة محرك الوكيل.
        
        Args:
            config: إعدادات الوكيل (اختياري)
            intent_classifier: مصنف النوايا (اختياري)
            entity_extractor: مستخرج الكيانات (اختياري)
            action_executor: منفذ الإجراءات (اختياري)
            memory_manager: مدير الذاكرة (اختياري)
        """
        self.config: AgentConfig = config or default_config

        # تهيئة المكونات
        self.intent_classifier: IntentClassifier = (
            intent_classifier or IntentClassifier()
        )
        self.entity_extractor: EntityExtractor = (
            entity_extractor or EntityExtractor()
        )
        self.action_executor: ActionExecutor = (
            action_executor or ActionExecutor()
        )
        self.memory_manager: MemoryManager = (
            memory_manager or default_memory
        )

        logger.info(
            "agent_engine_initialized",
            extra={
                "config": {
                    "llm_provider": self.config.llm_provider,
                    "max_history": self.config.max_history,
                    "confidence_threshold": self.config.confidence_threshold,
                    "default_language": self.config.default_language,
                },
            },
        )

    # ==========================================
    # 🎯 PROCESS MESSAGE
    # ==========================================

    async def process(
        self,
        *,
        user_id: int,
        message: str,
        session_id: Optional[str] = None,
        channel: str = "telegram",
        context: Optional[Dict[str, Any]] = None,
    ) -> ProcessResult:
        """
        معالجة رسالة المستخدم.
        
        Args:
            user_id: معرف المستخدم
            message: نص الرسالة
            session_id: معرف الجلسة (اختياري)
            channel: القناة (telegram, web, whatsapp)
            context: سياق إضافي (اختياري)
            
        Returns:
            ProcessResult: {
                "response": str,
                "session_id": str,
                "language": str,
                "intent": str,
                "entities": Dict,
                "action_result": Dict,
                "context": Dict,
                "channel": str,
            }
        """
        logger.info(
            "agent_process_started",
            extra={
                "user_id": user_id,
                "session_id": session_id,
                "channel": channel,
                "message_preview": message[:50],
            },
        )

        # 1️⃣ كشف اللغة
        detected_lang, confidence = detect_language(text=message)
        language = detected_lang or self.config.default_language

        logger.debug(
            "agent_language_detected",
            extra={
                "language": language,
                "confidence": confidence,
            },
        )

        # 2️⃣ الحصول على الجلسة أو إنشاؤها
        if session_id:
            session = await self.memory_manager.get_session(
                session_id=session_id,
            )
        else:
            session = None

        if not session:
            # إنشاء جلسة جديدة
            session = await self.memory_manager.create_session(
                session_id=session_id or f"{channel}_{user_id}",
                user_id=user_id,
                initial_context=context,
            )
            session_id = session["session_id"]

            # إضافة رسالة الترحيب إلى السياق
            await self.memory_manager.add_message(
                session_id=session_id,
                message=GREETING_RESPONSES.get(
                    language,
                    GREETING_RESPONSES["ar"],
                ),
                role="assistant",
            )

            logger.info(
                "agent_new_session_created",
                extra={
                    "session_id": session_id,
                    "user_id": user_id,
                },
            )

        # 3️⃣ إضافة رسالة المستخدم إلى الذاكرة
        await self.memory_manager.add_message(
            session_id=session_id,
            message=message,
            role="user",
            metadata={
                "language": language,
                "channel": channel,
            },
        )

        # 4️⃣ استخراج الكيانات
        extraction_result = await self.entity_extractor.extract(
            text=message,
            language=language,
        )

        entities = extraction_result.get("entities", [])
        entities_dict = {
            e.get("type"): e.get("value")
            for e in entities
            if e.get("type") and e.get("value") is not None
        }

        logger.debug(
            "agent_entities_extracted",
            extra={
                "entities": entities_dict,
                "count": len(entities),
            },
        )

        # 5️⃣ تصنيف النية
        intent_result = await self.intent_classifier.classify(
            text=message,
            language=language,
        )

        intent = intent_result.get("intent", "unknown")
        intent_confidence = intent_result.get("confidence", 0.0)

        # دمج الكيانات من المصنف والمستخرج
        classifier_entities = intent_result.get("entities", {})
        all_entities = {**classifier_entities, **entities_dict}

        logger.debug(
            "agent_intent_classified",
            extra={
                "intent": intent,
                "confidence": intent_confidence,
            },
        )

        # 6️⃣ تحديث الذاكرة بالنتائج
        await self.memory_manager.update_context(
            session_id=session_id,
            updates={
                "last_intent": intent,
                "last_language": language,
            },
        )

        if all_entities:
            await self.memory_manager.update_entities(
                session_id=session_id,
                entities=all_entities,
            )

        # 7️⃣ تنفيذ الإجراء
        action_context: ActionContext = {
            "session_id": session_id,
            "user_id": user_id,
            "channel": channel,
            "language": language,
            "history": await self.memory_manager.get_history(
                session_id=session_id,
                limit=5,
            ),
            "context": await self.memory_manager.get_context(
                session_id=session_id,
            ),
        }

        action_result = await self.action_executor.execute(
            intent_result={
                "intent": intent,
                "confidence": intent_confidence,
                "entities": all_entities,
                "language": language,
            },
            context=action_context,
        )

        # 8️⃣ توليد الرد
        response = await self._generate_response(
            intent=intent,
            language=language,
            action_result=action_result,
            message=message,
        )

        # 9️⃣ حفظ رد الوكيل في الذاكرة
        await self.memory_manager.add_message(
            session_id=session_id,
            message=response,
            role="assistant",
            metadata={
                "intent": intent,
                "action": action_result.get("action"),
                "success": action_result.get("success"),
            },
        )

        # 🔟 تحديث آخر نشاط
        await self.memory_manager.update_context(
            session_id=session_id,
            updates={
                "last_action": action_result.get("action"),
                "last_response": response[:100],
            },
        )

        logger.info(
            "agent_process_completed",
            extra={
                "session_id": session_id,
                "intent": intent,
                "action": action_result.get("action"),
                "success": action_result.get("success"),
            },
        )

        return {
            "response": response,
            "session_id": session_id,
            "language": language,
            "intent": intent,
            "entities": all_entities,
            "intent_confidence": intent_confidence,
            "action_result": action_result,
            "context": await self.memory_manager.get_context(
                session_id=session_id,
            ),
            "channel": channel,
        }

    # ==========================================
    # 📝 RESPONSE GENERATION
    # ==========================================

    async def _generate_response(
        self,
        *,
        intent: str,
        language: str,
        action_result: ExecutionResult,
        message: str,
    ) -> str:
        """
        توليد الرد المناسب.
        
        Args:
            intent: النية المستخرجة
            language: رمز اللغة
            action_result: نتيجة تنفيذ الإجراء
            message: رسالة المستخدم الأصلية
            
        Returns:
            الرد النهائي
        """
        # إذا كان الإجراء ناجحاً، استخدم رسالة الإجراء
        if action_result.get("success"):
            response = action_result.get("message", "")
            if response:
                return response

        # إذا فشل الإجراء، استخدم رسالة الخطأ
        if not action_result.get("success"):
            error = action_result.get("error")
            if error == "unknown_intent":
                return ERROR_RESPONSES.get(
                    language,
                    ERROR_RESPONSES["ar"],
                )
            return action_result.get("message", "حدث خطأ غير متوقع.")

        # حالات خاصة للنوايا
        if intent == "greeting":
            return GREETING_RESPONSES.get(
                language,
                GREETING_RESPONSES["ar"],
            )

        if intent == "goodbye":
            return GOODBYE_RESPONSES.get(
                language,
                GOODBYE_RESPONSES["ar"],
            )

        if intent == "help":
            return HELP_RESPONSES.get(
                language,
                HELP_RESPONSES["ar"],
            )

        # رد افتراضي
        return "آسف، لم أتمكن من معالجة طلبك. يرجى المحاولة مرة أخرى."

    # ==========================================
    # 📊 GET SESSION INFO
    # ==========================================

    async def get_session_info(
        self,
        *,
        session_id: str,
    ) -> Dict[str, Any]:
        """
        الحصول على معلومات الجلسة.
        
        Args:
            session_id: معرف الجلسة
            
        Returns:
            معلومات الجلسة
        """
        return await self.memory_manager.get_session_summary(
            session_id=session_id,
        )

    async def get_context(
        self,
        *,
        session_id: str,
    ) -> Dict[str, Any]:
        """
        الحصول على سياق الجلسة.
        
        Args:
            session_id: معرف الجلسة
            
        Returns:
            سياق الجلسة
        """
        return await self.memory_manager.get_context(
            session_id=session_id,
        )

    async def clear_session(
        self,
        *,
        session_id: str,
    ) -> bool:
        """
        مسح الجلسة.
        
        Args:
            session_id: معرف الجلسة
            
        Returns:
            True إذا تم المسح
        """
        return await self.memory_manager.delete_session(
            session_id=session_id,
        )


# ==============================================
# 🌍 GLOBAL INSTANCE
# ==============================================

# إنشاء محرك وكيل عالمي
agent_engine = AgentEngine()


# ==============================================
# 🔍 UTILITY FUNCTIONS
# ==============================================

# ==============================================
# PROCESS MESSAGE
# ==============================================

async def process_message(
    *,
    user_id: int,
    message: str,
    session_id: Optional[str] = None,
    channel: str = "telegram",
    engine: Optional[AgentEngine] = None,
) -> ProcessResult:
    """
    معالجة رسالة المستخدم (دالة مساعدة).
    
    Args:
        user_id: معرف المستخدم
        message: نص الرسالة
        session_id: معرف الجلسة (اختياري)
        channel: القناة
        engine: محرك الوكيل (اختياري)
        
    Returns:
        نتيجة المعالجة
    """
    logger.debug(
        "process_message_called",
        extra={
            "user_id": user_id,
            "session_id": session_id,
            "channel": channel,
            "message_length": len(message) if message else 0,
        },
    )

    if engine is None:
        engine = agent_engine

    return await engine.process(
        user_id=user_id,
        message=message,
        session_id=session_id,
        channel=channel,
    )


# ==============================================
# 📋 EXPORTS
# ==============================================

__all__ = [
    "AgentEngine",
    "agent_engine",
    "process_message",
    "AgentResponse",
    "ProcessResult",
]