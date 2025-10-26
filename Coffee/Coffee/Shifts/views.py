from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages as dj_messages
from django.utils import timezone
from datetime import datetime
from django.contrib.auth import get_user_model
from .models import Shift, ShiftRegistration, AssignedShift, ShiftSwapRequest
from .forms import ShiftForm, ShiftRegistrationForm, AssignedShiftForm, ShiftSwapRequestForm
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import ensure_csrf_cookie
# --- Chủ quán quản lý ca ---
@login_required
def shift_list(request):
    # Hiển thị ca theo ngày + giờ
    shifts = Shift.objects.all().order_by('date', 'start_time')
    # Tính số người đã đăng ký/được chỉ định cho đúng ngày của ca
    reg_counts = {}
    for s in shifts:
        if s.date:
            r = ShiftRegistration.objects.filter(shift=s, date=s.date).count()
            a = AssignedShift.objects.filter(shift=s, date=s.date).count()
            reg_counts[s.id] = r + a
        else:
            reg_counts[s.id] = 0
    return render(request, "shifts/shifts_list.html", {"shifts": shifts, "reg_counts": reg_counts})

@login_required
def shift_detail(request, pk):
    shift = get_object_or_404(Shift, pk=pk)
    # Chỉ chủ quán xem chi tiết danh sách nhân viên
    if getattr(request.user, 'role', '') != 'owner':
        return redirect('shift_list')
    regs = []
    assigned = []
    total = 0
    if getattr(shift, 'date', None):
        regs = list(ShiftRegistration.objects.select_related('user').filter(shift=shift, date=shift.date))
        assigned = list(AssignedShift.objects.select_related('user').filter(shift=shift, date=shift.date))
        total = len(regs) + len(assigned)
    context = {
        'shift': shift,
        'regs': regs,
        'assigned': assigned,
        'total': total,
    }
    return render(request, 'shifts/shift_detail.html', context)

@login_required
def shift_create(request):
    if request.user.role != "owner":
        return redirect("shift_list")
    if request.method == "POST":
        form = ShiftForm(request.POST)
        if form.is_valid():
            shift = form.save(commit=False)
            # Không cho tạo ca trong quá khứ (dựa theo date + start_time)
            if shift.date:
                start_dt = datetime.combine(shift.date, shift.start_time)
                if start_dt < timezone.now().replace(tzinfo=None):
                    dj_messages.error(request, "Không thể tạo ca trong quá khứ.")
                    return render(request, "shifts/shift_form.html", {"form": form})
            shift.save()
            return redirect("shift_list")
    else:
        form = ShiftForm()
    return render(request, "shifts/shift_form.html", {"form": form})

@login_required
def shift_update(request, pk):
    if request.user.role != "owner":
        return redirect("shift_list")
    shift = get_object_or_404(Shift, pk=pk)
    if request.method == "POST":
        form = ShiftForm(request.POST, instance=shift)
        if form.is_valid():
            shift = form.save(commit=False)
            if shift.date:
                start_dt = datetime.combine(shift.date, shift.start_time)
                if start_dt < timezone.now().replace(tzinfo=None):
                    dj_messages.error(request, "Không thể đặt ca về quá khứ.")
                    return render(request, "shifts/shift_form.html", {"form": form})
            shift.save()
            return redirect("shift_list")
    else:
        form = ShiftForm(instance=shift)
    return render(request, "shifts/shift_form.html", {"form": form})

@login_required
def shift_delete(request, pk):
    if request.user.role != "owner":
        return redirect("shift_list")
    shift = get_object_or_404(Shift, pk=pk)
    shift.delete()
    return redirect("shift_list")

# --- Nhân viên đăng ký ca ---
@never_cache
@ensure_csrf_cookie
@login_required
def shift_register(request):
    if request.method == "POST":
        form = ShiftRegistrationForm(request.POST)
        if form.is_valid():
            registration = form.save(commit=False)
            registration.user = request.user
            # kiểm tra capacity (nếu có)
            shift = registration.shift
            # ngày đăng ký trùng theo ngày của ca (bắt buộc ca có ngày)
            if not getattr(shift, 'date', None):
                dj_messages.error(request, "Ca này chưa có ngày. Liên hệ quản lý.")
                return redirect("my_shifts")
            registration.date = shift.date
            # chặn đăng ký quá khứ
            if registration.date < timezone.localdate():
                dj_messages.error(request, "Không thể đăng ký ca trong quá khứ.")
                return redirect("my_shifts")
            if shift.capacity and (
                ShiftRegistration.objects.filter(shift=shift, date=registration.date).count() +
                AssignedShift.objects.filter(shift=shift, date=registration.date).count()
            ) >= shift.capacity:
                dj_messages.error(request, "Ca đã đủ số lượng.")
            else:
                registration.save()
                dj_messages.success(request, "Đăng ký ca thành công.")
            return redirect("my_shifts")
    else:
        form = ShiftRegistrationForm()
    return render(request, "shifts/shifts_register.html", {"form": form})

@login_required
def my_shifts(request):
    my_shifts = ShiftRegistration.objects.select_related('shift').filter(user=request.user).order_by('-date')
    received_swaps = ShiftSwapRequest.objects.filter(responder=request.user, status='pending')
    return render(request, "shifts/my_shifts.html", {"my_shifts": my_shifts, "received_swaps": received_swaps})

# --- Chủ quán chỉ định nhân viên ---
@login_required
def assign_shift(request):
    if request.user.role != "owner":
        return redirect("shift_list")
    if request.method == "POST":
        form = AssignedShiftForm(request.POST)
        if form.is_valid():
            assigned = form.save(commit=False)
            shift = assigned.shift
            if shift.capacity and (
                ShiftRegistration.objects.filter(shift=shift, date=assigned.date).count() +
                AssignedShift.objects.filter(shift=shift, date=assigned.date).count()
            ) >= shift.capacity:
                dj_messages.error(request, "Ca đã đủ số lượng.")
            else:
                assigned.save()
                dj_messages.success(request, "Đã chỉ định nhân viên vào ca.")
            return redirect("shift_list")
    else:
        form = AssignedShiftForm()
    return render(request, "shifts/assign_form.html", {"form": form})

# --- Đổi ca ---
@login_required
def swap_request(request):
    User = get_user_model()
    initial = {}
    if request.method == "GET":
        shift_id = request.GET.get('shift')
        date_str = request.GET.get('date')
        if shift_id:
            initial['shift'] = get_object_or_404(Shift, pk=shift_id)
        if date_str:
            try:
                initial['date'] = datetime.strptime(date_str, '%Y-%m-%d').date()
            except ValueError:
                pass
    form = ShiftSwapRequestForm(request.POST or None, initial=initial)

    # Hạn chế danh sách người nhận theo cùng (shift, date)
    potential_ids = []
    if form.initial.get('shift') and form.initial.get('date'):
        s = form.initial['shift']
        d = form.initial['date']
        potential_ids = list(
            ShiftRegistration.objects.filter(shift=s, date=d).values_list('user_id', flat=True)
        ) + list(
            AssignedShift.objects.filter(shift=s, date=d).values_list('user_id', flat=True)
        )
    form.fields['responder'].queryset = User.objects.filter(id__in=potential_ids).exclude(pk=request.user.pk)

    if request.method == "POST" and form.is_valid():
        swap = form.save(commit=False)
        swap.requester = request.user
        # Validate requester & responder đều thuộc ca/ngày đó
        s, d, r_user = swap.shift, swap.date, swap.responder
        req_has = ShiftRegistration.objects.filter(user=request.user, shift=s, date=d).exists() or \
                  AssignedShift.objects.filter(user=request.user, shift=s, date=d).exists()
        res_has = ShiftRegistration.objects.filter(user=r_user, shift=s, date=d).exists() or \
                  AssignedShift.objects.filter(user=r_user, shift=s, date=d).exists()
        if not (req_has and res_has):
            dj_messages.error(request, "Hai bên phải đang thuộc ca này mới có thể đổi.")
        elif ShiftSwapRequest.objects.filter(requester=request.user, responder=r_user, shift=s, date=d, status='pending').exists():
            dj_messages.info(request, "Bạn đã gửi yêu cầu đổi ca này và đang chờ duyệt.")
        else:
            swap.save()
            dj_messages.success(request, "Đã gửi yêu cầu đổi ca.")
            return redirect("my_shifts")
    return render(request, "shifts/swap_form.html", {"form": form})

@login_required
def swap_respond(request, pk, action):
    swap = get_object_or_404(ShiftSwapRequest, pk=pk, responder=request.user)
    if swap.status != 'pending':
        return redirect("my_shifts")
    if action == 'approve':
        swap.status = 'approved'
        # chuyển quyền đăng ký ca
        ShiftRegistration.objects.filter(user=swap.requester, shift=swap.shift, date=swap.date).delete()
        ShiftRegistration.objects.get_or_create(user=swap.responder, shift=swap.shift, date=swap.date)
        dj_messages.success(request, "Đã chấp nhận đổi ca.")
    elif action == 'reject':
        swap.status = 'rejected'
        dj_messages.info(request, "Đã từ chối yêu cầu đổi ca.")
    swap.save()
    return redirect("my_shifts")
