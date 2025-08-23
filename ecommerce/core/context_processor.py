from core.models import Product, Category


def default(request):
    categories = Category.objects.all()

    return {"categories": categories}
