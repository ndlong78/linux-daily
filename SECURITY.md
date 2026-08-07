# Security Policy

## Supported version

Linux Daily vận hành trực tiếp từ nhánh `main`. Chỉ trạng thái hiện tại của `main` được xem là phiên bản đang được hỗ trợ.

## Báo cáo lỗ hổng

Không đăng thông tin khai thác, secret hoặc chi tiết lỗ hổng chưa được xử lý vào issue/public discussion.

Ưu tiên sử dụng **GitHub private vulnerability reporting / Security Advisory** của repository nếu tính năng này được bật. Nếu không khả dụng, hãy liên hệ maintainer qua một kênh GitHub riêng tư và chỉ cung cấp thông tin tối thiểu cần thiết để tái hiện vấn đề.

Báo cáo nên gồm:

- thành phần/file bị ảnh hưởng;
- tác động dự kiến;
- điều kiện để tái hiện;
- bằng chứng hoặc bước tái hiện an toàn;
- đề xuất giảm thiểu nếu có.

Không gửi credential thật, private key, access token hoặc dữ liệu nhạy cảm của hệ thống sản xuất.

## Phạm vi ưu tiên

Các vấn đề sau được ưu tiên xử lý:

- secret hoặc credential bị commit/expose;
- GitHub Actions có quyền rộng hơn mức cần thiết hoặc có đường injection;
- dependency/build script có khả năng thực thi mã ngoài ý muốn;
- nội dung hướng dẫn có thể dẫn tới thao tác phá hủy hệ thống do thiếu guardrail rõ ràng;
- website sinh ra nội dung/script không mong muốn từ dữ liệu không tin cậy.

## Nguyên tắc xử lý

- Xác minh trước khi công bố rộng rãi.
- Ưu tiên bản vá nhỏ, có thể review và có rollback path.
- Không bypass `quality-gate` để merge bản vá trừ khi GitHub itself không thể chạy CI; khi đó maintainer phải đánh giá thủ công phạm vi thay đổi.
- Sau khi xử lý, có thể công bố mô tả ngắn gọn không chứa secret hoặc chi tiết khai thác nguy hiểm.
