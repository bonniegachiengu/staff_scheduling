from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils import timezone
from .scheduling import create_schedule
from .models import Employee, Shift, Schedule, SchedulingResult, EmployeeRole, Role, ShiftTime
from .forms import EmployeePreferencesForm, ShiftGenerationForm
from datetime import timedelta

def is_manager(user):
    return user.groups.filter(name='Managers').exists()

@login_required
def dashboard(request):
    # Add your dashboard logic here
    return render(request, 'scheduler/dashboard.html')

@login_required
def employee_preferences(request):
    employee, created = Employee.objects.get_or_create(user=request.user, defaults={'name': request.user.username})
    
    if request.method == 'POST':
        preferences_form = EmployeePreferencesForm(request.POST, instance=employee)
        if preferences_form.is_valid():
            preferences_form.save()
            return redirect('dashboard')
    else:
        preferences_form = EmployeePreferencesForm(instance=employee)
    
    return render(request, 'scheduler/employee_preferences.html', {
        'preferences_form': preferences_form,
    })

@user_passes_test(lambda u: u.is_staff)
def generate_shifts(request):
    if request.method == 'POST':
        form = ShiftGenerationForm(request.POST)
        if form.is_valid():
            start_date = form.cleaned_data['start_date']
            end_date = form.cleaned_data['end_date']
            generate_shifts_for_period(start_date, end_date)
            return redirect('view_schedule')
    else:
        form = ShiftGenerationForm()
    
    return render(request, 'scheduler/generate_shifts.html', {'form': form})

def generate_shifts_for_period(start_date, end_date):
    current_date = start_date
    while current_date <= end_date:
        for role in Role.choices:
            for shift_time in ShiftTime.choices:
                Shift.objects.get_or_create(
                    role=role[0],
                    date=current_date,
                    shift_time=shift_time[0]
                )
        current_date += timedelta(days=1)

@login_required
@user_passes_test(is_manager)
def generate_schedule(request):
    total_satisfaction, unassigned_shifts = create_schedule()
    return JsonResponse({
        'total_satisfaction': total_satisfaction,
        'unassigned_shifts': unassigned_shifts
    })

@login_required
@user_passes_test(is_manager)
def view_schedule(request):
    schedules = Schedule.objects.all().order_by('shift__date', 'shift__shift_time')
    return render(request, 'scheduler/schedule.html', {'schedules': schedules})

@login_required
@user_passes_test(is_manager)
def view_results(request):
    results = SchedulingResult.objects.all().order_by('-created_at')
    return render(request, 'scheduler/results.html', {'results': results})

def home(request):
    return render(request, 'scheduler/home.html')
