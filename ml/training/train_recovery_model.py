import os
import pandas as pd
import joblib

from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score
)


# ============================================================
# 1. HISTORICAL RECOVERY DATA
# ============================================================

data = [

    # ========================================================
    # UPI TIMEOUT
    # ========================================================

    [500,   "UPI", "UPI_TIMEOUT", 95, 9, 1],
    [800,   "UPI", "UPI_TIMEOUT", 90, 7, 1],
    [1100,  "UPI", "UPI_TIMEOUT", 85, 6, 1],
    [1500,  "UPI", "UPI_TIMEOUT", 80, 4, 1],
    [1800,  "UPI", "UPI_TIMEOUT", 75, 3, 1],
    [2000,  "UPI", "UPI_TIMEOUT", 70, 3, 1],
    [2500,  "UPI", "UPI_TIMEOUT", 65, 3, 1],
    [3000,  "UPI", "UPI_TIMEOUT", 60, 2, 1],
    [3500,  "UPI", "UPI_TIMEOUT", 55, 2, 1],
    [4000,  "UPI", "UPI_TIMEOUT", 50, 1, 1],
    [5000,  "UPI", "UPI_TIMEOUT", 40, 1, 0],
    [6000,  "UPI", "UPI_TIMEOUT", 30, 0, 0],

    # ========================================================
    # INSUFFICIENT FUNDS
    # ========================================================

    [600,   "UPI", "INSUFFICIENT_FUNDS", 95, 8, 1],
    [900,   "UPI", "INSUFFICIENT_FUNDS", 90, 7, 1],
    [1200,  "UPI", "INSUFFICIENT_FUNDS", 80, 4, 1],
    [1300,  "UPI", "INSUFFICIENT_FUNDS", 70, 3, 1],
    [1700,  "UPI", "INSUFFICIENT_FUNDS", 85, 5, 1],
    [2200,  "UPI", "INSUFFICIENT_FUNDS", 45, 1, 0],
    [2500,  "UPI", "INSUFFICIENT_FUNDS", 50, 1, 1],
    [3500,  "UPI", "INSUFFICIENT_FUNDS", 40, 1, 0],
    [5000,  "UPI", "INSUFFICIENT_FUNDS", 30, 0, 0],

    # ========================================================
    # CARD EXPIRED
    # ========================================================

    [1500,  "CREDIT_CARD", "CARD_EXPIRED", 70, 3, 1],
    [3000,  "CREDIT_CARD", "CARD_EXPIRED", 65, 3, 1],
    [5000,  "CREDIT_CARD", "CARD_EXPIRED", 60, 2, 1],
    [5500,  "CREDIT_CARD", "CARD_EXPIRED", 50, 1, 0],
    [7000,  "CREDIT_CARD", "CARD_EXPIRED", 40, 1, 0],
    [10000, "CREDIT_CARD", "CARD_EXPIRED", 20, 0, 0],
    [15000, "CREDIT_CARD", "CARD_EXPIRED", 15, 0, 0],

    # ========================================================
    # BANK DECLINED
    # ========================================================

    [3000,  "DEBIT_CARD", "BANK_DECLINED", 70, 4, 1],
    [4000,  "DEBIT_CARD", "BANK_DECLINED", 60, 3, 1],
    [4500,  "DEBIT_CARD", "BANK_DECLINED", 40, 1, 0],
    [6500,  "DEBIT_CARD", "BANK_DECLINED", 35, 1, 0],
    [7000,  "DEBIT_CARD", "BANK_DECLINED", 30, 1, 0],
    [12000, "DEBIT_CARD", "BANK_DECLINED", 25, 0, 0],

    # ========================================================
    # AUTHENTICATION FAILED
    # ========================================================

    [2000, "CREDIT_CARD", "AUTHENTICATION_FAILED", 85, 5, 1],
    [3200, "CREDIT_CARD", "AUTHENTICATION_FAILED", 65, 3, 1],
    [3500, "CREDIT_CARD", "AUTHENTICATION_FAILED", 60, 3, 1],
    [5000, "CREDIT_CARD", "AUTHENTICATION_FAILED", 50, 2, 0],
    [7500, "CREDIT_CARD", "AUTHENTICATION_FAILED", 25, 0, 0],
    [8000, "CREDIT_CARD", "AUTHENTICATION_FAILED", 30, 1, 0],

    # ========================================================
    # HIGH-VALUE TRANSACTIONS
    # A strong customer track record (high success rate,
    # multiple previous successes) can still recover a
    # high-value payment. Without these examples, the model
    # only ever saw "large amount" co-occurring with "poor
    # customer history", so it learned to treat amount alone
    # as a near-automatic disqualifier. These rows let the
    # model separate the two signals, so high-value + strong
    # history transactions can correctly reach the policy
    # engine's autonomous-amount-ceiling check and ESCALATE,
    # instead of being stopped early on probability alone.
    # ========================================================

    [12000, "UPI",          "UPI_TIMEOUT",          85, 6, 1],
    [15000, "UPI",          "UPI_TIMEOUT",          80, 5, 1],
    [18000, "UPI",          "UPI_TIMEOUT",          75, 4, 1],
    [22000, "UPI",          "UPI_TIMEOUT",           70, 4, 1],
    [25000, "UPI",          "UPI_TIMEOUT",           65, 3, 1],
    [30000, "UPI",          "UPI_TIMEOUT",           60, 2, 0],

    [14000, "CREDIT_CARD",  "AUTHENTICATION_FAILED", 80, 5, 1],
    [18000, "CREDIT_CARD",  "AUTHENTICATION_FAILED", 70, 3, 1],
    [24000, "CREDIT_CARD",  "AUTHENTICATION_FAILED", 55, 2, 0],

    [13000, "DEBIT_CARD",   "BANK_DECLINED",         75, 4, 1],
    [20000, "DEBIT_CARD",   "BANK_DECLINED",         55, 2, 0],

    [16000, "UPI",          "INSUFFICIENT_FUNDS",    80, 5, 1],
    [21000, "UPI",          "INSUFFICIENT_FUNDS",    50, 1, 0],
]


columns = [
    "amount",
    "payment_method",
    "failure_reason",
    "customer_success_rate",
    "previous_successes",
    "recovered"
]

df = pd.DataFrame(data, columns=columns)


# ============================================================
# 2. FEATURES / TARGET
# ============================================================

X = df.drop("recovered", axis=1)
y = df["recovered"]


# ============================================================
# 3. PREPROCESSING
# ============================================================

categorical_features = [
    "payment_method",
    "failure_reason"
]

numeric_features = [
    "amount",
    "customer_success_rate",
    "previous_successes"
]


preprocessor = ColumnTransformer(
    transformers=[
        (
            "categorical",
            OneHotEncoder(
                handle_unknown="ignore"
            ),
            categorical_features
        ),

        (
            "numeric",
            StandardScaler(),
            numeric_features
        )
    ]
)


# ============================================================
# 4. ML MODEL
# ============================================================

model = Pipeline(
    steps=[
        (
            "preprocessor",
            preprocessor
        ),

        (
            "classifier",
            LogisticRegression(
                max_iter=2000,
                C=1.5
            )
        )
    ]
)


# ============================================================
# 5. HONEST VALIDATION
# (train/test split, evaluated before the final production fit)
# ============================================================

X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.25,
    random_state=42,
    stratify=y
)

eval_model = Pipeline(
    steps=[
        ("preprocessor", preprocessor),
        ("classifier", LogisticRegression(max_iter=2000, C=1.5))
    ]
)

eval_model.fit(X_train, y_train)
y_pred = eval_model.predict(X_test)

print("=== Held-out test set metrics ===")
print(f"Test set size : {len(y_test)} rows")
print(f"Accuracy      : {accuracy_score(y_test, y_pred):.2f}")
print(f"Precision     : {precision_score(y_test, y_pred, zero_division=0):.2f}")
print(f"Recall        : {recall_score(y_test, y_pred, zero_division=0):.2f}")
print(f"F1 score      : {f1_score(y_test, y_pred, zero_division=0):.2f}")
print(
    "Note: dataset is small and hand-authored, so these numbers "
    "are indicative, not a rigorous benchmark."
)


# ============================================================
# 6. TRAIN FINAL MODEL ON FULL DATASET
# (small dataset, so we use all of it for the production model
# after validating generalization above)
# ============================================================

model.fit(X, y)


# ============================================================
# 7. SAVE MODEL
# ============================================================

model_directory = os.path.join(
    os.path.dirname(__file__),
    "..",
    "models"
)

os.makedirs(
    model_directory,
    exist_ok=True
)


model_path = os.path.join(
    model_directory,
    "recovery_probability_model.pkl"
)


joblib.dump(
    model,
    model_path
)


print("Recovery probability model trained successfully.")
print(f"Training records: {len(df)}")
print(f"Model saved to: {model_path}")