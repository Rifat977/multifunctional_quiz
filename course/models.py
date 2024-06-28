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
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Subject"
        verbose_name_plural = "   Subjects"

class QuestionPattern(models.Model):
    TIER_CHOICES = [
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
    ]

    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    tier = models.CharField(max_length=10, choices=TIER_CHOICES)
    pattern =models.CharField(max_length=32, null=True, blank=True)
    exam_duration = models.PositiveIntegerField(default=30)
    points = models.FloatField(default=1.0, verbose_name="Points for each Question")
    random_serve = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    total_questions_served = models.PositiveIntegerField(default=0, verbose_name="Total Questions Served")

    def __str__(self):
        return f"{self.pattern} | {self.subject.name} |  {self.subject.course.name} | {self.get_tier_display()}"

    @property
    def points_label(self):
        return "Points"

    class Meta:
        verbose_name = "Question Pattern"
        verbose_name_plural = "  Question Patterns"

class Question(models.Model):
    pattern = models.ForeignKey(QuestionPattern, on_delete=models.CASCADE)
    text = models.TextField()
    option_a = models.CharField(max_length=255, blank=True, null=True)
    option_b = models.CharField(max_length=255, blank=True, null=True)
    option_c = models.CharField(max_length=255, blank=True, null=True)
    option_d = models.CharField(max_length=255, blank=True, null=True)
    correct_answer = models.CharField(max_length=1, choices=[('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D')])
    visit_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.text[:50]

    class Meta:
        verbose_name = "Question"
        verbose_name_plural = " Questions"

class UserAttempt(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    question = models.ForeignKey(QuestionPattern, on_delete=models.CASCADE)
    attempt_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} - {self.question.subject}"

    class Meta:
        verbose_name = "User Attempt"
        verbose_name_plural = "User Attempts"

class UserAnswer(models.Model):
    user_attempt = models.ForeignKey(UserAttempt, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_answer = models.CharField(max_length=1, null=True, blank=True)
    is_correct = models.BooleanField(default=False)