from django.shortcuts import render
from core.models import Product, Category
from django.db.models import Count


def index(request):
    products = Product.objects.filter(
        product_status="published", featured=True
    ).order_by("-date")

    context = {
        "products": products,
    }
    return render(request, "core/index.html", context)


def category_list_view(request):
    # categories = Category.objects.all()
    categories = Category.objects.all().annotate(product_count=Count("category"))

    context = {
        "categories": categories,
    }
    return render(request, "core/category-list.html", context)
