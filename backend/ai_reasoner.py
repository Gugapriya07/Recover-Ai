def generate_recovery_explanation(
    transaction_id,
    amount,
    failure_reason,
    payment_method,
    recovery_probability,
    expected_recovery_value,
    recommended_action,
    customer_success_rate,
    previous_successes
):
    explanation_parts = []

    # Failure analysis
    if failure_reason == "INSUFFICIENT_FUNDS":
        failure_analysis = (
            "The payment failed because the available customer funds "
            "were insufficient."
        )

    elif failure_reason == "UPI_TIMEOUT":
        failure_analysis = (
            "The payment appears to have encountered a temporary "
            "UPI timeout."
        )

    elif failure_reason == "CARD_EXPIRED":
        failure_analysis = (
            "The payment failed because the card has expired, "
            "so repeatedly retrying the same card is unlikely to help."
        )

    elif failure_reason == "AUTHENTICATION_FAILED":
        failure_analysis = (
            "The payment failed during the authentication stage."
        )

    elif failure_reason == "BANK_DECLINED":
        failure_analysis = (
            "The customer's bank declined the payment."
        )

    else:
        failure_analysis = (
            "The payment failed due to an unidentified failure reason."
        )

    explanation_parts.append(failure_analysis)

    # Customer behavior
    if customer_success_rate >= 70:
        customer_analysis = (
            f"The customer has a relatively strong payment history, "
            f"with a success rate of {customer_success_rate:.1f}% "
            f"and {previous_successes} previous successful payments."
        )
    elif customer_success_rate >= 40:
        customer_analysis = (
            f"The customer's payment history is mixed, with a "
            f"success rate of {customer_success_rate:.1f}%."
        )
    else:
        customer_analysis = (
            f"The customer's historical payment success rate is "
            f"relatively low at {customer_success_rate:.1f}%."
        )

    explanation_parts.append(customer_analysis)

    # Recovery probability
    probability_analysis = (
        f"RecoverAI estimates a recovery probability of "
        f"{recovery_probability:.1f}%."
    )

    explanation_parts.append(probability_analysis)

    # Economic value
    value_analysis = (
        f"The estimated expected recovery value is "
        f"₹{expected_recovery_value:.2f} for a payment of "
        f"₹{amount:.2f}."
    )

    explanation_parts.append(value_analysis)

    # Final recommendation
    recommendation = (
        f"Based on these signals, RecoverAI recommends "
        f"{recommended_action}."
    )

    explanation_parts.append(recommendation)

    explanation = " ".join(explanation_parts)

    return {
        "transaction_id": transaction_id,
        "reasoning": explanation,
        "confidence": round(recovery_probability, 2),
        "recommended_action": recommended_action
    }