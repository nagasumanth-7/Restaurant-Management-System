from decimal import Decimal
from django.core.exceptions import ValidationError
from django.db.models import Sum, Count
from django.utils import timezone
from ..models import Bill, Payment, TableSession, RestaurantTable


GST_RATE = Decimal("0.05")  # 5% Restaurant GST (2.5% CGST + 2.5% SGST)


def calculate_and_generate_bill(session, cashier=None, discount_pct=Decimal("0.00"), tip_amount=Decimal("0.00")):
    """
    Computes subtotal from all session orders, applies 5% GST, calculates discounts,
    adds tip, and generates/updates an active Bill.
    """
    if session.status != "ACTIVE" and session.status != "COMPLETED":
        raise ValidationError(f"Cannot generate bill for session with status {session.status}.")

    subtotal = session.running_subtotal
    if subtotal <= Decimal("0.00"):
        raise ValidationError("Cannot generate a bill with 0 total. No served items found.")

    discount_amount = (subtotal * (Decimal(str(discount_pct)) / Decimal("100.00"))).quantize(Decimal("0.01"))
    taxable_amount = max(Decimal("0.00"), subtotal - discount_amount)
    tax_amount = (taxable_amount * GST_RATE).quantize(Decimal("0.01"))
    tip_dec = Decimal(str(tip_amount)).quantize(Decimal("0.01"))
    total_amount = (taxable_amount + tax_amount + tip_dec).quantize(Decimal("0.01"))

    bill, created = Bill.objects.get_or_create(
        session=session,
        defaults={
            "subtotal": subtotal,
            "tax": tax_amount,
            "discount": discount_amount,
            "tip": tip_dec,
            "total": total_amount,
            "status": "UNPAID",
            "cashier": cashier,
        },
    )

    if not created:
        bill.subtotal = subtotal
        bill.tax = tax_amount
        bill.discount = discount_amount
        bill.tip = tip_dec
        bill.total = total_amount
        if cashier and not bill.cashier:
            bill.cashier = cashier
        bill.save()

    # Update table status to BILL_PENDING if not already
    table = session.table
    if table.status != "BILL_PENDING":
        table.status = "BILL_PENDING"
        table.save()

    return bill


def process_bill_payment(bill, payment_method, amount_paid, transaction_id="", processed_by=None):
    """
    Processes payment for a bill, creates Payment record, marks bill PAID,
    completes the TableSession, and frees the table back to AVAILABLE.
    """
    if bill.status == "PAID":
        raise ValidationError("This bill has already been paid in full.")

    amount_dec = Decimal(str(amount_paid))
    if amount_dec < bill.total:
        raise ValidationError(f"Amount paid (₹{amount_dec}) is less than total bill amount (₹{bill.total}).")

    payment = Payment.objects.create(
        bill=bill,
        amount=amount_dec,
        payment_method=payment_method,
        status="SUCCESS",
        transaction_id=transaction_id.strip(),
        processed_by=processed_by,
    )

    bill.status = "PAID"
    bill.paid_at = timezone.now()
    if processed_by and not bill.cashier:
        bill.cashier = processed_by
    bill.save()

    # Complete the session
    session = bill.session
    session.status = "COMPLETED"
    session.closed_at = timezone.now()
    session.save()

    # Free the table
    table = session.table
    table.status = "AVAILABLE"
    table.save()

    return payment


def get_unpaid_bills():
    """Retrieves all unpaid bills for the cashier dashboard."""
    return (
        Bill.objects.filter(status="UNPAID")
        .select_related("session__table", "session__waiter", "cashier")
        .order_by("-created_at")
    )


def get_daily_cashier_summary(target_date=None):
    """
    Aggregates financial statistics for a given day (defaults to today):
    total revenue, paid bills count, breakdown by payment method.
    """
    if target_date is None:
        target_date = timezone.localdate()

    payments_today = Payment.objects.filter(
        status="SUCCESS",
        created_at__date=target_date,
    )

    total_revenue = payments_today.aggregate(total=Sum("amount"))["total"] or Decimal("0.00")
    total_transactions = payments_today.count()

    # Method breakdowns
    cash_total = payments_today.filter(payment_method="CASH").aggregate(total=Sum("amount"))["total"] or Decimal("0.00")
    upi_total = payments_today.filter(payment_method="UPI").aggregate(total=Sum("amount"))["total"] or Decimal("0.00")
    card_total = payments_today.filter(payment_method="CARD").aggregate(total=Sum("amount"))["total"] or Decimal("0.00")

    return {
        "date": target_date,
        "total_revenue": total_revenue,
        "total_transactions": total_transactions,
        "cash_total": cash_total,
        "upi_total": upi_total,
        "card_total": card_total,
        "payments": payments_today.select_related("bill__session__table", "processed_by").order_by("-created_at")[:20],
    }
