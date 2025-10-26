from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Supply, Purchase, Damage
from .forms import SupplyForm, PurchaseForm, DamageForm

# --- Chủ quán quản lý vật tư ---
@login_required
def supply_list(request):
    t = request.GET.get("type", "")
    supplies = Supply.objects.all()
    if t in ("supply", "ingredient"):
        supplies = supplies.filter(type=t)
    return render(request, "inventory/supply_list.html", {"supplies": supplies, "t": t})

@login_required
def supply_create(request):
    if request.user.role != "owner":
        return redirect("supply_list")
    if request.method == "POST":
        form = SupplyForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("supply_list")
    else:
        form = SupplyForm()
    return render(request, "inventory/supply_form.html", {"form": form})

@login_required
def supply_update(request, pk):
    if request.user.role != "owner":
        return redirect("supply_list")
    supply = get_object_or_404(Supply, pk=pk)
    if request.method == "POST":
        form = SupplyForm(request.POST, instance=supply)
        if form.is_valid():
            form.save()
            return redirect("supply_list")
    else:
        form = SupplyForm(instance=supply)
    return render(request, "inventory/supply_form.html", {"form": form})

@login_required
def supply_delete(request, pk):
    if request.user.role != "owner":
        return redirect("supply_list")
    supply = get_object_or_404(Supply, pk=pk)
    supply.delete()
    return redirect("supply_list")

# --- Nhập vật tư ---
@login_required
def purchase_list(request):
    purchases = Purchase.objects.all()
    return render(request, "inventory/purchase_list.html", {"purchases": purchases})

@login_required
def purchase_create(request):
    if request.user.role != "owner":
        return redirect("purchase_list")
    if request.method == "POST":
        form = PurchaseForm(request.POST)
        if form.is_valid():
            purchase = form.save(commit=False)
            # Cập nhật số lượng vật tư
            purchase.supply.quantity += purchase.quantity
            purchase.supply.save()
            purchase.save()
            return redirect("purchase_list")
    else:
        form = PurchaseForm()
    return render(request, "inventory/purchase_form.html", {"form": form})

# --- Vật tư/Nguyên liệu hỏng ---
@login_required
def damage_list(request):
    damages = Damage.objects.select_related("supply").all()
    return render(request, "inventory/damage_list.html", {"damages": damages})

@login_required
def damage_create(request):
    if request.user.role != "owner":
        return redirect("damage_list")
    if request.method == "POST":
        form = DamageForm(request.POST)
        if form.is_valid():
            damage = form.save(commit=False)
            # Trừ tồn kho
            damage.supply.quantity = max(0, damage.supply.quantity - damage.quantity)
            damage.supply.save()
            damage.save()
            return redirect("damage_list")
    else:
        form = DamageForm()
    return render(request, "inventory/damage_form.html", {"form": form})
