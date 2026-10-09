// Live preview for the cost calculator. Mirrors app/helpers/costing_helpers.py —
// keep the two in step. Nothing computed here is trusted: the server recalculates
// every total from its own unit costs when the recipe is saved.
(function () {
    "use strict";

    const form = document.getElementById("recipe-form");
    if (!form) {
        return;
    }

    const rows = document.getElementById("recipe-items");
    const template = document.getElementById("recipe-item-template");
    const addButton = document.getElementById("add-recipe-item");
    const unitCosts = JSON.parse(form.dataset.materialCosts || "{}");

    let nextIndex = rows.querySelectorAll(".recipe-item-row").length;

    function number(value) {
        const parsed = parseFloat(value);
        return Number.isFinite(parsed) ? parsed : 0;
    }

    function fieldValue(name) {
        const field = form.elements[name];
        return field ? number(field.value) : 0;
    }

    function setSummary(id, value) {
        document.getElementById(id).textContent = value.toFixed(2);
    }

    function recalculate() {
        let totalMaterialCost = 0;

        rows.querySelectorAll(".recipe-item-row").forEach(function (row) {
            const materialId = row.querySelector(".recipe-item-material").value;
            const quantity = number(row.querySelector(".recipe-item-quantity").value);
            const subtotal = quantity * (unitCosts[materialId] || 0);

            row.querySelector(".recipe-item-subtotal").textContent = subtotal.toFixed(2);
            totalMaterialCost += subtotal;
        });

        const laborCost = fieldValue("labor_hours") * fieldValue("hourly_rate");
        const overheadCost = (totalMaterialCost + laborCost) * (fieldValue("overhead_percentage") / 100);
        const netCost = totalMaterialCost + laborCost + overheadCost;
        const priceBeforeTax = netCost * (1 + fieldValue("profit_margin_percentage") / 100);
        const suggestedPrice = priceBeforeTax * (1 + fieldValue("tax_percentage") / 100);

        setSummary("summary-material-cost", totalMaterialCost);
        setSummary("summary-labor-cost", laborCost);
        setSummary("summary-overhead-cost", overheadCost);
        setSummary("summary-net-cost", netCost);
        setSummary("summary-price-before-tax", priceBeforeTax);
        setSummary("summary-tax-amount", suggestedPrice - priceBeforeTax);
        setSummary("summary-suggested-price", suggestedPrice);
    }

    addButton.addEventListener("click", function () {
        // WTForms reads the indices out of the field names, and only needs them
        // sorted — gaps left by removed rows are fine, so the counter never resets.
        const markup = template.innerHTML.split("__index__").join(String(nextIndex));
        const holder = document.createElement("tbody");

        holder.innerHTML = markup.trim();
        rows.appendChild(holder.firstElementChild);
        nextIndex += 1;
        recalculate();
    });

    rows.addEventListener("click", function (event) {
        if (!event.target.classList.contains("recipe-item-remove")) {
            return;
        }

        // Keep one row so the form never renders empty.
        if (rows.querySelectorAll(".recipe-item-row").length > 1) {
            event.target.closest(".recipe-item-row").remove();
        } else {
            rows.querySelector(".recipe-item-material").value = "";
            rows.querySelector(".recipe-item-quantity").value = "";
        }

        recalculate();
    });

    form.addEventListener("input", recalculate);
    form.addEventListener("change", recalculate);

    recalculate();
})();
