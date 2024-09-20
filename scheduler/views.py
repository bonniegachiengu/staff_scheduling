from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils import timezone
from .scheduling import create_schedule
from .models import Employee, Shift, Schedule, SchedulingResult, EmployeeRole, Role, ShiftBlock
from .forms import EmployeePreferencesForm, AvailabilityForm, ShiftGenerationForm
from datetime import timedelta

def is_manager(user):
    return user.groups.filter(name='Managers').exists()

@login_required
def dashboard(request):
    latest_result = SchedulingResult.objects.order_by('-created_at').first()
    upcoming_shifts = Schedule.objects.filter(
        employee=request.user.employee,
        shift__date__gte=timezone.now().date()
    ).order_by('shift__date', 'shift__start_time')[:5]
    return render(request, 'scheduler/dashboard.html', {
        'latest_result': latest_result,
        'upcoming_shifts': upcoming_shifts
    })

@login_required
def employee_preferences(request):
    employee, created = Employee.objects.get_or_create(user=request.user, defaults={'name': request.user.username})
    
    if request.method == 'POST':
        preferences_form = EmployeePreferencesForm(request.POST, instance=employee)
        availability_form = AvailabilityForm(request.POST)
        
        if preferences_form.is_valid() and availability_form.is_valid():
            preferences_form.save()
            
            # Process availability
            availability = []
            for field, value in availability_form.cleaned_data.items():
                if value:
                    day, time = field.split('_')
                    shift_block, _ = ShiftBlock.objects.get_or_create(day=day, time=time)
                    availability.append(shift_block)
            
            employee.availability.set(availability)
            employee.save()
            
            return redirect('dashboard')
    else:
        preferences_form = EmployeePreferencesForm(instance=employee)
        initial_availability = {
            f'{shift_block.day}_{shift_block.time}': True
            for shift_block in employee.availability.all()
        }
        availability_form = AvailabilityForm(initial=initial_availability)
    
    return render(request, 'scheduler/employee_preferences.html', {
        'preferences_form': preferences_form,
        'availability_form': availability_form
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
            for shift_block in ShiftBlock.choices:
                Shift.objects.create(
                    role=role[0],
                    date=current_date,
                    shift_block=shift_block[0]
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
    schedules = Schedule.objects.all().order_by('shift__date', 'shift__start_time')
    return render(request, 'scheduler/schedule.html', {'schedules': schedules})

@login_required
@user_passes_test(is_manager)
def view_results(request):
    results = SchedulingResult.objects.all().order_by('-created_at')
    return render(request, 'scheduler/results.html', {'results': results})

def home(request):
    return render(request, 'scheduler/home.html')
