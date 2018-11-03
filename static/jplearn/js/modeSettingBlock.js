// usage : modeChoiceCallback.bind( element )
let modeChoiceCallback = function () {
    let arr = []

    $(this).find(".modeBtn").each(function () {
        if ($(this).hasClass("btn-primary"))
            arr.push(parseInt($(this).data("target")));
    })

    if (arr.length === 0) {
        let def = 0; // default: 0 (kanji)
        arr.push(def);

        $(this).find(".modeBtn").each(function () {
            if ($(this).data("target") === def)
                $(this).click();
        })
    }

    return arr[Math.floor(Math.random() * arr.length)];
}


let ModeSettingBlock = function () {
    $(".modeSettingBlock").find(".modeBtn").each(function () {
        $(this).click(toggleClass.bind(this, ["btn-light", "btn-primary"]));
    })
}