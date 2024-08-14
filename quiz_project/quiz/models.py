from django.db import models
from django.utils import timezone

class ParentRegistration(models.Model):
    CLASS_CHOICES = [
        ('LZQ', 'LZQ'),
        ('MZQ', 'MZQ'),
        ('UZQ', 'UZQ'),
    ]
    
    parent_name = models.CharField(max_length=100)
    student_name = models.CharField(max_length=100)
    admission_number = models.CharField(max_length=20, unique=True)
    class_name = models.CharField(max_length=3, choices=CLASS_CHOICES)
    mobile_number = models.CharField(max_length=15)
    score = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.parent_name} - {self.student_name}"

class Quiz(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()

    def __str__(self):
        return self.title

class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    text = models.TextField()

    def __str__(self):
        return self.text

class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    text = models.CharField(max_length=200)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.text

class ParentAttempt(models.Model):
    parent = models.ForeignKey(ParentRegistration, on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    start_time = models.DateTimeField(default=timezone.now)
    is_completed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.parent} - {self.quiz}"

class Answer(models.Model):
    attempt = models.ForeignKey(ParentAttempt, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_choice = models.ForeignKey(Choice, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.attempt} - {self.question}"

