from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_page, name='home'),
    path('mbti/', views.mbti_test, name='mbti_test'),
    path('holland/', views.holland_test, name='holland_test'),
    path('profile/', views.profile_page, name='profile'),
    path('recommend/', views.recommend_page, name='recommend'),
    path('game/', views.game_page, name='game'),
    path('report/', views.report_page, name='report'),
]