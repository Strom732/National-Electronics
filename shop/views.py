from django.shortcuts import render
from products.models import Product, Category
from django.core.paginator import Paginator
from django.db.models import Q

def shop_view(request):
    query = request.GET.get('query', '')
    category_id = request.GET.get('category', '')
    sort_by = request.GET.get('sort_by', '')

    products = Product.objects.all().select_related('category')

    if query:
        products = products.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        )

    if category_id and category_id != 'all':
        products = products.filter(category__id=category_id)

    if sort_by == 'popularity':
        products = products.order_by('-popularity')
    elif sort_by == 'newest':
        products = products.order_by('-id')
    elif sort_by == 'price':
        products = products.order_by('price')

    paginator = Paginator(products, 24)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    categories = Category.objects.all()

    context = {
        'products': page_obj,
        'categories': categories,
        'selected_category': category_id,
        'query': query,
        'sort_by': sort_by,
        'current_page': page_obj.number,
        'total_results': paginator.count,
    }

    return render(request, 'shop.html', context)
