"""Audit local Electronics data for weekly price forecasting, not model selection on test."""

import json
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
OUT = ROOT / "outputs" / "reports" / "electronics_price_feasibility"


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    specs = {
        "SalesOrders": ["SalesOrderID"], "SalesOrderLines": ["SalesOrderLineID"],
        "ProductVariants": ["SKU_ID"], "Products": ["ProductID"],
        "Brands": ["BrandID"], "Subcategories": ["SubcategoryID"],
        "Categories": ["CategoryID"], "Promotions": ["PromotionID"],
    }
    frames, checks = {}, []
    for name, keys in specs.items():
        frame = pd.read_csv(RAW / f"{name}.csv")
        unique = frame.drop_duplicates()
        conflicts = unique.duplicated(keys, keep=False)
        checks.append({"table": name, "raw_rows": len(frame), "full_duplicates": int(frame.duplicated().sum()),
                       "conflicting_key_rows": int(conflicts.sum()), "missing_key_rows": int(unique[keys].isna().any(axis=1).sum())})
        frames[name] = unique.loc[~conflicts & ~unique[keys].isna().any(axis=1)].copy()
    orders, lines = frames["SalesOrders"], frames["SalesOrderLines"]
    status = orders.OrderStatus.astype("string").str.strip().str.lower().replace({"complete": "completed", "canceled": "cancelled"})
    orders["OrderDate"] = pd.to_datetime(orders.OrderDate, errors="coerce")
    links = {}
    for child, key, parent in [("SalesOrderLines", "SalesOrderID", "SalesOrders"),
                               ("SalesOrderLines", "SKU_ID", "ProductVariants"),
                               ("ProductVariants", "ProductID", "Products"),
                               ("Products", "BrandID", "Brands"),
                               ("Products", "SubcategoryID", "Subcategories"),
                               ("Subcategories", "CategoryID", "Categories")]:
        links[f"{child}.{key}->{parent}"] = int((~frames[child][key].isin(frames[parent][key])).sum())
    valid_orders = orders.loc[status.eq("completed") & orders.OrderDate.between("2023-07-01", "2025-12-31")]
    business_conflicts = lines.duplicated(["SalesOrderID", "LineNumber"], keep=False)
    valid_lines = lines.loc[~business_conflicts & lines.Quantity.gt(0) & lines.ActualSellingPrice.gt(0)
                           & np.isfinite(lines.Quantity) & np.isfinite(lines.ActualSellingPrice)]
    data = valid_lines.merge(valid_orders[["SalesOrderID", "OrderDate"]], on="SalesOrderID", validate="many_to_one")
    data = data.loc[data.SKU_ID.isin(frames["ProductVariants"].SKU_ID)].copy()
    # Retain only full Monday–Sunday weeks inside the declared research interval.
    data["week"] = data.OrderDate.dt.to_period("W-SUN").dt.start_time
    data = data.loc[data.week.between("2023-07-03", "2025-12-22")].copy()
    data["value"] = data.Quantity * data.ActualSellingPrice
    data["regular_value"] = data.Quantity * data.RegularUnitPrice
    weekly = data.groupby(["SKU_ID", "week"], as_index=False).agg(
        qty=("Quantity", "sum"), value=("value", "sum"), regular_value=("regular_value", "sum"),
        line_count=("SalesOrderLineID", "size"))
    weekly["price"] = weekly.value / weekly.qty
    assert not weekly.duplicated(["SKU_ID", "week"]).any()
    assert np.isclose(weekly.qty.sum(), data.Quantity.sum())
    assert np.isclose(weekly.value.sum(), data.value.sum())
    calendar = pd.date_range("2023-07-03", "2025-12-22", freq="7D")
    panel = pd.MultiIndex.from_product([sorted(weekly.SKU_ID.unique()), calendar], names=["SKU_ID", "week"]).to_frame(index=False)
    panel = panel.merge(weekly, on=["SKU_ID", "week"], how="left", validate="one_to_one").sort_values(["SKU_ID", "week"])
    group = panel.groupby("SKU_ID", sort=False)
    panel["anchor"] = group.price.ffill()
    panel["observed_week"] = panel.week.where(panel.price.notna())
    panel["last_observed_week"] = panel.groupby("SKU_ID").observed_week.ffill()
    panel["recency"] = (panel.week - panel.last_observed_week).dt.days / 7
    panel["target"] = panel.groupby("SKU_ID").price.shift(-1)
    panel["target_week"] = panel.week + pd.Timedelta(weeks=1)
    panel["history_observations"] = panel.price.notna().groupby(panel.SKU_ID).cumsum()
    eligible = panel.loc[panel.anchor.notna() & panel.target_week.le(calendar[-1])].copy()
    target_weeks = calendar[1:]
    train_end = target_weeks[int(len(target_weeks) * 0.7) - 1]
    val_end = target_weeks[int(len(target_weeks) * 0.85) - 1]
    eligible["split"] = np.select([eligible.target_week.le(train_end), eligible.target_week.le(val_end)], ["train", "validation"], default="test")
    eligible["relative_change"] = (eligible.target / eligible.anchor - 1).abs()
    summary = []
    for name, subset in eligible.groupby("split"):
        observed = subset.loc[subset.target.notna()]
        summary.append({"split": name, "eligible_origins": len(subset), "observed_labels": len(observed),
                        "label_coverage_pct": 100 * len(observed) / len(subset), "skus": subset.SKU_ID.nunique(),
                        "target_week_min": str(subset.target_week.min().date()), "target_week_max": str(subset.target_week.max().date())})
    # Dynamics and baseline inspected on train/validation only. Test reserved for final experiments.
    dynamics = []
    for name in ["train", "validation"]:
        observed = eligible.loc[eligible.split.eq(name) & eligible.target.notna()].copy()
        error = (observed.target - observed.anchor).abs()
        row = {"split": name, "rows": len(observed), "last_price_WAPE_pct": 100 * error.sum() / observed.target.sum(),
               "last_price_MAE_source_currency": error.mean(),
               "unchanged_within_1cent_pct": 100 * error.le(0.01).mean(),
               "median_relative_change_pct": 100 * observed.relative_change.median()}
        for threshold in [0.001, 0.01, 0.05, 0.1]:
            mask = observed.relative_change.gt(threshold)
            row[f"change_gt_{threshold:g}_pct"] = 100 * mask.mean()
            row[f"change_gt_{threshold:g}_count"] = int(mask.sum())
        dynamics.append(row)
    sku_stats = panel.groupby("SKU_ID").agg(observed_weeks=("price", "count"), first_observed=("observed_week", "min"), last_observed=("observed_week", "max"))
    # Retrospective first-to-last coverage is descriptive only, never a deployment cohort rule.
    sku_stats["observed_span_weeks"] = (sku_stats.last_observed - sku_stats.first_observed).dt.days / 7 + 1
    sku_stats["coverage_within_observed_span"] = sku_stats.observed_weeks / sku_stats.observed_span_weeks
    pretest = eligible.loc[~eligible.split.eq("test")]
    qty = weekly.qty
    regular_nunique = data.groupby("SKU_ID").RegularUnitPrice.nunique()
    price_nunique = data.groupby("SKU_ID").ActualSellingPrice.nunique()
    report = {
        "scope": "Local data audit, train/validation dynamics only; not source authenticity verification or final benchmark",
        "raw_table_count": len(list(RAW.glob("*.csv"))), "quality": checks, "orphan_counts": links,
        "completed_orders_within_period": len(valid_orders), "retained_full_week_lines": len(data),
        "weekly_observed_rows": len(weekly), "skus": weekly.SKU_ID.nunique(), "full_weeks": len(calendar),
        "sku_observed_weeks_quantiles": sku_stats.observed_weeks.quantile([0, .1, .25, .5, .75, .9, 1]).to_dict(),
        "sku_coverage_within_observed_span_quantiles": sku_stats.coverage_within_observed_span.quantile([0, .1, .25, .5, .75, .9, 1]).to_dict(),
        "sku_with_at_least_32_observed_weeks": int(sku_stats.observed_weeks.ge(32).sum()),
        "weekly_qty_quantiles": qty.quantile([.1, .5, .9]).to_dict(),
        "sku_constant_regular_unit_price_count": int(regular_nunique.eq(1).sum()),
        "sku_constant_actual_line_price_count": int(price_nunique.eq(1).sum()),
        "line_actual_equals_regular_pct": 100 * np.isclose(data.ActualSellingPrice, data.RegularUnitPrice, atol=.01, rtol=0).mean(),
        "discount_without_promotion_pct": 100 * ((data.ActualSellingPrice < data.RegularUnitPrice - .01) & data.PromotionID.isna()).mean(),
        "actual_above_regular_count": int((data.ActualSellingPrice > data.RegularUnitPrice + .01).sum()),
        "missing_unit_cost_pct": 100 * data.UnitCostAtSale.isna().mean(),
        "pretest_labeled_origins_with_history_le4_pct": 100 * pretest.loc[pretest.target.notna(), "history_observations"].le(4).mean(),
        "split_summary": summary, "train_validation_dynamics": dynamics,
        "limitations": ["Synthetic/real provenance, license and currency not verified by this audit", "No ingest timestamp; actual availability latency unknown", "No controlled benchmark of model gains yet", "History sparsity is heterogeneous; not automatically cold start or few-shot"],
    }
    for name, frame in [("quality", pd.DataFrame(checks)), ("split_summary", pd.DataFrame(summary)), ("price_dynamics_train_validation", pd.DataFrame(dynamics)), ("sku_history", sku_stats.reset_index())]:
        frame.to_csv(OUT / f"{name}.csv", index=False, encoding="utf-8-sig")
    (OUT / "audit_summary.json").write_text(json.dumps(report, indent=2, ensure_ascii=False, default=lambda v: v.item() if isinstance(v, np.generic) else str(v)), encoding="utf-8")
    print(json.dumps(report, indent=2, ensure_ascii=False, default=lambda v: v.item() if isinstance(v, np.generic) else str(v)))


if __name__ == "__main__":
    main()