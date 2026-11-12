# Dashboard phân tích chuỗi thời gian tài chính

Ứng dụng Streamlit trực quan hóa dữ liệu phân tích cổ phiếu Việt Nam đã được xử lý bằng PySpark.

## Chức năng
- Biểu đồ nến OHLC, MA5/MA20/MA50, Bollinger Bands.
- RSI14, biểu đồ khối lượng và ngưỡng bất thường.
- Lợi nhuận trung bình theo tháng và thứ; bảng lợi nhuận tháng.
- Heatmap tương quan Pearson theo ngành.
- Cảnh báo khối lượng > 3 lần trung bình 20 phiên trước.
- Thống kê lợi nhuận nắm giữ 1, 3, 12 tháng.
- Lọc mã cổ phiếu và khoảng thời gian, tải dữ liệu CSV.

## Dữ liệu đầu vào
Sao chép các thư mục kết quả Spark từ `BT11/results/financial_analysis/` vào `results/financial_analysis/` tại thư mục dự án dashboard. Giữ nguyên tên bảng, tên cột và file `part-*.csv`. Không cần chạy Spark trong ứng dụng.

## Chạy cục bộ
```bash
python -m pip install -r requirements_dashboard.txt
python -m pytest -q tests
python -m dashboard.validate_export --data results/financial_analysis
streamlit run streamlit_app.py
```

Có thể đặt biến môi trường `BT11_DATA_DIR` để chỉ đến thư mục kết quả ở vị trí khác.

## Triển khai
Đưa `streamlit_app.py`, `dashboard/`, `requirements_dashboard.txt` (đổi tên thành `requirements.txt` trên repository triển khai), và `results/financial_analysis/` lên GitHub. Trong Streamlit Community Cloud, chọn entrypoint `streamlit_app.py`. Không đưa Google Drive credentials, dữ liệu cá nhân hoặc khóa bí mật lên GitHub.

## Giới hạn phân tích
Giá đóng cửa có thể chưa được điều chỉnh đầy đủ theo sự kiện doanh nghiệp. Các phép tính lợi nhuận không bao gồm cổ tức, phí và thuế. Số liệu phục vụ nghiên cứu học thuật, không phải khuyến nghị đầu tư.
