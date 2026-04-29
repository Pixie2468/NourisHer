import pandas as pd
from utils.paths import DATA_DIR

df = pd.read_json(DATA_DIR / "pcos_without_infertility.jsonl", lines=True)


if __name__ == "__main__":
    print(df.describe())
