# MediCare Microservices System

Đây là hệ thống API Microservices dành cho hệ thống quản lý bệnh viện **MediCare** được xây dựng theo mô hình **Controller → Service → Repository** dùng Spring Boot (Java 17, Spring Data JPA, MySQL) cùng công cụ khởi tạo và chạy giả lập bằng Python.

## 1. Cấu Trúc Hệ Thống (5 Microservices)

| Tên Service | Port | Đường dẫn API | Database Name | Tính năng chính |
| :--- | :--- | :--- | :--- | :--- |
| **patient-service** | `8081` | `/api/patients` | `medicare_patient_db` | Quản lý thông tin bệnh nhân (CRUD) |
| **doctor-service** | `8082` | `/api/doctors` | `medicare_doctor_db` | Quản lý thông tin bác sĩ (CRUD) |
| **appointment-service** | `8083` | `/api/appointments` | `medicare_appointment_db` | Đặt và quản lý lịch hẹn khám bệnh (CRUD) |
| **medical-record-service** | `8084` | `/api/medical-records` | `medicare_medical_record_db` | Quản lý hồ sơ bệnh án (CRUD) |
| **pharmacy-service** | `8085` | `/api/medications` | `medicare_pharmacy_db` | Quản lý danh mục dược phẩm & kho thuốc (CRUD) |

---

## 2. Cách Khởi Chạy Nhanh Chóng

Hệ thống được tích hợp bộ công cụ thông minh viết bằng **Python** (`main.py`) cho phép bạn làm 2 việc cực kỳ tiện lợi:
1. **Tự động sinh toàn bộ mã nguồn Java** (Spring Boot + Gradle) có cấu trúc chuẩn cho cả 5 dự án.
2. **Khởi chạy máy chủ Giả lập (Mock Server)** ngay lập tức trên cả 5 Port (8081 - 8085) để test thử API bằng Postman mà không cần tốn thời gian cấu hình Java hay MySQL cục bộ.

### Bước 1: Khởi tạo/Sinh mã nguồn Java
Để sinh cấu trúc thư mục chuẩn của 5 dự án Java Spring Boot cùng đầy đủ các file Controller, Service, Repository, DTO, Entity, `build.gradle`, và `application.yml`, hãy chạy lệnh:
```bash
python main.py --generate
```
Sau khi chạy, 5 thư mục dự án tương ứng sẽ tự động được tạo ra ở thư mục hiện tại.

### Bước 2: Chạy giả lập 5 Microservices (Để test nhanh API)
Nếu bạn muốn chạy thử nghiệm các API RESTful ngay lập tức bằng Python mà không cần cài đặt Gradle/Java/MySQL:
```bash
python main.py --run-mock
```
Máy chủ sẽ kích hoạt 5 luồng xử lý độc lập chạy trên 5 port riêng biệt: `8081, 8082, 8083, 8084, 8085` tương thích hoàn toàn với tài liệu API của bài tập.

### Bước 3: Build và Run trên môi trường Java thực tế
Sau khi sinh code Java bằng lệnh `--generate`, bạn có thể mở từng dự án bằng IntelliJ IDEA hoặc chạy trực tiếp bằng dòng lệnh:
1. Tạo sẵn các database tương ứng trong MySQL (`medicare_patient_db`, `medicare_doctor_db`, v.v.).
2. Cấu hình username/password database của bạn trong file `application.yml` của từng service.
3. Di chuyển vào thư mục của service bất kỳ và khởi động bằng Gradle:
   ```bash
   cd patient-service
   ./gradlew bootRun
   ```

---

## 3. Danh Sách API Test Mẫu trên Postman

### A. Patient Service (Port 8081)
- **POST** `/api/patients` - Thêm bệnh nhân mới:
  ```json
  {
      "fullName": "Nguyễn Văn A",
      "dateOfBirth": "1990-05-15",
      "gender": "MALE",
      "phone": "0901234567",
      "address": "123 Trần Hưng Đạo, Hà Nội",
      "insuranceId": "BH123456789"
  }
  ```
- **GET** `/api/patients` - Lấy toàn bộ bệnh nhân.
- **GET** `/api/patients/{id}` - Lấy bệnh nhân cụ thể.
- **PUT** `/api/patients/{id}` - Cập nhật bệnh nhân.
- **DELETE** `/api/patients/{id}` - Xóa bệnh nhân.

### B. Doctor Service (Port 8082)
- **POST** `/api/doctors` - Thêm bác sĩ mới:
  ```json
  {
      "fullName": "Bác sĩ Trần Quốc Bảo",
      "specialty": "Cardiology",
      "phone": "0987654321",
      "email": "bao.tran@medicare.com",
      "department": "Khoa Tim Mạch"
  }
  ```
- **GET** `/api/doctors` - Lấy toàn bộ danh sách bác sĩ.

### C. Appointment Service (Port 8083)
- **POST** `/api/appointments` - Đặt lịch hẹn mới:
  ```json
  {
      "patientId": 1,
      "doctorId": 1,
      "appointmentDate": "2024-12-25T10:30:00",
      "status": "SCHEDULED",
      "notes": "Khám định kỳ tim mạch"
  }
  ```
- **GET** `/api/appointments` - Lấy toàn bộ lịch hẹn.

### D. Medical Record Service (Port 8084)
- **POST** `/api/medical-records` - Tạo bệnh án mới:
  ```json
  {
      "patientId": 1,
      "doctorId": 1,
      "diagnosis": "Cao huyết áp nhẹ",
      "treatment": "Uống thuốc đúng giờ, hạn chế ăn mặn",
      "recordDate": "2024-12-20"
  }
  ```
- **GET** `/api/medical-records` - Lấy toàn bộ hồ sơ bệnh án.

### E. Pharmacy Service (Port 8085)
- **POST** `/api/medications` - Thêm thuốc mới vào kho:
  ```json
  {
      "name": "Paracetamol 500mg",
      "description": "Thuốc giảm đau, hạ sốt nhanh",
      "price": 1500.0,
      "stockQuantity": 1000
  }
  ```
- **GET** `/api/medications` - Lấy danh mục thuốc hiện tại.