# payments/citypay.py
import requests
from django.conf import settings

def charge_citypay_token(token: str, amount_gbp: float, reference: str):
    """
    Minimal example; adapt to CityPay's exact API schema.
    """
    r = requests.post(
        f"{settings.CITYPAY_BASE_URL}/charge",  # replace with real endpoint
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {settings.CITYPAY_LICENCE}",
        },
        json={
            "merchantId": settings.CITYPAY_MERCHANT_ID,
            "token": token,
            "amount": float(amount_gbp),
            "currency": "GBP",
            "reference": reference,
            "description": "Monthly platform subscription",
        },
        timeout=20,
    )
    r.raise_for_status()
    return r.json()
