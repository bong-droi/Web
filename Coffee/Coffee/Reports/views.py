from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from orders.models import Order, OrderItem
from Staff.models import Salary
from Inventory.models import Purchase, Supply
from Shifts.models import ShiftRegistration

@login_required
def report_dashboard(request):
    if request.user.role != "owner":
        return redirect("menu_list")

    # Tổng doanh thu từ orders
    revenue = 0
    for order in Order.objects.all():
        revenue += order.total_price()

    # Tổng lương phải trả
    total_salary = Salary.objects.aggregate(total=Sum("amount"))["total"] or 0

    # Tổng chi phí nhập hàng
    total_purchase = Purchase.objects.aggregate(total=Sum("cost"))["total"] or 0

    context = {
        "revenue": revenue,
        "total_salary": total_salary,
        "total_purchase": total_purchase,
    }
    return render(request, "reports/report_dashboard.html", context)

@login_required
def revenue_report(request):
    if request.user.role != "owner":
        return redirect("menu_list")
    orders = Order.objects.all().order_by("-created_at")
    return render(request, "reports/revenue_report.html", {"orders": orders})

@login_required
def salary_report(request):
    if request.user.role != "owner":
        return redirect("menu_list")
    salaries = Salary.objects.all()
    return render(request, "reports/salary_report.html", {"salaries": salaries})

@login_required
def inventory_report(request):
    if request.user.role != "owner":
        return redirect("menu_list")
    supplies = Supply.objects.all()
    purchases = Purchase.objects.all()
    return render(request, "reports/inventory_report.html", {"supplies": supplies, "purchases": purchases})

@login_required
def shift_report(request):
    if request.user.role != "owner":
        return redirect("menu_list")
    regs = ShiftRegistration.objects.all().order_by("-date")
    return render(request, "reports/shift_report.html", {"regs": regs})
