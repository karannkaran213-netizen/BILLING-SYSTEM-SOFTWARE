# Restaurant Billing System

A comprehensive restaurant billing system built with Django, featuring menu management, billing operations, QR code generation, and detailed reporting capabilities.

## Features

- **Menu Management**: CRUD operations for menu items (idly, poori, dosai, vada, and more)
- **Billing System**: Cart-based billing with add-to-cart, update quantities, remove items, and clear cart
- **Order Management**: Create orders, view bills, mark as paid, print bills
- **QR Code Generation**: Generate static QR codes with bill details for each order
- **Reports**: 
  - Daily Sales Report
  - Monthly Sales Report
  - Expenses Report
  - Profit Report (Sales - Expenses)
  - PDF and Excel export for all reports
- **Admin Interface**: Protected admin panel with username/password authentication

## Technology Stack

- **Backend**: Django 4.2.7
- **Database**: MySQL
- **Frontend**: HTML, CSS, JavaScript
- **Libraries**:
  - qrcode: QR code generation
  - reportlab: PDF generation
  - openpyxl: Excel export
  - python-decouple: Environment variable management

## Prerequisites

- Python 3.8 or higher
- MySQL Server
- pip (Python package manager)

## Installation

1. **Clone or download the project**

2. **Create a virtual environment** (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure MySQL database**:
   - Create a MySQL database:
     ```sql
     CREATE DATABASE restaurant_billing;
     ```
   - Update database credentials in `.env` file (see `.env.example`)

5. **Create `.env` file**:
   ```bash
   cp .env.example .env
   ```
   Edit `.env` and set your database credentials:
   ```
   SECRET_KEY=your-secret-key-here
   DEBUG=True
   ALLOWED_HOSTS=localhost,127.0.0.1
   DB_NAME=restaurant_billing
   DB_USER=root
   DB_PASSWORD=your_password
   DB_HOST=localhost
   DB_PORT=3306
   ```

6. **Run migrations**:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

7. **Create a superuser** (for admin access):
   ```bash
   python manage.py createsuperuser
   ```

8. **Add initial menu items** (optional):
   ```bash
   python manage.py shell
   ```
   Then run:
   ```python
   from billing_app.models import Menu
   Menu.objects.create(name='Idly', price=15.00, category='Breakfast', is_available=True)
   Menu.objects.create(name='Poori', price=30.00, category='Breakfast', is_available=True)
   Menu.objects.create(name='Dosai', price=40.00, category='Breakfast', is_available=True)
   Menu.objects.create(name='Vada', price=20.00, category='Breakfast', is_available=True)
   ```

9. **Collect static files** (for production):
   ```bash
   python manage.py collectstatic --noinput
   ```

10. **Run the development server**:
    ```bash
    python manage.py runserver
    ```

## Usage

### Admin Interface

1. Access admin panel at: `http://localhost:8000/admin/`
2. Login with your superuser credentials
3. Manage menu items, view reports, and export data

### Billing Interface

1. Access billing page at: `http://localhost:8000/billing/`
2. Click menu items to add to cart
3. Update quantities or remove items from cart
4. Create order and view bill
5. Generate QR code, print bill, or mark as paid

## URLs

- **Admin Login**: `/admin/login/`
- **Admin Dashboard**: `/admin/dashboard/`
- **Menu Management**: `/admin/menu/`
- **Reports**: `/admin/reports/`
- **Billing Interface**: `/billing/`

## Project Structure

```
restaurant_billing/
├── billing_app/          # Main application
│   ├── models.py        # Database models
│   ├── views.py         # Views and business logic
│   ├── urls.py          # Admin URLs
│   ├── billing_urls.py  # Billing URLs
│   ├── forms.py         # Forms
│   ├── utils.py         # Utility functions (QR code, reports)
│   └── admin.py         # Django admin configuration
├── restaurant_billing/   # Project settings
│   ├── settings.py      # Django settings
│   ├── urls.py          # Root URL configuration
│   └── wsgi.py          # WSGI configuration
├── templates/           # HTML templates
│   ├── admin/          # Admin templates
│   └── billing/        # Billing templates
├── static/             # Static files
│   ├── css/           # Stylesheets
│   └── js/            # JavaScript files
├── manage.py          # Django management script
└── requirements.txt   # Python dependencies
```

## Production Deployment

1. Set `DEBUG=False` in `.env`
2. Update `ALLOWED_HOSTS` with your domain
3. Set a strong `SECRET_KEY`
4. Configure static files serving (use a web server like Nginx or Apache)
5. Use a production WSGI server like Gunicorn
6. Set up proper database backups

## Environment Variables

- `SECRET_KEY`: Django secret key
- `DEBUG`: Debug mode (True/False)
- `ALLOWED_HOSTS`: Comma-separated list of allowed hosts
- `DB_NAME`: MySQL database name
- `DB_USER`: MySQL username
- `DB_PASSWORD`: MySQL password
- `DB_HOST`: MySQL host (default: localhost)
- `DB_PORT`: MySQL port (default: 3306)

## Support

For issues or questions, please refer to the Django documentation or create an issue in the project repository.

## License

This project is open source and available for use.

