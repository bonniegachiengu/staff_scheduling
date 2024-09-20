from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone

class EmployeeType(models.TextChoices):
    CREW = 'CREW', 'Crew'
    DRIVER = 'DRIVER', 'Driver'
    MANAGEMENT = 'MANAGEMENT', 'Management'

class Role(models.TextChoices):
    COOK = 'COOK', 'Cook'
    CASHIER = 'CASHIER', 'Cashier'
    DISPATCH = 'DISPATCH', 'Dispatch'
    SANDWICH = 'SANDWICH', 'Sandwich'
    DRIVER = 'DRIVER', 'Driver'
    RESTAURANT_MANAGER = 'RESTAURANT_MANAGER', 'Restaurant Manager'
    SHIFT_SUPERVISOR = 'SHIFT_SUPERVISOR', 'Shift Supervisor'
    ASSISTANT_MANAGER = 'ASSISTANT_MANAGER', 'Assistant Manager'

    @classmethod
    def get_type(cls, role):
        crew_roles = [cls.COOK, cls.CASHIER, cls.DISPATCH, cls.SANDWICH]
        management_roles = [cls.RESTAURANT_MANAGER, cls.SHIFT_SUPERVISOR, cls.ASSISTANT_MANAGER]
        
        if role in crew_roles:
            return EmployeeType.CREW
        elif role == cls.DRIVER:
            return EmployeeType.DRIVER
        elif role in management_roles:
            return EmployeeType.MANAGEMENT
        else:
            raise ValueError(f"Unknown role: {role}")

class ShiftTime(models.TextChoices):
    MORNING = 'MORNING', '9AM to 6PM'
    AFTERNOON = 'AFTERNOON', '12PM to 9PM'
    EVENING = 'EVENING', '3PM to 12AM'
    NIGHT = 'NIGHT', '6PM to 3AM'
    LATE_NIGHT = 'LATE_NIGHT', '9PM to 6AM'
    EARLY_MORNING = 'EARLY_MORNING', '12AM to 9AM'

class Employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100)
    max_hours_per_week = models.IntegerField(default=48, validators=[MinValueValidator(0), MaxValueValidator(168)])
    availability = models.JSONField(default=dict)
    preferred_shifts = models.JSONField(default=dict)
    satisfaction_score = models.FloatField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])

    def __str__(self):
        return self.name

    @property
    def employee_type(self):
        roles = self.roles.all()
        if not roles:
            return None
        return Role.get_type(roles.first().role)

class EmployeeRole(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='roles')
    role = models.CharField(max_length=50, choices=Role.choices)
    rating = models.IntegerField(choices=[(i, f"{i} Star{'s' if i > 1 else ''}") for i in range(1, 6)],
                                 validators=[MinValueValidator(1), MaxValueValidator(5)])

    class Meta:
        unique_together = ('employee', 'role')

    def __str__(self):
        return f"{self.employee.name} - {self.get_role_display()} ({self.rating} Stars)"

class Shift(models.Model):
    role = models.CharField(max_length=50, choices=Role.choices)
    date = models.DateField()
    shift_time = models.CharField(max_length=20, choices=ShiftTime.choices, default=ShiftTime.MORNING)

    def __str__(self):
        return f"{self.get_role_display()} - {self.date} ({self.get_shift_time_display()})"

    @property
    def start_time(self):
        return self.get_shift_times()[0]

    @property
    def end_time(self):
        return self.get_shift_times()[1]

    def get_shift_times(self):
        shift_times = {
            ShiftTime.MORNING: (timezone.time(9, 0), timezone.time(18, 0)),
            ShiftTime.AFTERNOON: (timezone.time(12, 0), timezone.time(21, 0)),
            ShiftTime.EVENING: (timezone.time(15, 0), timezone.time(0, 0)),
            ShiftTime.NIGHT: (timezone.time(18, 0), timezone.time(3, 0)),
            ShiftTime.LATE_NIGHT: (timezone.time(21, 0), timezone.time(6, 0)),
            ShiftTime.EARLY_MORNING: (timezone.time(0, 0), timezone.time(9, 0)),
        }
        return shift_times[self.shift_time]

class Schedule(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    shift = models.ForeignKey(Shift, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.employee.name} - {self.shift}"

class SchedulingResult(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    total_satisfaction = models.FloatField()
    unassigned_shifts = models.IntegerField()

    def __str__(self):
        return f"Scheduling Result {self.created_at}"
