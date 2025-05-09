from django.urls import path
from . import views

app_name = 'main_app'
urlpatterns = [
    path('', views.home, name='home'),
    path('expense/delete/<int:pk>/', views.delete_expense, name='delete_expense'),
    path('expense/edit/<int:pk>/', views.edit_expense, name='edit_expense'),
    path('expense/report/', views.filtered_report, name='report'),
]
