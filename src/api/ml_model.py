import os
import logging
from typing import Any, Dict

from .config import settings

logger = logging.getLogger(__name__)

_model = None
_tokenizer = None


def load_model(model_path: str | None = None):
    """Attempt to load the model and tokenizer. This function is tolerant and will
    try 4-bit loading if configured. It returns a (model, tokenizer) tuple.
    """
    global _model, _tokenizer
    model_path = model_path or settings.MODEL_PATH
    try:
        from transformers import AutoModelForCausalLM, AutoTokenizer
    except Exception as e:
        raise RuntimeError("transformers is required to load the LLM: install transformers") from e

    # lazy import bitsandbytes only if requested
    load_in_4bit = settings.LOAD_IN_4BIT
    try:
        if load_in_4bit:
            # 4-bit loading requires bitsandbytes to be installed
            import bitsandbytes as bnb  # type: ignore
            _model = AutoModelForCausalLM.from_pretrained(
                model_path,
                load_in_4bit=True,
                device_map="auto",
                trust_remote_code=True,
            )
        else:
            _model = AutoModelForCausalLM.from_pretrained(model_path, device_map="auto", trust_remote_code=True)
    except Exception:
        # fallback to CPU loading (very slow or may OOM)
        logger.exception("Failed to load model with 4-bit/device_map fallback, trying cpu.")
        _model = AutoModelForCausalLM.from_pretrained(model_path, device_map={"": "cpu"}, trust_remote_code=True)

    try:
        _tokenizer = AutoTokenizer.from_pretrained(model_path, use_fast=False)
    except Exception:
        _tokenizer = AutoTokenizer.from_pretrained(model_path)

    return _model, _tokenizer


def generate(prompt: str, max_new_tokens: int = 128, **gen_kwargs) -> Dict[str, Any]:
    """Generate text from prompt. Returns a dict with the output text and raw model output.
    This function is blocking (calls into HF/torch) — call via run_in_threadpool if needed.
    """
    global _model, _tokenizer
    if _model is None or _tokenizer is None:
        load_model()

    inputs = _tokenizer(prompt, return_tensors="pt")
    # move inputs to model device
    device = next(_model.parameters()).device
    inputs = {k: v.to(device) for k, v in inputs.items()}
    output_ids = _model.generate(**inputs, max_new_tokens=max_new_tokens, **gen_kwargs)
    text = _tokenizer.decode(output_ids[0], skip_special_tokens=True)
    return {"text": text}
