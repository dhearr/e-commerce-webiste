from core.models import Product, Category, Address


def default(request):
    categories = Category.objects.all()

    address = None
    if request.user.is_authenticated:
        address = Address.objects.filter(user=request.user).first()

    return {"categories": categories, "address": address}
