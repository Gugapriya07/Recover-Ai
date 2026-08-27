import os
import joblib
import pandas as pd


# ============================================================
# LOAD TRAINED MODEL
# ============================================================

MODEL_PATH = os.path.join(
    os.path.dirname(__file__),
    "models",
    "recovery_probability_model.pkl"
)


model = joblib.load(MODEL_PATH)


# ============================================================
# PREDICT RECOVERY PROBABILITY
# ============================================================

def predict_recovery_probability(
    amount,
    customer_success_rate,
    failure_reason,
    payment_method,
    previous_successes=0
):
    """
    Predict the probability that a failed payment
    can be successfully recovered.

    Returns probability between 0 and 100.
    """

    try:

        # ----------------------------------------------------
        # Prepare input exactly like training data
        # ----------------------------------------------------

        input_data = pd.DataFrame([
            {
                "amount": float(amount),

                "payment_method":
                    payment_method or "UNKNOWN",

                "failure_reason":
                    failure_reason or "UNKNOWN",

                "customer_success_rate":
                    float(customer_success_rate),

                "previous_successes":
                    int(previous_successes or 0)
            }
        ])


        # ----------------------------------------------------
        # Predict probability
        # ----------------------------------------------------

        probability = model.predict_proba(
            input_data
        )[0][1]


        # Convert 0-1 → 0-100
        probability = round(
            probability * 100,
            2
        )


        # Keep within valid range
        probability = max(
            0,
            min(100, probability)
        )


        return probability


    except Exception as e:

        print(
            f"ML prediction error: {e}"
        )

        return 0.0