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

        $(".comment-list").prepend(newReview); // tambahkan di atas
        $("#commentForm")[0].reset(); // reset form setelah submit
      }
    },
  });
});

$(document).ready(function () {
  $(".filter-checkbox").on("click", function () {
    let filter_objects = {};

    $(".filter-checkbox").each(function () {
      let filter_value = $(this).val();
      let filter_key = $(this).data("filter");

      filter_objects[filter_key] = Array.from(
        document.querySelectorAll(`input[data-filter=${filter_key}]:checked`)
      ).map(function (el) {
        return el.value;
      });
    });
    console.log(filter_objects);
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
});
