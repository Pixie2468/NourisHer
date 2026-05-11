This directory is the designated location for the fine-tuned model adapters.
Once training using `scripts/finetune_qlora.py` is completed with `--output_dir ml/models/finetuned-llama`, the adapter configuration and weights will be saved here.
The API will load the model from this directory based on the `MODEL_PATH` setting in the `.env` file.