from django.urls import path

from authentication import views

app_name = 'authentication'
urlpatterns = [
    path('sign_up/', views.RegistrationAPIView.as_view()),
    path('log_in/', views.LogInAPIView.as_view()),
    path('profile/', views.ProfileAPIView.as_view()),
    path('all_users/', views.AllUsersAPIView.as_view()),
]
