from django.contrib import messages as dj_messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import ensure_csrf_cookie

from menu.models import MenuItem

from .forms import RegisterForm

# accounts/views.py (thêm vào dưới các view sẵn có)
from django.contrib.auth import get_user_model, update_session_auth_hash
from django.core.paginator import Paginator
from django.db.models import Q, Case, When, IntegerField, Value
from django.db.models.functions import Concat
from django.shortcuts import get_object_or_404, redirect, render
from .permissions import owner_required
from .forms import UserEditForm, RoleForm, QuickCreateStaffForm
from django.contrib.auth.forms import SetPasswordForm

User = get_user_model()

def _is_last_owner(user: User) -> bool: # type: ignore
    """True nếu user là owner cuối cùng (active)."""
    return user.role == "owner" and User.objects.filter(role="owner", is_active=True).exclude(pk=user.pk).count() == 0

@owner_required
def user_list(request):
    q = request.GET.get("q", "").strip()
    qs = User.objects.all()
    # Tìm kiếm không phân biệt hoa thường theo username và Họ Tên (gộp)
    if q:
        qs = qs.annotate(
            full_name=Concat("first_name", Value(" "), "last_name")
        ).filter(
            Q(username__icontains=q) |
            Q(full_name__icontains=q)
        )
    # Sắp xếp theo role: owner -> staff -> customer, sau đó theo username a-z
    role_order = Case(
        When(role="owner", then=Value(0)),
        When(role="staff", then=Value(1)),
        When(role="customer", then=Value(2)),
        default=Value(9),
        output_field=IntegerField(),
    )
    qs = qs.order_by(role_order, "username")
    paginator = Paginator(qs, 12)
    page = paginator.get_page(request.GET.get("page"))
    return render(request, "accounts/users/list.html", {
        "page": page,
        "q": q,
        "create_form": QuickCreateStaffForm()
    })

@owner_required
def user_create(request):
    if request.method != "POST":
        return redirect("user_list")
    form = QuickCreateStaffForm(request.POST)
    if not form.is_valid():
        dj_messages.error(request, "Dữ liệu không hợp lệ.")
        return redirect("user_list")
    d = form.cleaned_data
    if User.objects.filter(username=d["username"]).exists():
        dj_messages.error(request, "Tên đăng nhập đã tồn tại.")
        return redirect("user_list")
    user = User.objects.create_user(
        username=d["username"],
        password=d["password"],
        first_name=d.get("first_name",""),
        last_name=d.get("last_name",""),
        email=d.get("email",""),
    )
    user.role = "staff"
    user.save(update_fields=["role"])
    dj_messages.success(request, f"Tạo nhân viên {user.username} thành công.")
    return redirect("user_list")

@owner_required
def user_detail(request, pk):
    u = get_object_or_404(User, pk=pk)
    return render(request, "accounts/users/detail.html", {"u": u})

@owner_required
def user_edit(request, pk):
    u = get_object_or_404(User, pk=pk)
    form = UserEditForm(request.POST or None, instance=u)
    if request.method == "POST" and form.is_valid():
        form.save()
        dj_messages.success(request, "Đã lưu thông tin.")
        return redirect("user_detail", pk=u.pk)
    return render(request, "accounts/users/edit.html", {"form": form, "u": u})

@owner_required
def user_role(request, pk):
    u = get_object_or_404(User, pk=pk)
    form = RoleForm(request.POST or None, instance=u)
    if request.method == "POST" and form.is_valid():
        new_role = form.cleaned_data["role"]
        if _is_last_owner(u) and new_role != "owner":
            dj_messages.error(request, "Không thể giáng cấp/chuyển role vì đây là chủ quán cuối cùng.")
        else:
            u.role = new_role
            u.save(update_fields=["role"])
            dj_messages.success(request, f"Đã đổi role thành '{new_role}'.")
        return redirect("user_detail", pk=u.pk)
    return render(request, "accounts/users/role.html", {"form": form, "u": u})

@owner_required
def user_password(request, pk):
    u = get_object_or_404(User, pk=pk)
    form = SetPasswordForm(user=u, data=request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        # nếu đổi mật khẩu cho tài khoản đang đăng nhập
        if u.pk == request.user.pk:
            update_session_auth_hash(request, u)
        dj_messages.success(request, "Đã đặt lại mật khẩu.")
        return redirect("user_detail", pk=u.pk)
    return render(request, "accounts/users/password.html", {"form": form, "u": u})

@owner_required
def user_delete(request, pk):
    u = get_object_or_404(User, pk=pk)
    if request.method == "POST":
        if u.pk == request.user.pk:
            dj_messages.error(request, "Bạn không thể tự xoá tài khoản của chính mình.")
        elif _is_last_owner(u):
            dj_messages.error(request, "Không thể xoá chủ quán cuối cùng.")
        else:
            u.delete()
            dj_messages.success(request, "Đã xoá tài khoản.")
            return redirect("user_list")
    return render(request, "accounts/users/delete_confirm.html", {"u": u})


# ========== AUTH ==========
# def login_view(request):
#     if request.method == "POST":
#         u = request.POST.get("username", "").strip()
#         p = request.POST.get("password", "").strip()

#         if not u or not p:
#             dj_messages.error(request, "Vui lòng nhập đủ thông tin.")
#             return render(request, "accounts/login.html", status=400)

#         user = authenticate(request, username=u, password=p)
#         if user is None:
#             dj_messages.error(request, "Sai tên đăng nhập hoặc mật khẩu.")
#             return render(request, "accounts/login.html", status=401)

#         login(request, user)
#         role = getattr(user, "role", "")
#         if role == "owner":
#             return redirect("owner_frameset")
#         if role == "staff":
#             return redirect("staff_dashboard")
#         # Fallback: nếu chưa có trang 'home', quay về dashboard chủ quán
#         return redirect("owner_frameset")

#     return render(request, "accounts/login.html")

def login_view(request):
    if request.method == "POST":
        u = request.POST.get("username", "").strip()
        p = request.POST.get("password", "").strip()

        if not u or not p:
            dj_messages.error(request, "Vui lòng nhập đủ thông tin.")
            return render(request, "accounts/login.html", status=400)

        user = authenticate(request, username=u, password=p)
        if user is None:
            dj_messages.error(request, "Sai tên đăng nhập hoặc mật khẩu.")
            return render(request, "accounts/login.html", status=401)

        login(request, user)
        role = getattr(user, "role", "customer")
        if role == "owner":
            return redirect("owner_frameset")
        if role == "staff":
            return redirect("staff_dashboard")
        return redirect("customer_home")   # <-- khách hàng

    return render(request, "accounts/login.html")

def logout_view(request):
    logout(request)
    return redirect("login")   # quay lại trang chọn Đăng nhập/Đăng ký (ở bước 4)

def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()     # role=customer đã set trong form
            dj_messages.success(request, "Đăng ký thành công. Mời đăng nhập.")
            return redirect("login")
    else:
        form = RegisterForm()
    return render(request, "accounts/register.html", {"form": form})

# ---- Khách hàng xem menu (đọc-only) ----
@login_required
def customer_home(request):
    # chỉ cho customer; nếu owner/staff nhầm vào thì chuyển về đúng nơi
    role = getattr(request.user, "role", "")
    if role == "owner":
        return redirect("owner_frameset")
    if role == "staff":
        return redirect("staff_dashboard")

    items = MenuItem.objects.filter(is_available=True).order_by("-created_at")[:60]
    return render(request, "accounts/customer_home.html", {"items": items})


# ========== DASHBOARD ==========
@never_cache
@ensure_csrf_cookie
@login_required
def owner_frameset(request):
    """Dashboard chủ quán: render FRAMES/2 hàng (header + main)."""
    if getattr(request.user, "role", "") != "owner":
        return redirect("staff_dashboard")
    # dùng frameset làm shell
    return render(request, "accounts/owner_frameset.html")


@never_cache
@ensure_csrf_cookie
@login_required
def owner_header(request):
    """Header (nằm ở hàng trên của frameset)."""
    return render(request, "accounts/owner_header.html")


@never_cache
@ensure_csrf_cookie
@login_required
def owner_home(request):
    """Trang chủ (ảnh), mở trong frame 'main'."""
    return render(request, "accounts/owner_home.html")


@login_required
def staff_dashboard(request):
    if getattr(request.user, "role", "") != "staff":
        return redirect("owner_frameset")
    return render(request, "accounts/staff_dashboard.html")

def customer_dashboard(request):
    return render(request, "accounts/customer_dashboard.html")


# ===== Staff static order UI (no DB required) =====
@login_required
def staff_order_ui(request):
    if getattr(request.user, "role", "") != "staff":
        return redirect("owner_frameset")
    return render(request, "accounts/staff_order_ui.html")


@login_required
def customer_order_ui(request):
    if getattr(request.user, "role", "customer") != "customer":
        # nhân viên/owner nếu lỡ vào thì chuyển về đúng dashboard
        role = getattr(request.user, "role", "")
        if role == "owner":
            return redirect("owner_frameset")
        if role == "staff":
            return redirect("staff_dashboard")
    items = MenuItem.objects.filter(is_available=True).order_by("-created_at")
    return render(request, "accounts/customer_order_ui.html", {"items": items})