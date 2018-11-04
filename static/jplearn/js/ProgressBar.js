let ProgressBar = function (HTMLelement) {
    this.HTMLelement = HTMLelement;
}

ProgressBar.prototype.val = function (current, max) {
    let self = this,
        bar = $(self.HTMLelement).find(".progress-bar");

    bar
        .attr("aria-valuenow", current)
        .attr("aria-valuemax", max)
        .css("width", current / max * 100 + "%");
    
    return self;
}

ProgressBar.prototype.hide = function () {
    let self = this,
        bar = $(self.HTMLelement);
    
    bar.addClass("d-none");

    return self;
}

ProgressBar.prototype.show = function () {
    let self = this,
        bar = $(self.HTMLelement);
    
    bar.removeClass("d-none");

    return self;
}