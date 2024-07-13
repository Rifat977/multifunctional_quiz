from django.db import models
from django.utils.text import slugify
from django.conf import settings
from django.utils import timezone


class Course(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    status = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Course"
        verbose_name_plural = "    Courses"

class Subject(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Subject"
        verbose_name_plural = "   Subjects"

class QuestionPattern(models.Model):
    DIFFICULTY_CHOICES = [
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
    ]
    name = models.CharField(max_length=100, unique=True)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    tier = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES)
    exam_duration = models.IntegerField(default=0)  # Duration in seconds
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    total_questions_served = models.IntegerField(default=0)
    points = models.FloatField(default=1.0, verbose_name="Points for each Question")
    random_serve = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Question(models.Model):
    question_pattern = models.ForeignKey(QuestionPattern, on_delete=models.CASCADE, related_name="Question")
    question_type = models.CharField(max_length=255)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.question_pattern} - {self.question_type}"

class SingleChoiceQuestion(Question):
    question_text = models.TextField()

    def save(self, *args, **kwargs):
        self.question_type = "single_choice"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.question_text

class SingleChoiceOption(models.Model):
    question = models.ForeignKey(SingleChoiceQuestion, on_delete=models.CASCADE, related_name='options')
    option_text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.option_text

class MultipleChoiceQuestion(Question):
    question_text = models.TextField()

    def save(self, *args, **kwargs):
        self.question_type = "multiple_choice"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.question_text

class MultipleChoiceOption(models.Model):
    question = models.ForeignKey(MultipleChoiceQuestion, on_delete=models.CASCADE, related_name='options')
    option_text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.option_text

class DragAndDropQuestion(Question):
    question_text = models.TextField()
    sentence_to_complete = models.TextField()

    def save(self, *args, **kwargs):
        self.question_type = "drag_and_drop"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.question_text

class DragAndDropOption(models.Model):
    question = models.ForeignKey(DragAndDropQuestion, on_delete=models.CASCADE, related_name='options')
    option_text = models.CharField(max_length=255)
    is_correct_position = models.BooleanField(default=False)

    def __str__(self):
        return self.option_text

class DropDownQuestion(Question):
    question_text = models.TextField()

    def save(self, *args, **kwargs):
        self.question_type = "dropdown"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.question_text

class DropDownOption(models.Model):
    question = models.ForeignKey(DropDownQuestion, on_delete=models.CASCADE, related_name='options')
    option_text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.option_text

class UserAttempt(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    question_pattern = models.ForeignKey(QuestionPattern, on_delete=models.CASCADE)
    attempt_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} - {self.question_pattern.subject}"

    class Meta:
        verbose_name = "User Attempt"
        verbose_name_plural = "User Attempts"


class UserAnswer(models.Model):
    user_attempt = models.ForeignKey(UserAttempt, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_answer = models.CharField(max_length=1, null=True, blank=True)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user_attempt.user.username} - {self.question.question_pattern.subject}"