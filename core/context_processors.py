# context_processors.py
from course.models import QuestionPattern

def question_patterns(request):
    patterns = QuestionPattern.objects.all()[:5]
    return {
        'footer_question_patterns': patterns
    }
