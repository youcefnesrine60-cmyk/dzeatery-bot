# ==============================================
# 🧪 TEST LANGUAGE DETECTOR - Pytest
# اختبار كشف اللغة باستخدام pytest
# ==============================================

import pytest
from app.agent.language.detector import detect_language


class TestLanguageDetector:
    """
    اختبارات كاشف اللغة.
    """
    
    def test_arabic_detection(self):
        """
        اختبار كشف اللغة العربية.
        """
        text = "مرحبا كيف حالك"
        lang, confidence = detect_language(text=text)
        assert lang == "ar"
        assert confidence > 0.5
    
    def test_english_detection(self):
        """
        اختبار كشف اللغة الإنجليزية.
        """
        text = "Hello how are you"
        lang, confidence = detect_language(text=text)
        assert lang == "en"
        assert confidence > 0.5
    
    def test_french_detection(self):
        """
        اختبار كشف اللغة الفرنسية.
        """
        text = "Bonjour comment allez-vous"
        lang, confidence = detect_language(text=text)
        assert lang == "fr"
        assert confidence > 0.5
    
    def test_mixed_arabic_english(self):
        """
        اختبار كشف اللغة المختلطة (عربي + إنجليزي).
        """
        text = "مرحبا Hello كيف حالك"
        lang, confidence = detect_language(text=text)
        assert lang == "ar"
        assert confidence > 0.4
    
    def test_empty_text(self):
        """
        اختبار النص الفارغ.
        """
        text = ""
        lang, confidence = detect_language(text=text)
        assert lang == "ar"
        assert confidence == 0.0
    
    def test_short_text(self):
        """
        اختبار النص القصير.
        """
        text = "Hi"
        lang, confidence = detect_language(text=text)
        # قد يكتشف الإنجليزية أو العربية حسب السياق
        assert lang in ["en", "ar"]
    
    @pytest.mark.parametrize("text,expected_lang", [
        ("مرحبا", "ar"),
        ("Hello", "en"),
        ("Bonjour", "fr"),
        ("السلام عليكم", "ar"),
        ("Good morning", "en"),
        ("Bonsoir", "fr"),
    ])
    def test_multiple_texts(self, text, expected_lang):
        """
        اختبار نصوص متعددة.
        """
        lang, confidence = detect_language(text=text)
        assert lang == expected_lang
        assert confidence >= 0.0