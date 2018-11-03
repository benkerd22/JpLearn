let PlayBtn = function (relatedMedia) {
    let media = relatedMedia;

    $(".playBtn").click(function () {
        if ($(this).hasClass("disabled"))
            return;

        $(this).addClass("disabled").text("♪");
        autoRepeatTimes = 1;
        $(media).trigger("play");
    })

    $(".playBtn")
        .on("playBtn:changeSrc", function (e, url) {
            $(media)
                .attr("src", url)
                .trigger("load");

            $(this).text("▷").addClass("disabled invisible");
        })
        .on("playBtn:play", function (e, repeatTimes) {
            if (media.state >= 4) {
                $(media).trigger("play");
            } else {
                $(media).on("canplaythrough", function() {
                    $(media).trigger("play");
                })
            }
        })













/*
        .on("playBtn:load", function (e, repeatTimes) {
            repeatTimes = repeatTimes || 0;
            $(this).on("canplaythrough", function() {
                if (repeatTimes > 0) {

                    $(media).on("ended", function() {
                        $(this).trigger("canplaythrough");  // ??? is this needed?
                    })

                    repeatTimes--;
                    $(this).addClass("disabled").text("♪");
                    $(media).trigger("play");
                } else {
                    $(this).removeClass("disabled").text("▷");
                }
            })

            $(media).trigger("load");
        })

    $(media)
        .on("canplaythrough", function() {
            $(".playBtn").trigger("canplaythrough");
        })



    $(media)
        .on("pause", function () {
            if (autoRepeatTimes == 0)
                return;

            autoRepeatTimes--;
            if (autoRepeatTimes == 0) {
                $("#play").removeClass("disabled").text("▷");
            } else {
                $(media).trigger("play");
            }
        })
        .on("loadstart", function () {
            $("#play").addClass("disabled invisible");
        })
        .on("canplaythrough", function () {
            $("#play").removeClass("disabled invisible");
            if (autoRepeatTimes > 0) {
                $("#play").addClass("disabled").text("♪");

                $(media).trigger("play");
            }
        })*/
}