# Kiểm thử và tiêu chí chấp nhận

1. Cài đặt dependencies từ `requirements_dashboard.txt`.
2. Chạy `pytest -q tests`: kiểm tra dữ liệu, cấu trúc bảng Spark và khả năng dựng biểu đồ.
3. Chạy `python -m dashboard.validate_export --data <thư mục kết quả Spark>`: phải xuất `DASHBOARD_DATA_PASS`.
4. Chạy ứng dụng bằng `streamlit run streamlit_app.py` và kiểm tra giao diện.
5. Kiểm tra tất cả các tab, lọc thời gian, chuyển mã cổ phiếu, tải CSV.
6. Kiểm tra ứng dụng hoạt động độc lập với Spark và Google Colab.

Kết quả kiểm thử trên dữ liệu mô phỏng chỉ xác nhận chức năng phần mềm. Kết quả thực nghiệm chính thức phải lấy từ dữ liệu thực tế xuất bởi pipeline.
