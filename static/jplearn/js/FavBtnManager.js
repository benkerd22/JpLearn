let FavBtnManager = function (scope, urlChecked, urlUnchecked, urlAction) {
    let self = this;

    this.urlChecked = urlChecked;
    this.urlUnchecked = urlUnchecked;
    this.urlAction = urlAction;

    $(scope).on("click", ".favBtn", function () {
        self.clickHandler(this);
    })
}

FavBtnManager.prototype.check = function (HTMLelement) {
    let self = this;

    $(HTMLelement)
        .attr("src", self.urlChecked)
        .data("checked", true);
}

FavBtnManager.prototype.uncheck = function (HTMLelement) {
    let self = this;

    $(HTMLelement)
        .attr("src", self.urlUnchecked)
        .data("checked", false);
}

FavBtnManager.prototype.toggle = function (HTMLelement, checked) {
    let self = this;

    if (checked)
        self.check(HTMLelement);
    else
        self.uncheck(HTMLelement);
}

FavBtnManager.prototype.clickHandler = function (HTMLelement) {
    let self = this,
        btn = $(HTMLelement);

    if (btn.hasClass("disabled"))
        return;
    btn.addClass("disabled");
    self.toggle(btn, !btn.data("checked"));
    btn.data("checked", !btn.data("checked"));

    $.ajax(PostAsJson(self.urlAction, {
            "target": btn.data("target"),
            "action": btn.data("checked") ? "remove" : "add",
        }))
        .done(function (json) {
            self.toggle(btn, json.checked);
        })
        .fail(function (jqXHR, testStatus, err) {
            console.log(err);
        })
        .always(function () {
            btn.removeClass("disabled");
        })
}
