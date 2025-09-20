# management/commands/create_demo_data.py
"""
Create professional demo data for client presentation.
Place this file in: artworks/management/commands/create_demo_data.py
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
import random

from artworks.models import Category, Artwork, ArtworkImage
from accounts.models import CustomerProfile, ArtistProfile
from orders.models import Order, OrderItem
from subscriptions.models import Subscription
from cart.models import Cart, CartItem

User = get_user_model()

class Command(BaseCommand):
    help = 'Creates professional demo data for client presentation'

    def handle(self, *args, **options):
        self.stdout.write('Creating demo data...')
        
        # Clear existing demo data (optional)
        if options.get('clear', False):
            self.clear_demo_data()
        
        # Create categories
        categories = self.create_categories()
        
        # Create users
        admin = self.create_admin_user()
        artists = self.create_demo_artists()
        customers = self.create_demo_customers()
        
        # Create artworks
        artworks = self.create_demo_artworks(artists, categories)
        
        # Create sample orders
        self.create_demo_orders(customers, artworks)
        
        # Create some cart items for demo
        self.create_demo_carts(customers, artworks)
        
        self.stdout.write(self.style.SUCCESS('✅ Demo data created successfully!'))
        self.print_credentials()
    
    def clear_demo_data(self):
        """Optional: Clear existing data"""
        self.stdout.write('Clearing existing data...')
        User.objects.filter(email__contains='demo@').delete()
        Category.objects.all().delete()
        
    def create_categories(self):
        """Create artwork categories"""
        categories_data = [
            ('landscapes', 'Landscapes', 'Beautiful Jersey landscapes and seascapes'),
            ('portraits', 'Portraits', 'Portrait artworks and commissions'),
            ('abstract', 'Abstract', 'Modern abstract artwork'),
            ('wildlife', 'Wildlife', 'Local wildlife and nature'),
            ('heritage', 'Heritage', 'Jersey heritage and culture'),
            ('prints', 'Prints', 'High-quality art prints'),
        ]
        
        categories = []
        for slug, name, desc in categories_data:
            cat, _ = Category.objects.get_or_create(
                slug=slug,
                defaults={'name': name, 'description': desc}
            )
            categories.append(cat)
            
        self.stdout.write(f'Created {len(categories)} categories')
        return categories
    
    def create_admin_user(self):
        """Create admin superuser"""
        admin, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@demo.com',
                'first_name': 'Admin',
                'last_name': 'User',
                'is_staff': True,
                'is_superuser': True,
                'email_verified': True,
            }
        )
        if created:
            admin.set_password('AdminPass123!')
            admin.save()
            self.stdout.write('Created admin user')
        return admin
    
    def create_demo_artists(self):
        """Create demo artist accounts"""
        artists_data = [
            {
                'username': 'sarah_artist',
                'email': 'demo@artist.com',
                'first_name': 'Sarah',
                'last_name': 'Mitchell',
                'password': 'DemoPass123!',
                'display_name': 'Sarah Mitchell Art',
                'bio': 'Jersey-based artist specializing in coastal landscapes and seascapes. Inspired by the island\'s natural beauty.',
                'website': 'https://sarahmitchell.art',
                'instagram': '@sarahmitchellart',
            },
            {
                'username': 'james_creative',
                'email': 'james@demo.com',
                'first_name': 'James',
                'last_name': 'Thompson',
                'password': 'DemoPass123!',
                'display_name': 'Thompson Studio',
                'bio': 'Contemporary artist exploring Jersey\'s heritage through mixed media. Commission work available.',
                'website': 'https://thompsonstudio.je',
                'instagram': '@thompson_studio',
            },
            {
                'username': 'emma_paints',
                'email': 'emma@demo.com',
                'first_name': 'Emma',
                'last_name': 'Roberts',
                'password': 'DemoPass123!',
                'display_name': 'Emma Roberts Gallery',
                'bio': 'Wildlife and nature artist. Capturing Jersey\'s diverse flora and fauna in watercolor and oils.',
                'instagram': '@emmarobertsart',
            },
        ]
        
        artists = []
        for data in artists_data:
            user, created = User.objects.get_or_create(
                username=data['username'],
                defaults={
                    'email': data['email'],
                    'first_name': data['first_name'],
                    'last_name': data['last_name'],
                    'user_type': 'artist',
                    'email_verified': True,  # Auto-verified for demo
                }
            )
            if created:
                user.set_password(data['password'])
                user.save()
                
                # Create artist profile
                ArtistProfile.objects.create(
                    user=user,
                    display_name=data['display_name'],
                    bio=data['bio'],
                    website=data.get('website', ''),
                    instagram_handle=data.get('instagram', ''),
                    is_approved=True,  # Pre-approved for demo
                    commission_rate=Decimal('10.00'),
                    business_name=f"{data['display_name']} Ltd",
                    phone_number='+44 7700 900000',
                    studio_address='St. Helier, Jersey'
                )
                
                # Create subscription for artist
                if settings.DEMO_MODE:
                    Subscription.objects.create(
                        user=user,
                        status='active',
                        monthly_price=Decimal('15.00'),
                        trial_end=timezone.now() + timedelta(days=30),
                        current_period_end=timezone.now() + timedelta(days=30),
                        next_billing_date=timezone.now() + timedelta(days=30)
                    )
                
                self.stdout.write(f'Created artist: {user.username}')
            
            artists.append(user)
        
        return artists
    
    def create_demo_customers(self):
        """Create demo customer accounts"""
        customers_data = [
            {
                'username': 'john_customer',
                'email': 'demo@customer.com',
                'first_name': 'John',
                'last_name': 'Smith',
                'password': 'DemoPass123!',
            },
            {
                'username': 'mary_buyer',
                'email': 'mary@demo.com',
                'first_name': 'Mary',
                'last_name': 'Jones',
                'password': 'DemoPass123!',
            },
        ]
        
        customers = []
        for data in customers_data:
            user, created = User.objects.get_or_create(
                username=data['username'],
                defaults={
                    'email': data['email'],
                    'first_name': data['first_name'],
                    'last_name': data['last_name'],
                    'user_type': 'customer',
                    'email_verified': True,
                }
            )
            if created:
                user.set_password(data['password'])
                user.save()
                
                # Create customer profile
                CustomerProfile.objects.create(
                    user=user,
                    address_line_1='123 King Street',
                    parish='st_helier',
                    postcode='JE2 3AB',
                    marketing_consent=True
                )
                
                self.stdout.write(f'Created customer: {user.username}')
            
            customers.append(user)
        
        return customers
    
    def create_demo_artworks(self, artists, categories):
        """Create impressive demo artworks"""
        artworks_data = [
            # Sarah's artworks (landscapes/seascapes)
            {
                'artist_index': 0,
                'title': 'Sunset at St. Brelade\'s Bay',
                'description': 'A stunning capture of the golden sunset over St. Brelade\'s Bay, showcasing the vibrant colors of a Jersey evening.',
                'category': 'landscapes',
                'price': Decimal('450.00'),
                'artwork_type': 'original',
                'materials': 'Oil on canvas',
                'height': 60, 'width': 80,
                'year_created': 2024,
                'featured': True,
                'jersey_heritage': True,
            },
            {
                'artist_index': 0,
                'title': 'Corbière Lighthouse Morning',
                'description': 'The iconic Corbière Lighthouse bathed in morning light, with waves gently breaking on the causeway.',
                'category': 'landscapes',
                'price': Decimal('350.00'),
                'artwork_type': 'print',
                'stock_quantity': 25,
                'materials': 'Giclée print on archival paper',
                'height': 40, 'width': 60,
                'featured': True,
                'jersey_heritage': True,
            },
            # James's artworks (heritage/abstract)
            {
                'artist_index': 1,
                'title': 'Mont Orgueil Abstract',
                'description': 'A modern interpretation of Jersey\'s historic Mont Orgueil Castle, blending traditional and contemporary elements.',
                'category': 'abstract',
                'price': Decimal('650.00'),
                'artwork_type': 'original',
                'materials': 'Mixed media on board',
                'height': 100, 'width': 70,
                'year_created': 2024,
                'featured': True,
                'jersey_heritage': True,
            },
            {
                'artist_index': 1,
                'title': 'Jersey Lily Series #3',
                'description': 'Part of the Jersey Lily series, celebrating the island\'s famous daughter, Lillie Langtry.',
                'category': 'heritage',
                'price': Decimal('280.00'),
                'artwork_type': 'print',
                'stock_quantity': 30,
                'materials': 'Limited edition screen print',
                'height': 50, 'width': 40,
            },
            # Emma's artworks (wildlife/nature)
            {
                'artist_index': 2,
                'title': 'Puffins at Les Écréhous',
                'description': 'Delightful watercolor depicting puffins on the reef of Les Écréhous, capturing their playful nature.',
                'category': 'wildlife',
                'price': Decimal('320.00'),
                'artwork_type': 'original',
                'materials': 'Watercolor on paper',
                'height': 30, 'width': 40,
                'year_created': 2023,
                'featured': True,
            },
            {
                'artist_index': 2,
                'title': 'Jersey Orchid Study',
                'description': 'Botanical illustration of the rare Jersey Orchid, found in the island\'s sand dunes.',
                'category': 'wildlife',
                'price': Decimal('180.00'),
                'artwork_type': 'print',
                'stock_quantity': 50,
                'materials': 'Fine art print',
                'height': 30, 'width': 25,
                'jersey_heritage': True,
            },
            # Additional artworks for variety
            {
                'artist_index': 0,
                'title': 'St. Aubin\'s Harbour',
                'description': 'Traditional view of St. Aubin\'s Harbour with boats at rest during low tide.',
                'category': 'landscapes',
                'price': Decimal('380.00'),
                'artwork_type': 'original',
                'materials': 'Acrylic on canvas',
                'height': 50, 'width': 70,
            },
            {
                'artist_index': 1,
                'title': 'Liberation Day Celebration',
                'description': 'Commemorative piece celebrating Jersey\'s Liberation Day, May 9th.',
                'category': 'heritage',
                'price': Decimal('550.00'),
                'artwork_type': 'original',
                'materials': 'Oil and gold leaf on canvas',
                'height': 80, 'width': 60,
                'jersey_heritage': True,
            },
        ]
        
        artworks = []
        for data in artworks_data:
            artist = artists[data['artist_index']]
            category = next((c for c in categories if c.slug == data['category']), categories[0])
            
            artwork, created = Artwork.objects.get_or_create(
                title=data['title'],
                artist=artist,
                defaults={
                    'description': data['description'],
                    'category': category,
                    'price': data['price'],
                    'artwork_type': data.get('artwork_type', 'original'),
                    'materials': data.get('materials', ''),
                    'height': data.get('height'),
                    'width': data.get('width'),
                    'year_created': data.get('year_created'),
                    'status': 'active',  # All active for demo
                    'is_available': True,
                    'stock_quantity': data.get('stock_quantity', 1),
                    'featured': data.get('featured', False),
                    'jersey_heritage': data.get('jersey_heritage', False),
                    'is_local_artist': True,
                }
            )
            
            if created:
                # Note: You'll need to add placeholder images manually
                # or create a command to copy them from a demo_images folder
                self.stdout.write(f'Created artwork: {artwork.title}')
            
            artworks.append(artwork)
        
        return artworks
    
    def create_demo_orders(self, customers, artworks):
        """Create sample completed orders"""
        # Create a few completed orders to show in dashboards
        if customers and artworks:
            # Order 1: Recent successful order
            order1 = Order.objects.create(
                user=customers[0],
                email=customers[0].email,
                phone='+44 7700 900123',
                delivery_first_name=customers[0].first_name,
                delivery_last_name=customers[0].last_name,
                delivery_address_line_1='45 Queen Street',
                delivery_parish='st_helier',
                delivery_postcode='JE2 4WQ',
                status='delivered',
                subtotal=Decimal('450.00'),
                shipping_cost=Decimal('0.00'),
                total=Decimal('450.00'),
                is_paid=True,
                paid_at=timezone.now() - timedelta(days=3),
                delivered_at=timezone.now() - timedelta(days=1),
            )
            
            OrderItem.objects.create(
                order=order1,
                artwork=artworks[0] if artworks else None,
                artwork_title=artworks[0].title if artworks else 'Sample Artwork',
                artwork_artist=str(artworks[0].artist.get_full_name()) if artworks else 'Demo Artist',
                quantity=1,
                price=Decimal('450.00'),
                total=Decimal('450.00')
            )
            
            self.stdout.write('Created demo orders')
    
    def create_demo_carts(self, customers, artworks):
        """Add items to customer carts for demo"""
        if customers and len(artworks) > 2:
            # Add items to first customer's cart
            cart, _ = Cart.objects.get_or_create(
                user=customers[0],
                is_active=True
            )
            
            # Add a couple items
            CartItem.objects.get_or_create(
                cart=cart,
                artwork=artworks[2],
                defaults={
                    'quantity': 1,
                    'price_at_time': artworks[2].price
                }
            )
            
            self.stdout.write('Created demo cart items')
    
    def print_credentials(self):
        """Print login credentials for demo"""
        self.stdout.write('\n' + '='*50)
        self.stdout.write(self.style.SUCCESS('DEMO CREDENTIALS'))
        self.stdout.write('='*50)
        self.stdout.write('\nAdmin Panel:')
        self.stdout.write('  Username: admin')
        self.stdout.write('  Password: AdminPass123!')
        self.stdout.write('\nArtist Account:')
        self.stdout.write('  Email: demo@artist.com')
        self.stdout.write('  Password: DemoPass123!')
        self.stdout.write('\nCustomer Account:')
        self.stdout.write('  Email: demo@customer.com')
        self.stdout.write('  Password: DemoPass123!')
        self.stdout.write('='*50 + '\n')