import exprEval from 'https://cdn.jsdelivr.net/npm/expr-eval@2.0.2/+esm';

const Parser = new exprEval.Parser();

window.calculateAmount = function () {
    try {
        // Attempt to parse the 'amount' value as a mathematical expression
        // rounding to 2 decimal places
        this.calculatedAmount = (Math.round(Parser.evaluate(this.amount) * 100) / 100).toFixed(2);
    } catch (e) {
        // If it fails, just use the raw value
        this.calculatedAmount = this.amount;
    }
}