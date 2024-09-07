from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

from course.models import *
from .models import *
from django.contrib import messages

import json, random, ast
from collections import Counter

from itertools import groupby
from django.db.models import F, Count, Q

from django.core.exceptions import ValidationError
from decimal import Decimal

from django.core.mail import send_mail


# Create your views here.
def index(request):
    
    quizzes = QuestionPattern.objects.all()
    
    return render(request, 'index.html', {
        'quizzes': quizzes,
    })

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
            user_attempt = UserAttempt.objects.get(user=user, question_pattern=q_pattern)
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
                question = Question.objects.get(pk=question_id)
                questions[question_id] = question

                selected_answer = None
                if question.question_type == 'single_choice':
                    selected_answer = request.POST.get(f'option_{question_id}')
                elif question.question_type == 'multiple_choice':
                    selected_answer = request.POST.getlist(f'option_{question_id}[]')
                elif question.question_type == 'drag_and_drop':
                    selected_answer = request.POST.get(f'drag_and_drop_{question_id}')
                    selected_answer = selected_answer.split(',') if selected_answer else []
                elif question.question_type == 'dropdown':
                    selected_answer = {}
                    for item in question.dropdownquestion.dropdown_items.all():
                        selected_answer[item.id] = request.POST.get(f'dropdown_{item.id}')

                user_selected_answers[question_id] = selected_answer

                is_correct = False
                if question.question_type == 'single_choice':
                    if selected_answer:
                        correct_option = SingleChoiceQuestion.objects.get(pk=question_id).options.filter(is_correct=True).first()
                        if correct_option and selected_answer == correct_option.option_text:
                            is_correct = True
                elif question.question_type == 'multiple_choice':
                    correct_options = set(
                        MultipleChoiceQuestion.objects.get(pk=question_id).options.filter(is_correct=True).values_list('option_text', flat=True)
                    )
                    if set(selected_answer) == correct_options:
                        is_correct = True
                
                
                elif question.question_type == 'drag_and_drop':
                    # Retrieve correct options
                    correct_options = DragAndDropQuestion.objects.get(pk=question_id).options.filter(is_correct_position=True)
                    
                    # Collect correct option texts
                    correct_option_texts = [opt.option_text for opt in correct_options]

                    
                    print(f"Correct option texts: {correct_option_texts}")
                    
                    # Collect selected option texts from POST data
                    selected_option_texts = []
                    
                    for key, value in request.POST.items():
                        if key.startswith('drag_and_drop_'):
                            question_number = key.split('_')[-1]
                            if int(question_number) == int(question_id):
                                try:
                                    selected_option_ids = json.loads(value)
                                    
                                    for opt_id in selected_option_ids:
                                        opt_id = int(opt_id)
                                        option = get_object_or_404(DragAndDropOption, pk=opt_id)
                                        selected_option_texts.append(option.option_text)
                                        
                                except (ValueError, json.JSONDecodeError) as e:
                                    print(f"Error processing drag and drop answers for key '{key}': {e}")
                    
                    print(f"Selected option texts: {selected_option_texts}")
                    
                    # Compare selected option texts with correct option texts
                    # Assuming order does not matter
                    is_correct = sorted(selected_option_texts) == sorted(correct_option_texts)
                    
                    if is_correct:
                        print("The selected answers are correct.")
                    else:
                        print("The selected answers are incorrect.")


                        
                elif question.question_type == 'dropdown':
                    correct = True
                    for item_id, selected_opt in selected_answer.items():
                        try:
                            correct_option = DropDownOption.objects.get(dropdown_item__id=item_id, is_correct=True)
                            if selected_opt != correct_option.option_text:
                                correct = False
                                break
                        except DropDownOption.DoesNotExist:
                            correct = False
                            break
                    is_correct = correct

                if is_correct:
                    if not UserAnswer.objects.filter(user_attempt=user_attempt, question=question, is_correct=True).exists():
                        score = question.question_pattern.points
                        total_score += score
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
    user_attempt = get_object_or_404(UserAttempt, pk=user_attempt_id, user=request.user)
    user_answers = UserAnswer.objects.filter(user_attempt=user_attempt)

    total_correct_answers = 0
    total_skipped_answers = 0
    total_wrong_answers = 0
    total_points = 0

    course_name = user_attempt.question_pattern.subject.course.name
    subject_name = user_attempt.question_pattern.subject.name
    course_tier = user_attempt.question_pattern.tier
    points_for_each = user_attempt.question_pattern.points

    drop_down_options = {}
    drag_and_drop_options = {}

    for user_answer in user_answers:
        question = user_answer.question
        is_correct = False

        if question.question_type == 'single_choice':
            correct_option = SingleChoiceQuestion.objects.get(pk=question.pk).options.filter(is_correct=True).first()
            is_correct = correct_option and user_answer.selected_answer == correct_option.option_text

        elif question.question_type == 'multiple_choice':
            # Fetch correct options and convert to a list
            correct_options = list(MultipleChoiceQuestion.objects.get(pk=question.pk)
                                .options.filter(is_correct=True)
                                .values_list('option_text', flat=True))
            
            # Convert `selected_answers` to a list if it is not already
            if isinstance(user_answer.selected_answer, str):
                try:
                    # Safely evaluate string to list
                    selected_answers = ast.literal_eval(user_answer.selected_answer)
                    if not isinstance(selected_answers, list):
                        selected_answers = []
                except (ValueError, SyntaxError):
                    selected_answers = []
            elif isinstance(user_answer.selected_answer, list):
                selected_answers = user_answer.selected_answer
            else:
                # Handle other cases, possibly converting to an empty list
                selected_answers = []

            # Use Counter to count occurrences and compare
            correct_options_counter = Counter(correct_options)
            selected_answers_counter = Counter(selected_answers)

            # Check if both Counters are equal
            is_correct = correct_options_counter == selected_answers_counter
            
            print(selected_answers, correct_options)
            print(is_correct)





        elif question.question_type == 'drag_and_drop':
            selected_option_ids = ast.literal_eval(user_answer.selected_answer) if isinstance(user_answer.selected_answer, str) else user_answer.selected_answer
            question_instance = DragAndDropQuestion.objects.get(pk=question.pk)
            drag_and_drop_options[question.pk] = question_instance.options.all()

            correct_options = question_instance.options.filter(is_correct_position=True)

            cleaned_ids = []
            for opt_id in selected_option_ids:
                cleaned_id = opt_id.strip('[]')
                cleaned_ids.extend(map(int, cleaned_id.split(',')))


            selected_option_texts = []
            for opt_id in cleaned_ids:
                try:
                    option = DragAndDropOption.objects.get(pk=opt_id)
                    selected_option_texts.append(option.option_text)
                except DragAndDropOption.DoesNotExist:
                    print(f"Option with ID {opt_id} does not exist.")


            correct_option_texts = [opt.option_text for opt in correct_options]
            is_correct = selected_option_texts == correct_option_texts

        elif question.question_type == 'dropdown':
            selected_answers = ast.literal_eval(user_answer.selected_answer) if isinstance(user_answer.selected_answer, str) else user_answer.selected_answer
            question_instance = DropDownQuestion.objects.get(pk=question.pk)
            drop_down_items = DropDownItem.objects.filter(question=question_instance)
            options = DropDownOption.objects.filter(dropdown_item__in=drop_down_items)

            # Structuring the dictionary to have dropdown items and their options
            # drop_down_options[question.pk] = {}
            # for item in drop_down_items:
            #     item_options = options.filter(dropdown_item=item)
            #     drop_down_options[question.pk][item.id] = {option.id: option.option_text for option in item_options}

            drop_down_options[question.pk] = {}
            for item in drop_down_items:
                item_options = options.filter(dropdown_item=item)
                
                drop_down_options[question.pk][item.id] = {
                    option.id: {
                        'option_text': option.option_text,
                        'is_correct': option.is_correct
                    }
                    for option in item_options
                }


            correct = True
            for item_id, selected_opt in selected_answers.items():
                try:
                    correct_option = DropDownOption.objects.get(dropdown_item__id=item_id, is_correct=True)
                    if selected_opt != correct_option.option_text:
                        correct = False
                        break
                except DropDownOption.DoesNotExist:
                    correct = False
                    break
            is_correct = correct

        if is_correct:
            total_correct_answers += 1
            total_points += points_for_each
        # elif not user_answer.selected_answer:
        #     total_skipped_answers += 1
        else:
            total_wrong_answers += 1

    context = {
        'user_attempt': user_attempt,
        'user_answers': user_answers,
        'total_correct_answers': total_correct_answers,
        'total_skipped_answers': total_skipped_answers,
        'total_wrong_answers': total_wrong_answers,
        'total_points': total_points,
        'course_name': course_name,
        'subject_name': subject_name,
        'course_tier': course_tier,
        'points_for_each': points_for_each,
        'drop_down_options': drop_down_options,
        'drag_and_drop_options': drag_and_drop_options,
    }

    return render(request, 'user/attempt_answer.html', context)

    
@login_required
def wallet(request):
    user = request.user
    per_point = get_object_or_404(PointSetting)
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

def about(request):
    return render(request, 'about.html')