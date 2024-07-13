from django.contrib import admin
from .models import Course, Subject, QuestionPattern, SingleChoiceQuestion, SingleChoiceOption, \
                    MultipleChoiceQuestion, MultipleChoiceOption, \
                    DragAndDropQuestion, DragAndDropOption, \
                    DropDownQuestion, DropDownOption

class SingleChoiceOptionInline(admin.TabularInline):
    model = SingleChoiceOption
    extra = 3  

class SingleChoiceQuestionAdmin(admin.ModelAdmin):
    inlines = [SingleChoiceOptionInline]
    list_display = ('question_text', 'question_pattern',)  
    list_filter = ('question_pattern',)  
    search_fields = ('question_text',)  

class MultipleChoiceOptionInline(admin.TabularInline):
    model = MultipleChoiceOption
    extra = 3  

class MultipleChoiceQuestionAdmin(admin.ModelAdmin):
    inlines = [MultipleChoiceOptionInline]
    list_display = ('question_text', 'question_pattern',)  
    list_filter = ('question_pattern',)  
    search_fields = ('question_text',)  

class DragAndDropOptionInline(admin.TabularInline):
    model = DragAndDropOption
    extra = 3  

class DragAndDropQuestionAdmin(admin.ModelAdmin):
    inlines = [DragAndDropOptionInline]
    list_display = ('question_text', 'sentence_to_complete' ,'question_pattern',)  
    list_filter = ('question_pattern',)  
    search_fields = ('question_text',)  

class DropDownOptionInline(admin.TabularInline):
    model = DropDownOption
    extra = 3  

class DropDownQuestionAdmin(admin.ModelAdmin):
    inlines = [DropDownOptionInline]
    list_display = ('question_text', 'question_pattern',)  
    list_filter = ('question_pattern',)  
    search_fields = ('question_text',)  

class QuestionInline(admin.TabularInline):
    model = SingleChoiceQuestion  
    extra = 0  

class QuestionPatternAdmin(admin.ModelAdmin):
    inlines = [QuestionInline]
    list_display = ('name', 'subject', 'tier', 'is_active', 'total_questions_served',)  # Replace with actual fields
    list_filter = ('subject',)  # Assuming these are fields on QuestionPattern
    search_fields = ('pattern_name',)  

# Registering models with their respective admin classes
admin.site.register(Course)
admin.site.register(Subject)
admin.site.register(QuestionPattern, QuestionPatternAdmin)
admin.site.register(SingleChoiceQuestion, SingleChoiceQuestionAdmin)
admin.site.register(MultipleChoiceQuestion, MultipleChoiceQuestionAdmin)
admin.site.register(DragAndDropQuestion, DragAndDropQuestionAdmin)
admin.site.register(DropDownQuestion, DropDownQuestionAdmin)
