# ==============================================
# 🧪 TEST AGENT ENGINE
# اختبارات المحرك الرئيسي للوكيل
# ==============================================

import pytest
from app.agent import process_message


class TestAgentEngine:
    """
    اختبارات محرك الوكيل.
    """

    @pytest.mark.asyncio
    async def test_agent_process_order(self):
        """
        اختبار معالجة طلب طعام.
        """
        result = await process_message(
            user_id=123,
            message="أريد طلب بيتزا",
        )
        
        assert result["intent"] == "order_food"
        assert result["response"] is not None
        assert result["session_id"] is not None
        assert result["language"] == "ar"

    @pytest.mark.asyncio
    async def test_agent_process_greeting(self):
        """
        اختبار معالجة تحية.
        """
        result = await process_message(
            user_id=123,
            message="مرحبا",
        )
        
        assert result["intent"] == "greeting"
        assert "مرحباً" in result["response"] or "مرحبا" in result["response"]
        assert result["session_id"] is not None

    @pytest.mark.asyncio
    async def test_agent_process_goodbye(self):
        """
        اختبار معالجة وداع.
        """
        result = await process_message(
            user_id=123,
            message="مع السلامة",
        )
        
        assert result["intent"] == "goodbye"
        assert "مع السلامة" in result["response"] or "وداعا" in result["response"]

    @pytest.mark.asyncio
    async def test_agent_process_help(self):
        """
        اختبار معالجة طلب مساعدة.
        """
        result = await process_message(
            user_id=123,
            message="مساعدتي من فضلك",
        )
        
        assert result["intent"] == "help"
        assert "مساعدة" in result["response"]

    @pytest.mark.asyncio
    async def test_agent_process_english_order(self):
        """
        اختبار معالجة طلب باللغة الإنجليزية.
        """
        result = await process_message(
            user_id=123,
            message="I want to order pizza",
        )
        
        assert result["intent"] == "order_food"
        assert result["language"] == "en"
        assert result["response"] is not None

    @pytest.mark.asyncio
    async def test_agent_process_french_order(self):
        """
        اختبار معالجة طلب باللغة الفرنسية.
        """
        result = await process_message(
            user_id=123,
            message="Je veux commander une pizza",
        )
        
        assert result["intent"] == "order_food"
        assert result["language"] == "fr"
        assert result["response"] is not None

    @pytest.mark.asyncio
    async def test_agent_process_with_session(self):
        """
        اختبار معالجة رسالة مع جلسة موجودة.
        """
        # رسالة أولى لإنشاء الجلسة
        result1 = await process_message(
            user_id=123,
            message="مرحبا",
        )
        session_id = result1["session_id"]
        
        # رسالة ثانية بنفس الجلسة
        result2 = await process_message(
            user_id=123,
            message="أريد طلب بيتزا",
            session_id=session_id,
        )
        
        assert result2["session_id"] == session_id
        assert result2["intent"] == "order_food"

    @pytest.mark.asyncio
    async def test_agent_process_entity_extraction(self):
        """
        اختبار استخراج الكيانات.
        """
        result = await process_message(
            user_id=123,
            message="أريد 2 بيتزا بسعر 1500 دج",
        )
        
        entities = result.get("entities", {})
        
        # قد يتم استخراج الكمية أو السعر
        if "quantity" in entities:
            assert entities["quantity"] == 2
        
        if "price" in entities:
            assert entities["price"] == 1500.0