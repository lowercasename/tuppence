// These have to be var because HTMX re-evaluates the script tag
// when using hx-boost
var balanceCtx = document.getElementById('balanceChart');
var categoriesCtx = document.getElementById('categoriesChart');

new Chart(balanceCtx, {
    type: 'line',
    data: {
        labels: balanceData[0].balances.map((_, i) => i),
        datasets: balanceData.map(a => ({
            label: a.name,
            data: a.balances.map(b => b / 100),
        }))
    },
    options: {
        scales: {
            y: {
                ticks: {
                    callback: function (value, index, values) {
                        return value.toLocaleString("en-GB", { style: "currency", currency: "GBP" });
                    }
                }
            },
            x: {
                ticks: {
                    callback: function (value, index, values) {
                        return value + 1;
                    }
                }
            }
        },
        plugins: {
            tooltip: {
                callbacks: {
                    label: function (context) {
                        return context.dataset.label + ': ' + context.parsed.y.toLocaleString("en-GB", { style: "currency", currency: "GBP" });
                    }
                }
            }
        }
    }
});

new Chart(categoriesCtx, {
    type: 'bar',
    data: {
        labels: categoriesData.map(a => a.name),
        datasets: [
            {
                label: 'This Month',
                data: categoriesData.map(a => Math.abs(a.amount / 100)),
            },
            {
                label: 'Last Month',
                data: lastMonthCategoriesData.map(a => Math.abs(a.amount / 100)),
            },
            {
                label: 'Last Year',
                data: lastYearCategoriesData.map(a => Math.abs(a.amount / 100)),
            },
        ]
    },
    options: {
        scales: {
            y: {
                ticks: {
                    callback: function (value, index, values) {
                        return value.toLocaleString("en-GB", { style: "currency", currency: "GBP" });
                    }
                }
            },
        },
        plugins: {
            tooltip: {
                callbacks: {
                    label: function (context) {
                        return context.dataset.label + ': ' + context.parsed.y.toLocaleString("en-GB", { style: "currency", currency: "GBP" });
                    }
                }
            },
        }
    }
});
