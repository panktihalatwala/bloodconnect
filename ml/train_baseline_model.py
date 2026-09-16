"""
Step 2 of ML groundwork: train a baseline classification model on the UCI
Blood Transfusion dataset to predict donation likelihood. This model will
later be adapted/retrained using our own project's MatchLog response data
as it accumulates, per the SRS assumption that initial predictions rely
more heavily on this reference dataset until project-specific data grows.
"""
import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, classification_report

RAW_DATA_PATH = "ml/transfusion_raw.csv"
MODEL_OUTPUT_PATH = "ml/donor_response_model.joblib"

FEATURE_COLUMNS = ["Recency (months)", "Frequency (times)", "Monetary (c.c. blood)", "Time (months)"]
TARGET_COLUMN = "whether he/she donated blood in March 2007"


def load_data():
    df = pd.read_csv(RAW_DATA_PATH)
    return df


def prepare_features(df):
    X = df[FEATURE_COLUMNS]
    y = df[TARGET_COLUMN]
    return X, y


def train_and_evaluate(X, y):
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, random_state=42, stratify=y
    )

    models = {
        "Logistic Regression": LogisticRegression(max_iter=1000, class_weight="balanced"),
        "Random Forest": RandomForestClassifier(n_estimators=100, random_state=42, class_weight="balanced"),
    }

    results = {}
    for name, model in models.items():
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)

        results[name] = {
            "model": model,
            "accuracy": accuracy_score(y_test, y_pred),
            "precision": precision_score(y_test, y_pred),
            "recall": recall_score(y_test, y_pred),
            "f1": f1_score(y_test, y_pred),
            "confusion_matrix": confusion_matrix(y_test, y_pred),
            "report": classification_report(y_test, y_pred),
        }

    return results, X_test, y_test


def print_results(results):
    print("=" * 70)
    print("MODEL COMPARISON")
    print("=" * 70)
    for name, r in results.items():
        print(f"\n--- {name} ---")
        print(f"Accuracy:  {r['accuracy']:.4f}")
        print(f"Precision: {r['precision']:.4f}")
        print(f"Recall:    {r['recall']:.4f}")
        print(f"F1 Score:  {r['f1']:.4f}")
        print(f"Confusion Matrix:\n{r['confusion_matrix']}")
        print(f"\nFull Report:\n{r['report']}")


if __name__ == "__main__":
    df = load_data()
    X, y = prepare_features(df)
    results, X_test, y_test = train_and_evaluate(X, y)
    print_results(results)

    # Save the better-performing model (by F1 score, since classes are imbalanced)
    best_name = max(results, key=lambda name: results[name]["f1"])
    best_model = results[best_name]["model"]
    joblib.dump(best_model, MODEL_OUTPUT_PATH)

    print("=" * 70)
    print(f"Best model: {best_name} (F1: {results[best_name]['f1']:.4f})")
    print(f"Saved to: {MODEL_OUTPUT_PATH}")
    print("=" * 70)