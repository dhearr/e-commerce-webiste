from django.urls import path
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
]
