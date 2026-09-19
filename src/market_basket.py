# -*- coding: utf-8 -*-
"""
Bai toan 4: Luat ket hop - Phan tich gio hang (Market Basket Analysis)
"""
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
from mlxtend.frequent_patterns import apriori, association_rules
from mlxtend.preprocessing import TransactionEncoder
import os

sns.set_theme(style="whitegrid")
FIG = "outputs/figures"
OUT = "data/processed"


def build_transactions(df, level="SubcategoryName", min_items=2):
    """Xay dung danh sach giao dich (transactions): moi don hang la 1 giao dich
    chua danh sach cac subcategory/brand da mua. Chi giu don hang Completed va
    co >= min_items nganh hang khac nhau (de luat ket hop co y nghia)."""
    completed = df[df["OrderStatus"] == "Completed"]
    basket = completed.groupby("SalesOrderID")[level].apply(lambda x: sorted(set(x.dropna())))
    basket = basket[basket.apply(len) >= min_items]
    return basket


def run_market_basket(df):
    print(">> Xay dung du lieu gio hang theo Nganh hang (Subcategory)...")
    basket = build_transactions(df, level="SubcategoryName", min_items=2)
    print(f"   So don hang co >=2 nganh hang khac nhau: {len(basket)}")

    te = TransactionEncoder()
    te_ary = te.fit(basket).transform(basket)
    basket_df = pd.DataFrame(te_ary, columns=te.columns_)

    print(">> Chay thuat toan Apriori tim tap pho bien...")
    freq_items = apriori(basket_df, min_support=0.002, use_colnames=True, max_len=3)
    print(f"   So tap pho bien tim duoc: {len(freq_items)}")

    if len(freq_items) == 0:
        print("   Khong tim duoc tap pho bien - giam min_support")
        return None, None

    rules = association_rules(freq_items, metric="lift", min_threshold=1.0)
    rules = rules.sort_values("lift", ascending=False)
    rules["antecedents_str"] = rules["antecedents"].apply(lambda x: ", ".join(sorted(x)))
    rules["consequents_str"] = rules["consequents"].apply(lambda x: ", ".join(sorted(x)))

    rules_export = rules[["antecedents_str", "consequents_str", "support", "confidence", "lift"]].copy()
    rules_export.columns = ["NeuMua(Antecedent)", "ThiCungMua(Consequent)", "Support", "Confidence", "Lift"]
    rules_export.to_csv(f"{OUT}/association_rules_subcategory.csv", index=False)

    print(f">> Tim duoc {len(rules)} luat ket hop (lift >= 1.0)")
    print(rules_export.head(15).to_string(index=False))

    # Bieu do: Top 15 luat theo Lift
    top_rules = rules_export.sort_values("Lift", ascending=False).head(15).copy()
    top_rules["RuleLabel"] = top_rules["NeuMua(Antecedent)"] + "  ->  " + top_rules["ThiCungMua(Consequent)"]
    plt.figure(figsize=(11, 8))
    sns.barplot(data=top_rules, x="Lift", y="RuleLabel", hue="RuleLabel", palette="rocket", legend=False)
    plt.title("Top 15 luat ket hop theo do do Lift (Nganh hang mua cung nhau)")
    plt.xlabel("Lift (do manh cua luat)")
    plt.ylabel("")
    plt.tight_layout()
    plt.savefig(f"{FIG}/27_association_rules_top_lift.png", bbox_inches="tight")
    plt.close()

    # Scatter: Support vs Confidence, mau theo Lift
    plt.figure(figsize=(8, 6))
    sc = plt.scatter(rules["support"], rules["confidence"], c=rules["lift"], cmap="viridis", s=40, alpha=0.7)
    plt.colorbar(sc, label="Lift")
    plt.xlabel("Support")
    plt.ylabel("Confidence")
    plt.title("Cac luat ket hop: Support vs Confidence (mau = Lift)")
    plt.tight_layout()
    plt.savefig(f"{FIG}/28_association_rules_scatter.png", bbox_inches="tight")
    plt.close()

    # Bang top 10 luat (hinh anh de dua vao bao cao)
    disp = top_rules[["NeuMua(Antecedent)", "ThiCungMua(Consequent)", "Support", "Confidence", "Lift"]].head(10).round(3)
    fig, ax = plt.subplots(figsize=(12, 4))
    ax.axis("off")
    tbl = ax.table(cellText=disp.values, colLabels=disp.columns, cellLoc="center", loc="center")
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(8.5)
    tbl.scale(1, 1.8)
    plt.title("Top 10 luat ket hop manh nhat (theo Lift)", pad=30)
    plt.tight_layout()
    plt.savefig(f"{FIG}/29_top10_rules_table.png", bbox_inches="tight", dpi=130, pad_inches=0.3)
    plt.close()

    return freq_items, rules_export


if __name__ == "__main__":
    df = pd.read_parquet(f"{OUT}/sales_fact.parquet")
    run_market_basket(df)
