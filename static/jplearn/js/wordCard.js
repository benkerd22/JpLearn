let wordCardActuate = function (json) {
    let gifrow = $(this).find(".wordCard-gifrow"),
        kanji = $(this).find(".wordCard-kanji"),
        gana = $(this).find(".wordCard-gana"),
        chn = $(this).find(".wordCard-chn");

    gifrow.empty();
    for (let i = 0; i < json.kanji.length; i++) {
        let code = json.kanji.charCodeAt(i);
        if (0x3040 <= code && code <= 0x30ff) {
            continue;
        }

        let hex = code.toString(16);
        let url = 'http://img.kakijun.com/kanjiphoto/gif/' + hex + '.gif';
        gifrow.append(
            `<div class="col-2">
                <img src="${url}" class="img-fluid" alt="${json.kanji[i]}">
            </div>`
        );
    }

    kanji.text("");
    if (json.gana != json.kanji)
        kanji.text(json.kanji);

    gana.empty().append(`${json.gana}&nbsp;${json.tone}`);

    chn.text(json.chn);
}

let WordCard = function () {
    $(".wordCard").on("wordCard:refresh", function (e, json) {

        if ($(this).hasClass("show")) {
            $(this)
                .on("hidden.bs.collapse", function () {
                    $(this).off("hidden.bs.collapse");
                    wordCardActuate.bind(this)(json);
                }.bind(this))
                .collapse("hide");
        } else
            wordCardActuate.bind(this)(json);
    })
}