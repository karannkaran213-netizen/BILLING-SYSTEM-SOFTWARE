import qrcode
from io import BytesIO
from django.http import HttpResponse
from django.utils import timezone
from decimal import Decimal


def generate_qr_code(order):
    """Generate QR code for an order with bill details"""
    # Prepare QR code data
    qr_data = f"""Order Details
Order Number: {order.order_number}
Date: {order.created_at.strftime('%Y-%m-%d %H:%M:%S')}
Status: {order.status.upper()}

Items:
"""
    for item in order.order_items.all():
        qr_data += f"- {item.menu_item.name} x{item.quantity} @ ₹{item.price} = ₹{item.subtotal}\n"
    
    qr_data += f"\nTotal Amount: ₹{order.total_amount}"
    
    # Generate QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(qr_data)
    qr.make(fit=True)
    
    # Create image
    img = qr.make_image(fill_color="black", back_color="white")
    
    return img


def generate_qr_code_response(order):
    """Generate QR code as HTTP response"""
    img = generate_qr_code(order)
    
    response = HttpResponse(content_type="image/png")
    img.save(response, "PNG")
    return response


def calculate_daily_sales(date, user_date_joined=None):
    """Calculate sales for a specific date"""
    from .models import Order
    orders = Order.objects.filter(
        created_at__date=date,
        status='paid'
    )
    # Filter by user creation date if provided
    if user_date_joined:
        orders = orders.filter(created_at__gte=user_date_joined)
    total_sales = sum(order.total_amount for order in orders)
    total_orders = orders.count()
    return {
        'date': date,
        'total_sales': total_sales,
        'total_orders': total_orders,
        'orders': orders
    }


def calculate_monthly_sales(year, month, user_date_joined=None):
    """Calculate sales for a specific month"""
    from .models import Order
    orders = Order.objects.filter(
        created_at__year=year,
        created_at__month=month,
        status='paid'
    )
    # Filter by user creation date if provided
    if user_date_joined:
        orders = orders.filter(created_at__gte=user_date_joined)
    total_sales = sum(order.total_amount for order in orders)
    total_orders = orders.count()
    return {
        'year': year,
        'month': month,
        'total_sales': total_sales,
        'total_orders': total_orders,
        'orders': orders
    }


def calculate_expenses(start_date, end_date, user_date_joined=None):
    """Calculate expenses between two dates"""
    from .models import Expense
    expenses = Expense.objects.filter(date__range=[start_date, end_date])
    # Filter by user creation date if provided
    if user_date_joined:
        expenses = expenses.filter(created_at__gte=user_date_joined)
    total_expenses = sum(expense.amount for expense in expenses)
    return {
        'start_date': start_date,
        'end_date': end_date,
        'total_expenses': total_expenses,
        'expenses': expenses
    }


def calculate_profit(sales, expenses):
    """Calculate profit (sales - expenses)"""
    return sales - expenses

