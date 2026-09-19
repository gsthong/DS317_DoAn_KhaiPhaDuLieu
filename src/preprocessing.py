"""
DS317 - Khai Pha Du Lieu Trong Doanh Nghiep
Module tien xu ly du lieu: doc 26 bang CSV goc, lam sach, ghep noi thanh
cac bang phan tich (fact tables) phuc vu EDA va cac mo hinh khai pha du lieu.

Dataset: Electronics Sales Dataset (B.Tech style) - Kaggle
"""
import pandas as pd
import numpy as np
import os

RAW = "data/raw"
OUT = "data/processed"
os.makedirs(OUT, exist_ok=True)

pd.set_option("display.max_columns", None)


def load_raw():
    """Doc toan bo 26 bang CSV goc vao dict, khu trung lap dong hoan toan
    (phat hien: SalesOrders, Shipments, Customers, CustomerReturns, Products
    co dong trung lap thuc su trong du lieu goc)."""
    names = [
        "SalesOrders", "SalesOrderLines", "Customers", "Products", "ProductVariants",
        "Payments", "CustomerReturns", "Shipments", "Categories", "Subcategories",
        "Brands", "Promotions", "SalesChannels", "PaymentMethods", "Locations",
        "Governorates", "InventoryBalances", "InventoryMovements", "Suppliers",
        "PurchaseOrders", "PurchaseOrderLines", "PurchaseReceipts", "PurchaseReceiptLines",
        "PurchaseReturns", "SKUSuppliers", "BrandSubcategoryMap",
    ]
    dfs = {}
    dedup_stats = {}
    for n in names:
        df = pd.read_csv(f"{RAW}/{n}.csv")
        before = len(df)
        df = df.drop_duplicates().reset_index(drop=True)
        removed = before - len(df)
        if removed > 0:
            dedup_stats[n] = removed
        dfs[n] = df
    if dedup_stats:
        print("   Da khu trung lap dong hoan toan:", dedup_stats)
    return dfs, dedup_stats


def data_quality_report(dfs):
    """Sinh bao cao chat luong du lieu cho tung bang: so dong, so cot,
    % thieu, so dong trung lap."""
    rows = []
    for name, df in dfs.items():
        n_rows, n_cols = df.shape
        n_dup = df.duplicated().sum()
        missing_pct = (df.isna().sum().sum() / (n_rows * n_cols) * 100) if n_rows else 0
        rows.append({
            "Bang": name, "SoDong": n_rows, "SoCot": n_cols,
            "SoDongTrungLap": n_dup, "TyLeThieuTB(%)": round(missing_pct, 2),
        })
    report = pd.DataFrame(rows).sort_values("SoDong", ascending=False).reset_index(drop=True)
    return report


def missing_by_column(dfs):
    """Chi tiet ty le thieu du lieu theo tung cot cua tung bang (chi liet ke cot co thieu)."""
    rows = []
    for name, df in dfs.items():
        miss = df.isna().mean() * 100
        miss = miss[miss > 0]
        for col, pct in miss.items():
            rows.append({"Bang": name, "Cot": col, "TyLeThieu(%)": round(pct, 2)})
    return pd.DataFrame(rows).sort_values(["Bang", "TyLeThieu(%)"], ascending=[True, False])


def build_dim_product(dfs):
    """Bang chieu san pham: SKU - Product - Subcategory - Category - Brand."""
    prod = dfs["Products"].merge(dfs["Brands"], on="BrandID", how="left")
    prod = prod.merge(dfs["Subcategories"], on="SubcategoryID", how="left")
    prod = prod.merge(dfs["Categories"], on="CategoryID", how="left")
    sku = dfs["ProductVariants"].merge(prod, on="ProductID", how="left")
    return sku


def build_dim_customer(dfs):
    cust = dfs["Customers"].merge(dfs["Governorates"], left_on="HomeGovernorateID",
                                   right_on="GovernorateID", how="left")
    cust["CustomerSinceDate"] = pd.to_datetime(cust["CustomerSinceDate"], errors="coerce")
    return cust


def build_sales_fact(dfs, dim_sku, dim_cust):
    """Bang fact chinh o muc order-line: moi dong la 1 dong hang trong 1 don hang.
    Day la bang trung tam dung cho EDA va cac mo hinh du doan."""
    lines = dfs["SalesOrderLines"].copy()
    orders = dfs["SalesOrders"].copy()

    orders["OrderDate"] = pd.to_datetime(orders["OrderDate"], errors="coerce")

    fact = lines.merge(orders, on="SalesOrderID", how="left")
    fact = fact.merge(dim_sku[["SKU_ID", "ProductID", "ColorName", "StorageGB", "MemoryGB",
                                "BrandID", "BrandName", "SubcategoryID", "SubcategoryName",
                                "CategoryID", "CategoryName", "ModelName"]],
                       on="SKU_ID", how="left")
    fact = fact.merge(dim_cust[["CustomerID", "AgeBand", "GovernorateName", "CustomerSinceDate"]],
                       on="CustomerID", how="left")
    fact = fact.merge(dfs["SalesChannels"], on="SalesChannelID", how="left")
    fact = fact.merge(dfs["Locations"][["LocationID", "LocationName", "LocationType", "GovernorateID"]],
                       left_on="SalesLocationID", right_on="LocationID", how="left")
    fact = fact.merge(dfs["Promotions"][["PromotionID", "PromotionName", "PromotionType"]],
                       on="PromotionID", how="left")

    # Danh dau co khuyen mai hay khong
    fact["HasPromotion"] = fact["PromotionID"].notna()

    # Danh dau dong hang co bi tra lai khong (join voi CustomerReturns)
    returns = dfs["CustomerReturns"].copy()
    returned_lines = returns.groupby("SalesOrderLineID").agg(
        ReturnQuantity=("ReturnQuantity", "sum"),
        ReturnReason=("ReturnReason", "first"),
        ReturnOutcome=("ReturnOutcome", "first"),
    ).reset_index()
    fact = fact.merge(returned_lines, on="SalesOrderLineID", how="left")
    fact["IsReturned"] = fact["ReturnQuantity"].notna() & (fact["ReturnQuantity"] > 0)

    # Doanh thu & chiet khau
    fact["Revenue"] = fact["Quantity"] * fact["ActualSellingPrice"]
    fact["RegularRevenue"] = fact["Quantity"] * fact["RegularUnitPrice"]
    fact["DiscountAmount"] = (fact["RegularUnitPrice"] - fact["ActualSellingPrice"]).clip(lower=0) * fact["Quantity"]
    fact["DiscountPct"] = np.where(
        fact["RegularUnitPrice"] > 0,
        (fact["RegularUnitPrice"] - fact["ActualSellingPrice"]) / fact["RegularUnitPrice"] * 100,
        0,
    )
    fact["Profit"] = np.where(
        fact["UnitCostAtSale"].notna(),
        (fact["ActualSellingPrice"] - fact["UnitCostAtSale"]) * fact["Quantity"],
        np.nan,
    )

    # Cac dac trung thoi gian
    fact["OrderYear"] = fact["OrderDate"].dt.year
    fact["OrderMonth"] = fact["OrderDate"].dt.month
    fact["OrderYearMonth"] = fact["OrderDate"].dt.to_period("M").astype(str)
    fact["OrderDayOfWeek"] = fact["OrderDate"].dt.day_name()
    fact["OrderQuarter"] = fact["OrderDate"].dt.quarter

    # Chi giu don hang hop le (loai bo cancel de tinh doanh thu that,
    # nhung van giu OrderStatus de phan tich ty le huy)
    return fact


def standardize_categoricals(fact):
    """Chuan hoa cac cot van ban bi 'ban' (khoang trang thua, viet hoa/thuong
    khong nhat quan, nhieu bien the cung nghia). Day la buoc rat quan trong
    trong tien xu ly du lieu doanh nghiep thuc te."""
    df = fact.copy()

    def norm(s):
        if pd.isna(s):
            return s
        return " ".join(str(s).strip().split())

    for col in ["OrderStatus", "FulfillmentMethod", "AgeBand", "ReturnOutcome"]:
        df[col] = df[col].apply(norm)

    # OrderStatus: gop cac bien the ve 1 nhan chuan
    status_map = {
        "Completed": "Completed", "Complete": "Completed",
        "Cancelled": "Cancelled", "Canceled": "Cancelled",
    }
    df["OrderStatus"] = df["OrderStatus"].replace(status_map)

    # FulfillmentMethod: gop bien the ve 3 nhom chuan
    def map_fulfillment(x):
        if pd.isna(x):
            return x
        v = x.lower()
        if "pickup" in v or "pick-up" in v or "pick up" in v:
            return "Store Pickup"
        if "immediate" in v or "take away" in v or "takeaway" in v:
            return "Immediate Takeaway"
        if "delivery" in v:
            return "Home Delivery"
        return x
    df["FulfillmentMethod"] = df["FulfillmentMethod"].apply(map_fulfillment)

    # AgeBand: chuan hoa ve dang "18-24", "65+"
    def map_ageband(x):
        if pd.isna(x) or x == "Khong xac dinh":
            return x
        v = x.replace(" to ", "-").replace(" - ", "-").replace("_", "-").replace(" ", "")
        if "65" in v:
            return "65+"
        return v
    df["AgeBand"] = df["AgeBand"].apply(map_ageband)

    # ReturnOutcome: gop bien the ve nhan chuan
    outcome_map = {
        "Rejected Return": "Rejected", "Rejected": "Rejected",
        "Replacement": "Replace", "Replace": "Replace",
        "Return": "Refund", "Refund": "Refund",
    }
    df["ReturnOutcome"] = df["ReturnOutcome"].replace(outcome_map)

    return df


def clean_sales_fact(fact):
    """Xu ly gia tri thieu / bat thuong tren bang fact."""
    df = standardize_categoricals(fact)

    # Loai cac dong khong co gia (loi du lieu / SKU khong xac dinh)
    before = len(df)
    df = df[df["ActualSellingPrice"].notna() & (df["ActualSellingPrice"] > 0)]
    removed_price = before - len(df)

    # Loai outlier gia theo phan vi 0.1% - 99.9% de tranh sai so nhap lieu
    q_low, q_high = df["ActualSellingPrice"].quantile([0.001, 0.999])
    before2 = len(df)
    df = df[(df["ActualSellingPrice"] >= q_low) & (df["ActualSellingPrice"] <= q_high)]
    removed_outlier = before2 - len(df)

    # Loai don hang co ngay dat hang la loi nhap lieu: khung hoat dong thuc te
    # cua doanh nghiep la 2023-07 -> 2025-12 (>99.9% du lieu). Cac thang con lai
    # (rai rac tu 2022-08 den 2026-12, vai don/thang) la outlier thoi gian.
    before3 = len(df)
    df = df[(df["OrderDate"] >= "2023-07-01") & (df["OrderDate"] <= "2025-12-31")]
    removed_date_outlier = before3 - len(df)

    # Dien khuyet gia tri phan loai. Rieng GovernorateName/AgeBand: neu CustomerID
    # rong (~28.7% don hang la khach vang lai khong co tai khoan - da xac nhan
    # tren du lieu goc SalesOrders.CustomerID), gan nhan ro rang thay vi nhan
    # "Khong xac dinh" chung chung de tranh hieu nham la loi du lieu.
    is_guest = df["CustomerID"].isna()
    for col in ["AgeBand", "GovernorateName"]:
        if col in df.columns:
            df.loc[is_guest, col] = "Khach vang lai (khong co tai khoan)"
    df["AgeBand"] = df["AgeBand"].fillna("Khong xac dinh")
    df["GovernorateName"] = df["GovernorateName"].fillna("Khong xac dinh")
    for col in ["CategoryName", "SubcategoryName", "BrandName"]:
        if col in df.columns:
            df[col] = df[col].fillna("Khong xac dinh")

    df["IsReturned"] = df["IsReturned"].fillna(False)
    df["HasPromotion"] = df["HasPromotion"].fillna(False)

    stats = {
        "SoDongGoc": before,
        "LoaiDoThieuGia": removed_price,
        "LoaiDoOutlierGia": removed_outlier,
        "LoaiDoOutlierNgay": removed_date_outlier,
        "SoDongConLai": len(df),
        "TyLeKhachVangLai(%)": round(is_guest.mean() * 100, 2),
    }
    return df, stats


def main():
    print(">> Dang doc du lieu tho...")
    dfs, dedup_stats = load_raw()
    if dedup_stats:
        pd.DataFrame(list(dedup_stats.items()), columns=["Bang", "SoDongTrungLapDaXoa"]).to_csv(
            f"{OUT}/dedup_stats.csv", index=False)

    print(">> Sinh bao cao chat luong du lieu...")
    dq = data_quality_report(dfs)
    dq.to_csv(f"{OUT}/data_quality_report.csv", index=False)
    miss_col = missing_by_column(dfs)
    miss_col.to_csv(f"{OUT}/missing_by_column.csv", index=False)

    print(">> Xay dung bang chieu (dimension tables)...")
    dim_sku = build_dim_product(dfs)
    dim_cust = build_dim_customer(dfs)
    dim_sku.to_csv(f"{OUT}/dim_product.csv", index=False)
    dim_cust.to_csv(f"{OUT}/dim_customer.csv", index=False)

    print(">> Xay dung bang fact ban hang (sales fact)...")
    fact = build_sales_fact(dfs, dim_sku, dim_cust)
    fact_clean, clean_stats = clean_sales_fact(fact)
    print("   Thong ke lam sach:", clean_stats)

    fact_clean.to_parquet(f"{OUT}/sales_fact.parquet", index=False)
    fact_clean.sample(min(50000, len(fact_clean)), random_state=42).to_csv(
        f"{OUT}/sales_fact_sample.csv", index=False)

    pd.DataFrame([clean_stats]).to_csv(f"{OUT}/cleaning_stats.csv", index=False)

    print(">> Hoan tat. Bang fact:", fact_clean.shape)
    return dfs, fact_clean


if __name__ == "__main__":
    main()
