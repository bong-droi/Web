from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.db import DatabaseError
from django.http import JsonResponse
from .models import Order, OrderItem
from .forms import OrderItemForm

@login_required
def order_list(request):
    error_message = None
    try:
        orders = Order.objects.all().order_by('-created_at')
    except DatabaseError as exc:
        orders = []
        error_message = str(exc)
    return render(request, "orders/order_list.html", {"orders": orders, "db_error": error_message})

@login_required
def order_create(request):
    if request.method == "POST":
        order_type = request.POST.get("order_type", "offline")
        delivery_address = request.POST.get("delivery_address", "").strip()
        table_number = request.POST.get("table_number", "").strip()
        order = Order.objects.create(
            staff=request.user,
            order_type=order_type,
            delivery_address=delivery_address if order_type == "online" else "",
            table_number=table_number if order_type == "offline" else "",
        )
        return redirect("order_detail", pk=order.pk)
    return render(request, "orders/order_create.html")

@login_required
def order_detail(request, pk):
    order = get_object_or_404(Order, pk=pk)
    items = order.items.all()

    if request.method == "POST":
        form = OrderItemForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)
            item.order = order
            item.save()
            return redirect("order_detail", pk=order.pk)
    else:
        form = OrderItemForm()

    return render(request, "orders/order_detail.html", {
        "order": order,
        "items": items,
        "form": form
    })

@login_required
def order_delete(request, pk):
    order = get_object_or_404(Order, pk=pk)
    order.delete()
    return redirect("order_list")


@login_required
@require_POST
def order_toggle_status(request, pk):
    order = get_object_or_404(Order, pk=pk)
    order.status = "processed" if order.status == "processing" else "processing"
    order.save(update_fields=["status"])
    return redirect("order_detail", pk=order.pk)


@login_required
def order_invoice(request, pk):
    order = get_object_or_404(Order, pk=pk)
    items = order.items.select_related("menu_item").all()
    return render(request, "orders/order_invoice.html", {"order": order, "items": items})


@login_required
@require_POST
def create_order_from_customer(request):
    # Expect JSON payload: { order_type, address/table, items: [{menu_item_id, qty}] }
    try:
        import json
        payload = json.loads(request.body.decode("utf-8"))
        order_type = payload.get("order_type", "offline")
        address = (payload.get("delivery_address") or "").strip()
        table_number = (payload.get("table_number") or "").strip()
        phone_number = (payload.get("phone_number") or "").strip()
        items = payload.get("items", [])
        if not isinstance(items, list) or len(items) == 0:
            return JsonResponse({"ok": False, "error": "No items"}, status=400)

        order = Order.objects.create(
            staff=None,
            customer=request.user,
            order_type=order_type,
            delivery_address=address if order_type == "online" else "",
            table_number=table_number if order_type == "offline" else "",
            phone_number=phone_number if order_type == "online" else "",
            status="processing",
        )
        # Create items
        from menu.models import MenuItem
        for it in items:
            menu_id = it.get("menu_item_id")
            qty = int(it.get("qty") or 0)
            if not menu_id or qty <= 0:
                continue
            try:
                mi = MenuItem.objects.get(pk=menu_id)
                OrderItem.objects.create(order=order, menu_item=mi, quantity=qty)
            except MenuItem.DoesNotExist:
                continue

        return JsonResponse({"ok": True, "order_id": order.id})
    except Exception as exc:
        return JsonResponse({"ok": False, "error": str(exc)}, status=400)


@login_required
def order_list_api(request):
    qs = Order.objects.all().order_by('-created_at')[:200]
    data = []
    for o in qs:
        data.append({
            'id': o.id,
            'order_type': o.order_type,
            'delivery_address': o.delivery_address,
            'table_number': o.table_number,
            'phone_number': o.phone_number,
            'status': o.status,
            'cancel_reason': o.cancel_reason,
            'canceled_at': o.canceled_at.strftime('%Y-%m-%d %H:%M') if o.canceled_at else None,
            'total': o.total_price(),
            'created_at': o.created_at.strftime('%Y-%m-%d %H:%M'),
        })
    return JsonResponse({'ok': True, 'orders': data})


@login_required
def order_detail_api(request, pk):
    o = get_object_or_404(Order, pk=pk)
    items = [{
        'name': i.menu_item.name,
        'price': i.menu_item.price,
        'qty': i.quantity,
        'line': i.menu_item.price * i.quantity,
    } for i in o.items.select_related('menu_item').all()]
    return JsonResponse({
        'ok': True,
        'order': {
            'id': o.id,
            'customer': o.customer.username if o.customer else None,
            'order_type': o.order_type,
            'delivery_address': o.delivery_address,
            'table_number': o.table_number,
            'phone_number': o.phone_number,
            'status': o.status,
            'cancel_reason': o.cancel_reason,
            'total': o.total_price(),
            'created_at': o.created_at.strftime('%Y-%m-%d %H:%M'),
            'completed_at': o.completed_at.strftime('%Y-%m-%d %H:%M') if o.completed_at else None,
            'canceled_at': o.canceled_at.strftime('%Y-%m-%d %H:%M') if o.canceled_at else None,
            'items': items,
        }
    })


@login_required
def my_orders_api(request):
    qs = Order.objects.filter(customer=request.user).order_by('-created_at')[:20]
    data = []
    for o in qs:
        items = [{
            'name': i.menu_item.name,
            'price': i.menu_item.price,
            'qty': i.quantity,
            'line': i.menu_item.price * i.quantity,
        } for i in o.items.select_related('menu_item').all()]
        data.append({
            'id': o.id,
            'order_type': o.order_type,
            'delivery_address': o.delivery_address,
            'table_number': o.table_number,
            'phone_number': o.phone_number,
            'status': o.status,
            'cancel_reason': o.cancel_reason,
            'total': o.total_price(),
            'created_at': o.created_at.strftime('%Y-%m-%d %H:%M'),
            'items': items,
        })
    return JsonResponse({'ok': True, 'orders': data})


@login_required
@require_POST
def order_complete_api(request, pk):
    o = get_object_or_404(Order, pk=pk)
    from django.utils import timezone
    if o.status != 'canceled':
        o.status = 'processed'
        o.completed_at = timezone.now()
        o.save(update_fields=['status', 'completed_at'])
    return JsonResponse({'ok': True})


@login_required
@require_POST
def order_cancel_api(request, pk):
    o = get_object_or_404(Order, pk=pk)
    if o.status == 'processed':
        return JsonResponse({'ok': False, 'error': 'Đơn đã hoàn thành, không thể hủy.'}, status=400)
    from django.utils import timezone
    reason = (request.POST.get('reason') or '').strip()
    if not reason:
        return JsonResponse({'ok': False, 'error': 'Vui lòng nhập lý do hủy.'}, status=400)
    o.status = 'canceled'
    o.canceled_at = timezone.now()
    o.cancel_reason = reason
    o.save(update_fields=['status', 'canceled_at', 'cancel_reason'])
    return JsonResponse({'ok': True})
