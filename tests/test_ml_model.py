import os
import sys
from types import SimpleNamespace

import pytest

# ensure src is importable as package
sys.path.insert(0, os.path.abspath("."))


class DummyTokenizer:
    def __init__(self):
        self.eos_token = "<eos>"
        self.last_text = None

    def __call__(self, text, return_tensors="pt"):
        del return_tensors
        self.last_text = text
        return {"input_ids": DummyTensor(len(text))}

    def decode(self, tokens, skip_special_tokens=True):
        del tokens
        del skip_special_tokens
        return "pcos: 1"


class DummyTensor:
    def __init__(self, size):
        self._size = size

    def to(self, device):
        del device
        return self

    @property
    def shape(self):
        return (1, self._size)

    def __getitem__(self, _key):
        return [0, 1, 2]


class DummyModel:
    def parameters(self):
        return iter([SimpleNamespace(device="cpu")])

    def generate(self, **kwargs):
        del kwargs
        return [list(range(10))]


def test_generate_uses_system_prompt(monkeypatch, tmp_path):
    import src.api.ml_model as ml_model

    prompt_path = tmp_path / "system_prompt.txt"
    prompt_path.write_text("SYSTEM", encoding="utf-8")

    monkeypatch.setattr(ml_model, "_model", DummyModel())
    tokenizer = DummyTokenizer()
    monkeypatch.setattr(ml_model, "_tokenizer", tokenizer)
    monkeypatch.setattr(ml_model.settings, "SYSTEM_PROMPT_PATH", str(prompt_path))
    monkeypatch.setattr(ml_model, "_system_prompt", None)

    out = ml_model.generate("INPUT")
    assert out["text"] == "pcos: 1"
    assert "SYSTEM" in tokenizer.last_text


def test_stream_generate_yields(monkeypatch):
    import src.api.ml_model as ml_model

    class DummyStreamer:
        def __init__(self, *args, **kwargs):
            del args
            del kwargs
            self._chunks = ["pc", "os", ": 0"]

        def __iter__(self):
            return iter(self._chunks)

    class DummyTransformers:
        TextIteratorStreamer = DummyStreamer

    monkeypatch.setitem(sys.modules, "transformers", DummyTransformers)
    monkeypatch.setattr(ml_model, "_model", DummyModel())
    monkeypatch.setattr(ml_model, "_tokenizer", DummyTokenizer())

    class DummyThread:
        def __init__(self, target=None, kwargs=None):
            del target
            del kwargs

        def start(self):
            return None

    monkeypatch.setattr(ml_model.threading, "Thread", DummyThread)

    chunks = list(ml_model.stream_generate("INPUT"))
    assert "".join(chunks) == "pcos: 0"
