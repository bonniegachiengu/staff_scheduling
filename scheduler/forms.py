from django import forms
from django.utils import timezone
from .models import Employee, Shift, EmployeeRole, Role, ShiftBlock

class AvailabilityForm(forms.Form):
    DAYS = [
        ('monday', 'Monday'),
        ('tuesday', 'Tuesday'),
        ('wednesday', 'Wednesday'),
        ('thursday', 'Thursday'),
        ('friday', 'Friday'),
        ('saturday', 'Saturday'),
        ('sunday', 'Sunday'),
    ]

    TIME_CHOICES = ShiftBlock.TIME_CHOICES

    for day, day_name in DAYS:
        for time_value, time_name in TIME_CHOICES:
            field_name = f'{day}_{time_value}'
            locals()[field_name] = forms.BooleanField(label=f'{day_name} {time_name}', required=False)

class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = ['name', 'max_hours_per_week', 'availability', 'preferred_shifts']
        widgets = {
            'availability': forms.CheckboxSelectMultiple,
            'preferred_shifts': forms.CheckboxSelectMultiple,
        }

class EmployeeRoleForm(forms.ModelForm):
    class Meta:
        model = EmployeeRole
        fields = ['role', 'rating']

EmployeeRoleFormSet = forms.inlineformset_factory(
    Employee, EmployeeRole, form=EmployeeRoleForm, extra=1, can_delete=True
)

class EmployeePreferencesForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = ['max_hours_per_week', 'availability', 'preferred_shifts']
        widgets = {
            'availability': forms.CheckboxSelectMultiple,
            'preferred_shifts': forms.CheckboxSelectMultiple,
        }

class ShiftForm(forms.ModelForm):
    class Meta:
        model = Shift
        fields = ['role', 'date', 'shift_block']
        widgets = {
            'role': forms.Select(choices=Role.choices),
            'date': forms.DateInput(attrs={'type': 'date'}),
            'shift_block': forms.Select(),
        }

class ShiftGenerationForm(forms.Form):
    start_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    end_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))