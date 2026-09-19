# -*- coding: utf-8 -*-
"""
EDA - Kham pha du lieu & truc quan hoa cho bo du lieu ban hang dien may.
Xuat toan bo bieu do vao outputs/figures/
"""
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import os

sns.set_theme(style="whitegrid", palette="viridis")
plt.rcParams["figure.dpi"] = 110
plt.rcParams["font.size"] = 11
plt.rcParams["axes.unicode_minus"] = False

FIG = "outputs/figures"
OUT = "data/processed"
os.makedirs(FIG, exist_ok=True)


def savefig(name):
    plt.tight_layout()
    plt.savefig(f"{FIG}/{name}.png", bbox_inches="tight")
    plt.close()


def fmt_money(ax, axis="y"):
    fmt = mticker.FuncFormatter(lambda x, p: f"{x/1e6:,.0f}M")
    if axis == "y":
        ax.yaxis.set_major_formatter(fmt)
    else:
        ax.xaxis.set_major_formatter(fmt)


def run_eda(df):
    completed = df[df["OrderStatus"] == "Completed"]

    # 1. Ty le trang thai don hang
    plt.figure(figsize=(6, 5))
    order_status = df.drop_duplicates("SalesOrderID")["OrderStatus"].value_counts()
    colors = ["#2E8B57", "#DC143C"]
    plt.pie(order_status.values, labels=order_status.index, autopct="%1.1f%%",
            colors=colors, startangle=90, wedgeprops={"edgecolor": "white"})
    plt.title("Ty le trang thai don hang (Completed vs Cancelled)")
    savefig("01_order_status_pie")

    # 2. Xu huong doanh thu theo thang
    monthly = completed.groupby("OrderYearMonth")["Revenue"].sum().reset_index()
    monthly = monthly.sort_values("OrderYearMonth")
    plt.figure(figsize=(13, 5))
    plt.plot(monthly["OrderYearMonth"], monthly["Revenue"], marker="o", color="#1f77b4", linewidth=2)
    plt.xticks(rotation=75, fontsize=8)
    ax = plt.gca()
    fmt_money(ax)
    plt.title("Xu huong doanh thu theo thang (don hang Completed)")
    plt.ylabel("Doanh thu (VND/EGP, trieu)")
    savefig("02_monthly_revenue_trend")

    # 3. Doanh thu theo nganh hang
    cat_rev = completed.groupby("CategoryName")["Revenue"].sum().sort_values(ascending=False)
    plt.figure(figsize=(9, 6))
    sns.barplot(x=cat_rev.values, y=cat_rev.index, hue=cat_rev.index, palette="mako", legend=False)
    ax = plt.gca()
    fmt_money(ax, "x")
    plt.title("Doanh thu theo nganh hang (Category)")
    plt.xlabel("Doanh thu")
    savefig("03_revenue_by_category")

    # 4. Top 15 thuong hieu theo doanh thu
    brand_rev = completed.groupby("BrandName")["Revenue"].sum().sort_values(ascending=False).head(15)
    plt.figure(figsize=(9, 7))
    sns.barplot(x=brand_rev.values, y=brand_rev.index, hue=brand_rev.index, palette="crest", legend=False)
    ax = plt.gca()
    fmt_money(ax, "x")
    plt.title("Top 15 thuong hieu theo doanh thu")
    plt.xlabel("Doanh thu")
    savefig("04_top_brands_revenue")

    # 5. Doanh thu theo kenh ban hang
    chn_rev = completed.groupby("ChannelName")["Revenue"].sum().sort_values(ascending=False)
    plt.figure(figsize=(7, 5))
    sns.barplot(x=chn_rev.index, y=chn_rev.values, hue=chn_rev.index, palette="flare", legend=False)
    ax = plt.gca()
    fmt_money(ax)
    plt.title("Doanh thu theo kenh ban hang")
    savefig("05_revenue_by_channel")

    # 6. Phan bo khach hang theo do tuoi
    age_order = ["18-24", "25-34", "35-44", "45-54", "55-64", "65+"]
    age_dist = df.drop_duplicates("CustomerID")["AgeBand"].value_counts()
    age_dist = age_dist.reindex([a for a in age_order if a in age_dist.index])
    plt.figure(figsize=(8, 5))
    sns.barplot(x=age_dist.index, y=age_dist.values, hue=age_dist.index, palette="viridis", legend=False)
    plt.title("Phan bo khach hang theo nhom tuoi")
    plt.ylabel("So luong khach hang")
    savefig("06_customer_age_distribution")

    # 7. Doanh thu theo tinh/thanh (Governorate) - top 10
    gov_rev = completed.groupby("GovernorateName")["Revenue"].sum().sort_values(ascending=False).head(10)
    plt.figure(figsize=(9, 6))
    sns.barplot(x=gov_rev.values, y=gov_rev.index, hue=gov_rev.index, palette="mako", legend=False)
    ax = plt.gca()
    fmt_money(ax, "x")
    plt.title("Top 10 khu vuc (Governorate) theo doanh thu")
    savefig("07_revenue_by_governorate")

    # 8. Phan phoi gia ban (histogram, log scale)
    plt.figure(figsize=(9, 5))
    sns.histplot(completed["ActualSellingPrice"], bins=60, color="#4C72B0", kde=True)
    plt.xscale("log")
    plt.title("Phan phoi don gia ban (thang log)")
    plt.xlabel("Don gia ban (log scale)")
    savefig("08_price_distribution")

    # 9. Ty le tra hang theo nganh hang
    ret_by_cat = df.groupby("CategoryName")["IsReturned"].mean().sort_values(ascending=False) * 100
    plt.figure(figsize=(9, 6))
    sns.barplot(x=ret_by_cat.values, y=ret_by_cat.index, hue=ret_by_cat.index, palette="rocket", legend=False)
    plt.title("Ty le tra hang (%) theo nganh hang")
    plt.xlabel("Ty le tra hang (%)")
    savefig("09_return_rate_by_category")

    # 10. Ly do tra hang
    reasons = df["ReturnReason"].value_counts()
    plt.figure(figsize=(8, 6))
    plt.pie(reasons.values, labels=reasons.index, autopct="%1.1f%%", startangle=90,
            wedgeprops={"edgecolor": "white"}, colors=sns.color_palette("Set2"))
    plt.title("Phan bo ly do tra hang")
    savefig("10_return_reasons")

    # 11. Heatmap doanh thu theo Thang x Nganh hang (nam gan nhat co du lieu day du)
    pivot = completed.pivot_table(index="CategoryName", columns="OrderMonth",
                                   values="Revenue", aggfunc="sum", fill_value=0)
    plt.figure(figsize=(11, 6))
    sns.heatmap(pivot / 1e6, cmap="YlGnBu", annot=False, cbar_kws={"label": "Doanh thu (trieu)"})
    plt.title("Heatmap doanh thu theo Thang x Nganh hang (gop tat ca cac nam)")
    plt.xlabel("Thang")
    savefig("11_heatmap_month_category")

    # 12. Ma tran tuong quan cac bien so
    num_cols = ["Quantity", "ActualSellingPrice", "DiscountPct", "Revenue", "Profit", "ShippingFeeAmount"]
    corr = completed[num_cols].corr()
    plt.figure(figsize=(7, 6))
    sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm", center=0, vmin=-1, vmax=1)
    plt.title("Ma tran tuong quan cac bien so")
    savefig("12_correlation_matrix")

    # 13. Doanh thu theo phuong thuc nhan hang
    ful_rev = completed.groupby("FulfillmentMethod")["Revenue"].sum().sort_values(ascending=False)
    plt.figure(figsize=(7, 5))
    sns.barplot(x=ful_rev.index, y=ful_rev.values, hue=ful_rev.index, palette="crest", legend=False)
    ax = plt.gca()
    fmt_money(ax)
    plt.title("Doanh thu theo phuong thuc nhan hang")
    savefig("13_revenue_by_fulfillment")

    # 14. Boxplot gia theo nganh hang (top 6 nganh doanh thu cao nhat)
    top6cat = cat_rev.head(6).index.tolist()
    plt.figure(figsize=(10, 6))
    sub = completed[completed["CategoryName"].isin(top6cat)]
    sns.boxplot(data=sub, x="CategoryName", y="ActualSellingPrice", hue="CategoryName",
                palette="Set3", showfliers=False, legend=False)
    plt.xticks(rotation=20)
    plt.yscale("log")
    plt.title("Phan phoi gia ban theo 6 nganh hang doanh thu cao nhat")
    savefig("14_price_boxplot_by_category")

    # 15. So luong don hang theo ngay trong tuan
    dow_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    dow = df.drop_duplicates("SalesOrderID")["OrderDayOfWeek"].value_counts().reindex(dow_order)
    plt.figure(figsize=(9, 5))
    sns.barplot(x=dow.index, y=dow.values, hue=dow.index, palette="viridis", legend=False)
    plt.title("So luong don hang theo ngay trong tuan")
    plt.xticks(rotation=30)
    savefig("15_orders_by_dayofweek")

    print("Da xuat 15 bieu do EDA vao", FIG)

    # Bang tom tat so lieu tong quan
    summary = {
        "TongSoDonHang": df["SalesOrderID"].nunique(),
        "TongSoKhachHang": df["CustomerID"].nunique(),
        "TongSoSanPham(SKU)": df["SKU_ID"].nunique(),
        "TongDoanhThu(Completed)": completed["Revenue"].sum(),
        "DoanhThuTrungBinh/Don": completed.groupby("SalesOrderID")["Revenue"].sum().mean(),
        "TyLeHuyDon(%)": (order_status.get("Cancelled", 0) / order_status.sum() * 100),
        "TyLeTraHang(%)": df["IsReturned"].mean() * 100,
        "KhoangThoiGian": f"{df['OrderDate'].min().date()} - {df['OrderDate'].max().date()}",
    }
    pd.DataFrame([summary]).T.rename(columns={0: "GiaTri"}).to_csv(f"{OUT}/eda_summary.csv")
    print(summary)
    return summary


if __name__ == "__main__":
    df = pd.read_parquet(f"{OUT}/sales_fact.parquet")
    run_eda(df)
