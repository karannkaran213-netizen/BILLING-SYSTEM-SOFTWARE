from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import datetime, timedelta, date
from decimal import Decimal
import json
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side

from .models import Menu, Order, OrderItem, Expense
from .forms import MenuForm, ExpenseForm
from .utils import (
    generate_qr_code_response,
    calculate_daily_sales,
    calculate_monthly_sales,
    calculate_expenses,
    calculate_profit
)


# Admin Authentication Views
def admin_login(request):
    """Admin login page"""
    if request.user.is_authenticated:
        return redirect('admin_dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('admin_dashboard')
        else:
            messages.error(request, 'Invalid username or password')
    
    return render(request, 'admin/login.html')


@login_required
def admin_dashboard(request):
    """Admin dashboard"""
    today = timezone.now().date()
    
    # Today's statistics
    today_orders = Order.objects.filter(created_at__date=today)
    today_sales = sum(order.total_amount for order in today_orders.filter(status='paid'))
    today_total_orders = today_orders.count()
    
    # Total menu items
    total_menu_items = Menu.objects.count()
    available_items = Menu.objects.filter(is_available=True).count()
    
    context = {
        'today_sales': today_sales,
        'today_total_orders': today_total_orders,
        'total_menu_items': total_menu_items,
        'available_items': available_items,
    }
    
    return render(request, 'admin/dashboard.html', context)


# Menu Management Views
@login_required
def menu_list(request):
    """List all menu items"""
    menu_items = Menu.objects.all()
    return render(request, 'admin/menu_list.html', {'menu_items': menu_items})


@login_required
def menu_add(request):
    """Add new menu item"""
    if request.method == 'POST':
        form = MenuForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Menu item added successfully!')
            return redirect('menu_list')
    else:
        form = MenuForm()
    
    return render(request, 'admin/menu_form.html', {'form': form, 'action': 'Add'})


@login_required
def menu_edit(request, pk):
    """Edit menu item"""
    menu_item = get_object_or_404(Menu, pk=pk)
    
    if request.method == 'POST':
        form = MenuForm(request.POST, instance=menu_item)
        if form.is_valid():
            form.save()
            messages.success(request, 'Menu item updated successfully!')
            return redirect('menu_list')
    else:
        form = MenuForm(instance=menu_item)
    
    return render(request, 'admin/menu_form.html', {'form': form, 'menu_item': menu_item, 'action': 'Edit'})


@login_required
def menu_delete(request, pk):
    """Delete menu item"""
    menu_item = get_object_or_404(Menu, pk=pk)
    
    if request.method == 'POST':
        menu_item.delete()
        messages.success(request, 'Menu item deleted successfully!')
        return redirect('menu_list')
    
    return render(request, 'admin/menu_delete.html', {'menu_item': menu_item})


@login_required
def menu_toggle_availability(request, pk):
    """Toggle menu item availability"""
    menu_item = get_object_or_404(Menu, pk=pk)
    menu_item.is_available = not menu_item.is_available
    menu_item.save()
    
    status = 'available' if menu_item.is_available else 'unavailable'
    messages.success(request, f'Menu item marked as {status}!')
    return redirect('menu_list')


# Reports Views
@login_required
def reports_dashboard(request):
    """Reports dashboard"""
    today = timezone.now().date()
    current_month = timezone.now().month
    current_year = timezone.now().year
    
    # Daily sales
    daily_sales = calculate_daily_sales(today)
    
    # Monthly sales
    monthly_sales = calculate_monthly_sales(current_year, current_month)
    
    # Current month expenses
    month_start = datetime(current_year, current_month, 1).date()
    month_expenses = calculate_expenses(month_start, today)
    
    # Profit calculation
    profit = calculate_profit(monthly_sales['total_sales'], month_expenses['total_expenses'])
    
    context = {
        'daily_sales': daily_sales,
        'monthly_sales': monthly_sales,
        'expenses': month_expenses,
        'profit': profit,
        'today': today,
        'current_month': current_month,
        'current_year': current_year,
    }
    
    return render(request, 'admin/reports.html', context)


# Expenses Management Views
@login_required
def expense_list(request):
    """List and filter expenses"""
    expenses = Expense.objects.all()
    return render(request, 'admin/expense_list.html', {'expenses': expenses})


@login_required
def expense_add(request):
    """Add new expense"""
    if request.method == 'POST':
        form = ExpenseForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Expense added successfully!')
            return redirect('expense_list')
    else:
        form = ExpenseForm()
    return render(request, 'admin/expense_form.html', {'form': form, 'action': 'Add'})


@login_required
def expense_edit(request, pk):
    """Edit expense"""
    expense = get_object_or_404(Expense, pk=pk)
    if request.method == 'POST':
        form = ExpenseForm(request.POST, instance=expense)
        if form.is_valid():
            form.save()
            messages.success(request, 'Expense updated successfully!')
            return redirect('expense_list')
    else:
        form = ExpenseForm(instance=expense)
    return render(request, 'admin/expense_form.html', {'form': form, 'action': 'Edit', 'expense': expense})


@login_required
def expense_delete(request, pk):
    """Delete expense"""
    expense = get_object_or_404(Expense, pk=pk)
    if request.method == 'POST':
        expense.delete()
        messages.success(request, 'Expense deleted successfully!')
        return redirect('expense_list')
    return render(request, 'admin/expense_delete.html', {'expense': expense})


# Billing Interface Views
def billing_index(request):
    """Public billing interface"""
    menu_items = Menu.objects.filter(is_available=True)
    return render(request, 'billing/index.html', {'menu_items': menu_items})


def add_to_cart(request):
    """Add item to cart via AJAX"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            menu_item_id = data.get('menu_item_id')
            
            menu_item = get_object_or_404(Menu, pk=menu_item_id, is_available=True)
            
            # Get or create cart from session
            cart = request.session.get('cart', {})
            item_key = str(menu_item_id)
            
            if item_key in cart:
                cart[item_key]['quantity'] += 1
            else:
                cart[item_key] = {
                    'id': menu_item.id,
                    'name': menu_item.name,
                    'price': str(menu_item.price),
                    'quantity': 1,
                }
            
            request.session['cart'] = cart
            request.session.modified = True
            
            return JsonResponse({
                'success': True,
                'message': f'{menu_item.name} added to cart',
                'cart_count': sum(item['quantity'] for item in cart.values())
            })
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    return JsonResponse({'success': False, 'message': 'Invalid request'})


def get_cart(request):
    """Get cart contents via AJAX"""
    cart = request.session.get('cart', {})
    total = sum(Decimal(item['price']) * item['quantity'] for item in cart.values())
    
    return JsonResponse({
        'cart': list(cart.values()),
        'total': str(total),
        'cart_count': sum(item['quantity'] for item in cart.values())
    })


def update_cart_item(request):
    """Update cart item quantity via AJAX"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            menu_item_id = str(data.get('menu_item_id'))
            quantity = int(data.get('quantity', 1))
            
            cart = request.session.get('cart', {})
            
            if menu_item_id in cart:
                if quantity <= 0:
                    del cart[menu_item_id]
                else:
                    cart[menu_item_id]['quantity'] = quantity
                
                request.session['cart'] = cart
                request.session.modified = True
                
                total = sum(Decimal(item['price']) * item['quantity'] for item in cart.values())
                
                return JsonResponse({
                    'success': True,
                    'cart_count': sum(item['quantity'] for item in cart.values()),
                    'total': str(total)
                })
            else:
                return JsonResponse({'success': False, 'message': 'Item not found in cart'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    return JsonResponse({'success': False, 'message': 'Invalid request'})


def remove_from_cart(request):
    """Remove item from cart via AJAX"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            menu_item_id = str(data.get('menu_item_id'))
            
            cart = request.session.get('cart', {})
            
            if menu_item_id in cart:
                del cart[menu_item_id]
                request.session['cart'] = cart
                request.session.modified = True
                
                total = sum(Decimal(item['price']) * item['quantity'] for item in cart.values())
                
                return JsonResponse({
                    'success': True,
                    'cart_count': sum(item['quantity'] for item in cart.values()),
                    'total': str(total)
                })
            else:
                return JsonResponse({'success': False, 'message': 'Item not found in cart'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    return JsonResponse({'success': False, 'message': 'Invalid request'})


def clear_cart(request):
    """Clear entire cart"""
    request.session['cart'] = {}
    request.session.modified = True
    return JsonResponse({'success': True, 'message': 'Cart cleared'})


def create_order(request):
    """Create order from cart"""
    if request.method == 'POST':
        try:
            cart = request.session.get('cart', {})
            
            if not cart:
                return JsonResponse({'success': False, 'message': 'Cart is empty'})
            
            # Calculate total
            total_amount = sum(Decimal(item['price']) * item['quantity'] for item in cart.values())
            
            # Create order
            order = Order.objects.create(total_amount=total_amount, status='pending')
            
            # Create order items
            for item in cart.values():
                menu_item = Menu.objects.get(pk=item['id'])
                OrderItem.objects.create(
                    order=order,
                    menu_item=menu_item,
                    quantity=item['quantity'],
                    price=Decimal(item['price'])
                )
            
            # Clear cart
            request.session['cart'] = {}
            request.session.modified = True
            
            return JsonResponse({
                'success': True,
                'order_id': order.id,
                'order_number': order.order_number,
                'message': 'Order created successfully!'
            })
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    return JsonResponse({'success': False, 'message': 'Invalid request'})


def view_bill(request, order_id):
    """View bill for an order"""
    order = get_object_or_404(Order, pk=order_id)
    return render(request, 'billing/bill.html', {'order': order})


def pay_now(request, order_id):
    """Mark order as paid"""
    if request.method == 'POST':
        order = get_object_or_404(Order, pk=order_id)
        order.status = 'paid'
        order.save()
        return JsonResponse({'success': True, 'message': 'Order marked as paid!'})
    
    return JsonResponse({'success': False, 'message': 'Invalid request'})


def generate_qr(request, order_id):
    """Generate QR code for an order"""
    order = get_object_or_404(Order, pk=order_id)
    return generate_qr_code_response(order)


# Export Views
@login_required
def export_daily_pdf(request, year, month, day):
    """Export daily sales report as PDF"""
    from datetime import date
    report_date = date(int(year), int(month), int(day))
    daily_sales = calculate_daily_sales(report_date)
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="daily_sales_{report_date}.pdf"'
    
    doc = SimpleDocTemplate(response, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()
    
    # Title
    title = Paragraph(f"Daily Sales Report - {report_date}", styles['Title'])
    elements.append(title)
    elements.append(Spacer(1, 0.3*inch))
    
    # Summary
    data = [
        ['Date', str(report_date)],
        ['Total Sales', f"₹{daily_sales['total_sales']:.2f}"],
        ['Total Orders', str(daily_sales['total_orders'])],
    ]
    
    table = Table(data, colWidths=[2*inch, 4*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.grey),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('BACKGROUND', (1, 0), (1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 0.5*inch))
    
    # Orders table
    if daily_sales['orders']:
        elements.append(Paragraph("Orders", styles['Heading2']))
        order_data = [['Order Number', 'Amount', 'Status', 'Time']]
        for order in daily_sales['orders']:
            order_data.append([
                order.order_number,
                f"₹{order.total_amount:.2f}",
                order.status,
                order.created_at.strftime('%H:%M:%S')
            ])
        
        order_table = Table(order_data, colWidths=[2*inch, 1.5*inch, 1*inch, 1.5*inch])
        order_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        elements.append(order_table)
    
    doc.build(elements)
    return response


@login_required
def export_daily_excel(request, year, month, day):
    """Export daily sales report as Excel"""
    report_date = date(int(year), int(month), int(day))
    daily_sales = calculate_daily_sales(report_date)
    
    wb = Workbook()
    ws = wb.active
    ws.title = f"Daily Sales {report_date}"
    
    # Header
    ws['A1'] = f"Daily Sales Report - {report_date}"
    ws['A1'].font = Font(size=16, bold=True)
    ws.merge_cells('A1:D1')
    
    # Summary
    ws['A3'] = 'Date'
    ws['B3'] = str(report_date)
    ws['A4'] = 'Total Sales'
    ws['B4'] = f"₹{daily_sales['total_sales']:.2f}"
    ws['A5'] = 'Total Orders'
    ws['B5'] = daily_sales['total_orders']
    
    # Orders table
    if daily_sales['orders']:
        ws['A7'] = 'Order Number'
        ws['B7'] = 'Amount'
        ws['C7'] = 'Status'
        ws['D7'] = 'Time'
        
        for i, order in enumerate(daily_sales['orders'], start=8):
            ws[f'A{i}'] = order.order_number
            ws[f'B{i}'] = f"${order.total_amount:.2f}"
            ws[f'C{i}'] = order.status
            ws[f'D{i}'] = order.created_at.strftime('%H:%M:%S')
    
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="daily_sales_{report_date}.xlsx"'
    wb.save(response)
    return response


@login_required
def export_monthly_pdf(request, year, month):
    """Export monthly sales report as PDF"""
    monthly_sales = calculate_monthly_sales(int(year), int(month))
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="monthly_sales_{year}_{month}.pdf"'
    
    doc = SimpleDocTemplate(response, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()
    
    # Title
    title = Paragraph(f"Monthly Sales Report - {month}/{year}", styles['Title'])
    elements.append(title)
    elements.append(Spacer(1, 0.3*inch))
    
    # Summary
    data = [
        ['Month', f"{month}/{year}"],
        ['Total Sales', f"₹{monthly_sales['total_sales']:.2f}"],
        ['Total Orders', str(monthly_sales['total_orders'])],
    ]
    
    table = Table(data, colWidths=[2*inch, 4*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.grey),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('BACKGROUND', (1, 0), (1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    elements.append(table)
    
    doc.build(elements)
    return response


@login_required
def export_monthly_excel(request, year, month):
    """Export monthly sales report as Excel"""
    monthly_sales = calculate_monthly_sales(int(year), int(month))
    
    wb = Workbook()
    ws = wb.active
    ws.title = f"Monthly Sales {month}/{year}"
    
    # Header
    ws['A1'] = f"Monthly Sales Report - {month}/{year}"
    ws['A1'].font = Font(size=16, bold=True)
    ws.merge_cells('A1:D1')
    
    # Summary
    ws['A3'] = 'Month'
    ws['B3'] = f"{month}/{year}"
    ws['A4'] = 'Total Sales'
    ws['B4'] = f"₹{monthly_sales['total_sales']:.2f}"
    ws['A5'] = 'Total Orders'
    ws['B5'] = monthly_sales['total_orders']
    
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="monthly_sales_{year}_{month}.xlsx"'
    wb.save(response)
    return response


@login_required
def export_expenses_pdf(request, start_date, end_date):
    """Export expenses report as PDF"""
    expenses_data = calculate_expenses(start_date, end_date)
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="expenses_{start_date}_{end_date}.pdf"'
    
    doc = SimpleDocTemplate(response, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()
    
    # Title
    title = Paragraph(f"Expenses Report - {start_date} to {end_date}", styles['Title'])
    elements.append(title)
    elements.append(Spacer(1, 0.3*inch))
    
    # Summary
    data = [
        ['Period', f"{start_date} to {end_date}"],
        ['Total Expenses', f"₹{expenses_data['total_expenses']:.2f}"],
    ]
    
    table = Table(data, colWidths=[2*inch, 4*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.grey),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('BACKGROUND', (1, 0), (1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 0.5*inch))
    
    # Expenses table
    if expenses_data['expenses']:
        elements.append(Paragraph("Expenses", styles['Heading2']))
        expense_data = [['Date', 'Description', 'Category', 'Amount']]
        for expense in expenses_data['expenses']:
            expense_data.append([
                str(expense.date),
                expense.description,
                expense.get_category_display(),
                f"₹{expense.amount:.2f}"
            ])
        
        expense_table = Table(expense_data, colWidths=[1.5*inch, 2.5*inch, 1.5*inch, 1*inch])
        expense_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        elements.append(expense_table)
    
    doc.build(elements)
    return response


@login_required
def export_expenses_excel(request, start_date, end_date):
    """Export expenses report as Excel"""
    expenses_data = calculate_expenses(start_date, end_date)
    
    wb = Workbook()
    ws = wb.active
    ws.title = "Expenses"
    
    # Header
    ws['A1'] = f"Expenses Report - {start_date} to {end_date}"
    ws['A1'].font = Font(size=16, bold=True)
    ws.merge_cells('A1:D1')
    
    # Summary
    ws['A3'] = 'Period'
    ws['B3'] = f"{start_date} to {end_date}"
    ws['A4'] = 'Total Expenses'
    ws['B4'] = f"₹{expenses_data['total_expenses']:.2f}"
    
    # Expenses table
    if expenses_data['expenses']:
        ws['A6'] = 'Date'
        ws['B6'] = 'Description'
        ws['C6'] = 'Category'
        ws['D6'] = 'Amount'
        
        for i, expense in enumerate(expenses_data['expenses'], start=7):
            ws[f'A{i}'] = str(expense.date)
            ws[f'B{i}'] = expense.description
            ws[f'C{i}'] = expense.get_category_display()
            ws[f'D{i}'] = f"₹{expense.amount:.2f}"
    
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="expenses_{start_date}_{end_date}.xlsx"'
    wb.save(response)
    return response


@login_required
def export_profit_pdf(request, start_date, end_date):
    """Export profit report as PDF"""
    monthly_sales = calculate_monthly_sales(timezone.now().year, timezone.now().month)
    expenses_data = calculate_expenses(start_date, end_date)
    profit = calculate_profit(monthly_sales['total_sales'], expenses_data['total_expenses'])
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="profit_{start_date}_{end_date}.pdf"'
    
    doc = SimpleDocTemplate(response, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()
    
    # Title
    title = Paragraph(f"Profit Report - {start_date} to {end_date}", styles['Title'])
    elements.append(title)
    elements.append(Spacer(1, 0.3*inch))
    
    # Summary
    data = [
        ['Period', f"{start_date} to {end_date}"],
        ['Total Sales', f"₹{monthly_sales['total_sales']:.2f}"],
        ['Total Expenses', f"₹{expenses_data['total_expenses']:.2f}"],
        ['Profit', f"₹{profit:.2f}"],
    ]
    
    table = Table(data, colWidths=[2*inch, 4*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.grey),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('BACKGROUND', (1, 0), (1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BACKGROUND', (1, 3), (1, 3), colors.lightgreen if profit > 0 else colors.lightcoral),
    ]))
    elements.append(table)
    
    doc.build(elements)
    return response


@login_required
def export_profit_excel(request, start_date, end_date):
    """Export profit report as Excel"""
    monthly_sales = calculate_monthly_sales(timezone.now().year, timezone.now().month)
    expenses_data = calculate_expenses(start_date, end_date)
    profit = calculate_profit(monthly_sales['total_sales'], expenses_data['total_expenses'])
    
    wb = Workbook()
    ws = wb.active
    ws.title = "Profit"
    
    # Header
    ws['A1'] = f"Profit Report - {start_date} to {end_date}"
    ws['A1'].font = Font(size=16, bold=True)
    ws.merge_cells('A1:B1')
    
    # Summary
    ws['A3'] = 'Period'
    ws['B3'] = f"{start_date} to {end_date}"
    ws['A4'] = 'Total Sales'
    ws['B4'] = f"₹{monthly_sales['total_sales']:.2f}"
    ws['A5'] = 'Total Expenses'
    ws['B5'] = f"₹{expenses_data['total_expenses']:.2f}"
    ws['A6'] = 'Profit'
    ws['B6'] = f"₹{profit:.2f}"
    ws['B6'].font = Font(size=14, bold=True, color='00FF00' if profit > 0 else 'FF0000')
    
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="profit_{start_date}_{end_date}.xlsx"'
    wb.save(response)
    return response
