from django.urls import path
from . import views

urlpatterns = [
    #Admin Side
    path('register_parent/', views.register_parent, name='register_parent'),
    path('login/', views.admin_login, name='admin_login'),
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin_logout/', views.admin_logout, name='admin_logout'),
    path('participant_list/', views.participant_list, name='participant_list'),
    path('<int:pk>/edit/', views.participant_update, name='participant_update'),
    path('<int:pk>/delete/', views.participant_delete, name='participant_delete'),
    path('upload_participants/', views.upload_participants, name='upload_participants'),
    
    #User Side
    path('', views.parent_login, name='parent_login'),
    path('parent_home/', views.parent_home, name='parent_home'),
    path('start-quiz/', views.start_quiz, name='start_quiz'),
    path('submit-quiz/', views.submit_quiz, name='submit_quiz'),
    path('check-time/', views.check_time, name='check_time'),
    path('show-result/', views.show_result, name='show_result'),
    path('logout/', views.custom_logout, name='logout'),    
]