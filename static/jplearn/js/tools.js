let PostAsJson = function (url, data) {
    return {
        url: url,
        method: "POST",
        headers: {
            'X-CSRFToken': $("#csrf_token").text()
        },
        data: JSON.stringify(data),
        dataType: "json",
    }
}

let toggleClass = function (element, class0, class1) {
    if ($(element).hasClass(class0)) {
        $(element).removeClass(class0).addClass(class1);
    } else if ($(element).hasClass(class1)) {
        $(element).removeClass(class1).addClass(class0);
    }
}

let Alert = function (HTMLelement) {
    this.HTMLelement = HTMLelement;
    this.text = $(HTMLelement).find("span");
    this.retryBtn = $(HTMLelement).find("button");
}

Alert.prototype.alert = function (msg, callback) {
    let self = this,
        alert = $(self.HTMLelement);

    $(self.text).text(msg);
    $(alert)
    .on("shown.bs.collapse", function () {
        $(alert).off("shown.bs.collapse");
        $(self.retryBtn).click(function () {
            $(self.retryBtn).off();
            $(alert)
                .on("hidden.bs.collapse", function () {
                    $(alert).off("hidden.bs.collapse");
                    callback();
                })
                .collapse("hide");
        })
    })
    .collapse("show");
}