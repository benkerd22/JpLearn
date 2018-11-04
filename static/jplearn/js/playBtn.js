let PlayBtn = function (HTMLelement, audio) {
    let self = this;
    this.HTMLelement = HTMLelement;

    this.staticUrl = $(audio).data("url");
    this.audio = audio;

    $(HTMLelement).click(function () {
        if ($(this).hasClass("disabled"))
            return;

        $(this)
            .text("♪")
            .addClass("disabled");

        self.play();
    })
}

PlayBtn.prototype.changesrc = function (url) {
    let self = this,
        btn = self.HTMLelement,
        def = $.Deferred();

    $(btn).addClass("disabled invisible");

    $(self.audio)
        .on("canplaythrough", function () {
            $(btn)
                .text("▷")
                .removeClass("disabled invisible");
            $(self.audio).off();

            def.resolve();
        })
        .attr("src", self.staticUrl + url)
        .trigger("load");

    return def.promise();
}

PlayBtn.prototype.play = function () {
    let self = this,
        btn = self.HTMLelement,
        def = $.Deferred();

    $(btn)
        .text("♪")
        .addClass("disabled");

    $(self.audio)
        .on("pause", function () {
            $(btn)
                .text("▷")
                .removeClass("disabled");
            $(self.audio).off();

            def.resolve();
        })
        .trigger("play");

    return def.promise();
}