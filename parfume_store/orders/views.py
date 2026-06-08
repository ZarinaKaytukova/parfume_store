from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from django.db.models import Q

from .models import Product
from .forms import ProductForm

# Create your views here.

def product_list(request):
    """Список товаров с поиском, фильтрацией по категории и сортировкой (только для менеджеров/админов)"""

    products = Product.objects.all()

    search_query = request.GET.get('search', '').strip()
    sort_order = request.GET.get('sort', '')
    category_filter = request.GET.get('category', 'all')
    
    categories = [('all', 'Все категории')] + list(Product.CATEGORY_CHOICES)

    if request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser):
        # Поиск
        if search_query:
            products = products.filter(
                Q(article__icontains=search_query) |
                Q(name__icontains=search_query) |
                Q(unit__icontains=search_query) |
                Q(supplier__icontains=search_query) |
                Q(manufacturer__icontains=search_query) |
                Q(category__icontains=search_query) |
                Q(description__icontains=search_query)
            )

        # Сортировка
        if sort_order == 'asc':
            products = products.order_by('stock')
        elif sort_order == 'desc':
            products = products.order_by('-stock')

        # Фильтрация по категории
        if category_filter and category_filter != 'all':
            products = products.filter(category=category_filter)

    context = {
        'products': products,
        'categories': categories,
        'search_query': search_query,
        'category_filter': category_filter,
        'sort_order': sort_order,
    }

    # AJAX-запрос
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return render(request, 'orders/product_list_partial.html', context)

    return render(request, 'orders/product_list.html', context)

@login_required
def add_product(request):
    if not request.user.is_superuser:
        return JsonResponse({'error': 'У вас нет прав для добавления товаров.'}, status=403)
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save()
            return redirect('orders:product_list',)
        return JsonResponse({'success': False, 'errors': form.errors}, status=400)
    form = ProductForm()
    context = {'form': form}
    return render(request, 'orders/product_form.html', context)


@login_required
def edit_product(request, product_id):
    if not request.user.is_superuser:
        return JsonResponse({'error': 'У вас нет прав для редактирования товаров.'}, status=403)
    
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            product = form.save()
            return redirect('orders:product_list',)
        return JsonResponse({'success': False, 'errors': form.errors}, status=400)
    form = ProductForm(instance=product)
    context= {'form': form, 'product': product,}
    return render(request, 'orders/product_form.html', context)


@login_required
def delete_product(request, product_id):
    if not request.user.is_superuser:
        return JsonResponse({'error': 'У вас нет прав для редактирования товаров.'}, status=403)

    product = get_object_or_404(Product, id=product_id)
    # В форму передаём только объект модели, передавать в форму параметры запроса уже не нужно.
    form = ProductForm(instance=product)
    context= {'form': form, 'product': product,}
    if request.method == 'POST':
        product.delete()
        return redirect('orders:product_list') 
    return render(request, 'orders/confirm_delete.html', context)
