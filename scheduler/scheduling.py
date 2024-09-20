from scipy.optimize import linear_sum_assignment
import numpy as np
from django.db.models import Sum, F
from datetime import timedelta
from .models import Employee, Shift, Schedule, SchedulingResult, EmployeeRole, EmployeeType, Role, ShiftTime

def is_peak_hour(shift):
    peak_hours = [ShiftTime.MORNING, ShiftTime.AFTERNOON, ShiftTime.EVENING]
    return shift.shift_time in peak_hours

def get_required_staff(shift):
    is_peak = is_peak_hour(shift)
    role_type = Role.get_type(shift.role)
    
    if role_type == EmployeeType.CREW:
        return 2 if is_peak else 1
    elif role_type == EmployeeType.DRIVER:
        return 5 if is_peak else 3
    elif role_type == EmployeeType.MANAGEMENT:
        return 2 if is_peak else 1
    else:
        raise ValueError(f"Unknown role type for role: {shift.role}")

def calculate_cost(employee, shift):
    cost = 100  # Base cost

    # Check if employee has the required role
    employee_roles = EmployeeRole.objects.filter(employee=employee, role=shift.role)
    if not employee_roles.exists():
        return float('inf')  # Employee doesn't have the required role

    # Use the highest rating if employee has multiple ratings for the role
    role_rating = max(role.rating for role in employee_roles)
    
    # Adjust cost based on role rating
    cost -= role_rating * 10

    if shift.date.isoformat() not in employee.availability:
        return float('inf')  # Employee not available

    # Preferred shift bonus
    if shift.id in employee.preferred_shifts:
        cost -= 20

    # Consider employee satisfaction
    cost -= employee.satisfaction_score * 0.5

    # Consider consecutive shifts
    previous_shift = Shift.objects.filter(date=shift.date - timedelta(days=1), employee=employee).first()
    if previous_shift:
        hours_between = (shift.start_time - previous_shift.end_time).total_seconds() / 3600
        if hours_between < 12:
            cost += 30  # Penalty for less than 12 hours between shifts

    # Consider weekly hours limit
    week_start = shift.date - timedelta(days=shift.date.weekday())
    week_end = week_start + timedelta(days=6)
    weekly_hours = Schedule.objects.filter(
        employee=employee,
        shift__date__range=[week_start, week_end]
    ).aggregate(total_hours=Sum(F('shift__end_time') - F('shift__start_time')))['total_hours'] or timedelta()
    weekly_hours = weekly_hours.total_seconds() / 3600

    if weekly_hours + (shift.end_time - shift.start_time).total_seconds() / 3600 > employee.max_hours_per_week:
        cost += 50  # Penalty for exceeding weekly hours limit

    return max(cost, 0)  # Ensure non-negative cost

def create_schedule():
    employees = Employee.objects.all()
    shifts = Shift.objects.all()

    cost_matrix = np.array([[calculate_cost(e, s) for s in shifts] for e in employees])

    row_ind, col_ind = linear_sum_assignment(cost_matrix)

    # Create schedule entries
    schedules = []
    for r, c in zip(row_ind, col_ind):
        if cost_matrix[r, c] < float('inf'):
            schedules.append(Schedule(employee=employees[r], shift=shifts[c]))

    # Check constraints
    for shift in shifts:
        required_staff = get_required_staff(shift)
        assigned_staff = sum(1 for s in schedules if s.shift == shift)
        
        # Adjust assignments if constraints are not met
        while assigned_staff < required_staff:
            # Find an available employee with the required role
            available_employee = next(
                (e for e in employees if EmployeeRole.objects.filter(employee=e, role=shift.role).exists() and calculate_cost(e, shift) < float('inf')),
                None
            )
            if available_employee:
                schedules.append(Schedule(employee=available_employee, shift=shift))
                assigned_staff += 1
            else:
                break  # No available employee found, constraint cannot be met

    # Save schedules
    Schedule.objects.bulk_create(schedules)

    # Calculate metrics
    total_satisfaction = sum(e.satisfaction_score for e in employees if any(s.employee == e for s in schedules))
    unassigned_shifts = shifts.count() - len(schedules)

    # Store scheduling result
    SchedulingResult.objects.create(
        total_satisfaction=total_satisfaction,
        unassigned_shifts=unassigned_shifts
    )

    return total_satisfaction, unassigned_shifts