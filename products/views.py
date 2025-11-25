from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from django.conf import settings
from .models import Product, Category, HomePage, OrderInquiry


def home(request):
    """Home page view with editable content"""
    # Handle case where migrations haven't run yet
    try:
        homepage = HomePage.objects.filter(is_active=True).first()
    except Exception:
        homepage = None
    
    # Get featured products (best sellers or newest) - show all products if none in stock
    try:
        featured_products = Product.objects.all().order_by('-review_count', '-rating', '-created_at')[:8]
    except Exception:
        featured_products = []
    
    # Get all categories
    try:
        categories = Category.objects.all()[:6]
    except Exception:
        categories = []
    
    context = {
        'homepage': homepage,
        'featured_products': featured_products,
        'categories': categories,
    }
    
    return render(request, 'products/home.html', context)


def product_list(request):
    """Product listing page with filtering and sorting"""
    # Handle case where migrations haven't run yet
    try:
        products = Product.objects.all().select_related('category')
    except Exception:
        products = Product.objects.none()
    
    # Only filter by in_stock if explicitly requested
    in_stock_filter = request.GET.get('in_stock', '')
    if in_stock_filter == 'true' and products.exists():
        try:
            products = products.filter(in_stock=True)
        except Exception:
            pass
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query and products.exists():
        try:
            products = products.filter(
                Q(name__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(category__name__icontains=search_query)
            )
        except Exception:
            pass
    
    # Category filter
    category_filter = request.GET.get('category', '')
    if category_filter and products.exists():
        try:
            products = products.filter(category__slug=category_filter)
        except Exception:
            pass
    
    # Price filter
    max_price = request.GET.get('max_price', '')
    if max_price and products.exists():
        try:
            products = products.filter(price__lte=float(max_price))
        except (ValueError, Exception):
            pass
    
    # Rating filter
    min_rating = request.GET.get('min_rating', '')
    if min_rating and products.exists():
        try:
            products = products.filter(rating__gte=float(min_rating))
        except (ValueError, Exception):
            pass
    
    # Sorting
    if products.exists():
        sort_by = request.GET.get('sort', 'bestsellers')
        try:
            if sort_by == 'price-low':
                products = products.order_by('price')
            elif sort_by == 'price-high':
                products = products.order_by('-price')
            elif sort_by == 'newest':
                products = products.order_by('-created_at')
            elif sort_by == 'rating':
                products = products.order_by('-rating')
            elif sort_by == 'name-asc':
                products = products.order_by('name')
            elif sort_by == 'name-desc':
                products = products.order_by('-name')
            else:  # bestsellers (default)
                products = products.order_by('-review_count', '-rating')
        except Exception:
            pass
    else:
        sort_by = request.GET.get('sort', 'bestsellers')
    
    # Get all categories for filter sidebar
    try:
        categories = Category.objects.all()
    except Exception:
        categories = []
    
    context = {
        'products': products,
        'categories': categories,
        'search_query': search_query,
        'selected_category': category_filter,
        'selected_sort': sort_by,
        'max_price': max_price,
        'min_rating': min_rating,
    }
    
    return render(request, 'products/product_list.html', context)


def product_detail(request, slug):
    """Product detail page with contact-for-order form (no real payment)."""
    product = get_object_or_404(Product, slug=slug)

    success = False
    error = None

    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        email = request.POST.get("email", "").strip()
        phone = request.POST.get("phone", "").strip()
        message = request.POST.get("message", "").strip()

        if not name or not email:
            error = "Please provide at least your name and email."
        else:
            OrderInquiry.objects.create(
                product=product,
                name=name,
                email=email,
                phone=phone,
                message=message,
            )
            success = True

    context = {
        'product': product,
        'success': success,
        'error': error,
    }

    return render(request, 'products/product_detail.html', context)


def contact(request):
    """Simple Contact Us page for general customer inquiries."""
    success = False
    error = None

    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        email = request.POST.get("email", "").strip()
        message = request.POST.get("message", "").strip()

        if not name or not email or not message:
            error = "Please fill in your name, email, and message."
        else:
            # For now we just flag success; emails can be wired later
            success = True

    context = {
        "success": success,
        "error": error,
        "store_owner_email": getattr(settings, "STORE_OWNER_EMAIL", "farshad.mhd.jp@gmail.com"),
    }

    return render(request, "contact.html", context)
