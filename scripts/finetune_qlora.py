#!/usr/bin/env python3
"""
Minimal QLoRA/LoRA fine-tuning script for LLaMA-family models.

Notes:
- This script targets low-VRAM setups by using 4-bit quantization (QLoRA) and LoRA adapters.
- It requires: transformers, datasets, accelerate, peft, bitsandbytes, safetensors (recommended)
- Recommended run command (use accelerate):
    accelerate launch --num_processes 1 --num_machines 1 scripts/finetune_qlora.py \
    --base_model <BASE_MODEL> --dataset examples/finetune_example.jsonl --output_dir ml/models/finetuned-llama

The script is conservative with memory but training large LLaMA models may still OOM on 4GB VRAM.
If you run out of memory, reduce batch sizes or use gradient accumulation and smaller sequence lengths.
"""

import argparse
import logging
import os

logger = logging.getLogger(__name__)


def parse_args():
    p = argparse.ArgumentParser(
        description="Fine-tune a causal LLM with LoRA/QLoRA (low-VRAM)"
    )
    p.add_argument(
        "--dataset",
        required=True,
        help="Path to JSONL dataset with fields 'prompt' and 'response'",
    )

    p.add_argument(
        "--base_model",
        required=True,
        help="HF model name or local path (e.g. meta-llama/Llama-2-7b-chat-hf)",
    )
    p.add_argument(
        "--output_dir", required=True, help="Where to save the fine-tuned adapter/model"
    )
    p.add_argument("--per_device_train_batch_size", type=int, default=1)
    p.add_argument(
        "--gradient_accumulation_steps",
        type=int,
        default=32,
        help="Gradient accumulation to simulate larger batches on low VRAM",
    )
    p.add_argument("--num_train_epochs", type=int, default=1)
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
    return p.parse_args()


def main():
    args = parse_args()

    # local imports
    try:
        import torch
        from datasets import load_dataset
        from transformers import (
            AutoTokenizer,
            AutoModelForCausalLM,
            TrainingArguments,
            Trainer,
            BitsAndBytesConfig,
        )
        from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
    except Exception as e:
        logger.error(
            "Missing training dependencies. Install transformers, datasets, peft, bitsandbytes, accelerate"
        )
        raise e

    # Load dataset
    ds = load_dataset("json", data_files=args.dataset)
    # dataset may return a dict or Dataset
    if isinstance(ds, dict):
        ds = ds[list(ds.keys())[0]]

    tokenizer = AutoTokenizer.from_pretrained(args.base_model, use_fast=False)

    def build_text(example):
        # simple formatting: prompt + tokenizer.eos + response
        prompt = example.get("prompt", "")
        response = example.get("response", "")
        return prompt + tokenizer.eos_token + response + tokenizer.eos_token

    def tokenize_func(example):
        text = build_text(example)
        tok = tokenizer(text, truncation=True, max_length=args.max_seq_length)
        tok["labels"] = tok["input_ids"].copy()
        return tok

    tokenized = ds.map(tokenize_func, remove_columns=ds.column_names)

    # Configure model loading
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
        # prepare for k-bit training
        model = prepare_model_for_kbit_training(model)
    else:
        model = AutoModelForCausalLM.from_pretrained(
            args.base_model, device_map="auto", trust_remote_code=True
        )

    # LoRA config — conservative defaults for low VRAM
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

    # TrainingArguments
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
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized,
        processing_class=tokenizer,
    )

    trainer.train()
    # save adapter / model
    os.makedirs(args.output_dir, exist_ok=True)
    model.save_pretrained(args.output_dir)
    tokenizer.save_pretrained(args.output_dir)


if __name__ == "__main__":
    main()
