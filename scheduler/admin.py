from django.contrib import admin
from .models import Employee, Shift, Schedule, SchedulingResult, EmployeeRole, ShiftBlock
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
    filter_horizontal = ('availability', 'preferred_shifts')

    def employee_type(self, obj):
        return obj.employee_type

    employee_type.short_description = 'Employee Type'

@admin.register(Shift)
class ShiftAdmin(admin.ModelAdmin):
    list_display = ('role', 'date', 'shift_block', 'start_time', 'end_time')
    list_filter = ('role', 'date', 'shift_block')
    search_fields = ('role', 'date')

admin.site.register(Schedule)
admin.site.register(SchedulingResult)
admin.site.register(ShiftBlock)
