"""A small billing service. The thing the agent is asked about."""
import os

STRIPE_API_BASE = "https://api.stripe.com/v1"


def charge(customer_id: str, amount_cents: int) -> dict:
    """Charge a customer. Retries are handled by the caller."""
    if amount_cents <= 0:
        raise ValueError("amount must be positive")
    return {"customer": customer_id, "amount": amount_cents, "status": "succeeded"}


def refund(charge_id: str) -> dict:
    return {"charge": charge_id, "status": "refunded"}
