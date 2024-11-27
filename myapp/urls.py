from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),  # Root URL for the homepage
    path('myapp/', views.index, name='index'),  # Duplicate homepage for testing or special case
    path('about/', views.about, name='about'),
    path('service/',views.service, name='service'),
    path('why/',views.why, name='why'),
    path('team/', views.team, name='team'),

    path('order_problem/', views.order_problem, name='order_problem'),  # Initial setup page
    path('optimal_solution/', views.optimal_solution, name='optimal_solution') , #Initial setup page
    path('order_problem/FlowShop/', views.order_problem_FS, name='order_problem_FS'),  # FlowShop-specific view
    path('process_problem/', views.process_problem, name='process_problem'),
    path('generate_sequence/', views.generate_sequence, name='generate_sequence'),
    path('evaluate_constraints/', views.evaluate_constraints, name='evaluate_constraints' ),
    path('machine_report', views.machine_report , name = 'machine_report'),
    path('job_report', views.job_report , name = 'job_report'),
    path('order_problem/FlowShop/P_matrix/', views.P_Matrix, name='P_Matrix'),
]
    