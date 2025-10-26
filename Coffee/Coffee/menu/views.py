from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages as dj_messages

from .models import MenuItem, Category
from .forms import MenuItemForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from .models import Category, MenuItem
from .forms import CategoryForm

@login_required
def menu_list(request):
    q = request.GET.get("q", "").strip()
    cat = request.GET.get("cat", "")
    only_on = request.GET.get("on", "") == "1"

    items = MenuItem.objects.select_related("category")
    if q:
        items = items.filter(Q(name__icontains=q) | Q(description__icontains=q))
    if cat:
        items = items.filter(category_id=cat)
    if only_on:
        items = items.filter(is_available=True)

    paginator = Paginator(items, 12)
    page = request.GET.get("page")
    page_obj = paginator.get_page(page)

    ctx = {
        "page_obj": page_obj,
        "q": q,
        "cat": cat,
        "only_on": only_on,
        "categories": Category.objects.filter(is_active=True).order_by("name"),
    }
    return render(request, "menu/list.html", ctx)

@login_required
def menu_create(request):
    if request.method == "POST":
        form = MenuItemForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            dj_messages.success(request, "Đã thêm món mới.")
            return redirect("list")
    else:
        form = MenuItemForm()
    return render(request, "menu/form.html", {"form": form, "title": "Thêm món"})

@login_required
def menu_edit(request, pk):
    item = get_object_or_404(MenuItem, pk=pk)
    if request.method == "POST":
        form = MenuItemForm(request.POST, request.FILES, instance=item)
        if form.is_valid():
            form.save()
            dj_messages.success(request, "Đã cập nhật món.")
            return redirect("list")
    else:
        form = MenuItemForm(instance=item)
    return render(request, "menu/form.html", {"form": form, "title": "Sửa món"})

@login_required
def menu_delete(request, pk):
    item = get_object_or_404(MenuItem, pk=pk)
    if request.method == "POST":
        item.delete()
        dj_messages.success(request, "Đã xóa món.")
        return redirect("list")
    return render(request, "menu/confirm_delete.html", {"item": item})

@login_required
def category_list(request):
    q = request.GET.get("q", "").strip()
    cats = Category.objects.all()
    if q:
        cats = cats.filter(name__icontains=q)
    ctx = {"cats": cats, "q": q}
    return render(request, "menu/category_list.html", ctx)

@login_required
def category_create(request):
    form = CategoryForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        dj_messages.success(request, "Đã thêm danh mục.")
        next_url = request.GET.get("next") or request.POST.get("next")
        return redirect(next_url or "menu_list")
    return render(request, "menu/category_form.html", {
        "form": form, "title": "Thêm danh mục", "next": request.GET.get("next", "")
    })

@login_required
def category_edit(request, pk):
    cat = get_object_or_404(Category, pk=pk)
    form = CategoryForm(request.POST or None, instance=cat)
    if request.method == "POST" and form.is_valid():
        form.save()
        dj_messages.success(request, "Đã cập nhật danh mục.")
        return redirect(request.POST.get("next") or "category_list")
    return render(request, "menu/category_form.html", {
        "form": form, "title": "Sửa danh mục", "next": request.GET.get("next", "")
    })

@login_required
def category_delete(request, pk):
    cat = get_object_or_404(Category, pk=pk)
    if request.method == "POST":
        cat.delete()
        dj_messages.success(request, "Đã xóa danh mục.")
        return redirect(request.POST.get("next") or "category_list")
    return render(request, "menu/category_confirm_delete.html", {
        "cat": cat, "next": request.GET.get("next", "")
    })