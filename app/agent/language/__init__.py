# ==============================================
# MoulAI Platform - Agent-as-a-Service
# Author: Youcef Nesrine
# License: CC BY-NC-ND 4.0
# Copyright (c) 2026 Youcef Nesrine
# ==============================================
# 🌍 LANGUAGE MODULE
# وحدة كشف اللغة
# ==============================================

from app.agent.language.detector import (
    LanguageDetector,
    detect_language,
    get_language_name,
    LanguageDetectionResult,
)

__all__ = [
    "LanguageDetector",
    "detect_language",
    "get_language_name",
    "LanguageDetectionResult",
]