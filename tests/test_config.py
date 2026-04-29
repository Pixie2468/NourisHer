import os
import sys

# ensure src is importable as package
sys.path.insert(0, os.path.abspath("."))


def test_settings_defaults():
    from nourisher.api.config import settings

    assert settings.MODEL_PATH
    assert settings.DATABASE_URL
    assert settings.SYSTEM_PROMPT_PATH == "configs/system_prompt.txt"
