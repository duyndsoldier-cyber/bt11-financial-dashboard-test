# Triển khai ứng dụng lên Streamlit Community Cloud

## Chuẩn bị dữ liệu
Ứng dụng đọc các bảng CSV đã được tính bởi Apache Spark. Không yêu cầu Spark trong môi trường triển khai.

1. Chạy notebook `notebooks/04_prepare_github_colab.ipynb` trong Google Colab.
2. Notebook sao chép dữ liệu đã xử lý từ Google Drive vào `results/financial_analysis/` của bản triển khai nằm trong `workspace/stage_04`.
3. Notebook kiểm tra các bảng, chạy kiểm thử và tạo tệp ZIP chứa mã nguồn và dữ liệu để đưa lên GitHub.
4. Tải tệp ZIP từ Drive, giải nén trên máy tính.

## GitHub
1. Tạo repository mới trên GitHub, ví dụ `bt11-financial-dashboard`.
2. Đưa **nội dung bên trong thư mục repository** lên nhánh `main` (không đưa thêm một cấp thư mục).
3. Bảo đảm tại thư mục gốc có `streamlit_app.py`, `requirements.txt`, `dashboard/`, `results/financial_analysis/`.
4. Không đưa tài khoản, token, secrets, hoặc dữ liệu cá nhân lên repository.

## Streamlit Community Cloud
1. Đăng nhập https://share.streamlit.io/ bằng GitHub.
2. Chọn **Create app** / **Deploy an app**.
3. Chọn repository và nhánh `main`.
4. Main file path: `streamlit_app.py`.
5. Chọn Deploy. Sau khi website hoạt động, thử tất cả các tab và bộ lọc.

## Kiểm thử nghiệm thu giao diện
- Chọn lần lượt VCB, FPT, HPG; kiểm tra đồ thị nến và chỉ báo.
- Đổi khoảng ngày, kiểm tra bảng lọc và biểu đồ.
- Xem heatmap ngành Ngân hàng và Bất động sản.
- Kiểm tra bảng cảnh báo và thống kê nắm giữ 1/3/12 tháng.
- Thử nút tải CSV.
- Đối chiếu tổng số bản ghi với `pipeline_audit.json`.

Kết quả website chỉ được công nhận sau khi truy cập và kiểm tra thực tế.
