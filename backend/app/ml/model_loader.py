from pathlib import Path

import joblib


# ============================================================
# MODEL DIRECTORY
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
MODEL_DIR = BASE_DIR / "models"


# ============================================================
# RANDOM FOREST MODEL PATH
# ============================================================

MODEL_PATH = MODEL_DIR / "random_forest.joblib"


# ============================================================
# LOAD RANDOM FOREST
# ============================================================

def load_random_forest():
    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"Random Forest model not found at:\n{MODEL_PATH}"
        )

    print(
        f"Loading Random Forest model from:\n{MODEL_PATH}"
    )

    model = joblib.load(MODEL_PATH)

    print("Random Forest model loaded successfully.")

    return model