var el = document.querySelectorAll('tbody')[0];
var sortable = Sortable.create(el, {
    ghostClass: "sortable-ghost",
    delay: 500,
    delayOnTouchOnly: true,
    animation: 150,
    // Disable sorting on the `end` event
    onEnd: function () {
        this.option("disabled", true);
    }
});

// Re-enable sorting on the `htmx:afterSwap` event
el.addEventListener("htmx:afterSwap", function () {
    sortable.option("disabled", false);
});