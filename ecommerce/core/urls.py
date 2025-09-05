from django.urls import path, include
from . import views

app_name = "core"

urlpatterns = [
    # Home Page
    path("", views.index, name="index"),
    # Product
    path("products/", views.product_list_view, name="product-list"),
    path("product/<pid>/", views.product_detail_view, name="product-detail"),
    # Category
    path("category/", views.category_list_view, name="category-list"),
    path(
        "category/<cid>/",
        views.category_product_list_view,
        name="category-product-list",
    ),
    # Vendor
    path("vendor/", views.vendor_list_view, name="vendor-list"),
    path("vendor/<vid>/", views.vendor_detail_view, name="vendor-detail"),
    # Tag
    path("products/tag/<slug:tag_slug>/", views.tag_list_view, name="tag-list"),
    # add review
    path("ajax-add-review/<int:pid>/", views.ajax_add_review, name="ajax-add-review"),
    # search
    path("search/", views.search_view, name="search"),
    # filter products
    path("filter-products/", views.filter_product, name="filter-products"),
    # add to cart
    path("add-to-cart/", views.add_to_cart, name="add-to-cart"),
    # cart page
    path("cart/", views.cart_view, name="cart"),
    path("cart/clear/", views.clear_cart, name="clear-cart"),
    # delete product from cart
    path("delete-from-cart/", views.delete_item_from_cart, name="delete-from-cart"),
    # update cart
    path("update-cart/", views.update_cart, name="update-cart"),
    # checkout
    path("checkout/", views.checkout_view, name="checkout"),
    # midtrans
    # path(
    #     "create-transaction/",
    #     views.transaction_midtrans_view,
    #     name="transaction_midtrans",
    # ),
    # paypal
    # path("paypal/", include("paypal.standard.ipn.urls")),
    # payment completed
    # path("payment-completed/", views.payment_completed_view, name="payment-completed"),
    # # payment failed
    # path("payment-failed/", views.payment_failed_view, name="payment-failed"),
    # midtrans
    path(
        "payments/create-snap-transaction/",
        views.create_snap_transaction,
        name="create_snap_transaction",
    ),
    path(
        "payments/notification/",
        views.midtrans_notification,
        name="midtrans_notification",
    ),
    path("payments/finish/", views.payment_finish, name="payment_finish"),
    path("payments/unfinish/", views.payment_unfinish, name="payment_unfinish"),
    path("payments/error/", views.payment_error, name="payment_error"),
    path(
        "payments/cancel-temp-order/", views.cancel_temp_order, name="cancel_temp_order"
    ),
    #
    path("invoice/pdf/", views.invoice_pdf, name="invoice-pdf"),
]
