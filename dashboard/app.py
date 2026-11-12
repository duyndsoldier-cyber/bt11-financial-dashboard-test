"""Ứng dụng trực quan hóa kết quả phân tích tài chính."""
import os
from pathlib import Path
import pandas as pd
import streamlit as st
from dashboard.data_loader import load_all, validate_tables, DatasetError
from dashboard.charts import (
    price_chart, rsi_chart, volume_chart, correlation_heatmap,
    monthly_chart, weekday_chart, holding_chart
)

st.set_page_config(page_title="Phân tích chuỗi thời gian tài chính",page_icon="📈",
                   layout="wide")
st.title("Phân tích chuỗi thời gian tài chính với Apache Spark")
st.caption("Dữ liệu cổ phiếu Việt Nam • Phân tích theo phiên giao dịch • Kết quả tính toán bằng PySpark")

DEFAULT_DATA=Path(__file__).resolve().parents[1]/"results"/"financial_analysis"
DATA_DIR=Path(os.getenv("BT11_DATA_DIR",str(DEFAULT_DATA))).expanduser()

@st.cache_data(show_spinner="Đang tải dữ liệu phân tích…")
def get_tables(path):
    tables=load_all(path)
    return tables,validate_tables(tables)

try:
    tables,stats=get_tables(str(DATA_DIR))
except (DatasetError, OSError, ValueError) as exc:
    st.error(f"Không thể tải dữ liệu phân tích: {exc}")
    st.info("Ứng dụng cần các bảng CSV đã xuất từ pipeline PySpark trong results/financial_analysis.")
    st.stop()

daily=tables["daily_indicators"]
symbols=stats["symbols"]
with st.sidebar:
    st.header("Bộ lọc phân tích")
    symbol=st.selectbox("Mã cổ phiếu",symbols)
    min_date=daily["Date"].min().date()
    max_date=daily["Date"].max().date()
    chosen=st.date_input("Khoảng thời gian",(min_date,max_date),
                         min_value=min_date,max_value=max_date)
    show_ma=st.checkbox("Hiển thị MA5 / MA20 / MA50",value=True)
    show_bb=st.checkbox("Hiển thị Bollinger Bands",value=True)

if not isinstance(chosen,(tuple,list)) or len(chosen)!=2:
    st.warning("Vui lòng chọn ngày bắt đầu và ngày kết thúc.")
    st.stop()
start,end=chosen
if start>end:
    st.warning("Ngày bắt đầu phải không muộn hơn ngày kết thúc.")
    st.stop()
selected=daily.loc[(daily["Symbol"]==symbol) &
                   (daily["Date"].dt.date>=start) &
                   (daily["Date"].dt.date<=end)].sort_values("Date")
if selected.empty:
    st.warning("Không có phiên giao dịch trong khoảng thời gian đã chọn.")
    st.stop()

last=selected.iloc[-1]
previous=selected.iloc[-2]["Close"] if len(selected)>1 else None
change=(last["Close"]/previous-1)*100 if previous else None
m1,m2,m3,m4=st.columns(4)
m1.metric("Giá đóng cửa cuối kỳ",f'{last["Close"]:,.0f} VND',
          f"{change:+.2f}%" if change is not None else None)
m2.metric("Số phiên giao dịch",f"{len(selected):,}")
m3.metric("Khối lượng phiên cuối",f'{int(last["Volume"]):,}')
m4.metric("RSI14 phiên cuối",f'{last["RSI14"]:.2f}' if pd.notna(last["RSI14"]) else "N/A")

tabs=st.tabs(["Giá và chỉ báo","Lợi nhuận","Tương quan ngành",
              "Cảnh báo khối lượng","Kỳ nắm giữ","Dữ liệu"])
with tabs[0]:
    st.plotly_chart(price_chart(selected,show_ma,show_bb),use_container_width=True)
    st.plotly_chart(rsi_chart(selected),use_container_width=True)
    st.plotly_chart(volume_chart(selected),use_container_width=True)
with tabs[1]:
    c1,c2=st.columns(2)
    with c1:
        month=tables["monthly_average"].query("Symbol == @symbol")
        st.plotly_chart(monthly_chart(month),use_container_width=True)
    with c2:
        weekday=tables["weekday_returns"].query("Symbol == @symbol")
        st.plotly_chart(weekday_chart(weekday),use_container_width=True)
    monthly=tables["monthly_returns"]
    monthly=monthly.loc[(monthly["Symbol"]==symbol) &
                        (monthly["Month_Start"].dt.date>=start) &
                        (monthly["Month_Start"].dt.date<=end)]
    st.dataframe(monthly.sort_values("Month_Start",ascending=False),use_container_width=True,hide_index=True)
    st.caption("Biểu đồ trung bình theo tháng và thứ được tính trên toàn bộ thời kỳ quan sát; bảng lợi nhuận tháng áp dụng bộ lọc thời gian.")
with tabs[2]:
    corr=tables["sector_correlations"]
    sectors=sorted(corr["Sector"].dropna().unique())
    sector=st.selectbox("Ngành có ít nhất hai cổ phiếu",sectors)
    st.plotly_chart(correlation_heatmap(corr,sector),use_container_width=True)
    st.dataframe(corr.loc[corr["Sector"]==sector],hide_index=True,use_container_width=True)
    st.caption("Hệ số Pearson được tính từ các phiên có dữ liệu lợi nhuận của cả hai cổ phiếu.")
with tabs[3]:
    alerts=tables["volume_alerts"]
    alerts=alerts.loc[(alerts["Symbol"]==symbol) &
                      (alerts["Date"].dt.date>=start) &
                      (alerts["Date"].dt.date<=end)]
    st.metric("Số phiên cảnh báo trong khoảng chọn",len(alerts))
    st.dataframe(alerts.sort_values("Date",ascending=False),use_container_width=True,hide_index=True)
    st.caption("Điều kiện: khối lượng phiên hiện tại lớn hơn 3 lần trung bình 20 phiên trước đó.")
with tabs[4]:
    holding=tables["holding_returns"]
    holding=holding.loc[(holding["Symbol"]==symbol) &
                        (holding["Buy_Date"].dt.date>=start) &
                        (holding["Buy_Date"].dt.date<=end)]
    if holding.empty:
        st.info("Không có kỳ nắm giữ hoàn chỉnh trong khoảng thời gian đã chọn.")
    else:
        st.plotly_chart(holding_chart(holding),use_container_width=True)
        st.dataframe(holding.sort_values("Buy_Date",ascending=False).head(500),
                     use_container_width=True,hide_index=True)
        st.caption("Lợi nhuận chưa bao gồm cổ tức, thuế, phí và các điều chỉnh doanh nghiệp.")
with tabs[5]:
    st.dataframe(selected,use_container_width=True,hide_index=True)
    st.download_button("Tải CSV của mã đang chọn",
                       selected.to_csv(index=False).encode("utf-8-sig"),
                       file_name=f"{symbol}_indicators.csv",mime="text/csv")
st.divider()
st.caption("Nguồn dữ liệu: Yahoo Finance (bản lưu lịch sử). Chỉ báo và thống kê được xử lý bằng Apache Spark. Kết quả phục vụ nghiên cứu học thuật, không phải khuyến nghị đầu tư.")
