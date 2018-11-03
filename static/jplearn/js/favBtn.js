let FavBtn = function (urlChecked, urlUnchecked, urlAction) {
    $(".favBtn")
        .on("favBtn:checked", function () {
            $(this)
                .attr("src", urlChecked)
                .data("checked", true);
        })
        .on("favBtn:unchecked", function () {
            $(this)
                .attr("src", urlUnchecked)
                .data("checked", false);
        });

    $(".favBtn").click(function (e) {
        if ($(this).hasClass("disabled"))
            return;
        $(this).addClass("disabled");

        $.ajax(PostAsJson(urlAction, {
                "target": $(this).data("target"),
                "action": $(this).data("checked") ? "remove" : "add",
            }))
            .done(function (json) {
                $(this).trigger(json.checked ? "favBtn:checked" : "favBtn:unchecked");
            }.bind(this))
            .fail(function (jqXHR, testStatus, err) {
                console.log(err);
            })
            .always(function () {
                $(this).removeClass("disabled");
            }.bind(this))
    })
}