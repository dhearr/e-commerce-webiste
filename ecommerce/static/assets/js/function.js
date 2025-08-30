$("#commentForm").submit(function (e) {
  e.preventDefault();

  $.ajax({
    data: $(this).serialize(),
    method: $(this).attr("method"),
    url: $(this).attr("action"),
    dataType: "json",
    success: function (response) {
      if (response.bool === true) {
        const today = new Date();
        const formattedDate = today.toLocaleDateString("en-GB", {
          day: "2-digit",
          month: "short",
          year: "numeric",
        });

        const newReview = `
        <div class="single-comment justify-content-between d-flex mb-30">
          <div class="user justify-content-between d-flex">
            <div class="thumb text-center">
              <img
                src="/static/assets/imgs/blog/author-2.png"
                alt="${response.context.user}"
              />
              <a href="#" class="font-heading text-brand">
                ${response.context.user}
              </a>
            </div>
            <div class="desc">
              <div class="d-flex justify-content-between mb-10">
                <div class="d-flex align-items-center">
                  <span class="font-xs text-muted">
                    ${formattedDate}
                  </span>
                </div>
                <div class="product-rate d-inline-block">
                  <div
                    class="product-rating"
                    style="width: ${response.context.rating * 20}%"
                  ></div>
                </div>
              </div>
              <p class="mb-10">
                ${response.context.review}
                <a href="#" class="reply">Reply</a>
              </p>
            </div>
          </div>
        </div>
      `;

        $(".comment-list").prepend(newReview);
        $("#commentForm")[0].reset();
      }
    },
  });
});

$(document).ready(function () {
  // filter product
  $(".filter-checkbox, #price-filter-btn").on("click", function () {
    let filter_objects = {};

    let is_price_filter = $(this).attr("id") === "price-filter-btn";

    if (is_price_filter) {
      filter_objects.min_price = $("#current_price").attr("min");
      filter_objects.max_price = $("#current_price").val();
    }

    $(".filter-checkbox").each(function () {
      let filter_value = $(this).val();
      let filter_key = $(this).data("filter");

      filter_objects[filter_key] = Array.from(
        document.querySelectorAll(`input[data-filter=${filter_key}]:checked`)
      ).map(function (el) {
        return el.value;
      });
    });

    $.ajax({
      url: "/filter-products",
      data: filter_objects,
      dataType: "json",
      beforeSend: function () {
        $("#product-filter-list").hide();
        $("#skeleton-loader").show();
      },
      success: function (response) {
        $("#product-filter-list").html(response.data);
        $("#product-count").html(response.count);
      },
      complete: function () {
        $("#skeleton-loader").hide();
        $("#product-filter-list").show();
      },
    });
  });

  // price range slider
  $("#current_price").on("blur", function () {
    let min_price = $(this).attr("min");
    let max_price = $(this).attr("max");
    let current_price = $(this).val();

    if (
      current_price < parseInt(min_price) ||
      current_price > parseInt(max_price)
    ) {
      min_price = Math.round(min_price * 100) / 100;
      max_price = Math.round(max_price * 100) / 100;

      $(this).val(min_price);
      $("#range").val(min_price);
      $(this).focus();

      return false;
    }
  });
});

// Add to cart
$(".add-to-cart-btn").on("click", function () {
  let this_val = $(this);
  let index = this_val.attr("data-index");

  let product_qty = $(`.product-quantity-${index}`).val();
  let product_id = $(`.product-id-${index}`).val();
  let product_title = $(`.product-title-${index}`).val();
  let product_price = $(`.current-product-price-${index}`).text();
  let product_pid = $(`.product-pid-${index}`).val();
  let product_image = $(`.product-image-${index}`).val();

  // --- ANIMASI FLY TO CART ---
  let cart = $(".mini-cart-icon"); // selector untuk ikon keranjang kamu
  let imgToDrag = $(`.product-image-${index}`).val()
    ? $(`<img src="${product_image}" />`)
    : null;

  if (imgToDrag) {
    imgToDrag
      .css({
        position: "absolute",
        top: this_val.offset().top,
        left: this_val.offset().left,
        width: "100px",
        zIndex: "1000",
        opacity: 0.8,
      })
      .appendTo("body")
      .animate(
        {
          top: cart.offset().top,
          left: cart.offset().left,
          width: 30,
          height: 30,
          opacity: 0.2,
        },
        800,
        "swing",
        function () {
          $(this).remove();
        }
      );
  }

  $.ajax({
    url: "/add-to-cart",
    data: {
      qty: product_qty,
      id: product_id,
      title: product_title,
      price: product_price,
      pid: product_pid,
      image: product_image,
    },
    dataType: "json",
    beforeSend: function () {
      this_val.html(
        `<div class="spinner-border spinner-border-sm" role="status"></div>`
      );
      this_val.attr("disabled", "disabled");
    },
    success: function (response) {
      $(".cart-items-count").text(response.totalcartitems);
      this_val.html(`<i class="fi-rs-shopping-cart-check"></i>`);
      setTimeout(function () {
        this_val.html(`<i class="fi-rs-shopping-cart mr-5"></i> Add`);
        this_val.removeAttr("disabled");
      }, 5000);
    },
  });
});

// Delete from cart
$(document).on("click", ".delete-product", function () {
  let product_id = $(this).attr("data-product");
  let this_val = $(this);

  $.ajax({
    url: "/delete-from-cart",
    data: {
      id: product_id,
    },
    dataType: "json",
    beforeSend: function () {
      this_val.html(
        `<div class="spinner-border spinner-border-sm" role="status"></div>`
      );
    },
    success: function (response) {
      this_val.show();
      $(".cart-items-count").text(response.totalcartitems);
      $("#cart-list").html(response.data);
    },
  });
});

// update product
$(document).on("click", ".update-product", function () {
  let product_id = $(this).attr("data-product");
  let product_qty = $(`.product-qty-${product_id}`).val();
  let this_val = $(this);

  $.ajax({
    url: "/update-cart",
    data: {
      id: product_id,
      qty: product_qty,
    },
    dataType: "json",
    beforeSend: function () {
      this_val.html(
        `<div class="spinner-border spinner-border-sm" role="status"></div>`
      );
    },
    success: function (response) {
      this_val.show();
      $(".cart-items-count").text(response.totalcartitems);
      $("#cart-list").html(response.data);
    },
  });
});
