import pytest
from echo_tutor.config import get_settings

def test_settings():
    """Test that settings can be loaded"""
    settings = get_settings()
    assert settings is not None
    assert settings.qwen_model == "qwen-turbo"
