from django.contrib import admin
from .models import *

class ParentRegistrationAdmin(admin.ModelAdmin):
    list_display = ('parent_name', 'student_name', 'admission_number', 'class_name', 'mobile_number')

admin.site.register(ParentRegistration, ParentRegistrationAdmin)
admin.site.register(Quiz)
admin.site.register(Question)
admin.site.register(ParentAttempt)
admin.site.register(Answer)
admin.site.register(Choice)
