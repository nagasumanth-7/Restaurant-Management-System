from decimal import Decimal
from django.core.exceptions import ValidationError
from django.utils import timezone
from ..models import MenuItem, Order, OrderItem
from .menu_service import validate_menu_item_availability


def validate_order_item_selection(menu_item_id, quantity=1):
    """
    Verifies that a menu item exists, is active, and is available for ordering.
    """
    try:
        item = MenuItem.objects.get(pk=menu_item_id)
    except MenuItem.DoesNotExist:
        raise ValidationError(f"Menu item with ID {menu_item_id} does not exist.")

    is_valid, error_msg = validate_menu_item_availability(item)
    if not is_valid:
        raise ValidationError(error_msg)

    if quantity <= 0:
        raise ValidationError("Quantity must be at least 1.")

    return item


def validate_cart_items(cart_items):
    """
    Validates a collection of cart items: [{'item_id': ..., 'quantity': ...}, ...]
    Returns: (is_valid: bool, errors: list[str])
    """
    errors = []
    for entry in cart_items:
        item_id = entry.get("item_id")
        try:
            item = MenuItem.objects.get(pk=item_id)
            is_valid, msg = validate_menu_item_availability(item)
            if not is_valid:
                errors.append(msg)
        except MenuItem.DoesNotExist:
            errors.append(f"Item #{item_id} does not exist.")

    return (len(errors) == 0, errors)


def create_order_for_session(session, items_data, placed_by=None, source="WAITER", instructions=""):
    """
    Creates an Order and associated OrderItem records for a table session.
    items_data format: [{'item_id': 1, 'quantity': 2, 'notes': 'Extra spicy'}, ...]
    """
    if not items_data:
        raise ValidationError("Cannot place an empty order. Select at least one item.")

    if session.status != "ACTIVE":
        raise ValidationError("Cannot place orders for an inactive session.")

    # 1. Validate all items before persisting any database changes
    validated_items = []
    for entry in items_data:
        item_id = entry.get("item_id")
        qty = int(entry.get("quantity", 1))
        notes = entry.get("notes", "").strip()
        menu_item = validate_order_item_selection(item_id, quantity=qty)
        validated_items.append((menu_item, qty, notes))

    # 2. Create the parent Order
    order = Order.objects.create(
        session=session,
        placed_by=placed_by,
        source=source,
        status="ACCEPTED",
        special_instructions=instructions.strip(),
    )

    # 3. Create OrderItems with frozen unit_price
    for menu_item, qty, notes in validated_items:
        OrderItem.objects.create(
            order=order,
            menu_item=menu_item,
            quantity=qty,
            unit_price=menu_item.price,
            special_instructions=notes,
            status="PREPARING",
            started_at=timezone.now(),
        )

    return order


def update_order_item_status(order_item_id, new_status, updated_by=None):
    """
    Transitions OrderItem status (PREPARING -> READY -> SERVED).
    Also updates timestamps and checks if parent order is fully served.
    """
    try:
        item = OrderItem.objects.select_related("order").get(pk=order_item_id)
    except OrderItem.DoesNotExist:
        raise ValidationError(f"OrderItem #{order_item_id} not found.")

    valid_transitions = {
        "PREPARING": ["READY", "CANCELLED"],
        "READY": ["SERVED", "CANCELLED"],
        "SERVED": [],
        "CANCELLED": [],
    }

    if new_status not in valid_transitions.get(item.status, []):
        raise ValidationError(f"Cannot transition status from {item.status} to {new_status}.")

    item.status = new_status
    now = timezone.now()

    if new_status == "READY":
        item.ready_at = now
    elif new_status == "SERVED":
        item.served_at = now

    item.save()

    # Check if all items in order are now served
    parent_order = item.order
    remaining_items = parent_order.items.exclude(status__in=["SERVED", "CANCELLED"]).exists()
    if not remaining_items:
        parent_order.status = "SERVED"
        parent_order.save()
    elif parent_order.items.filter(status="READY").exists():
        parent_order.status = "READY"
        parent_order.save()
    else:
        parent_order.status = "PREPARING"
        parent_order.save()

    return item


def get_kitchen_active_orders():
    """
    Retrieves orders that have items currently preparing or ready in the kitchen.
    """
    return (
        Order.objects.filter(status__in=["ACCEPTED", "PREPARING", "READY"])
        .select_related("session__table", "placed_by")
        .prefetch_related("items__menu_item")
        .order_by("created_at")
    )


def get_pending_serves_for_waiter(waiter=None):
    """
    Retrieves OrderItem items that are READY in kitchen but not yet SERVED to guests.
    """
    qs = OrderItem.objects.filter(status="READY").select_related(
        "order__session__table", "menu_item", "order__placed_by"
    )
    if waiter:
        qs = qs.filter(order__session__waiter=waiter)
    return qs.order_by("ready_at")
