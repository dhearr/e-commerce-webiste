from django.shortcuts import render, get_object_or_404
from core.models import Product, Category, Vendor, ProductReview
from django.db.models import Count, Avg, Q
from taggit.models import Tag
from core.forms import ProductReviewForm
from django.http import JsonResponse
from django.template.loader import render_to_string


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

    for r in reviews:
        r.rating_width = r.rating * 20

    # get average rating review
    avg_rating = ProductReview.objects.filter(product=product).aggregate(
        rating=Avg("rating")
    )
    avg_rating_data = avg_rating["rating"] or 0
    rating_width = (avg_rating_data / 5) * 100

    # rating count
    # hitung total review
    total_reviews = ProductReview.objects.filter(product=product).count()

    # hitung jumlah tiap bintang (1–5)
    rating_counts = (
        ProductReview.objects.filter(product=product)
        .values("rating")
        .annotate(count=Count("rating"))
    )

    # bikin list dari 5 → 1
    progres_data = []
    for star in range(5, 0, -1):
        count = next((r["count"] for r in rating_counts if r["rating"] == star), 0)
        percent = (count / total_reviews) * 100 if total_reviews else 0
        progres_data.append({"star": star, "percent": percent})

    # product review form
    product_review_form = ProductReviewForm()

    context = {
        "product": product,
        "product_images": product_images,
        "products": products,
        "reviews": reviews,
        "avg_rating": avg_rating,
        "product_review_form": product_review_form,
        "avg_rating_data": avg_rating_data,
        "rating_width": rating_width,
        "progres_data": progres_data,
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


# Other Views
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


def ajax_add_review(request, pid):
    if not request.user.is_authenticated:
        return JsonResponse(
            {"bool": False, "error": "Anda harus login untuk memberi review."}
        )

    product = Product.objects.get(pk=pid)
    user = request.user

    review = ProductReview.objects.create(
        user=user,
        product=product,
        review=request.POST["review"],
        rating=request.POST["rating"],
    )

    average_reviews = ProductReview.objects.filter(product=product).aggregate(
        rating=Avg("rating")
    )

    context = {
        "user": user.username,
        "review": request.POST["review"],
        "rating": request.POST["rating"],
    }

    return JsonResponse(
        {
            "bool": True,
            "context": context,
            "average_reviews": average_reviews,
        }
    )


def search_view(request):
    query = request.GET.get("q")
    cat_cid = request.GET.get("category")
    products = Product.objects.filter(
        Q(title__icontains=query) | Q(description__icontains=query)
    ).order_by("-date")

    if cat_cid:
        products = products.filter(category__cid=cat_cid)

    context = {"products": products, "query": query}

    return render(request, "core/search.html", context)


def filter_product(request):
    categories = request.GET.getlist("category[]")
    vendors = request.GET.getlist("vendor[]")
    min_price = request.GET.get("min_price")
    max_price = request.GET.get("max_price")

    products = (
        Product.objects.filter(product_status="published").order_by("-id").distinct()
    )

    if min_price and max_price:
        products = products.filter(price__gte=min_price, price__lte=max_price)

    if len(categories) > 0:
        products = products.filter(category__id__in=categories).distinct()

    if len(vendors) > 0:
        products = products.filter(vendor__id__in=vendors).distinct()

    data = render_to_string("core/async/product-list.html", {"products": products})
    count = products.count()

    return JsonResponse({"data": data, "count": count})


def add_to_cart(request):
    cart_product = {}

    cart_product[str(request.GET["id"])] = {
        "title": request.GET["title"],
        "qty": request.GET["qty"],
        "price": request.GET["price"],
        "pid": request.GET["pid"],
        "image": request.GET["image"],
    }

    if "cart_data_obj" in request.session:
        if str(request.GET["id"]) in request.session["cart_data_obj"]:
            cart_data = request.session["cart_data_obj"]
            cart_data[str(request.GET["id"])]["qty"] = int(
                cart_product[str(request.GET["id"])]["qty"]
            )
            cart_data.update(cart_data)
            request.session["cart_data_obj"] = cart_data
        else:
            cart_data = request.session["cart_data_obj"]
            cart_data.update(cart_product)
            request.session["cart_data_obj"] = cart_data
    else:
        request.session["cart_data_obj"] = cart_product

    return JsonResponse(
        {
            "data": request.session["cart_data_obj"],
            "totalcartitems": len(request.session["cart_data_obj"]),
        }
    )
