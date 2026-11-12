"""Đọc và kiểm tra các bảng phân tích được xuất bởi Apache Spark."""
from pathlib import Path
import pandas as pd

TABLES = {
    "daily_indicators": ["Date", "Symbol", "Open", "High", "Low", "Close", "Volume",
                         "MA5", "MA20", "MA50", "RSI14", "BB_Middle", "BB_Upper", "BB_Lower"],
    "volume_alerts": ["Date", "Symbol", "Volume", "Volume20_Avg", "Volume_Ratio"],
    "weekday_returns": ["Symbol", "Weekday", "Trading_Sessions", "Avg_Daily_Return"],
    "monthly_returns": ["Symbol", "Month_Start", "Monthly_Return"],
    "monthly_average": ["Symbol", "Month", "Observed_Months", "Avg_Monthly_Return"],
    "sector_correlations": ["Sector", "Symbol_A", "Symbol_B", "Pearson_R"],
    "holding_returns": ["Symbol", "Buy_Date", "Sell_Date", "Holding_Months",
                        "Holding_Days", "Holding_Return"],
}
DATE_COLUMNS = {"Date", "Month_Start", "Buy_Date", "Sell_Date", "Target_Date"}

class DatasetError(ValueError):
    """Bảng đầu vào không đáp ứng lược đồ yêu cầu."""

def locate_table(base, name):
    base = Path(base)
    if name not in TABLES:
        raise DatasetError(f"Bảng không được hỗ trợ: {name}")
    folder = base / name
    if folder.is_dir():
        parts = sorted(p for p in folder.glob("part-*.csv") if p.is_file())
        if not parts:
            raise DatasetError(f"Không tìm thấy tệp dữ liệu trong {folder}")
        return parts
    csv = base / f"{name}.csv"
    if csv.is_file():
        return [csv]
    raise DatasetError(f"Không tìm thấy bảng {name} trong {base}")

def load_table(base, name):
    files = locate_table(base, name)
    try:
        frame = pd.concat((pd.read_csv(p) for p in files), ignore_index=True)
    except (OSError, ValueError, pd.errors.ParserError) as exc:
        raise DatasetError(f"Không thể đọc bảng {name}: {exc}") from exc
    missing = sorted(set(TABLES[name]) - set(frame.columns))
    if missing:
        raise DatasetError(f"Bảng {name} thiếu các cột: {', '.join(missing)}")
    for col in DATE_COLUMNS.intersection(frame.columns):
        frame[col] = pd.to_datetime(frame[col], errors="coerce")
        if frame[col].isna().any():
            raise DatasetError(f"Bảng {name} có giá trị ngày không hợp lệ ở cột {col}")
    if "Symbol" in frame:
        frame["Symbol"] = frame["Symbol"].astype(str).str.strip().str.upper()
    return frame

def load_all(base):
    return {name: load_table(base, name) for name in TABLES}

def validate_tables(tables):
    daily = tables["daily_indicators"]
    if daily.empty:
        raise DatasetError("Bảng chỉ báo hằng ngày không có dữ liệu")
    if daily.duplicated(["Symbol", "Date"]).any():
        raise DatasetError("Dữ liệu chỉ báo có khóa Symbol-Date trùng lặp")
    for col in ["Open", "High", "Low", "Close", "Volume"]:
        if pd.to_numeric(daily[col], errors="coerce").isna().any():
            raise DatasetError(f"Cột {col} có giá trị không hợp lệ")
    if ((daily["Low"] > daily[["Open","Close"]].min(axis=1)) |
        (daily["High"] < daily[["Open","Close"]].max(axis=1)) |
        (daily["Close"] <= 0) | (daily["Volume"] <= 0)).any():
        raise DatasetError("Dữ liệu OHLCV không hợp lệ")
    corr = tables["sector_correlations"]
    if (pd.to_numeric(corr["Pearson_R"],errors="coerce").abs() > 1).any():
        raise DatasetError("Hệ số tương quan nằm ngoài [-1,1]")
    periods = set(pd.to_numeric(tables["holding_returns"]["Holding_Months"],errors="coerce").dropna().astype(int))
    if not {1,3,12}.issubset(periods):
        raise DatasetError("Thiếu một hoặc nhiều kỳ nắm giữ 1, 3, 12 tháng")
    return {"daily_rows": len(daily), "symbols": sorted(daily["Symbol"].unique().tolist()),
            "volume_alerts":len(tables["volume_alerts"]),
            "correlation_pairs":len(corr),
            "holding_rows":len(tables["holding_returns"])}

def resolve_data_dir(project_root):
    return Path(project_root) / "results" / "financial_analysis"
