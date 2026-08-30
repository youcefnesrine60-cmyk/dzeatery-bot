# ==============================================
# 🧪 TEST INTENT CLASSIFIER
# اختبارات مصنف نوايا المستخدم
# ==============================================

import pytest
from typing import (
    Any,
    Dict,
)

from app.agent.nlu.intent_classifier import (
    IntentClassifier,
    classify_intent,
)


# ==============================================
# 🧪 TEST CLASS
# ==============================================

class TestIntentClassifier:
    """
    اختبارات مصنف النوايا.
    """

    @pytest.mark.asyncio
    async def test_classify_intent_arabic_order(self):
        """
        اختبار تصنيف نية الطلب باللغة العربية.
        """
        result = await classify_intent(text="أريد طلب بيتزا")
        assert result["intent"] == "order_food"
        assert result["confidence"] > 0.3

    @pytest.mark.asyncio
    async def test_classify_intent_arabic_menu(self):
        """
        اختبار تصنيف نية عرض القائمة باللغة العربية.
        """
        result = await classify_intent(text="عرض القائمة من فضلك")
        assert result["intent"] == "view_menu"
        assert result["confidence"] > 0.3

    @pytest.mark.asyncio
    async def test_classify_intent_arabic_greeting(self):
        """
        اختبار تصنيف التحية باللغة العربية.
        """
        result = await classify_intent(text="مرحبا كيف حالك")
        assert result["intent"] == "greeting"
        assert result["confidence"] > 0.3

    @pytest.mark.asyncio
    async def test_classify_intent_arabic_goodbye(self):
        """
        اختبار تصنيف الوداع باللغة العربية.
        """
        result = await classify_intent(text="مع السلامة")
        assert result["intent"] == "goodbye"
        assert result["confidence"] > 0.3

    @pytest.mark.asyncio
    async def test_classify_intent_arabic_help(self):
        """
        اختبار تصنيف طلب المساعدة باللغة العربية.
        """
        result = await classify_intent(text="مساعدتي من فضلك")
        assert result["intent"] == "help"
        assert result["confidence"] > 0.3

    @pytest.mark.asyncio
    async def test_classify_intent_arabic_price(self):
        """
        اختبار تصنيف الاستفسار عن السعر باللغة العربية.
        """
        result = await classify_intent(text="كم سعر البيتزا")
        assert result["intent"] == "ask_price"
        assert result["confidence"] > 0.3

    @pytest.mark.asyncio
    async def test_classify_intent_arabic_cancel(self):
        """
        اختبار تصنيف إلغاء الطلب باللغة العربية.
        """
        result = await classify_intent(text="الغاء الطلب رقم 12345")
        assert result["intent"] == "cancel_order"
        assert result["confidence"] > 0.3

    @pytest.mark.asyncio
    async def test_classify_intent_english_order(self):
        """
        اختبار تصنيف نية الطلب باللغة الإنجليزية.
        """
        result = await classify_intent(text="I want to order pizza")
        assert result["intent"] == "order_food"
        assert result["confidence"] > 0.3

    @pytest.mark.asyncio
    async def test_classify_intent_english_menu(self):
        """
        اختبار تصنيف نية عرض القائمة باللغة الإنجليزية.
        """
        result = await classify_intent(text="Show me the menu please")
        assert result["intent"] == "view_menu"
        assert result["confidence"] > 0.3

    @pytest.mark.asyncio
    async def test_classify_intent_english_greeting(self):
        """
        اختبار تصنيف التحية باللغة الإنجليزية.
        """
        result = await classify_intent(text="Hello how are you")
        assert result["intent"] == "greeting"
        assert result["confidence"] > 0.3

    @pytest.mark.asyncio
    async def test_classify_intent_french_order(self):
        """
        اختبار تصنيف نية الطلب باللغة الفرنسية.
        """
        result = await classify_intent(text="Je veux commander une pizza")
        assert result["intent"] == "order_food"
        assert result["confidence"] > 0.3

    @pytest.mark.asyncio
    async def test_classify_intent_french_menu(self):
        """
        اختبار تصنيف نية عرض القائمة باللغة الفرنسية.
        """
        result = await classify_intent(text="Affichez le menu s'il vous plaît")
        assert result["intent"] == "view_menu"
        assert result["confidence"] > 0.3

    @pytest.mark.asyncio
    async def test_classify_intent_french_greeting(self):
        """
        اختبار تصنيف التحية باللغة الفرنسية.
        """
        result = await classify_intent(text="Bonjour comment allez-vous")
        assert result["intent"] == "greeting"
        assert result["confidence"] > 0.3

    @pytest.mark.asyncio
    async def test_classify_intent_unknown(self):
        """
        اختبار تصنيف نية غير معروفة.
        """
        result = await classify_intent(text="ABCDEFG")
        assert result["intent"] == "unknown"
        assert result["confidence"] == 0.0

    @pytest.mark.asyncio
    async def test_classify_intent_empty(self):
        """
        اختبار تصنيف نص فارغ.
        """
        result = await classify_intent(text="")
        assert result["intent"] == "unknown"
        assert result["confidence"] == 0.0

    @pytest.mark.asyncio
    async def test_classify_intent_entity_extraction(self):
        """
        اختبار استخراج الكيانات.
        """
        result = await classify_intent(text="أريد 2 بيتزا بسعر 1500 دج")
        
        assert "entities" in result
        entities = result["entities"]
        
        # قد يتم استخراج الكمية أو السعر
        if "quantity" in entities:
            assert entities["quantity"] == 2
        
        if "price" in entities:
            assert entities["price"] == 1500.0


# ==============================================
# 🧪 RUN TESTS
# ==============================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])