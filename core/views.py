from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from course.models import *
from .models import *
from django.contrib import messages

import json, random

from itertools import groupby
from django.db.models import F, Count, Q

from django.core.exceptions import ValidationError
from decimal import Decimal

from django.core.mail import send_mail


# Create your views here.
def index(request):
    return render(request, 'index.html')

def policy(request):
    return render(request, 'policy.html')

def feedback(request):
    return render(request, 'feedback.html')

def contact(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')

        if name and email and message:
            send_mail(
                'New Contact Us Form Submission',
                f'Name: {name}\nEmail: {email}\nMessage: {message}',
                settings.EMAIL_HOST_USER,
                ['support@entrancequiz.com'],
                fail_silently=False,
            )
        return redirect('core:contact')
    return render(request, 'contact.html')

@login_required
def home(request):
    user = request.user
    user_course = request.user.course

    f_quizzes = QuestionPattern.objects.all()

    f_quizzes_grouped_by_subject = {}
    for subject, quizzes_in_subject in groupby(f_quizzes, lambda quiz: quiz.subject):
        f_quizzes_grouped_by_subject[subject] = list(quizzes_in_subject)


    notification = Notification.objects.filter(is_active=True).first()

    attempt_ids = {}
    f_participation_status = {}
    is_all_correct = {}

    for quizzes_in_subject in f_quizzes_grouped_by_subject.values():
        for quiz in quizzes_in_subject:
            attempt = UserAttempt.objects.filter(user=user, question_pattern=quiz).first()
            if attempt:
                f_participation_status[quiz.id] = True
                attempt_ids[quiz.id] = attempt.id
                is_all_correct[quiz.id] = attempt.is_correct
            else:
                f_participation_status[quiz.id] = False

    return render(request, 'user/home.html', {
        'f_quizzes_grouped_by_subject': f_quizzes_grouped_by_subject,
        'f_participation_status': f_participation_status,
        'notification': notification,
        'attempt_ids': attempt_ids,
        'is_all_correct' : is_all_correct
    })

@login_required
def quizes(request):
    user = request.user
    user_course = request.user.course
    quizzes = QuestionPattern.objects.all()
    
    participation_status = {}
    attempt_ids = {}
    is_all_correct = {}

    for quiz in quizzes:
        attempt = UserAttempt.objects.filter(user=user, question_pattern=quiz).first()
        if attempt:
            participation_status[quiz.id] = True
            attempt_ids[quiz.id] = attempt.id
            is_all_correct[quiz.id] = attempt.is_correct
        else:
            participation_status[quiz.id] = False


    return render(request, 'user/quizes.html', {
        'quizzes': quizzes, 'participation_status': participation_status,
        'attempt_ids': attempt_ids,
        'is_all_correct': is_all_correct
        }
    )

# @login_required
# def quiz(request):
#     if request.method == 'POST':
#         user = request.user
#         q_pattern_id = request.POST.get('quiz')
#         q_pattern = QuestionPattern.objects.get(pk=q_pattern_id)

#         user_attempt = UserAttempt.objects.get_or_create(user=user, question_pattern=q_pattern)
#         atm = UserAttempt.objects.get(user=user, question_pattern=q_pattern)
#         if q_pattern.random_serve:
#             questions = Question.objects.filter(question_pattern=q_pattern)
#             total_questions_served = min(q_pattern.total_questions_served, questions.count())
#             questions = random.sample(list(questions), total_questions_served)
#         else:
#             questions = Question.objects.filter(question_pattern=q_pattern).order_by('id')[:q_pattern.total_questions_served]

#         return render(request, 'user/quiz_test.html', {'q_pattern': q_pattern, 'questions': questions, 'user_attempt':atm})
#     return redirect("core:home")

@login_required
def quiz(request):
    if request.method == 'POST':
        user = request.user
        q_pattern_id = request.POST.get('quiz')
        q_pattern = QuestionPattern.objects.get(pk=q_pattern_id)

        user_attempt, created = UserAttempt.objects.get_or_create(user=user, question_pattern=q_pattern)

        if q_pattern.random_serve:
            questions = Question.objects.filter(question_pattern=q_pattern)
            total_questions_served = min(q_pattern.total_questions_served, questions.count())
            questions = random.sample(list(questions), total_questions_served)
        else:
            questions = Question.objects.filter(question_pattern=q_pattern).order_by('id')[:q_pattern.total_questions_served]

        context = {
            'q_pattern': q_pattern,
            'questions': questions,
            'user_attempt': user_attempt,
        }
        return render(request, 'user/quiz_test.html', context)

    return redirect("core:home")


@login_required
def submit_answer(request):
    if request.method == 'POST':
        user = request.user
        total_score = 0
        user_selected_answers = {}
        questions = {} 

        q_pattern_id = request.POST.get('q_pattern')
        q_pattern = QuestionPattern.objects.get(pk=q_pattern_id)
        try:
            user_attempt = UserAttempt.objects.get(user=user, question=q_pattern)
            user_attempt.attempt_count += 1
            user_attempt.save()
        except UserAttempt.DoesNotExist:
                messages.error(request, "Something went wrong!")
                return redirect("core:home")

        correct_answers_count = 0
        total_questions_count = 0 

        for key, value in request.POST.items():
            if key.startswith('question_'):
                question_id = int(value)
                selected_answer = request.POST.get('customRadio_' + str(question_id))

                user_selected_answers[question_id] = selected_answer 
                question = Question.objects.get(pk=question_id)
                questions[question_id] = question 

                if selected_answer == question.correct_answer:
                    if not UserAnswer.objects.filter(user_attempt=user_attempt, question=question, is_correct=True).exists():
                        score = question.pattern.points
                        total_score += score
                        is_correct = True
                        correct_answers_count += 1
                    else:
                        is_correct = True
                        correct_answers_count += 1
                else:
                    is_correct = False

                UserAnswer.objects.update_or_create(
                    user_attempt=user_attempt,
                    question=question,
                    defaults={
                        'selected_answer': selected_answer,
                        'is_correct': is_correct
                    }
                )

                total_questions_count += 1

        user.point = F('point') + total_score
        user.save()

        if correct_answers_count == total_questions_count:
            user_attempt.is_correct = True
            user_attempt.save()

        return redirect('core:attempt_answer', user_attempt_id=user_attempt.id)

    return redirect("core:home")

@login_required
def show_user_answers(request, user_attempt_id):
    user_attempt = UserAttempt.objects.get(pk=user_attempt_id, user=request.user)
    user_answers = UserAnswer.objects.filter(user_attempt=user_attempt)

    total_correct_answers = 0
    total_skipped_answers = 0
    total_wrong_answers = 0
    total_points = 0

    course_name = user_attempt.question_pattern.subject.course.name
    subject_name = user_attempt.question_pattern.subject.name
    course_tier = user_attempt.question_pattern.tier
    points_for_each = user_attempt.question_pattern.points

    for user_answer in user_answers:
        if user_answer.selected_answer == user_answer.question.correct_answer:
            total_correct_answers += 1
            total_points += user_answer.question.pattern.points
        elif not user_answer.selected_answer:
            total_skipped_answers += 1
        else:
            total_wrong_answers += 1

    context = {
        'user_attempt' : user_attempt,
        'user_answers': user_answers,
        'total_correct_answers': total_correct_answers,
        'total_skipped_answers': total_skipped_answers,
        'total_wrong_answers': total_wrong_answers,
        'total_points': total_points,
        'course_name': course_name,
        'subject_name': subject_name,
        'course_tier': course_tier,
        'points_for_each': points_for_each
    }

    return render(request, 'user/attempt_answer.html', context)



@login_required
def wallet(request):
    user = request.user
    per_point = PointSetting.objects.first()
    total_amount = per_point.per_point * user.point
    withdrawals = Withdrawal.objects.filter(user=user).order_by('-id')

    context = {
        'per_point': per_point,
        'user': user,
        'total_amount': total_amount,
        'withdrawals': withdrawals
    }
    return render(request, 'user/wallet.html', context)


@login_required
def withdrawal(request):
    if request.method == 'POST':
        user = request.user
        amount = request.POST.get('amount')
        wallet_address = request.POST.get('wallet_address')
        network = request.POST.get('network')

        point_setting = PointSetting.objects.first()
        per_point = point_setting.per_point
        user_balance = per_point * user.point


        if not amount or not wallet_address or not network:
            messages.error(request, "Input fields must be required")
            return redirect('core:wallet')

        if int(amount) > user_balance:
            messages.error(request, "Insuficcent balance.")
            return redirect('core:wallet')

        if int(amount) < point_setting.min_withdrawal:
            messages.error(request, f"Minimum withdrawal amount {point_setting.min_withdrawal} {point_setting.currency}.")
            return redirect('core:wallet')

        else:
            point_setting = PointSetting.objects.first()
            per_point = point_setting.per_point
            user.point = Decimal(user.point) - Decimal(amount) / Decimal(per_point)
            if user.point >= 0:
                user.save()

                withdrawal = Withdrawal(user=user, amount=amount, wallet_address=wallet_address, payment_method=network)
                withdrawal.save()
            else:
                messages.error(request, "Something went wrong.")

        return redirect('core:wallet')


def quiz_test(request):
    return render(request, 'user/quiz_test.html')