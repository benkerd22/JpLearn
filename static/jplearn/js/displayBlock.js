let DisplayBlock = function (HTMLelement, favBtnManager, modeSettingBlock, margin, index) {
    let block = $(HTMLelement);

    this.HTMLelement = HTMLelement;
    this.text = block.find(".displayText");
    this.favBtn = block.find(".favBtn");
    this.playBtn = new PlayBtn(block.find(".playBtn"), block.find("audio")[0]);

    this.favBtnManager = favBtnManager;
    this.modeSettingBlock = modeSettingBlock;

    this.width = block.width() + margin;
    this.index = index;

    this.data = null;
}

// A jQuery Deferred object
DisplayBlock.prototype.show = function () {
    let self = this,
        def = $.Deferred();

    if (self.playBtn.autoplay) {
        self.playBtn.promise
            .then(function () {
                return self.playBtn.play();
            })
            .then(function () {
                return self.playBtn.play();
            })
            .then(def.resolve)
    } else
        def.resolve();

    return def.promise();
}

// This is an instant function
DisplayBlock.prototype.refresh = function (def) {
    let self = this,
        json = self.data,
        choice = self.modeSettingBlock.getChoice();

    if (!json) {
        def.resolve();
        return;
    }

    self.playBtn.promise = self.playBtn.changesrc(json.audio);
    self.playBtn.autoplay = choice === 3;

    self.favBtnManager.toggle(self.favBtn, json.checked);
    self.favBtn.data("target", json.id);

    // 0:kanji  1:gana  2:chn  3:music
    switch (choice) {
        case 0:
            self.text
                .text(json.kanji)
                .css("font-family", "MYTTF")
                .removeClass("h2 lead")
                .addClass("h1");
            break;
        case 1:
            self.text
                .empty()
                .append(`${json.gana}<small>&nbsp;${json.tone}</small>`)
                .css("font-family", "MYTTF")
                .removeClass("lead h1 h2")
                .addClass((json.gana + json.tone).length >= 6 ? "h2" : "h1");
            break;
        case 2:
            self.text
                .text(json.chn)
                .css("font-family", "")
                .removeClass("h2")
                .addClass("h1 lead");
            break;
        case 3:
            self.text.text("");
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
        .fail(function (jqXHR, textStatus) {
            def.reject(textStatus);
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

        self.data = null; // mark as disabled, wait for post action from the container

        def.resolve();
    } else {
        // the block is still visible, so use animation
        $(self.HTMLelement).animate({
            left: newindex * self.width,
            position: "relative",
        }, {
            duration: 600,
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


// *****************************

let DisplayBlockContainer = function (HTMLelement, wordCard, progressbar, favBtnManager, modeSettingBlock, alert) {
    let self = this;

    self.blocks = [];
    $(HTMLelement).find(".displayBlock").each(function (index) {
        self.blocks.push(
            new DisplayBlock(this, favBtnManager, modeSettingBlock, 60, index - 1)
        );
    })

    self.wordCard = wordCard;
    self.progressbar = progressbar;
    self.alert = alert;

    modeSettingBlock.onChange(self.refresh.bind(this));

    self.current = 1;
    self.valid = false; // can accept action ?

    $.when(
            self.blocks[self.current]
            .post("new")
            .then(function () {
                return self.wordCard.refresh(self.blocks[self.current].data)
            }),
            self.blocks[self.current - 1].post("prelast"),
            self.blocks[self.current + 1].post("prefetch"),
        )
        .done(function () {
            self.valid = true;
        })
        .fail(function () {
            self.alert.alert("Oops! The network is down. ", function () {
                location.reload(false);
            });
        })
}

// A jQuery Deferred Object
DisplayBlockContainer.prototype.post = function (direction) {
    //post for general & new block
    let self = this,
        cur = self.current,
        dir = direction === "left" ? 1 : -1,
        def = $.Deferred();

    cur = (cur + dir + 3) % 3;
    $.ajax(PostAsJson("", {
            action: direction === "left" ? "next" : "previous",
        }))
        .done(function (json) {
            switch (json.status) {
                case "random_mode":
                    self.progressbar.hide();
                    break;

                case "continue":
                    self.progressbar
                        .show()
                        .val(json.current, json.max);
                    break;

                case "not allowed":
                    def.reject("not allowed");
                    return;

                case "finish":
                    self.progressbar
                        .show()
                        .val(json.max, json.max);

                    $("#wordCount").text(json.max);
                    $("#successAlert").modal("show"); // TODO: improve this

                    def.reject("finished");
                    return;
            }

            self.current = cur;
            def.resolve();
        })
        .fail(function (jqXHR, textStatus) {
            def.reject(textStatus);
        })

    return def.promise();
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
        dir = x > 0 ? 1 : (x === 0 ? 0 : -1);

    if (!self.valid)
        return;

    cur = (cur + dir + 3) % 3;
    if (!self.blocks[cur].data) {
        if (Math.abs(x) > 80) // TODO: swipe seeing invalid block
            return;
    }

    self.valid = false;
    $.when(...self.locateBlocks(x, duration))
        .done(function () {
            self.valid = true;
        })
}

DisplayBlockContainer.prototype.move = function (direction) {
    let self = this,
        cur = self.current,
        dir = direction === "left" ? 1 : -1;

    let post_with_retry = function () {
        switch (self.stage) {
            case 1:
                retry1();
                break;
            case 2:
                retry2();
                break;
            default:
        }
    }

    let retry1 = function () {
        self.post(direction)
            .done(function () {
                self.stage = 2;
                post_with_retry();
            })
            .fail(function () {
                self.alert.alert("Oops! The network is down. ", post_with_retry);
            })
    }

    let retry2 = function () {
        self.blocks[(cur + dir + 3) % 3].post(direction === "left" ? "prefetch" : "prelast")
            .done(function () {
                self.stage = 0;
            })
            .fail(function () {
                self.alert.alert("Oops! The network is down. ", post_with_retry);
            })
    }

    if (!self.valid)
        return;

    if (self.stage) {
        self.locate(0, 500);
        return;
    }

    cur = (cur + dir + 3) % 3;
    if (!self.blocks[cur].data) {
        return;
    }

    self.valid = false;
    $.when(
            ...self.moveBlocks(dir),
            self.blocks[cur].show(),
            self.wordCard.refresh(self.blocks[cur].data),
            (function () {
                self.stage = 1;
                post_with_retry();
            })()
        )
        .done(function () {
            self.valid = true;
        })
}

DisplayBlockContainer.prototype.refresh = function () {
    let self = this,
        cur = self.current;

    self.blocks[(cur + 1) % 3].refresh($.Deferred());
    self.blocks[(cur + 2) % 3].refresh($.Deferred());
}