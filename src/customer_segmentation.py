# -*- coding: utf-8 -*-
"""
Bai toan 1: Phan cum khach hang (RFM + K-Means)
"""
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.decomposition import PCA
import joblib
import os

sns.set_theme(style="whitegrid")
FIG = "outputs/figures"
OUT = "data/processed"
MODEL = "outputs/models"
os.makedirs(MODEL, exist_ok=True)


def compute_rfm(df):
    """Tinh Recency, Frequency, Monetary cho tung khach hang tu don hang Completed."""
    completed = df[df["OrderStatus"] == "Completed"].copy()
    snapshot_date = completed["OrderDate"].max() + pd.Timedelta(days=1)

    orders = completed.groupby("SalesOrderID").agg(
        CustomerID=("CustomerID", "first"),
        OrderDate=("OrderDate", "first"),
        OrderRevenue=("Revenue", "sum"),
    ).reset_index()

    rfm = orders.groupby("CustomerID").agg(
        Recency=("OrderDate", lambda x: (snapshot_date - x.max()).days),
        Frequency=("SalesOrderID", "nunique"),
        Monetary=("OrderRevenue", "sum"),
    ).reset_index()

    rfm["AvgOrderValue"] = rfm["Monetary"] / rfm["Frequency"]
    return rfm


def find_optimal_k(X_scaled, k_range=range(2, 9)):
    """Tim so cum toi uu bang phuong phap Elbow va Silhouette Score."""
    inertias, silhouettes = [], []
    for k in k_range:
        km = KMeans(n_clusters=k, random_state=42, n_init=10)
        labels = km.fit_predict(X_scaled)
        inertias.append(km.inertia_)
        silhouettes.append(silhouette_score(X_scaled, labels, sample_size=20000, random_state=42))

    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    axes[0].plot(list(k_range), inertias, marker="o", color="#1f77b4")
    axes[0].set_title("Phuong phap Elbow")
    axes[0].set_xlabel("So cum (k)")
    axes[0].set_ylabel("Inertia (WCSS)")

    axes[1].plot(list(k_range), silhouettes, marker="o", color="#d62728")
    axes[1].set_title("Silhouette Score theo so cum")
    axes[1].set_xlabel("So cum (k)")
    axes[1].set_ylabel("Silhouette Score")
    plt.tight_layout()
    plt.savefig(f"{FIG}/16_kmeans_elbow_silhouette.png", bbox_inches="tight")
    plt.close()

    best_score = max(silhouettes)
    best_k = next(k for k, s in zip(k_range, silhouettes) if s >= best_score - 0.01)
    return best_k, dict(zip(k_range, silhouettes))


def label_segment(row):
    """Gan nhan kinh doanh cho tung cum dua tren dac diem RFM trung binh."""
    if row["Recency"] <= row["Recency_median"] and row["Frequency"] >= row["Frequency_median"] and row["Monetary"] >= row["Monetary_median"]:
        return "Khach hang VIP / Trung thanh"
    if row["Recency"] > row["Recency_median"] * 1.5 and row["Frequency"] <= row["Frequency_median"]:
        return "Khach hang co nguy co roi bo (Churn Risk)"
    if row["Frequency"] <= row["Frequency_median"] and row["Monetary"] <= row["Monetary_median"]:
        return "Khach hang moi / Gia tri thap"
    return "Khach hang tiem nang"


def run_segmentation(df):
    print(">> Tinh toan RFM...")
    rfm = compute_rfm(df)
    print("   So khach hang co don hang hop le:", len(rfm))

    # Loc outlier cuc doan (khach hang mua qua nhieu / qua it bat thuong)
    for col in ["Frequency", "Monetary"]:
        q99 = rfm[col].quantile(0.995)
        rfm = rfm[rfm[col] <= q99]

    features = ["Recency", "Frequency", "Monetary"]
    X = rfm[features].copy()
    X_log = np.log1p(X)  # giam do lech (skewness)
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X_log)

    print(">> Tim so cum toi uu (Elbow + Silhouette)...")
    best_k, sil_scores = find_optimal_k(X_scaled)
    print(f"   So cum toi uu duoc chon: k={best_k}")
    print("   Silhouette scores:", sil_scores)

    kmeans = KMeans(n_clusters=best_k, random_state=42, n_init=10)
    rfm["Cluster"] = kmeans.fit_predict(X_scaled)
    final_sil = silhouette_score(X_scaled, rfm["Cluster"], sample_size=20000, random_state=42)
    print(f"   Silhouette score cuoi cung: {final_sil:.4f}")

    # Gan nhan kinh doanh de de hieu
    rfm["Recency_median"] = rfm["Recency"].median()
    rfm["Frequency_median"] = rfm["Frequency"].median()
    rfm["Monetary_median"] = rfm["Monetary"].median()
    cluster_profile_tmp = rfm.groupby("Cluster")[["Recency", "Frequency", "Monetary"]].mean()

    # Xep hang cum theo Monetary va Recency de gan nhan
    prof = cluster_profile_tmp.copy()
    prof["MonetaryRank"] = prof["Monetary"].rank(ascending=True)
    prof["RecencyGoodRank"] = (-prof["Recency"]).rank(ascending=True)
    prof["Score"] = prof["MonetaryRank"] * 2 + prof["RecencyGoodRank"]
    prof = prof.sort_values("Score", ascending=False)

    ordered_clusters = prof.index.tolist()
    groups = np.array_split(ordered_clusters, 3)  # nhom cao / trung binh / thap
    tier_names = ["Khach hang VIP / Trung thanh", "Khach hang tiem nang / Trung binh",
                  "Khach hang gia tri thap / Nguy co roi bo"]

    label_map = {}
    for tier_idx, group in enumerate(groups):
        tier_name = tier_names[min(tier_idx, len(tier_names) - 1)]
        if len(group) == 1:
            label_map[group[0]] = tier_name
        else:
            for j, cl in enumerate(group, start=1):
                label_map[cl] = f"{tier_name} ({j})"
    rfm["SegmentName"] = rfm["Cluster"].map(label_map)

    # Truc quan hoa: PCA 2D scatter
    pca = PCA(n_components=2, random_state=42)
    coords = pca.fit_transform(X_scaled)
    rfm["PC1"], rfm["PC2"] = coords[:, 0], coords[:, 1]

    plt.figure(figsize=(9, 7))
    sns.scatterplot(data=rfm.sample(min(15000, len(rfm)), random_state=42),
                     x="PC1", y="PC2", hue="SegmentName", palette="tab10", alpha=0.5, s=15)
    plt.title(f"Phan khuc khach hang bang K-Means (k={best_k}) - Chieu PCA 2D")
    plt.legend(bbox_to_anchor=(1.02, 1), loc="upper left", fontsize=8)
    plt.tight_layout()
    plt.savefig(f"{FIG}/17_customer_segments_pca.png", bbox_inches="tight")
    plt.close()

    # Bar chart so luong khach hang / phan khuc
    seg_count = rfm["SegmentName"].value_counts()
    plt.figure(figsize=(9, 5))
    sns.barplot(x=seg_count.values, y=seg_count.index, hue=seg_count.index, palette="Set2", legend=False)
    plt.title("So luong khach hang theo phan khuc")
    plt.xlabel("So khach hang")
    plt.tight_layout()
    plt.savefig(f"{FIG}/18_segment_customer_count.png", bbox_inches="tight")
    plt.close()

    # Radar-style: bang profile trung binh moi phan khuc
    profile = rfm.groupby("SegmentName")[["Recency", "Frequency", "Monetary", "AvgOrderValue"]].mean().round(1)
    profile["SoLuongKH"] = rfm["SegmentName"].value_counts()
    profile = profile.sort_values("Monetary", ascending=False)

    fig, ax = plt.subplots(figsize=(13, 4.5))
    ax.axis("off")
    tbl = ax.table(cellText=profile.reset_index().round(1).values,
                    colLabels=["Phan khuc", "Recency(ngay)", "Frequency(don)", "Monetary", "GTB don hang", "So KH"],
                    cellLoc="center", loc="center",
                    colWidths=[0.34, 0.13, 0.13, 0.13, 0.13, 0.13])
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(9)
    tbl.scale(1, 1.8)
    for (row, col), cell in tbl.get_celld().items():
        if col == 0:
            cell.set_text_props(ha="left")
            cell.PAD = 0.02
    plt.title("Ho so trung binh (profile) tung phan khuc khach hang", pad=20)
    plt.tight_layout()
    plt.savefig(f"{FIG}/19_segment_profile_table.png", bbox_inches="tight", dpi=130, pad_inches=0.3)
    plt.close()

    rfm.to_csv(f"{OUT}/customer_segments.csv", index=False)
    joblib.dump({"scaler": scaler, "kmeans": kmeans, "features": features, "label_map": label_map},
                f"{MODEL}/customer_segmentation_model.pkl")

    print(">> Ho so cac phan khuc:")
    print(profile)
    return rfm, profile, final_sil


if __name__ == "__main__":
    df = pd.read_parquet(f"{OUT}/sales_fact.parquet")
    run_segmentation(df)
