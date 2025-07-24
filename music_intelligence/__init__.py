"""
Music Intelligence Module for AI Music Producer Extension

This module provides AI-powered music intelligence including:
- Style analysis and generation
- Stock plugin expertise
- Sample curation
- Harmonic analysis
- Arrangement generation
"""

__version__ = "1.0.0"

from .gemini_orchestrator import GeminiOrchestrator
from .style_analyzer import StyleAnalyzer
from .stock_plugin_expert import StockPluginExpert
from .ableton_integration import EnhancedAbletonIntegration
from .instrument_manager import InstrumentManager
from .ai_experts import (
    AIExpertOrchestrator,
    DrumExpert,
    BassExpert,
    HarmonyExpert,
    MelodyExpert
)

__all__ = [
    "GeminiOrchestrator",
    "StyleAnalyzer", 
    "StockPluginExpert",
    "EnhancedAbletonIntegration",
    "InstrumentManager",
    "AIExpertOrchestrator",
    "DrumExpert",
    "BassExpert",
    "HarmonyExpert",
    "MelodyExpert"
] 