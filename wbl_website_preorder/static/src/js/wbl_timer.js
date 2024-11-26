/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";

publicWidget.registry.ProductTimer = publicWidget.Widget.extend({
    selector: '.product_timer_js',
    init: function () {
        this._super.apply(this, arguments);
        console.log("Initializing product timer...");
        $(document).ready(() => {
            this._startTimer();
        });
    },

    _startTimer: function () {
        var productAvailableDateStr = $('#wbl_product_available_date').val();
        if (productAvailableDateStr) {
            var productEndTime = new Date(productAvailableDateStr).getTime();
            this._updateProductTimer(productEndTime);
        }
    },

    _formatTime: function (time) {
        return time < 10 ? '0' + time : time;
    },

    _updateProductTimer: function (endTime) {
        var updateTimer = () => {
            var now = new Date().getTime();
            var distance = endTime - now;

            if (distance < 0) {
                $('#days').text("00");
                $('#hours').text("00");
                $('#minutes').text("00");
                $('#seconds').text("00");
                return;
            }

            var days = Math.floor(distance / (1000 * 60 * 60 * 24));
            var hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
            var minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
            var seconds = Math.floor((distance % (1000 * 60)) / 1000);

            $('#days').text(this._formatTime(days));
            $('#hours').text(this._formatTime(hours));
            $('#minutes').text(this._formatTime(minutes));
            $('#seconds').text(this._formatTime(seconds));

            setTimeout(updateTimer, 1000);
        };

        updateTimer();
    }
});

export default publicWidget.registry.ProductTimer;



publicWidget.registry.PreorderTimer = publicWidget.Widget.extend({
    selector: '.countdown-timer',
    start: function () {
        const self = this;
        this.$el.each(function () {
            const $timer = $(this);
            const availableDate = new Date($timer.data('available-date')).getTime();
            const themeColor = $timer.data('theme-color'); // Get the theme color from data attribute
            self.updateTimer($timer, availableDate, themeColor);
            setInterval(function () {
                self.updateTimer($timer, availableDate, themeColor);
            }, 1000);
        });
    },
    updateTimer: function ($timer, availableDate, themeColor) {
        const now = new Date().getTime();
        const distance = availableDate - now;

        if (distance < 0) {
            $timer.html("Preorder available");
            return;
        }

        const days = Math.floor(distance / (1000 * 60 * 60 * 24));
        const hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
        const minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
        const seconds = Math.floor((distance % (1000 * 60)) / 1000);

        // Update timer display
        $timer.find('.timer-days').text(days < 10 ? '0' + days : days);
        $timer.find('.timer-hours').text(hours < 10 ? '0' + hours : hours);
        $timer.find('.timer-minutes').text(minutes < 10 ? '0' + minutes : minutes);
        $timer.find('.timer-seconds').text(seconds < 10 ? '0' + seconds : seconds);
    },
});

export default publicWidget.registry.PreorderTimer;

