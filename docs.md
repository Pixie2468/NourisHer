# Training and using a Fine-Tuned Model with QLoRA

This document outlines how to use the provided training script `scripts/finetune_qlora.py` to fine-tune a model and how the API consumes the resulting fine-tuned model.

## 1. Fine-tuning using `finetune_qlora.py`

The script `scripts/finetune_qlora.py` provides a minimal approach to fine-tuning large causal language models like LLaMA using QLoRA. This approach combines 4-bit quantization (to reduce base model memory footprint) with Low-Rank Adaptation (LoRA) (to only train a small number of extra parameters), making it feasible to train models on low-VRAM GPUs.

### Steps and Script Details:

1. **Prerequisites and Imports**:
   - The script requires HuggingFace libraries such as `transformers`, `datasets`, `peft`, and `bitsandbytes`.
   - Run the script via `accelerate launch` to manage device placement seamlessly:
     ```bash
     accelerate launch --num_processes 1 --num_machines 1 scripts/finetune_qlora.py \
         --base_model <BASE_MODEL> \
         --dataset <DATASET.jsonl> \
         --output_dir <OUTPUT_DIR> \
         --use_4bit
     ```

2. **Loading and Tokenizing the Dataset**:
   - Uses `--dataset` parameter to specify a `.jsonl` file. The expected fields are `prompt` and `response`.
   - The script formats each example into `prompt + EOS + response + EOS` and tokenizes it using the tokenizer loaded from the `--base_model`.
   - `--max_seq_length` limits the length of tokens to save memory.

3. **Loading the Model (Quantization)**:
   - When `--use_4bit` is set, `BitsAndBytesConfig` is created to load the model in 4-bit precision (NF4 type) and uses double quantization for extra memory savings.
   - `prepare_model_for_kbit_training(model)` enables gradient checkpointing and casts layer norms into float32 to ensure stable training for the adapters.

4. **Applying LoRA Adapters**:
   - A `LoraConfig` is defined with specific rank `r=8` and `alpha=32`, targeting the query and value projection layers (`q_proj` and `v_proj`).
   - `get_peft_model(model, lora_config)` wraps the quantized base model with these trainable adapters.

5. **Training Arguments & Loop**:
   - `TrainingArguments` dictates the batch size, gradient accumulation (defaulting to 32 to simulate larger batches on small GPUs), learning rate, and optimizer (`paged_adamw_32bit` to further save memory by paging optimizer states to CPU RAM if needed).
   - `Trainer` is instantiated and `trainer.train()` executes the training loop.

6. **Saving the Output**:
   - The trained LoRA adapters and the tokenizer are saved to the path specified by `--output_dir`. (Note: It only saves the small adapter weights, not the full base model).

## 2. Usage in the API

Once you have trained the model, you can serve it via the API. The API is designed to load either full models or Peft adapters natively if the `--output_dir` from the training step is used as the `MODEL_PATH`.

### Accessing the model from the API:

1. **Configuration (`src/nourisher/api/config.py`)**:
   - Set the `MODEL_PATH` environment variable to the directory containing your fine-tuned model (the same path used for `--output_dir` during training).
   - Ensure `LOAD_IN_4BIT=True` is set in your environment if you want the API to run the model via quantization, similar to how it was trained.
   - `SYSTEM_PROMPT_PATH` can optionally point to a text file for prepending custom system prompts.

2. **Model Loading (`src/nourisher/api/ml_model.py`)**:
   - The API lazily loads the model upon the first inference request via `load_model(model_path)`.
   - It utilizes `AutoModelForCausalLM.from_pretrained()` and `AutoTokenizer.from_pretrained()`. Since HuggingFace Transformers automatically recognizes PEFT adapters saved in `MODEL_PATH`, it will load the base model and apply the adapter weights onto it implicitly.
   - If `LOAD_IN_4BIT` is enabled, it uses `bitsandbytes` to load the base model in 4-bit precision before applying the adapter.

3. **Inference Endpoints (`src/nourisher/api/routes/stream.py`)**:
   - **`/stream`**: Accepts `application/x-ndjson` content. Parses prompt payloads, uses the `generate()` function in `ml_model.py` to get predictions, and flushes inputs/outputs directly to the PostgreSQL database in batches.
   - **`/stream/sse`**: Accepts a standard JSON payload and utilizes `stream_generate()`. It wraps the generation call in a background thread with a `TextIteratorStreamer` to yield Server-Sent Events (SSE) tokens back to the client in real-time.

By bridging `finetune_qlora.py` and `src/nourisher/api/ml_model.py`, the system provides an end-to-end pipeline from parameter-efficient fine-tuning on low-end hardware to streaming asynchronous inference within a FastAPI backend.