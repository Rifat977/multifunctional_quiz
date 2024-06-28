from django.contrib import admin
from .models import *

# Register your models here.
class CourseDisplay(admin.ModelAdmin):
    list_display = ('name','slug', 'status')
    search_fields  = ('name','slug', 'status')


class SubjectDisplay(admin.ModelAdmin):
    list_display = ('name', 'course', 'is_active')
    search_fields = ('course', 'name')
    list_filter = ('course__name', 'name')
    ordering = ('-id',) 


admin.site.register(Course, CourseDisplay)

admin.site.register(Subject, SubjectDisplay)

admin.site.register(QuestionPattern)

admin.site.register(Question)

admin.site.register(UserAttempt)

admin.site.register(UserAnswer)


# class QuestionDisplay(admin.ModelAdmin):
#     list_display = ('subject', 'tier', 'shortened_text', 'correct_answer')
#     search_fields = ('subject__name', 'tier', 'text', 'correct_answer')
#     list_filter = ('subject__name',)
#     ordering = ('-id',)

#     def shortened_text(self, obj):
#         return obj.text[:30] + '...' if len(obj.text) > 30 else obj.text

#     shortened_text.short_description = 'Text'

# admin.site.register(Question, QuestionDisplay)