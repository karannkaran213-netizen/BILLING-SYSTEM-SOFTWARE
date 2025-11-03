from django.core.management.base import BaseCommand
from billing_app.models import Menu


class Command(BaseCommand):
    help = 'Seed initial menu items'

    def handle(self, *args, **options):
        menu_items = [
            {'name': 'Idly', 'price': 15.00, 'category': 'Breakfast', 'description': 'Soft and fluffy idly served with sambar and chutney'},
            {'name': 'Poori', 'price': 30.00, 'category': 'Breakfast', 'description': 'Crispy poori with potato curry'},
            {'name': 'Dosai', 'price': 40.00, 'category': 'Breakfast', 'description': 'Crispy dosai with sambar and chutney'},
            {'name': 'Vada', 'price': 20.00, 'category': 'Breakfast', 'description': 'Crispy vada with sambar and chutney'},
        ]
        
        created_count = 0
        for item_data in menu_items:
            menu_item, created = Menu.objects.get_or_create(
                name=item_data['name'],
                defaults={
                    'price': item_data['price'],
                    'category': item_data['category'],
                    'description': item_data['description'],
                    'is_available': True
                }
            )
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'Created menu item: {menu_item.name}'))
            else:
                self.stdout.write(self.style.WARNING(f'Menu item already exists: {menu_item.name}'))
        
        self.stdout.write(self.style.SUCCESS(f'\nSuccessfully created {created_count} new menu items!'))

