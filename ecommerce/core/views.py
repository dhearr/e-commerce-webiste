from django.shortcuts import render, get_object_or_404, redirect
from core.models import (
    Product,
    Category,
    Vendor,
    ProductReview,
    CartOrder,
    CartOrderItems,
)
from django.db.models import Count, Avg, Q
from taggit.models import Tag
from core.forms import ProductReviewForm
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponse
from django.template.loader import render_to_string
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib.staticfiles import finders
import base64, json, requests, hashlib, hmac
from weasyprint import HTML, CSS


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

    product_id = str(request.GET["id"])

    try:
        new_qty = int(request.GET["qty"])
        if new_qty < 1:
            new_qty = 1
    except (ValueError, TypeError):
        new_qty = 1

    cart_product[str(request.GET["id"])] = {
        "title": request.GET["title"],
        "qty": new_qty,
        "price": request.GET["price"],
        "pid": request.GET["pid"],
        "image": request.GET["image"],
    }

    if "cart_data_obj" in request.session:
        if product_id in request.session["cart_data_obj"]:
            cart_data = request.session["cart_data_obj"]

            current_qty = int(cart_data[product_id]["qty"])
            cart_data[product_id]["qty"] = current_qty + new_qty

            # cart_data[str(request.GET["id"])]["qty"] = int(
            #     cart_product[str(request.GET["id"])]["qty"]
            # )
            # cart_data.update(cart_data)
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


def cart_view(request):
    cart_total_amount = 0

    if "cart_data_obj" in request.session:
        for product_id, item in request.session["cart_data_obj"].items():
            price_rep = item["price"].strip().replace(",", "")
            subtotal = int(price_rep) * int(item["qty"])
            item["price"] = price_rep
            item["subtotal"] = subtotal
            cart_total_amount += subtotal
        return render(
            request,
            "core/cart.html",
            {
                "cart_data": request.session["cart_data_obj"],
                "totalcartitems": len(request.session["cart_data_obj"]),
                "cart_total_amount": cart_total_amount,
            },
        )
    else:
        return render(
            request,
            "core/cart.html",
            {
                "cart_data": {},
                "totalcartitems": 0,
                "cart_total_amount": cart_total_amount,
            },
        )


def delete_item_from_cart(request):
    product_id = str(request.GET["id"])

    if "cart_data_obj" in request.session:
        if product_id in request.session["cart_data_obj"]:
            cart_data = request.session["cart_data_obj"]
            del request.session["cart_data_obj"][product_id]
            request.session["cart_data_obj"] = cart_data

    cart_total_amount = 0
    if "cart_data_obj" in request.session:
        for product_id, item in request.session["cart_data_obj"].items():
            price_rep = item["price"].strip().replace(",", "")
            subtotal = int(price_rep) * int(item["qty"])
            item["price"] = price_rep
            item["subtotal"] = subtotal
            cart_total_amount += subtotal

    context = render_to_string(
        "core/async/cart-list.html",
        {
            "cart_data": request.session["cart_data_obj"],
            "totalcartitems": len(request.session["cart_data_obj"]),
            "cart_total_amount": cart_total_amount,
        },
    )

    return JsonResponse(
        {
            "data": context,
            "totalcartitems": len(request.session["cart_data_obj"]),
        }
    )


def update_cart(request):
    product_id = str(request.GET["id"])

    try:
        product_qty = int(request.GET["qty"])
        if product_qty < 1:
            product_qty = 1
    except (ValueError, TypeError):
        product_qty = 1

    if "cart_data_obj" in request.session:
        if product_id in request.session["cart_data_obj"]:
            cart_data = request.session["cart_data_obj"]
            cart_data[str(request.GET["id"])]["qty"] = product_qty
            request.session["cart_data_obj"] = cart_data

    cart_total_amount = 0
    if "cart_data_obj" in request.session:
        for product_id, item in request.session["cart_data_obj"].items():
            price_rep = item["price"].strip().replace(",", "")
            subtotal = int(price_rep) * int(item["qty"])
            item["price"] = price_rep
            item["subtotal"] = subtotal
            cart_total_amount += subtotal

    context = render_to_string(
        "core/async/cart-list.html",
        {
            "cart_data": request.session["cart_data_obj"],
            "totalcartitems": len(request.session["cart_data_obj"]),
            "cart_total_amount": cart_total_amount,
        },
    )

    return JsonResponse(
        {
            "data": context,
            "totalcartitems": len(request.session["cart_data_obj"]),
        }
    )


@login_required
def checkout_view(request):
    cart_total_amount = 0
    if "cart_data_obj" in request.session:
        for product_id, item in request.session["cart_data_obj"].items():
            price_rep = item["price"].strip().replace(",", "")
            subtotal = int(price_rep) * int(item["qty"])
            item["price"] = price_rep
            item["subtotal"] = subtotal
            cart_total_amount += subtotal

        return render(
            request,
            "core/checkout.html",
            {
                "cart_data": request.session["cart_data_obj"],
                "totalcartitems": len(request.session["cart_data_obj"]),
                "cart_total_amount": cart_total_amount,
            },
        )


def _cart_totals_from_session(request):
    """
    Hitung total dari session cart kamu:
    request.session["cart_data_obj"] = { product_id(str): {title, qty, price(str), pid, image} }
    """
    cart_total = 0
    items = []
    cart = request.session.get("cart_data_obj", {})
    for pid, item in cart.items():
        price_rep = item["price"].strip().replace(",", "")
        price = int(price_rep)
        qty = int(item["qty"])
        subtotal = price * qty
        cart_total += subtotal
        items.append(
            {
                "pid": pid,
                "title": item["title"],
                "image": item["image"],
                "qty": qty,
                "price": price,
                "subtotal": subtotal,
            }
        )

    return cart_total, items


def create_snap_transaction(request):
    if request.method != "GET":
        return HttpResponseBadRequest("Use GET")

    if "cart_data_obj" not in request.session or not request.session["cart_data_obj"]:
        return HttpResponseBadRequest("Cart is empty")

    # 1) hitung total & siapkan items
    cart_total, items = _cart_totals_from_session(request)

    # 2) buat CartOrder (pending)
    if not request.user.is_authenticated:
        # kalau belum login, kamu bisa pakai user anon khusus atau handle sesuai kebutuhan
        return HttpResponseBadRequest("User must be authenticated")

    order = CartOrder.objects.create(
        user=request.user,
        price=cart_total,
        paid_status=False,
        product_status="processing",
    )

    # 3) simpan line items (opsional tapi best practice)
    for it in items:
        CartOrderItems.objects.create(
            order=order,
            item=it["title"],
            image=it["image"],
            qty=it["qty"],
            price=it["price"],
            total=it["subtotal"],
        )

    # 4) request Snap token
    url = (
        "https://app.sandbox.midtrans.com/snap/v1/transactions"
        if not settings.MIDTRANS_IS_PRODUCTION
        else "https://app.midtrans.com/snap/v1/transactions"
    )

    auth_string = f"{settings.MIDTRANS_SERVER_KEY}:"
    auth_header = base64.b64encode(auth_string.encode()).decode()

    # Midtrans butuh gross_amount integer (IDR tanpa desimal)
    gross_amount = int(order.price)  # atau round(Decimal) → tapi Pastikan sesuai IDR

    payload = {
        "transaction_details": {
            "order_id": order.order_id,
            "gross_amount": gross_amount,
        },
        # (opsional) lampirkan item_details biar detail di dashboard Midtrans rapi
        "item_details": [
            {
                "id": it["pid"],
                "price": int(it["price"]),
                "quantity": it["qty"],
                "name": it["title"][:50],
            }
            for it in items
        ],
        # (opsional) customer_details
        "customer_details": {
            "first_name": getattr(request.user, "first_name", "")
            or request.user.username,
            "email": request.user.email or "noemail@example.com",
        },
        # (opsional) set urls redirect
        # "callbacks": {
        #     "finish": request.build_absolute_uri("/payments/finish/"),
        # },
        "notification_url": request.build_absolute_uri("/payments/notification/"),
    }

    response = requests.post(
        url,
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Basic {auth_header}",
        },
        data=json.dumps(payload),
    )
    data = response.json()

    if response.status_code >= 400 or "token" not in data:
        # roll back order kalau mau, atau tandai error
        return JsonResponse(data, status=400)

    # simpan snap_token agar bisa di-reuse (misal tombol bayar ulang)
    order.snap_token = data["token"]
    order.save(update_fields=["snap_token"])

    # NOTE: jangan kosongin cart session di sini; kosongkan setelah settlement/callback
    return JsonResponse(
        {
            "token": data["token"],
            "order_id": order.order_id,
            "redirect_url": data.get("redirect_url"),
        }
    )


@csrf_exempt
def midtrans_notification(request):
    if request.method != "POST":
        return HttpResponseBadRequest("Only POST")

    payload = json.loads(request.body.decode("utf-8"))
    order_id = payload.get("order_id")
    status_code = payload.get("status_code")
    gross_amount = payload.get("gross_amount")
    signature_key = payload.get("signature_key")
    transaction_status = payload.get("transaction_status")
    payment_type = payload.get("payment_type")
    fraud_status = payload.get("fraud_status")
    transaction_id = payload.get("transaction_id")

    # Ambil order
    try:
        order = CartOrder.objects.get(order_id=order_id)
    except CartOrder.DoesNotExist:
        return HttpResponseBadRequest("Order not found")

    # Validasi jumlah pembayaran
    if str(order.price) != str(int(float(gross_amount))):
        return HttpResponseBadRequest("Invalid gross amount")

    # Verifikasi signature
    raw = f"{order_id}{status_code}{gross_amount}{settings.MIDTRANS_SERVER_KEY}"
    valid_sig = hashlib.sha512(raw.encode("utf-8")).hexdigest()
    if signature_key != valid_sig:
        return HttpResponseBadRequest("Invalid signature")

    # Update info pembayaran
    order.payment_type = payment_type
    order.transaction_status = transaction_status
    order.fraud_status = fraud_status
    order.midtrans_transaction_id = transaction_id

    # Mapping status
    if transaction_status in ["capture", "settlement"]:
        order.paid_status = True
        order.product_status = "shipped"
    elif transaction_status in ["cancel", "expire", "deny"]:
        order.paid_status = False
        order.product_status = "cancelled"
    elif transaction_status == "pending":
        order.paid_status = False
        order.product_status = "processing"

    order.save()
    return HttpResponse("OK")


@login_required
def cancel_temp_order(request):
    if request.method == "POST":
        order_id = request.POST.get("order_id")
        CartOrder.objects.filter(order_id=order_id, paid_status=False).delete()
        return JsonResponse({"status": "ok"})
    return JsonResponse({"error": "Invalid request"}, status=400)


@login_required
def clear_cart(request):
    if "cart_data_obj" in request.session:
        del request.session["cart_data_obj"]
    return JsonResponse({"status": "cleared"})


@login_required
def payment_finish(request):
    order = CartOrder.objects.filter(user=request.user).order_by("-order_date").first()
    if not order:
        return HttpResponseBadRequest("Order not found")

    items = CartOrderItems.objects.filter(order=order)
    subtotal = sum(item.total for item in items)

    # print("====== order ======:", order)
    # print("====== subtotal ======:", list(items.values()))
    # print("====== subtotal ======:", subtotal)

    return render(
        request,
        "core/payment-finish.html",
        {
            "order_id": order.order_id,
            "order_date": order.order_date,
            "payment_method": order.payment_type,
            "items": items,
            "subtotal": subtotal,
            "grand_total": subtotal,
        },
    )


@login_required
def payment_unfinish(request):
    return render(request, "core/payment-unfinish.html")


@login_required
def payment_error(request):
    return render(request, "core/payment-error.html")


@login_required
def invoice_pdf(request, order_id):
    # Ambil order terbaru user
    order = CartOrder.objects.filter(user=request.user).order_by("-order_date").first()
    # order = get_object_or_404(CartOrder, order_id=order_id, user=request.user)
    if not order:
        return HttpResponseBadRequest("Order tidak ditemukan")

    items = CartOrderItems.objects.filter(order=order)
    subtotal = sum(item.total for item in items)
    grand_total = subtotal  # Kalau ada pajak atau diskon, hitung di sini

    context = {
        "order_id": order.order_id,
        "order_date": order.order_date,
        "payment_method": order.payment_type,
        "items": items,
        "subtotal": subtotal,
        "grand_total": grand_total,
        "request": request,
    }

    html_string = render_to_string("core/payment-finish.html", context)

    css = CSS(
        string="""
        @page { size: A2; margin: 0.1cm; }
        body { font-size: 8px; } 
        """
    )

    pdf = HTML(string=html_string, base_url=request.build_absolute_uri()).write_pdf(
        stylesheets=[css]
    )

    response = HttpResponse(pdf, content_type="application/pdf")
    response["Content-Disposition"] = 'inline; filename="invoice.pdf"'
    return response


@login_required
def dashboard_view(request):
    orders = CartOrder.objects.filter(user=request.user).order_by("-order_date")

    context = {
        "orders": orders,
    }
    return render(request, "core/dashboard.html", context)


@login_required
def order_detail_modal(request, id):
    order = get_object_or_404(CartOrder, id=id, user=request.user)
    items = CartOrderItems.objects.filter(order=order)

    # Hitung subtotal, ongkir, total
    subtotal = sum(item.total for item in items)
    shipping = getattr(order, "shipping", 0)
    total = subtotal + shipping

    steps = ["ordered", "processing", "shipped", "delivered"]

    if order.product_status == "cancelled":
        steps[0] = "cancelled"
        progress_percent = 100
    else:
        progress_percent = 100

    current_index = (
        steps.index(order.product_status) if order.product_status in steps else 0
    )

    html = render_to_string(
        "core/order-detail-modal-content.html",
        {
            "order": order,
            "items": items,
            "steps": steps,
            "current_index": current_index,
            "progress_percent": progress_percent,
            "subtotal": subtotal,
            "shipping": shipping,
            "total": total,
        },
        request=request,
    )

    return JsonResponse({"html": html})
