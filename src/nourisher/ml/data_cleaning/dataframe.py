import pandas as pd
from pathlib import Path

from nourisher.utils.paths import DATA_DIR

INPUT_FILE = DATA_DIR / "pcos_data_cleaned.jsonl"
OUTPUT_FILE = DATA_DIR / "pcos_final.jsonl"


def load_data(file_path: Path) -> pd.DataFrame:
    df = pd.read_json(file_path, lines=True)
    return df.copy()


def clean_data(df: pd.DataFrame):
    columns_to_drop = [
        "blood_18",
        "blood_17",
        "blood_16",
        "blood_15",
        "blood_14",
        "blood_13",
        "blood_12",
        "blood_11",
    ]
    df = df.drop(columns=columns_to_drop, errors="ignore")

    labels = df["pcos"]
    df = df.drop(columns=["pcos"])

    return df, labels


def save_to_json(df: pd.DataFrame, file_path: Path):
    df.to_json(file_path, orient="records", lines=True)


def main():
    df = load_data(INPUT_FILE)
    df_clean, labels = clean_data(df)

    df_final = df_clean.copy()
    df_final["pcos"] = labels

    save_to_json(df_final, OUTPUT_FILE)

    print(f"Data successfully saved to: {OUTPUT_FILE}")
    print(f"Shape: {df_final.shape}")


if __name__ == "__main__":
    main()
