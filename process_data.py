import os
import glob
import pandas as pd
import matplotlib.pyplot as plt

# ---------- STEP 1: LOAD & CLEAN ----------
# pick up data/daily_sales_data_0.csv ... _2.csv
files = glob.glob(os.path.join("data", "daily_sales_data_*.csv"))
if not files:
    raise FileNotFoundError("No CSVs found in data/")

dfs = []
for fp in files:
    df = pd.read_csv(fp)

    # normalise column names
    df.columns = [c.strip().lower() for c in df.columns]

    # clean price (e.g. "$2.50" -> 2.50)
    df["price"] = (
        df["price"].astype(str)
        .str.replace("$", "", regex=False)
        .str.replace(",", "", regex=False)
    )
    df["price"] = pd.to_numeric(df["price"], errors="coerce")

    # make quantity numeric too
    df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce")

    dfs.append(df)

df = pd.concat(dfs, ignore_index=True)

# ---------- STEP 2: FILTER & TRANSFORM ----------
# keep only Pink Morsel (case-insensitive)
df = df[df["product"].str.lower() == "pink morsel"].copy()

# compute sales
df["sales"] = df["quantity"] * df["price"]

# output file with required columns (lowercase names)
final = df[["sales", "date", "region"]].copy()
final.to_csv("output.csv", index=False)
print(f"Wrote {len(final):,} rows to output.csv")

# ---------- STEP 3: PLOT (aggregate per day) ----------
# parse date and aggregate sales by day
final["date"] = pd.to_datetime(final["date"], errors="coerce")
daily = final.groupby("date", as_index=False)["sales"].sum().sort_values("date")

plt.figure(figsize=(10, 6))
plt.plot(daily["date"], daily["sales"], label="Daily Sales")

# mark price change date
price_change_date = pd.to_datetime("2021-01-15")
plt.axvline(price_change_date, color="red", linestyle="--", label="Price change (15 Jan 2021)")

plt.xlabel("Date")
plt.ylabel("Sales")
plt.title("Pink Morsel Sales Over Time")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.savefig("sales_chart.png")
print("Saved chart to sales_chart.png")
# plt.show()  # optional
