from dataclasses import dataclass
from uuid import uuid4


@dataclass(frozen=True)
class MockInvoice:
    invoice: str
    payment_hash: str
    amount: int
    paid: bool = False


_MOCK_PAYMENTS: dict[str, MockInvoice] = {}


def create_mock_invoice(amount_sats: int, description: str) -> MockInvoice:
    payment_hash = f"mock_hash_{uuid4().hex}"
    invoice = f"lnmock_{uuid4().hex}"

    payment = MockInvoice(
        invoice=invoice,
        payment_hash=payment_hash,
        amount=amount_sats * 1000,
        paid=False,
    )

    _MOCK_PAYMENTS[payment_hash] = payment

    return payment


def check_mock_payment(payment_hash: str) -> MockInvoice:
    payment = _MOCK_PAYMENTS.get(payment_hash)

    if payment is None:
        raise RuntimeError("Mock payment not found.")

    return payment


def mark_mock_payment_paid(payment_hash: str) -> MockInvoice:
    payment = _MOCK_PAYMENTS.get(payment_hash)

    if payment is None:
        raise RuntimeError("Mock payment not found.")

    paid_payment = MockInvoice(
        invoice=payment.invoice,
        payment_hash=payment.payment_hash,
        amount=payment.amount,
        paid=True,
    )

    _MOCK_PAYMENTS[payment_hash] = paid_payment

    return paid_payment