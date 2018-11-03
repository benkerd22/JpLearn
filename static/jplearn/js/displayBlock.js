let DisplayBlock = function (HTMLelement, urlAudio, modeChoice, margin, index) {
    this.HTMLelement = HTMLelement;
    this.width = $(HTMLelement).width() + margin;
    this.urlAudio = urlAudio;
    this.modeChoice = modeChoice;
    this.index = index;

    this.data = null;
}

DisplayBlock.prototype.display = function () {
    // load music ?
}

DisplayBlock.prototype.refresh = function (def) {
    let self = this,

        json = self.data,
        text = $(self.HTMLelement).find(".displayText"),
        playBtn = $(self.HTMLelement).find(".playBtn"),
        favBtn = $(self.HTMLelement).find(".favBtn"),
        choice = self.modeChoice();

    if (!json) {
        def.resolve();
        return;
    }

    playBtn.trigger("playBtn:changeSrc", self.urlAudio + `/${json.gana}.mp3`);
    favBtn.trigger(json.checked ? "favBtn:checked" : "favBtn:unchecked");

    // 0:kanji  1:gana  2:chn  3:music
    switch (choice) {
        case 0:
            text
                .text(json.kanji)
                .css("font-family", "MYTTF")
                .removeClass("h2 lead")
                .addClass("h1");
            break;
        case 1:
            text
                .empty()
                .append(`${json.gana}<small>&nbsp;${json.tone}</small>`)
                .css("font-family", "MYTTF")
                .removeClass("lead h1 h2")
                .addClass((json.gana + json.tone).length >= 6 ? "h2" : "h1");
            break;
        case 2:
            text
                .text(json.chn)
                .css("font-family", "")
                .removeClass("h2")
                .addClass("h1 lead");
            break;
        case 3:
            text.text("");
    }

    def.resolve();
}

// A jQuery Deferred object
DisplayBlock.prototype.post = function (action) {
    let self = this,
        def = $.Deferred();

    $.ajax(PostAsJson("", {
            action: action,
        }))
        .done(function (json) {
            if (json.status === "not allowed")
                self.data = null;
            else {
                self.data = json;
            }

            self.refresh(def); // promise will be resolve here
        })
        .fail(function (jqXHR, textStatus, err) {
            console.log(err);
        })

    return def.promise();
}

// A jQuery Deferred Object
DisplayBlock.prototype.move = function (direction) {
    let self = this,
        newindex = self.index + direction,
        def = $.Deferred();

    if (newindex < -1 || newindex > 1) {
        // out of index, should not enable animation
        if (newindex === -2)
            newindex = 1;
        else if (newindex === 2)
            newindex = -1;

        $(self.HTMLelement).css({
            left: newindex * self.width,
            position: "relative",
        })

        def.resolve();
    } else {
        // the block is still visible, so use animation
        $(self.HTMLelement).animate({
            left: newindex * self.width,
            position: "relative",
        }, {
            duration: 700,
            complete: def.resolve
        })
    }

    self.index = newindex;

    return def.promise();
}

// A jQuery Deferred Object
DisplayBlock.prototype.locate = function (x, duration) {
    let self = this,
        def = $.Deferred();

    duration = duration || 0;
    $(self.HTMLelement).animate({
        left: x + self.index * self.width,
        position: "relative",
    }, {
        duration: duration,
        complete: def.resolve,
    })

    return def.promise();
}

let DisplayBlockContainer = function (HTMLelement, wordCard, urlAudio, modeChoice) {
    let self = this;

    self.blocks = [];
    $(HTMLelement).find(".displayBlock").each(function (index) {
        self.blocks.push(
            new DisplayBlock(this, urlAudio, modeChoice, 60, index - 1)
        );
    })

    self.current = 1;
    self.wordCard = wordCard;
    self.valid = false; // can accept action ?

    $.when(
            self.blocks[self.current].post("new")
            .then(function () {
                $(wordCard).trigger("wordCard:refresh", [self.blocks[self.current].data]);
            }),
            self.blocks[self.current - 1].post("prelast"),
            self.blocks[self.current + 1].post("prefetch"),
        )
        .done(function () {
            self.valid = true;
        })
}

DisplayBlockContainer.prototype.moveBlocks = function (dir) {
    let self = this,
        defs = [];

    self.blocks.forEach(block => defs.push(block.move(-dir)));

    return defs;
}

DisplayBlockContainer.prototype.locateBlocks = function (x, duration) {
    let self = this,
        defs = [];

    self.blocks.forEach(block => defs.push(block.locate(x, duration)));

    return defs;
}

DisplayBlockContainer.prototype.locate = function (x, duration) {
    let self = this,
        cur = self.current,
        dir = x > 0 ? 1 : -1;

    if (!self.valid)
        return;
    
    cur = (cur + dir + 3) % 3;
    if (!self.blocks[cur].data) {
        if (Math.abs(x) > 80)  // TODO: swipe seeing invalid block
            return;
    }

    self.valid = false;
    $.when(
        ...self.locateBlocks(x, duration),
    )
        .done(function () {
            self.valid = true;
        })
}

DisplayBlockContainer.prototype.move = function (direction) {
    let self = this,
        cur = self.current,
        dir = direction === "left" ? 1 : -1;

    if (!self.valid)
        return;

    cur = (cur + dir + 3) % 3;
    if (!self.blocks[cur].data) {
        self.locate(0, 500);
        return;
    }

    self.valid = false;
    $.when(
            ...self.moveBlocks(dir),
            $.ajax(PostAsJson("", {
                action: direction === "left" ? "next" : "previous",
            }))
            .then(function () {
                return self.blocks[(cur + dir + 3) % 3].post(direction === "left" ? "prefetch" : "prelast");
            }),
            $(self.wordCard).trigger("wordCard:refresh", [self.blocks[cur].data])
        )
        .done(function () {
            self.valid = true;
            self.current = cur;
        })
}