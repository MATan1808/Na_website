import { Multirange } from "@website/../lib/multirange/multirange_custom";

const origFormatNumber = Multirange.prototype.formatNumber;

Multirange.prototype.formatNumber = function (number) {
    if (this.currency === "₫" || Number(this.step) >= 1) {
        const language = document.querySelector("html")?.getAttribute("lang") || "vi-VN";
        const locale = (() => {
            switch (language) {
                case "sr@latin":
                    return "sr-Latn";
                case "sr@Cyrl":
                    return "sr-Cyrl";
                default:
                    return language.replaceAll("_", "-");
            }
        })();
        const rounded = Math.round(Number(number) || 0);
        let formatted = rounded.toLocaleString(locale, {
            minimumFractionDigits: 0,
            maximumFractionDigits: 0,
        });
        if (this.currency && this.currency.length) {
            formatted =
                this.currencyPosition === "after"
                    ? `${formatted} ${this.currency}`
                    : `${this.currency} ${formatted}`;
        }
        return formatted;
    }
    return origFormatNumber.call(this, number);
};
