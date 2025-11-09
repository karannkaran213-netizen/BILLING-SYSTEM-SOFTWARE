from django.urls import path
from . import views

urlpatterns = [
    # Admin Authentication
    path('', views.admin_login, name='admin_login'),
    path('logout/', views.admin_logout, name='admin_logout'),
    
    # Admin Dashboard
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),
    
    # Menu Management
    path('menu/', views.menu_list, name='menu_list'),
    path('menu/add/', views.menu_add, name='menu_add'),
    path('menu/edit/<int:pk>/', views.menu_edit, name='menu_edit'),
    path('menu/delete/<int:pk>/', views.menu_delete, name='menu_delete'),
    path('menu/toggle/<int:pk>/', views.menu_toggle_availability, name='menu_toggle'),
    
    # Reports
    path('reports/', views.reports_dashboard, name='reports_dashboard'),
    path('reports/graphs/', views.reports_graphs, name='reports_graphs'),
    path('reports/yearly/', views.yearly_sales_report, name='yearly_sales_report'),
    
    # Expenses Management
    path('expenses/', views.expense_list, name='expense_list'),
    path('expenses/add/', views.expense_add, name='expense_add'),
    path('expenses/edit/<int:pk>/', views.expense_edit, name='expense_edit'),
    path('expenses/delete/<int:pk>/', views.expense_delete, name='expense_delete'),
    
    # Export Reports
    path('reports/daily/<int:year>/<int:month>/<int:day>/pdf/', views.export_daily_pdf, name='export_daily_pdf'),
    path('reports/daily/<int:year>/<int:month>/<int:day>/excel/', views.export_daily_excel, name='export_daily_excel'),
    path('reports/monthly/<int:year>/<int:month>/pdf/', views.export_monthly_pdf, name='export_monthly_pdf'),
    path('reports/monthly/<int:year>/<int:month>/excel/', views.export_monthly_excel, name='export_monthly_excel'),
    path('reports/expenses/<str:start_date>/<str:end_date>/pdf/', views.export_expenses_pdf, name='export_expenses_pdf'),
    path('reports/expenses/<str:start_date>/<str:end_date>/excel/', views.export_expenses_excel, name='export_expenses_excel'),
    path('reports/profit/<str:start_date>/<str:end_date>/pdf/', views.export_profit_pdf, name='export_profit_pdf'),
    path('reports/profit/<str:start_date>/<str:end_date>/excel/', views.export_profit_excel, name='export_profit_excel'),
    path('reports/yearly/pdf/', views.export_yearly_pdf, name='export_yearly_pdf'),
    path('reports/yearly/excel/', views.export_yearly_excel, name='export_yearly_excel'),
    path('reports/daily-breakdown/pdf/', views.export_daily_breakdown_pdf, name='export_daily_breakdown_pdf'),
    path('reports/daily-breakdown/excel/', views.export_daily_breakdown_excel, name='export_daily_breakdown_excel'),
    path('reports/top-items-7days/pdf/', views.export_top_items_7days_pdf, name='export_top_items_7days_pdf'),
    path('reports/top-items-7days/excel/', views.export_top_items_7days_excel, name='export_top_items_7days_excel'),
    path('reports/top-items-6months/pdf/', views.export_top_items_6months_pdf, name='export_top_items_6months_pdf'),
    path('reports/top-items-6months/excel/', views.export_top_items_6months_excel, name='export_top_items_6months_excel'),
    path('reports/monthly-breakdown/pdf/', views.export_monthly_breakdown_pdf, name='export_monthly_breakdown_pdf'),
    path('reports/monthly-breakdown/excel/', views.export_monthly_breakdown_excel, name='export_monthly_breakdown_excel'),
]

