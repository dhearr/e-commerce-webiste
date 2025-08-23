from django.shortcuts import render
from core.models import Product, Category


def index(request):
    products = Product.objects.filter(
        product_status="published", featured=True
    ).order_by("-date")

    context = {
        "products": products,
    }
    return render(request, "core/index.html", context)
