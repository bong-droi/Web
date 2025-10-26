from django import forms
from .models import Shift, ShiftRegistration, AssignedShift, ShiftSwapRequest

class ShiftForm(forms.ModelForm):
    class Meta:
        model = Shift
        fields = '__all__'
        widgets = {
            'date': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date'}),
            'start_time': forms.TimeInput(format='%H:%M', attrs={'type': 'time'}),
            'end_time': forms.TimeInput(format='%H:%M', attrs={'type': 'time'}),
        }

    def clean(self):
        cleaned = super().clean()
        date = cleaned.get('date')
        start_time = cleaned.get('start_time')
        end_time = cleaned.get('end_time')
        from django.utils import timezone
        from datetime import datetime
        if not date:
            self.add_error('date', 'Vui lòng chọn ngày cho ca.')
            return cleaned
        if start_time and end_time and end_time <= start_time:
            self.add_error('end_time', 'Giờ kết thúc phải sau giờ bắt đầu.')
        try:
            start_dt = datetime.combine(date, start_time)
            if start_dt < timezone.now().replace(tzinfo=None):
                self.add_error('date', 'Không thể tạo ca trong quá khứ.')
        except Exception:
            pass
        return cleaned

class ShiftRegistrationForm(forms.ModelForm):
    class ShiftChoiceField(forms.ModelChoiceField):
        def label_from_instance(self, obj: Shift) -> str:  # type: ignore[name-defined]
            date_str = obj.date.strftime('%d/%m/%Y') if getattr(obj, 'date', None) else '—'
            return f"{obj.name} ({obj.start_time} - {obj.end_time}) · Ngày: {date_str}"

    shift = ShiftChoiceField(queryset=Shift.objects.all().order_by('date', 'start_time'))
    class Meta:
        model = ShiftRegistration
        fields = ['shift']

class AssignedShiftForm(forms.ModelForm):
    class Meta:
        model = AssignedShift
        fields = ['user', 'shift', 'date']

class ShiftSwapRequestForm(forms.ModelForm):
    class Meta:
        model = ShiftSwapRequest
        fields = ['responder', 'shift', 'date']
