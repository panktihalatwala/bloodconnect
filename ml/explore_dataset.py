"""
Step 1 of ML groundwork: download the UCI Blood Transfusion Service Center
dataset and do an initial exploration to understand its structure before
mapping it onto our own Donor/MatchLog schema.
"""
import pandas as pd

DATASET_URL = "https://archive.ics.uci.edu/ml/machine-learning-databases/blood-transfusion/transfusion.data"

def load_dataset():
    df = pd.read_csv(DATASET_URL)
    return df

if __name__ == "__main__":
    df = load_dataset()

    print("=" * 60)
    print("DATASET SHAPE:", df.shape)
    print("=" * 60)

    print("\nCOLUMN NAMES:")
    print(df.columns.tolist())

    print("\nFIRST 5 ROWS:")
    print(df.head())

    print("\nDATA TYPES:")
    print(df.dtypes)

    print("\nSUMMARY STATISTICS:")
    print(df.describe())

    print("\nTARGET CLASS BALANCE:")
    print(df.iloc[:, -1].value_counts())

    # Save a local copy so we don't need internet every time we work with it
    df.to_csv("ml/transfusion_raw.csv", index=False)
    print("\nSaved local copy to ml/transfusion_raw.csv")