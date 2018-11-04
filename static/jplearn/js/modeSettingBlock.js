let ModeSettingBlock = function (HTMLelement) {
    let self = this;

    this.HTMLelement = HTMLelement;
    this.callback = function () {}

    $(HTMLelement).find(".modeBtn").click(function () {
        toggleClass(this, "btn-primary", "btn-light");
        self.callback();
    })
}

ModeSettingBlock.prototype.getChoice = function () {
    let self = this,
        block = $(self.HTMLelement),
        arr = [];

    block.find(".modeBtn").each(function () {
        if ($(this).hasClass("btn-primary"))
            arr.push(parseInt($(this).data("target")));
    })

    if (arr.length === 0) {
        let de = 0; // default: 0 (kanji)
        arr.push(de);

        /*
        block.find(".modeBtn").each(function () {
            if ($(this).data("target") === de)
                $(this).click();
        })
        */
    }

    return arr[Math.floor(Math.random() * arr.length)];
}

ModeSettingBlock.prototype.onChange = function (callback) {
    let self = this;

    self.callback = callback;
}