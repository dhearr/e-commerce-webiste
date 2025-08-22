from django.shortcuts import render
from core.models import Product


def index(request):
    products = Product.objects.filter(
        product_status="published", featured=True
    ).order_by("-date")

    context = {
        "head_title": "Sellara | E-Commerce Website",
        "products": products,
    }
    return render(request, "core/index.html", context)
