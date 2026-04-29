import os
import sys

# ensure src is importable as package
sys.path.insert(0, os.path.abspath("."))


def test_load_system_prompt_default():
    from scripts.finetune_pcos_lora import load_system_prompt

    prompt = load_system_prompt(None)
    assert "pcos" in prompt.lower()


def test_iter_records_reads_jsonl(tmp_path):
    from scripts.finetune_pcos_lora import iter_records

    data = '{"a":1,"pcos":0}\n{"a":2,"pcos":1}\n'
    path = tmp_path / "pcos.jsonl"
    path.write_text(data, encoding="utf-8")

    records = list(iter_records(str(path)))
    assert len(records) == 2
    assert records[0]["pcos"] == 0
    assert records[1]["pcos"] == 1


def test_build_prompt_includes_features():
    from scripts.finetune_pcos_lora import build_prompt

    system_prompt = "SYSTEM"
    features = {"Age": 28, "weight_kg": 44.6}
    prompt = build_prompt(system_prompt, features)
    assert "SYSTEM" in prompt
    assert "Patient features" in prompt
    assert "Age" in prompt
    assert "weight_kg" in prompt
