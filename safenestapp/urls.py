from django.urls import path
from . import views
from .views import CustomLoginView, report_missing, parent_dashboard

urlpatterns = [
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', views.custom_logout, name='logout'),
    path('parent_dashboard/', parent_dashboard, name='parent_dashboard'),
    path('report_missing/', report_missing, name='report_missing'),
    path('', views.dashboard, name='dashboard'),
    path('report-found/',views.report_found,name='report_found'),
    path('register/', views.register, name='register'),
    path('upload_found/', views.upload_found_child, name='upload_found_child'),
    path('report/<int:report_id>/', views.view_report, name='view_report'),
    path('report/<int:report_id>/edit/', views.edit_report, name='edit_report'),
    path('report/<int:report_id>/delete/', views.delete_report, name='delete_report'),
]
 