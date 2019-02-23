let WordCard = function (HTMLelement) {
    let card = $(HTMLelement);

    this.HTMLelement = HTMLelement;
    this.gifrow = card.find(".wordCard-gifrow");
    this.kanji = card.find(".wordCard-kanji");
    this.gana = card.find(".wordCard-gana");
    this.chn = card.find(".wordCard-chn");
    this.link = card.find("a");

    this.data = null;
}

WordCard.prototype.actuate = function (def) {  
    let self = this,
        json = self.data;

    self.gifrow.empty();
    for (let i = 0; i < json.kanji.length; i++) {
        let code = json.kanji.charCodeAt(i);
        if (0x3040 <= code && code <= 0x30ff) {
            continue;
        }

        let hex = code.toString(16);
        let url = 'http://img.kakijun.com/kanjiphoto/gif/' + hex + '.gif';
        self.gifrow.append(
            `<div class="col-2">
                <img src="${url}" class="img-fluid" alt="${json.kanji[i]}">
            </div>`
        );
    }

    self.kanji.text("");
    if (json.gana != json.kanji)
        self.kanji.text(json.kanji);

    self.gana.empty().append(`${json.gana}&nbsp;${json.tone}`);

    self.chn.empty().append(json.type === '' ? json.chn : `[${json.type}]&nbsp;${json.chn}`);

    self.link.attr("href", "https://kotobank.jp/word/" + json.kanji);

    def.resolve();
}

// A jQuery Deferred Object
WordCard.prototype.refresh = function (json) {
    let self = this,
        card = $(self.HTMLelement),
        def = $.Deferred();

    if (!json || json.status === "not allowed" || json.status === "finish")
        return;

    self.data = json;

    if (card.hasClass("show")) {
        card
            .on("hidden.bs.collapse", function () {
                card.off("hidden.bs.collapse");
                self.actuate(def); // def will be resolved here
            })
            .collapse("hide");
    } else
        self.actuate(def); // def will be resolved here

    return def.promise();
}