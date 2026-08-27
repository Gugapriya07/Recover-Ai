import os
import joblib
import pandas as pd


MODEL_PATH = os.path.join(
    os.path.dirname(__file__),
    "..",
    "ml",
    "models",
    "recovery_probability_model.pkl"
)

model = joblib.load(MODEL_PATH)


def predict_recovery_probability(
    amount,
    payment_method,
    failure_reason,
    customer_success_rate,
    previous_successes
):
    data = pd.DataFrame([
        {
            "amount": amount,
            "payment_method": payment_method,
            "failure_reason": failure_reason,
            "customer_success_rate": customer_success_rate,
            "previous_successes": previous_successes
        }
    ])

    probability = model.predict_proba(data)[0][1]

    return round(float(probability) * 100, 2)