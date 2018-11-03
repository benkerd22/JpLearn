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