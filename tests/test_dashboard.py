"""Kiểm thử cấu trúc đầu vào và chức năng dựng biểu đồ."""
import pandas as pd
import pytest
from dashboard.data_loader import load_table, validate_tables, DatasetError
from dashboard.charts import price_chart, rsi_chart, correlation_heatmap, holding_chart

def example_tables():
    date=pd.date_range("2025-01-02",periods=3,freq="B")
    daily=pd.DataFrame({
        "Date":date,"Symbol":["VCB"]*3,"Open":[100.,101.,102.],
        "High":[102.,103.,104.],"Low":[99.,100.,101.],
        "Close":[101.,102.,103.],"Volume":[1000,1100,1200],
        "MA5":[None]*3,"MA20":[None]*3,"MA50":[None]*3,
        "RSI14":[None]*3,"BB_Middle":[None]*3,"BB_Upper":[None]*3,
        "BB_Lower":[None]*3,"Volume20_Avg":[None]*3})
    return {
        "daily_indicators":daily,
        "volume_alerts":pd.DataFrame({"Date":[],"Symbol":[],"Volume":[],"Volume20_Avg":[],"Volume_Ratio":[]}),
        "weekday_returns":pd.DataFrame({"Symbol":["VCB"],"Weekday":[1],"Trading_Sessions":[1],"Avg_Daily_Return":[0.01]}),
        "monthly_returns":pd.DataFrame({"Symbol":["VCB"],"Month_Start":date[:1],"Monthly_Return":[0.02]}),
        "monthly_average":pd.DataFrame({"Symbol":["VCB"],"Month":[1],"Observed_Months":[1],"Avg_Monthly_Return":[0.02]}),
        "sector_correlations":pd.DataFrame({"Sector":["Banking"],"Symbol_A":["VCB"],"Symbol_B":["BID"],"Pearson_R":[0.7]}),
        "holding_returns":pd.DataFrame({"Symbol":["VCB"]*3,"Buy_Date":date,
            "Sell_Date":date,"Holding_Months":[1,3,12],
            "Holding_Days":[30,90,365],"Holding_Return":[0.02,0.03,0.1]})
    }

def test_validation():
    stats=validate_tables(example_tables())
    assert stats["daily_rows"]==3
    assert stats["symbols"]==["VCB"]

def test_duplicate_rejected():
    tables=example_tables()
    tables["daily_indicators"]=pd.concat([tables["daily_indicators"]]*2)
    with pytest.raises(DatasetError,match="trùng"):
        validate_tables(tables)

def test_ohlc_rejected():
    tables=example_tables()
    tables["daily_indicators"].loc[0,"Low"]=105
    with pytest.raises(DatasetError,match="OHLCV"):
        validate_tables(tables)

def test_spark_csv_parts(tmp_path):
    d=tmp_path/"daily_indicators"
    d.mkdir()
    frame=example_tables()["daily_indicators"]
    frame.to_csv(d/"part-00000-abc.csv",index=False)
    (d/"_SUCCESS").write_text("")
    (d/".part-00000-abc.csv.crc").write_text("")
    result=load_table(tmp_path,"daily_indicators")
    assert len(result)==3
    assert pd.api.types.is_datetime64_any_dtype(result["Date"])

def test_missing_columns(tmp_path):
    d=tmp_path/"daily_indicators"
    d.mkdir()
    pd.DataFrame({"Symbol":["VCB"]}).to_csv(d/"part-00000.csv",index=False)
    with pytest.raises(DatasetError,match="thiếu"):
        load_table(tmp_path,"daily_indicators")

def test_charts():
    t=example_tables()
    assert len(price_chart(t["daily_indicators"]).data)==7
    assert len(rsi_chart(t["daily_indicators"]).data)==1
    assert len(correlation_heatmap(t["sector_correlations"],"Banking").data)==1
    assert len(holding_chart(t["holding_returns"]).data)==1
