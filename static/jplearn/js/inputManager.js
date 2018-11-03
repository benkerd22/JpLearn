function InputManager() {
    this.events = {};

    if (window.navigator.msPointerEnabled) {
        //Internet Explorer 10 style
        this.eventTouchstart = "MSPointerDown";
        this.eventTouchmove = "MSPointerMove";
        this.eventTouchend = "MSPointerUp";
    } else {
        this.eventTouchstart = "touchstart";
        this.eventTouchmove = "touchmove";
        this.eventTouchend = "touchend";
    }

    this.listen();
}

InputManager.prototype.on = function (event, callback) {
    if (!this.events[event]) {
        this.events[event] = [];
    }
    this.events[event].push(callback);

    return this;
};

InputManager.prototype.emit = function (event, data) {
    var callbacks = this.events[event];
    if (callbacks) {
        callbacks.forEach(function (callback) {
            callback(data);
        });
    }
};

InputManager.prototype.listen = function () {
    var self = this;

    var map = {
        38: 0, // Up
        39: 3, // Right
        40: 2, // Down
        37: 1, // Left
        75: 0, // Vim up
        76: 3, // Vim right
        74: 2, // Vim down
        72: 1, // Vim left
        87: 0, // W
        68: 3, // D
        83: 2, // S
        65: 1 // A
    };

    // Respond to direction keys
    $(document).on("keydown", function (event) {
        var modifiers = event.altKey || event.ctrlKey || event.metaKey ||
            event.shiftKey;
        var mapped = map[event.which];

        if (!modifiers) {
            if (mapped !== undefined) {
                //event.preventDefault();
                self.emit("move", mapped);
            }
        }
    });

    // Respond to swipe events
    var touchStartClientX, touchStartClientY,
        touchLastClientX, touchLastClientY;

    $(document).on(self.eventTouchstart, function (event) {
        if ((!window.navigator.msPointerEnabled && event.touches.length > 1) ||
            event.targetTouches.length > 1) {
            return; // Ignore if touching with more than 1 finger
        }

        if (window.navigator.msPointerEnabled) {
            touchStartClientX = event.pageX;
            touchStartClientY = event.pageY;
        } else {
            touchStartClientX = event.touches[0].clientX;
            touchStartClientY = event.touches[0].clientY;
        }
    });

    $(document).on(self.eventTouchmove, function (event) {
        var touchClientX, touchClientY;

        if (window.navigator.msPointerEnabled) {
            touchClientX = event.pageX;
            touchClientY = event.pageY;
        } else {
            touchClientX = event.changedTouches[0].clientX;
            touchClientY = event.changedTouches[0].clientY;
        }

        var dx = touchClientX - touchStartClientX;
        self.emit("moving", dx);

        touchLastClientX = touchClientX;
        touchLastClientY = touchClientY;
    });

    $(document).on(self.eventTouchend, function (event) {
        if ((!window.navigator.msPointerEnabled && event.touches.length > 0) ||
            event.targetTouches.length > 0) {
            return; // Ignore if still touching with one or more fingers
        }

        var touchEndClientX, touchEndClientY;

        if (window.navigator.msPointerEnabled) {
            touchEndClientX = event.pageX;
            touchEndClientY = event.pageY;
        } else {
            touchEndClientX = event.changedTouches[0].clientX;
            touchEndClientY = event.changedTouches[0].clientY;
        }

        var dx = touchEndClientX - touchStartClientX;
        var absDx = Math.abs(dx);

        var dy = touchEndClientY - touchStartClientY;
        var absDy = Math.abs(dy);

        if (absDx > 50 || absDy > 20) {
            // (right : left) : (down : up)
            self.emit("move", absDx > absDy ? (dx > 0 ? 1 : 3) : (dy > 0 ? 2 : 0));
        } else {
            self.emit("notmove");
        }
    });
};