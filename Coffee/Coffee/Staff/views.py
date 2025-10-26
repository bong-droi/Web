from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import StaffProfile, Salary
from .forms import StaffProfileForm, SalaryForm

# --- Chủ quán quản lý nhân viên ---
@login_required
def staff_list(request):
    if request.user.role != "owner":
        return redirect("menu_list")
    staff_profiles = StaffProfile.objects.all()
    return render(request, "staff/staff_list.html", {"staff_profiles": staff_profiles})

@login_required
def staff_create(request):
    if request.user.role != "owner":
        return redirect("menu_list")
    if request.method == "POST":
        form = StaffProfileForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("staff_list")
    else:
        form = StaffProfileForm()
    return render(request, "staff/staff_form.html", {"form": form})

@login_required
def staff_update(request, pk):
    if request.user.role != "owner":
        return redirect("menu_list")
    profile = get_object_or_404(StaffProfile, pk=pk)
    if request.method == "POST":
        form = StaffProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            return redirect("staff_list")
    else:
        form = StaffProfileForm(instance=profile)
    return render(request, "staff/staff_form.html", {"form": form})

@login_required
def staff_delete(request, pk):
    if request.user.role != "owner":
        return redirect("menu_list")
    profile = get_object_or_404(StaffProfile, pk=pk)
    profile.delete()
    return redirect("staff_list")

# --- Quản lý lương ---
@login_required
def salary_list(request):
    if request.user.role != "owner":
        return redirect("menu_list")
    salaries = Salary.objects.all()
    return render(request, "staff/salary_list.html", {"salaries": salaries})

@login_required
def salary_create(request):
    if request.user.role != "owner":
        return redirect("menu_list")
    if request.method == "POST":
        form = SalaryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("salary_list")
    else:
        form = SalaryForm()
    return render(request, "staff/salary_form.html", {"form": form})

@login_required
def salary_update(request, pk):
    if request.user.role != "owner":
        return redirect("menu_list")
    salary = get_object_or_404(Salary, pk=pk)
    if request.method == "POST":
        form = SalaryForm(request.POST, instance=salary)
        if form.is_valid():
            form.save()
            return redirect("salary_list")
    else:
        form = SalaryForm(instance=salary)
    return render(request, "staff/salary_form.html", {"form": form})

@login_required
def salary_delete(request, pk):
    if request.user.role != "owner":
        return redirect("menu_list")
    salary = get_object_or_404(Salary, pk=pk)
    salary.delete()
    return redirect("salary_list")
