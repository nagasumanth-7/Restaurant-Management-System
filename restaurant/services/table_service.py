from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from django.utils import timezone
from ..models import RestaurantTable, TableSession, Reservation


def get_all_tables(status_filter=None, area_filter=None):
    """Returns active restaurant tables, optionally filtered by status or floor area."""
    qs = RestaurantTable.objects.filter(is_active=True)
    if status_filter and status_filter != "ALL":
        qs = qs.filter(status=status_filter)
    if area_filter and area_filter != "ALL":
        qs = qs.filter(floor_area=area_filter)
    return qs.order_by("table_number")


def get_table_by_id(table_id):
    """Retrieves a single RestaurantTable by ID or raises 404."""
    return get_object_or_404(RestaurantTable, pk=table_id, is_active=True)


def get_active_session_for_table(table_id):
    """Returns the currently active TableSession for a table, if one exists."""
    return TableSession.objects.filter(table_id=table_id, status="ACTIVE").first()


def open_table_session(table, guest_name, guest_count, waiter_user=None, reservation=None):
    """
    Opens a new dining session for a table.
    Sets table status to OCCUPIED and creates TableSession.
    """
    if table.status not in ["AVAILABLE", "RESERVED"]:
        raise ValidationError(f"Table {table.table_number} is currently {table.status} and cannot be seated.")

    # Check if there is already an active session
    existing_session = get_active_session_for_table(table.id)
    if existing_session:
        return existing_session

    session = TableSession.objects.create(
        table=table,
        guest_name=guest_name.strip() or f"Walk-in Guest ({table.table_number})",
        guest_count=int(guest_count) if guest_count else 1,
        waiter=waiter_user,
        reservation=reservation,
        status="ACTIVE",
    )

    table.status = "OCCUPIED"
    table.save()

    return session


def close_table_session(session):
    """Closes an active TableSession and frees the table."""
    session.status = "COMPLETED"
    session.closed_at = timezone.now()
    session.save()

    table = session.table
    table.status = "AVAILABLE"
    table.save()


def set_table_bill_pending(table_id):
    """Marks a table status as BILL_PENDING when guests request their check."""
    table = get_table_by_id(table_id)
    table.status = "BILL_PENDING"
    table.save()
    return table
