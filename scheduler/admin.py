from django.contrib import admin
from .models import Employee, Shift, Schedule, SchedulingResult, EmployeeRole
from .forms import EmployeeForm, EmployeeRoleFormSet

class EmployeeRoleInline(admin.TabularInline):
    model = EmployeeRole
    formset = EmployeeRoleFormSet
    extra = 1

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    form = EmployeeForm
    inlines = [EmployeeRoleInline]
    list_display = ('name', 'employee_type', 'max_hours_per_week', 'satisfaction_score')
    list_filter = ('roles__role',)
    search_fields = ('name', 'user__username')

    def employee_type(self, obj):
        return obj.employee_type

    employee_type.short_description = 'Employee Type'

@admin.register(Shift)
class ShiftAdmin(admin.ModelAdmin):
    list_display = ('role', 'date', 'shift_time', 'start_time', 'end_time')
    list_filter = ('role', 'date', 'shift_time')
    search_fields = ('role', 'date')

@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ('employee', 'shift', 'date')
    list_filter = ('employee', 'shift__date')
    search_fields = ('employee__name', 'shift__role')

@admin.register(SchedulingResult)
class SchedulingResultAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'total_satisfaction', 'unassigned_shifts')
    list_filter = ('created_at',)
