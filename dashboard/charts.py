"""Biểu đồ phân tích chuỗi thời gian tài chính."""
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

def price_chart(frame, show_ma=True, show_bb=True):
    df=frame.sort_values("Date")
    fig=go.Figure()
    fig.add_trace(go.Candlestick(x=df["Date"],open=df["Open"],high=df["High"],
                                 low=df["Low"],close=df["Close"],name="OHLC"))
    if show_ma:
        for col in ("MA5","MA20","MA50"):
            fig.add_trace(go.Scatter(x=df["Date"],y=df[col],name=col,mode="lines"))
    if show_bb:
        for col in ("BB_Upper","BB_Middle","BB_Lower"):
            fig.add_trace(go.Scatter(x=df["Date"],y=df[col],name=col,mode="lines",
                                     line={"dash":"dot"}))
    fig.update_layout(title="Giá và chỉ báo xu hướng",xaxis_title="Ngày",
                      yaxis_title="Giá (VND)",height=530,
                      xaxis_rangeslider_visible=False,legend={"orientation":"h"})
    return fig

def rsi_chart(frame):
    df=frame.sort_values("Date")
    fig=go.Figure()
    fig.add_trace(go.Scatter(x=df["Date"],y=df["RSI14"],name="RSI14",mode="lines"))
    fig.add_hline(y=70,line_dash="dash",annotation_text="70")
    fig.add_hline(y=30,line_dash="dash",annotation_text="30")
    fig.update_layout(title="Chỉ số sức mạnh tương đối (RSI14)",
                      xaxis_title="Ngày",yaxis_title="RSI",yaxis_range=[0,100],height=280)
    return fig

def volume_chart(frame):
    df=frame.sort_values("Date")
    fig=go.Figure(go.Bar(x=df["Date"],y=df["Volume"],name="Khối lượng"))
    if "Volume20_Avg" in df:
        fig.add_trace(go.Scatter(x=df["Date"],y=3*df["Volume20_Avg"],
                                 name="3 × TB 20 phiên trước",mode="lines"))
    fig.update_layout(title="Khối lượng giao dịch và ngưỡng bất thường",
                      xaxis_title="Ngày",yaxis_title="Cổ phiếu",height=280)
    return fig

def correlation_heatmap(frame, sector):
    d=frame.loc[frame["Sector"]==sector]
    symbols=sorted(set(d["Symbol_A"]).union(d["Symbol_B"]))
    if not symbols:
        return go.Figure()
    matrix=pd.DataFrame(1.0,index=symbols,columns=symbols)
    for _,r in d.iterrows():
        matrix.loc[r["Symbol_A"],r["Symbol_B"]]=r["Pearson_R"]
        matrix.loc[r["Symbol_B"],r["Symbol_A"]]=r["Pearson_R"]
    fig=px.imshow(matrix, text_auto=".2f",zmin=-1,zmax=1,
                  color_continuous_scale="RdBu_r",aspect="auto")
    fig.update_layout(title=f"Tương quan lợi nhuận hằng ngày – {sector}",height=400)
    return fig

def monthly_chart(frame):
    d=frame.sort_values("Month")
    fig=go.Figure(go.Bar(x=d["Month"],y=d["Avg_Monthly_Return"]*100))
    fig.update_layout(title="Lợi nhuận trung bình theo tháng",
                      xaxis_title="Tháng",yaxis_title="Lợi nhuận (%)",height=330)
    return fig

def weekday_chart(frame):
    d=frame.sort_values("Weekday")
    labels={1:"Thứ Hai",2:"Thứ Ba",3:"Thứ Tư",4:"Thứ Năm",5:"Thứ Sáu"}
    fig=go.Figure(go.Bar(x=d["Weekday"].map(labels),y=d["Avg_Daily_Return"]*100))
    fig.update_layout(title="Lợi nhuận trung bình theo thứ",
                      xaxis_title="Ngày trong tuần",yaxis_title="Lợi nhuận (%)",height=330)
    return fig

def holding_chart(frame):
    d=frame.groupby("Holding_Months",as_index=False)["Holding_Return"].mean()
    fig=go.Figure(go.Bar(x=d["Holding_Months"].astype(str)+" tháng",
                         y=d["Holding_Return"]*100))
    fig.update_layout(title="Lợi nhuận nắm giữ trung bình theo kỳ",
                      xaxis_title="Kỳ nắm giữ",yaxis_title="Lợi nhuận (%)",height=330)
    return fig
