// These have to be var because HTMX re-evaluates the script tag
// when using hx-boost
var balanceCtx = document.getElementById('balanceChart');
var categoriesCtx = document.getElementById('categoriesChart');

// Normalize the category data for this month, last month, and last year
// The categories for last month and last year are not guaranteed to be the same
// as this month so we need to filter out the ones that don't exist in this month,
// add the ones that do exist in this month but not in last month/last year as 0,
// and sort them in the same order as this month
categoriesData = categoriesData.map(a => ({
    name: a.name,
    amount: Math.abs(a.amount / 100),
}));
lastMonthCategoriesData = lastMonthCategoriesData.map(a => ({
    name: a.name,
    amount: Math.abs(a.amount / 100),
}));
lastYearCategoriesData = lastYearCategoriesData.map(a => ({
    name: a.name,
    amount: Math.abs(a.amount / 100),
}));

lastMonthCategoriesData = categoriesData.map(a => ({
    name: a.name,
    amount: lastMonthCategoriesData.find(b => b.name === a.name)?.amount ?? 0,
}));
lastYearCategoriesData = categoriesData.map(a => ({
    name: a.name,
    amount: lastYearCategoriesData.find(b => b.name === a.name)?.amount ?? 0,
}));
categoriesData.sort((a, b) => a.name.localeCompare(b.name));
lastMonthCategoriesData.sort((a, b) => a.name.localeCompare(b.name));
lastYearCategoriesData.sort((a, b) => a.name.localeCompare(b.name));

console.log(categoriesData);
console.log(lastMonthCategoriesData)


new Chart(balanceCtx, {
    type: 'line',
    data: {
        labels: Array(balanceData[0].days_in_month).fill().map((_, i) => i + 1),
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
                    title: function (context) {
                        return `${ordinalOf(context[0].dataIndex + 1)} ${monthName}`;
                    },
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
                data: categoriesData.map(a => a.amount),
            },
            {
                label: 'Last Month',
                data: lastMonthCategoriesData.map(a => a.amount),
            },
            {
                label: 'Last Year',
                data: lastYearCategoriesData.map(a => a.amount),
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
