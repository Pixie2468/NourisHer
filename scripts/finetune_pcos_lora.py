#!/usr/bin/env python3
"""
Fine-tune a causal LLM with LoRA/QLoRA for PCOS classification.

This script builds prompt/response pairs from data/pcos_final.jsonl where
each row is a JSON object of features plus a "pcos" label (0/1).
"""

from __future__ import annotations

import argparse
import json
import logging
import os
from typing import Dict, Iterable

logger = logging.getLogger(__name__)


DEFAULT_SYSTEM_PROMPT = (
    "You are a clinical classification assistant for PCOS.\n"
    "Given patient features, output only \"pcos: 0\" or \"pcos: 1\".\n"
    "Do not add explanations or extra text."
)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Fine-tune a causal LLM with LoRA/QLoRA for PCOS labels"
    )
    p.add_argument(
        "--dataset",
        required=True,
        help="Path to JSONL dataset with features and 'pcos' label",
    )
    p.add_argument(
        "--base_model",
        required=True,
        help="HF model name or local path (e.g. meta-llama/Llama-2-7b-chat-hf)",
    )
    p.add_argument(
        "--output_dir",
        required=True,
        help="Where to save the fine-tuned adapter/model",
    )
    p.add_argument(
        "--system_prompt",
        default=None,
        help="Optional system prompt text file; overrides default",
    )
    p.add_argument("--per_device_train_batch_size", type=int, default=1)
    p.add_argument(
        "--gradient_accumulation_steps",
        type=int,
        default=32,
        help="Gradient accumulation to simulate larger batches on low VRAM",
    )
    p.add_argument("--num_train_epochs", type=int, default=3)
    p.add_argument(
        "--max_seq_length",
        type=int,
        default=512,
        help="Maximum sequence length (reduce to save memory)",
    )
    p.add_argument("--learning_rate", type=float, default=2e-4)
    p.add_argument(
        "--use_4bit",
        action="store_true",
        help="Enable 4-bit loading (requires bitsandbytes)",
    )
    p.add_argument(
        "--train_split",
        type=float,
        default=0.95,
        help="Fraction for training split (rest used for eval)",
    )
    return p.parse_args()


def load_system_prompt(path: str | None) -> str:
    if not path:
        return DEFAULT_SYSTEM_PROMPT
    with open(path, "r", encoding="utf-8") as handle:
        return handle.read().strip()


def build_prompt(system_prompt: str, features: Dict[str, object]) -> str:
    lines = ["Patient features:"]
    for key, value in features.items():
        lines.append(f"- {key}: {value}")
    features_text = "\n".join(lines)
    return f"{system_prompt}\n\n{features_text}\n\nAnswer:".strip()


def iter_records(path: str) -> Iterable[Dict[str, object]]:
    with open(path, "r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            yield json.loads(line)


def main() -> None:
    args = parse_args()

    try:
        import torch
        from datasets import Dataset
        from transformers import (
            AutoTokenizer,
            AutoModelForCausalLM,
            TrainingArguments,
            Trainer,
            BitsAndBytesConfig,
        )
        from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
    except Exception as exc:
        logger.error(
            "Missing training dependencies. Install transformers, datasets, peft, bitsandbytes, accelerate"
        )
        raise exc

    system_prompt = load_system_prompt(args.system_prompt)
    records = list(iter_records(args.dataset))
    if not records:
        raise ValueError("Dataset is empty")

    def to_example(record: Dict[str, object]) -> Dict[str, str]:
        record = dict(record)
        label = record.pop("pcos", None)
        if label is None:
            raise ValueError("Missing 'pcos' label in record")
        prompt = build_prompt(system_prompt, record)
        response = f"pcos: {int(label)}"
        return {"prompt": prompt, "response": response}

    examples = [to_example(r) for r in records]
    dataset = Dataset.from_list(examples)

    if 0.0 < args.train_split < 1.0:
        split = dataset.train_test_split(test_size=1.0 - args.train_split, seed=42)
        train_ds = split["train"]
        eval_ds = split["test"]
    else:
        train_ds = dataset
        eval_ds = None

    tokenizer = AutoTokenizer.from_pretrained(args.base_model, use_fast=False)

    def build_text(example: Dict[str, str]) -> str:
        return (
            example.get("prompt", "")
            + tokenizer.eos_token
            + example.get("response", "")
            + tokenizer.eos_token
        )

    def tokenize_func(example: Dict[str, str]) -> Dict[str, object]:
        text = build_text(example)
        tok = tokenizer(text, truncation=True, max_length=args.max_seq_length)
        tok["labels"] = tok["input_ids"].copy()
        return tok

    tokenized_train = train_ds.map(tokenize_func, remove_columns=train_ds.column_names)
    tokenized_eval = None
    if eval_ds is not None:
        tokenized_eval = eval_ds.map(tokenize_func, remove_columns=eval_ds.column_names)

    if args.use_4bit:
        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_compute_dtype=torch.float16,
            bnb_4bit_use_double_quant=True,
            bnb_4bit_quant_type="nf4",
        )
        model = AutoModelForCausalLM.from_pretrained(
            args.base_model,
            quantization_config=bnb_config,
            device_map="auto",
            trust_remote_code=True,
        )
        model = prepare_model_for_kbit_training(model)
    else:
        model = AutoModelForCausalLM.from_pretrained(
            args.base_model, device_map="auto", trust_remote_code=True
        )

    lora_config = LoraConfig(
        r=8,
        lora_alpha=32,
        target_modules=["q_proj", "v_proj"],
        lora_dropout=0.05,
        bias="none",
        task_type="CAUSAL_LM",
    )

    model = get_peft_model(model, lora_config)
    model.print_trainable_parameters()

    training_args = TrainingArguments(
        args.output_dir,
        per_device_train_batch_size=args.per_device_train_batch_size,
        gradient_accumulation_steps=args.gradient_accumulation_steps,
        num_train_epochs=args.num_train_epochs,
        learning_rate=args.learning_rate,
        fp16=True,
        logging_steps=10,
        save_total_limit=2,
        remove_unused_columns=False,
        optim="paged_adamw_32bit",
        evaluation_strategy="steps" if tokenized_eval is not None else "no",
        eval_steps=50 if tokenized_eval is not None else None,
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_train,
        eval_dataset=tokenized_eval,
        processing_class=tokenizer,
    )

    trainer.train()
    os.makedirs(args.output_dir, exist_ok=True)
    model.save_pretrained(args.output_dir)
    tokenizer.save_pretrained(args.output_dir)


if __name__ == "__main__":
    main()
