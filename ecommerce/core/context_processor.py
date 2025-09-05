from core.models import Product, Category, Address, Vendor
from django.db.models import Min, Max
from django.conf import settings


def default(request):
    categories = Category.objects.all()
    vendors = Vendor.objects.all()
    min_max_price = Product.objects.aggregate(Min("price"), Max("price"))

    address = None
    if request.user.is_authenticated:
        address = Address.objects.filter(user=request.user).first()

    return {
        "categories": categories,
        "address": address,
        "vendors": vendors,
        "min_max_price": min_max_price,
    }


def midtrans_keys(request):
    return {"MIDTRANS_CLIENT_KEY": getattr(settings, "MIDTRANS_CLIENT_KEY", "")}
