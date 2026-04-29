# NourisHer: Step-by-Step Model Training Guide

This guide provides a detailed, step-by-step walkthrough on how to fine-tune a language model for the NourisHer project using QLoRA.

## Step 1: Environment Setup

Ensure you have the required dependencies installed. You will need a GPU (preferably with at least 16GB+ VRAM, though 4-bit quantization helps fit 7B models on smaller GPUs).

```bash
# Install the required Python packages
pip install torch transformers datasets accelerate peft bitsandbytes safetensors
```

## Step 2: Prepare the Dataset

The training script expects a `.jsonl` (JSON Lines) file where each line is a JSON object containing a `prompt` and a `response`.

Create a file named `data/dataset.jsonl` (you may need to create the `data/` directory).

Example `data/dataset.jsonl` format:

```json
{"prompt": "What are some good breakfast options for someone with PCOS?", "response": "A balanced PCOS-friendly breakfast should focus on high protein, healthy fats, and complex carbs to avoid blood sugar spikes. Consider a spinach and mushroom omelet, Greek yogurt with chia seeds and berries, or avocado toast on whole grain bread with eggs."}
{"prompt": "How does sugar affect hormonal acne?", "response": "High sugar intake can spike insulin levels, which in turn can increase androgen production and sebum (oil) synthesis in the skin, often worsening hormonal acne. Focusing on low-glycemic foods can help manage these breakouts."}
```

## Step 3: Run the Training Script

We use Hugging Face `accelerate` to manage the device placement. The `scripts/finetune_qlora.py` script will load the base model in 4-bit, attach LoRA adapters, and train them.

Run the following command from the root of the project:

```bash
accelerate launch --num_processes 1 --num_machines 1 scripts/finetune_qlora.py \
    --base_model meta-llama/Llama-2-7b-chat-hf \
    --dataset data/dataset.jsonl \
    --output_dir ml/models/finetuned-llama \
    --use_4bit \
    --per_device_train_batch_size 1 \
    --gradient_accumulation_steps 16 \
    --num_train_epochs 3 \
    --learning_rate 2e-4
```
*(Note: Replace `meta-llama/Llama-2-7b-chat-hf` with your chosen base model. If you use LLaMA, ensure you have requested access and logged in via `huggingface-cli login`)*

### Parameter Breakdown:
- `--use_4bit`: Shrinks the model footprint so it fits in lower VRAM.
- `--per_device_train_batch_size`: Kept at 1 to save memory.
- `--gradient_accumulation_steps`: Simulates a larger batch size (1 * 16 = 16) by accumulating gradients before updating weights.
- `--output_dir`: Where the final fine-tuned adapter weights will be saved.

## Step 4: Verify the Output

Once the training completes, check the output directory:

```bash
ls -la ml/models/finetuned-llama
```

You should see files like `adapter_config.json`, `adapter_model.safetensors`, and tokenizer files. Because we used LoRA, this directory will be relatively small (typically < 100MB) compared to the base model.

## Step 5: Configure the API to use the Model

Now, configure your `.env` file to point to this newly trained adapter.

1. Copy the example env file if you haven't already: `cp .env.example .env`
2. Ensure the following variables are set in `.env`:
   ```env
   MODEL_PATH=ml/models/finetuned-llama
   LOAD_IN_4BIT=true
   SYSTEM_PROMPT_PATH=configs/system_prompt.txt
   ```
   *(Because Hugging Face's `AutoModel` natively supports PEFT, passing the adapter directory to `MODEL_PATH` will automatically load the base model and apply your newly trained weights).*

## Step 6: Start the API
Start your FastAPI server to test the model:
```bash
uvicorn src.nourisher.main:app --reload
```

You can now send requests to your endpoints (e.g., `POST /stream/sse`) and the model will respond utilizing your new fine-tuned weights and the detailed NourisHer system prompt!