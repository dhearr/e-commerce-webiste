from django.shortcuts import render, get_object_or_404
from core.models import Product, Category, Vendor, ProductReview
from django.db.models import Count, Avg
from taggit.models import Tag


def index(request):
    products = Product.objects.filter(
        product_status="published", featured=True
    ).order_by("-date")

    context = {
        "products": products,
    }

    return render(request, "core/index.html", context)


# Product Views
def product_list_view(request):
    products = Product.objects.filter(product_status="published").order_by("-date")

    context = {
        "products": products,
    }

    return render(request, "core/product-list.html", context)


def product_detail_view(request, pid):
    product = Product.objects.get(pid=pid)
    product_images = product.product_images.all()
    products = Product.objects.filter(category=product.category).exclude(pid=pid)

    # get product reviews
    reviews = ProductReview.objects.filter(product=product).order_by("-date")

    # get average rating review
    avg_rating = ProductReview.objects.filter(product=product).aggregate(
        rating=Avg("rating")
    )

    context = {
        "product": product,
        "product_images": product_images,
        "products": products,
        "reviews": reviews,
        "avg_rating": avg_rating,
    }

    return render(request, "core/product-detail.html", context)


# Category Views
def category_list_view(request):
    # categories = Category.objects.all()
    categories = Category.objects.all().annotate(product_count=Count("products"))

    context = {
        "categories": categories,
    }

    return render(request, "core/category-list.html", context)


def category_product_list_view(request, cid):
    category = Category.objects.get(cid=cid)
    products = Product.objects.filter(
        product_status="published", category=category
    ).order_by("-date")

    context = {
        "products": products,
        "category": category,
    }

    return render(request, "core/category-product-list.html", context)


# Vendor Views
def vendor_list_view(request):
    vendors = Vendor.objects.all()

    context = {
        "vendors": vendors,
    }

    return render(request, "core/vendor-list.html", context)


def vendor_detail_view(request, vid):
    vendor = Vendor.objects.get(vid=vid)
    # vendor = get_object_or_404(Vendor, vid=vid)
    products = Product.objects.filter(
        vendor=vendor, product_status="published"
    ).order_by("-date")

    context = {
        "vendor": vendor,
        "products": products,
    }

    return render(request, "core/vendor-detail.html", context)


# Tag Views
def tag_list_view(request, tag_slug=None):
    products = Product.objects.filter(product_status="published").order_by("-date")

    tag = None
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        products = products.filter(tags__in=[tag])

    context = {
        "products": products,
        "tag": tag,
    }

    return render(request, "core/tag.html", context)
