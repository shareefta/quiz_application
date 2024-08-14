from django.shortcuts import render, redirect, HttpResponse, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import *
from django.contrib import messages
from django.http import JsonResponse
from django.urls import reverse
from .models import Quiz, Question, ParentAttempt, Answer, ParentRegistration
from .forms import QuizForm
import datetime
from django.contrib.auth import authenticate, login, logout
from functools import wraps
from django.views.decorators.cache import never_cache
from datetime import timedelta
from django.core.paginator import Paginator
import pandas as pd
from datetime import datetime, time
from django.utils import timezone
import pytz


def parent_login_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.session.get('parent_id') is None:
            return redirect(f"{reverse('parent_login')}?next={request.path}")
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def admin_login(request):
    if request.method == 'POST':
        form = AdminLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('admin_dashboard')
    else:
        form = AdminLoginForm()
    return render(request, 'admin/admin_login.html', {'form': form})

@never_cache
@login_required
def admin_dashboard(request):
    return render(request, 'admin/admin_dashboard.html')

@never_cache
@login_required
def register_parent(request):
    if request.method == 'POST':
        form = ParentRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponse('Successfully Registered')  # Redirect to a success page or any other page
    else:
        form = ParentRegistrationForm()
    
    return render(request, 'register_parent.html', {'form': form})

@never_cache
@login_required
def participant_list(request):
    class_name = request.GET.get('class_name')
    
    if class_name:
        participants = ParentRegistration.objects.filter(class_name=class_name).order_by('-score','id')
    else:
        participants = ParentRegistration.objects.all().order_by('-score', 'id')

    classes = ParentRegistration.objects.values_list('class_name', flat=True).distinct()

    paginator = Paginator(participants, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'admin/parent_list.html', {
        'page_obj': page_obj,
        'class_name': class_name,
        'classes': classes
    })

@never_cache
@login_required
def participant_update(request, pk):
    participant = get_object_or_404(ParentRegistration, pk=pk)
    if request.method == 'POST':
        form = ParentRegistrationForm(request.POST, instance=participant)
        if form.is_valid():
            form.save()
            return redirect('participant_list')
    else:
        form = ParentRegistrationForm(instance=participant)
    return render(request, 'register_parent.html', {'form': form})

@never_cache
@login_required
def participant_delete(request, pk):
    participant = get_object_or_404(ParentRegistration, pk=pk)
    if request.method == 'POST':
        participant.delete()
        return redirect('participant_list')
    return render(request, 'admin/delete_participant.html', {'participant': participant})

@never_cache
@login_required
def upload_participants(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['file']
            if file.name.endswith('.xlsx') or file.name.endswith('.xls'):
                try:
                    # Read the Excel file
                    df = pd.read_excel(file)
                    print('File read successfully')
                    print(df.head())  # Print the first few rows for debugging
                    
                    df.columns = [col.strip().lower() for col in df.columns]

                    # Process the file and save to the database
                    for index, row in df.iterrows():
                        # Create or update delegate
                        participant_data = {
                            'parent_name': row.get('parent_name'),
                            'student_name': row.get('student_name'),
                            'admission_number': row.get('admission_number'),
                            'class_name': row.get('class_name'),
                            'mobile_number': row.get('mobile_number'),
                        }

                        form = ParentRegistrationForm(data=participant_data)
                        if form.is_valid():
                            form.save()
                            print(f'Form saved: {participant_data["mobile_number"]}')
                        else:
                            print(f'Form errors for row {index + 1}: {form.errors}')
                            messages.error(request, f"Error with row {index + 1}: {form.errors}")

                    messages.success(request, 'Participants uploaded successfully.')
                    print('Upload completed')
                    return redirect('participant_list')
                except Exception as e:
                    print(f'Error processing file: {e}')
                    messages.error(request, f'Error processing file: {e}')
            else:
                messages.error(request, 'Please upload an Excel file.')
        else:
            print('Form is not valid')
            print(form.errors)  # Print form errors for debugging
    else:
        form = UploadFileForm()

    return render(request, 'admin/upload_parents.html', {'form': form})

@never_cache
@login_required
def admin_logout(request):
    logout(request)
    return redirect('admin_login')

def parent_login(request):
    next_url = request.GET.get('next')  # Get the 'next' parameter

    if request.method == 'POST':
        form = ParentLoginForm(request.POST)
        if form.is_valid():
            admission_number = form.cleaned_data['admission_number']
            mobile_number = form.cleaned_data['mobile_number']
            try:
                parent = ParentRegistration.objects.get(admission_number=admission_number, mobile_number=mobile_number)
                request.session['parent_id'] = parent.id  # Saving parent id in session
                request.session['student_name'] = parent.student_name
                request.session['class_name'] = parent.class_name
                
                messages.success(request, f"Welcome, {parent.student_name}!")
        
                if next_url:  # If there's a next URL, redirect to it
                    return redirect(next_url)
                else:  # Otherwise, redirect to the home page
                    return redirect('parent_home')
            except ParentRegistration.DoesNotExist:
                messages.error(request, 'Admission Number not found. Please check and try again.')
        else:
            messages.error(request, 'Invalid form submission.')
    else:
        form = ParentLoginForm()

    return render(request, 'parent_login.html', {'form': form})

@never_cache
@parent_login_required
def parent_home(request):
    parent_id = request.session.get('parent_id')
    if not parent_id:
        return redirect('parent_login')
    
    parent = ParentRegistration.objects.get(id=parent_id)
    quiz = Quiz.objects.first()  # Get the first quiz, or filter based on need

    # Get or create ParentAttempt
    attempt = ParentAttempt.objects.filter(parent_id=parent_id, quiz=quiz).first()

    context = {
        'parent': parent,
        'quiz': quiz,
        'attempt': attempt
    }

    return render(request, 'home.html', context)

local_tz = pytz.timezone('Asia/Kolkata')

# Convert UTC time to local time
def convert_to_local(utc_dt):
    return utc_dt.astimezone(local_tz)

# Current UTC time
now_utc = timezone.now()
# Scheduled start time in UTC
scheduled_start_time_utc = timezone.make_aware(datetime.combine(timezone.now().date(), time(20, 30)))

# Convert to local time
now_local = convert_to_local(now_utc)
scheduled_start_time_local = convert_to_local(scheduled_start_time_utc)

print(f"Current Time: {now_local}")
print(f"Quiz Time: {scheduled_start_time_local}")

@never_cache
@parent_login_required
def start_quiz(request):
    parent_id = request.session.get('parent_id')
    if not parent_id:
        return redirect('parent_login')

    quiz = Quiz.objects.first()  # Assuming there's one quiz
    attempt = ParentAttempt.objects.filter(parent_id=parent_id, quiz=quiz).first()
    
    now = timezone.localtime(timezone.now())  # Convert to local timezone
    scheduled_start_time = timezone.localtime(timezone.make_aware(datetime.combine(timezone.now().date(), time(20, 30))))

    if now < scheduled_start_time:
        remaining_time = (scheduled_start_time - now).total_seconds()
    else:
        remaining_time = 0

    return render(request, 'admin/countdown.html', {
        'remaining_time': remaining_time,
        'scheduled_start_time': scheduled_start_time
    })       

    if attempt:
        # Check if the quiz is completed
        if attempt.is_completed:
            messages.success(request, 'You have already submitted the quiz.')
            return redirect('parent_home')

        # Check if time has expired and submit the quiz if needed
        if timezone.now() > attempt.start_time + timedelta(seconds=600):
            attempt.is_completed = True
            attempt.save()
            messages.success(request, 'Time is up! Your quiz has been submitted automatically.')
            return redirect('parent_home')
    else:
        # If no attempt exists, create a new one
        attempt = ParentAttempt.objects.create(
            parent_id=parent_id,
            quiz=quiz,
            start_time=timezone.now()
        )

    questions = list(quiz.question_set.all())

    if request.method == 'POST':
        for question in questions:
            form = QuizForm(request.POST, question=question)
            if form.is_valid():
                selected_choice_id = form.cleaned_data.get(f'question_{question.id}')
                if selected_choice_id:
                    selected_choice = Choice.objects.get(id=selected_choice_id)
                    Answer.objects.update_or_create(
                        attempt=attempt,
                        question=question,
                        defaults={'selected_choice': selected_choice}
                    )
        return redirect('submit_quiz')
    else:
        forms = [QuizForm(question=question) for question in questions]

    return render(request, 'start_quiz.html', {
        'forms': forms,
        'quiz': quiz,
        'total_questions': len(questions),
    })

@never_cache
@parent_login_required
def submit_quiz(request):
    parent_id = request.session.get('parent_id')
    quiz = Quiz.objects.first()  # or fetch the relevant quiz
    attempt = ParentAttempt.objects.filter(parent_id=parent_id, quiz=quiz).first()
    parent = ParentRegistration.objects.get(id=parent_id)    

    if attempt and not attempt.is_completed:
        attempt.is_completed = True
        attempt.save()
        
        correct_answers = Answer.objects.filter(
            attempt=attempt,
            selected_choice__in=Choice.objects.filter(is_correct=True)
        ).count()

        parent.score = correct_answers
        parent.save()
        print(parent.score)

    messages.success(request, 'Successfully submitted')
    return redirect('parent_home')

@never_cache
@parent_login_required
def check_time(request):
    parent_id = request.session.get('parent_id')
    quiz = Quiz.objects.first()
    attempt = ParentAttempt.objects.filter(parent_id=parent_id, quiz=quiz).first()
    time_limit = datetime.timedelta(minutes=10)  # Set your time limit

    if timezone.now() > (attempt.start_time + time_limit):
        return JsonResponse({'submit': True})
    return JsonResponse({'submit': False})

@never_cache
@parent_login_required
def show_result(request):
    parent_id = request.session.get('parent_id')
    quiz = Quiz.objects.first()  # Adjust if necessary to fetch the correct quiz
    attempt = ParentAttempt.objects.filter(parent_id=parent_id, quiz=quiz).first()

    if not attempt or not attempt.is_completed:
        return redirect('parent_home')

    total_questions = quiz.question_set.count()
    sumbitted_questions = Answer.objects.filter(attempt=attempt).count()
    correct_answers = Answer.objects.filter(
        attempt=attempt,
        selected_choice__in=Choice.objects.filter(is_correct=True)
    ).count()

    return render(request, 'result.html', {
        'total_questions': total_questions,
        'submitted_questions' : sumbitted_questions,
        'correct_answers': correct_answers,
        'score': correct_answers,
    })

@never_cache
@parent_login_required
def custom_logout(request):
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('parent_login')