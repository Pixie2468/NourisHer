import logging
import threading
from typing import Any, Dict, Iterator, cast

from api.config import settings

logger = logging.getLogger(__name__)

_model = None
_tokenizer = None
_system_prompt: str | None = None


def load_system_prompt(path: str | None = None) -> str:
    global _system_prompt
    if _system_prompt is not None:
        return _system_prompt
    prompt_path = path or settings.SYSTEM_PROMPT_PATH
    try:
        with open(prompt_path, "r", encoding="utf-8") as handle:
            _system_prompt = handle.read().strip()
    except Exception:
        _system_prompt = ""
    return _system_prompt


def load_model(model_path: str | None = None):
    """Attempt to load the model and tokenizer. This function is tolerant and will
    try 4-bit loading if configured. It returns a (model, tokenizer) tuple.
    """
    global _model, _tokenizer
    model_path = model_path or settings.MODEL_PATH
    try:
        from transformers import AutoModelForCausalLM, AutoTokenizer
    except Exception as e:
        raise RuntimeError(
            "transformers is required to load the LLM: install transformers"
        ) from e

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
            _model = AutoModelForCausalLM.from_pretrained(
                model_path, device_map="auto", trust_remote_code=True
            )
    except Exception:
        # fallback to CPU loading (very slow or may OOM)
        logger.exception(
            "Failed to load model with 4-bit/device_map fallback, trying cpu."
        )
        _model = AutoModelForCausalLM.from_pretrained(
            model_path, device_map={"": "cpu"}, trust_remote_code=True
        )

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
        _model, _tokenizer = load_model()

    system_prompt = load_system_prompt()
    final_prompt = prompt if not system_prompt else f"{system_prompt}\n\n{prompt}".strip()
    inputs = _tokenizer(final_prompt, return_tensors="pt")
    # move inputs to model device
    device = next(_model.parameters()).device
    inputs = {k: v.to(device) for k, v in inputs.items()}
    output_ids = cast(Any, _model).generate(
        **inputs, max_new_tokens=max_new_tokens, **gen_kwargs
    )
    input_len = inputs["input_ids"].shape[-1]
    new_tokens = output_ids[0][input_len:]
    text = _tokenizer.decode(new_tokens, skip_special_tokens=True)
    return {"text": text}


def stream_generate(
    prompt: str, max_new_tokens: int = 128, **gen_kwargs
) -> Iterator[str]:
    """Stream generated tokens for a prompt."""
    global _model, _tokenizer
    if _model is None or _tokenizer is None:
        _model, _tokenizer = load_model()

    try:
        from transformers import TextIteratorStreamer
    except Exception as e:
        raise RuntimeError(
            "transformers is required to stream tokens: install transformers"
        ) from e

    system_prompt = load_system_prompt()
    final_prompt = prompt if not system_prompt else f"{system_prompt}\n\n{prompt}".strip()
    inputs = _tokenizer(final_prompt, return_tensors="pt")
    device = next(_model.parameters()).device
    inputs = {k: v.to(device) for k, v in inputs.items()}

    streamer = TextIteratorStreamer(
        _tokenizer, skip_prompt=True, skip_special_tokens=True
    )
    generation_kwargs = dict(
        **inputs, max_new_tokens=max_new_tokens, streamer=streamer, **gen_kwargs
    )
    thread = threading.Thread(target=cast(Any, _model).generate, kwargs=generation_kwargs)
    thread.start()
    for text in streamer:
        if text:
            yield text
