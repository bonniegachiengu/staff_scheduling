from django import forms
from django.utils import timezone
from .models import Employee, Shift, EmployeeRole, Role, ShiftTime

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

    for day, day_name in DAYS:
        for shift_time, shift_name in ShiftTime.choices:
            field_name = f'{day}_{shift_time}'
            locals()[field_name] = forms.BooleanField(label=f'{day_name} {shift_name}', required=False)

class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = ['name', 'max_hours_per_week']

class EmployeeRoleForm(forms.ModelForm):
    class Meta:
        model = EmployeeRole
        fields = ['role', 'rating']

EmployeeRoleFormSet = forms.inlineformset_factory(
    Employee, EmployeeRole, form=EmployeeRoleForm, extra=1, can_delete=True
)

class EmployeePreferencesForm(forms.ModelForm):
    preferred_shifts = forms.ModelMultipleChoiceField(
        queryset=Shift.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    class Meta:
        model = Employee
        fields = ['max_hours_per_week', 'preferred_shifts']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['preferred_shifts'].queryset = Shift.objects.filter(date__gte=timezone.now().date())

class ShiftGenerationForm(forms.Form):
    start_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    end_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))

class ShiftForm(forms.ModelForm):
    class Meta:
        model = Shift
        fields = ['role', 'date', 'shift_time']
        widgets = {
            'role': forms.Select(choices=Role.choices),
            'date': forms.DateInput(attrs={'type': 'date'}),
            'shift_time': forms.Select(choices=ShiftTime.choices),
        }