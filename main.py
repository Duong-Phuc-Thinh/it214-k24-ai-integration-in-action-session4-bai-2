import os
import sys
import json
import threading
from urllib.parse import urlparse
from http.server import HTTPServer, BaseHTTPRequestHandler

# Database giả lập lưu trong RAM phục vụ cho Mock API
DATABASE = {
    'patients': [
        {
            "id": 1,
            "fullName": "Nguyễn Văn A",
            "dateOfBirth": "1990-05-15",
            "gender": "MALE",
            "phone": "0901234567",
            "address": "123 Trần Hưng Đạo, Hà Nội",
            "insuranceId": "BH123456789"
        }
    ],
    'doctors': [
        {
            "id": 1,
            "fullName": "Bác sĩ Trần Quốc Bảo",
            "specialty": "Cardiology",
            "phone": "0987654321",
            "email": "bao.tran@medicare.com",
            "department": "Khoa Tim Mạch"
        }
    ],
    'appointments': [
        {
            "id": 1,
            "patientId": 1,
            "doctorId": 1,
            "appointmentDate": "2024-12-25T10:30:00",
            "status": "SCHEDULED",
            "notes": "Khám định kỳ tim mạch"
        }
    ],
    'medical_records': [
        {
            "id": 1,
            "patientId": 1,
            "doctorId": 1,
            "diagnosis": "Cao huyết áp nhẹ",
            "treatment": "Uống thuốc đúng giờ, hạn chế ăn mặn",
            "recordDate": "2024-12-20"
        }
    ],
    'medications': [
        {
            "id": 1,
            "name": "Paracetamol 500mg",
            "description": "Thuốc giảm đau, hạ sốt",
            "price": 1500.0,
            "stockQuantity": 1000
        }
    ]
}

PORT_MAPPING = {
    8081: ("patients", "/api/patients"),
    8082: ("doctors", "/api/doctors"),
    8083: ("appointments", "/api/appointments"),
    8084: ("medical_records", "/api/medical-records"),
    8085: ("medications", "/api/medications")
}

# Tầng Handler giả lập cơ chế Controller -> Service -> Repository của Spring Boot trong Python
class MockAPIRequestHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass  # Ẩn logs truy cập mặc định để hiển thị gọn gàng hơn

    def get_resource_config(self):
        port = self.server.server_address[1]
        return PORT_MAPPING.get(port)

    def send_json(self, status, data):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_GET(self):
        config = self.get_resource_config()
        if not config:
            self.send_json(404, {"error": "Not Found"})
            return
        
        db_key, base_path = config
        parsed_path = urlparse(self.path)
        path = parsed_path.path

        # API GET Toàn bộ danh sách (tương đương Controller.getAll -> Service.getAll)
        if path == base_path:
            self.send_json(200, DATABASE[db_key])
            return
        
        # API GET theo ID (tương đương Controller.getById -> Service.getById)
        if path.startswith(base_path + "/"):
            try:
                item_id = int(path[len(base_path)+1:])
                item = next((x for x in DATABASE[db_key] if x['id'] == item_id), None)
                if item:
                    self.send_json(200, item)
                else:
                    self.send_json(404, {"error": f"{db_key[:-1].capitalize()} with ID {item_id} not found"})
            except ValueError:
                self.send_json(400, {"error": "Invalid ID format"})
            return

        self.send_json(404, {"error": "Not Found"})

    def do_POST(self):
        config = self.get_resource_config()
        if not config:
            self.send_json(404, {"error": "Not Found"})
            return
        
        db_key, base_path = config
        if self.path == base_path:
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            try:
                data = json.loads(body.decode('utf-8'))
                # Tạo ID tự tăng (tương đương Auto-increment trong Repository)
                new_id = max([x['id'] for x in DATABASE[db_key]] + [0]) + 1
                data['id'] = new_id
                DATABASE[db_key].append(data)
                self.send_json(201, data)
            except Exception as e:
                self.send_json(400, {"error": f"Invalid data format: {str(e)}"})
            return
        self.send_json(404, {"error": "Not Found"})

    def do_PUT(self):
        config = self.get_resource_config()
        if not config:
            self.send_json(404, {"error": "Not Found"})
            return
        
        db_key, base_path = config
        if self.path.startswith(base_path + "/"):
            try:
                item_id = int(self.path[len(base_path)+1:])
                item = next((x for x in DATABASE[db_key] if x['id'] == item_id), None)
                if not item:
                    self.send_json(404, {"error": f"{db_key[:-1].capitalize()} not found"})
                    return
                
                content_length = int(self.headers.get('Content-Length', 0))
                body = self.rfile.read(content_length)
                data = json.loads(body.decode('utf-8'))
                
                # Cập nhật thông tin bệnh án, dược phẩm, lịch hẹn...
                for k, v in data.items():
                    if k != 'id':
                        item[k] = v
                self.send_json(200, item)
            except Exception as e:
                self.send_json(400, {"error": f"Invalid input: {str(e)}"})
            return
        self.send_json(404, {"error": "Not Found"})

    def do_DELETE(self):
        config = self.get_resource_config()
        if not config:
            self.send_json(404, {"error": "Not Found"})
            return
        
        db_key, base_path = config
        if self.path.startswith(base_path + "/"):
            try:
                item_id = int(self.path[len(base_path)+1:])
                item = next((x for x in DATABASE[db_key] if x['id'] == item_id), None)
                if not item:
                    self.send_json(404, {"error": f"{db_key[:-1].capitalize()} not found"})
                    return
                DATABASE[db_key].remove(item)
                self.send_json(200, {"message": f"Successfully deleted item {item_id}"})
            except Exception as e:
                self.send_json(400, {"error": f"Invalid ID: {str(e)}"})
            return
        self.send_json(404, {"error": "Not Found"})

# Khởi chạy luồng mạng cho từng Port
def start_mock_server(port):
    server = HTTPServer(('0.0.0.0', port), MockAPIRequestHandler)
    db_key, base_path = PORT_MAPPING[port]
    print(f"[+] Port {port}: Khởi chạy {db_key.upper()} Service thành công tại http://localhost:{port}{base_path}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()

# --- CODE GENERATOR FOR JAVA SPRING BOOT --- 

JAVA_TEMPLATES = {
    "application.yml": """server:
  port: __PORT__

spring:
  application:
    name: __APP_NAME__
  datasource:
    url: jdbc:mysql://localhost:3306/__DB_NAME__?createDatabaseIfNotExist=true&useSSL=false&serverTimezone=UTC
    username: root
    password: rootpassword
  jpa:
    hibernate:
      ddl-auto: update
    show-sql: true
    properties:
      hibernate:
        format_sql: true
""",
    "build.gradle": """plugins { 
    id 'org.springframework.boot' version '3.2.2'
    id 'io.spring.dependency-management' version '1.1.4'
    id 'java'
}

group = 'com.medicare'
version = '0.0.1-SNAPSHOT'
sourceCompatibility = '17'

configurations {
    compileOnly {
        extendsFrom annotationProcessor
    }
}

repositories {
    mavenCentral()
}

dependencies {
    implementation 'org.springframework.boot:spring-boot-starter-data-jpa'
    implementation 'org.springframework.boot:spring-boot-starter-web'
    compileOnly 'org.projectlombok:lombok'
    runtimeOnly 'com.mysql:mysql-connector-j'
    annotationProcessor 'org.projectlombok:lombok'
    testImplementation 'org.springframework.boot:spring-boot-starter-test'
}

tasks.named('test') {
    useJUnitPlatform()
}
""",
    "MainApplication.java": """package com.medicare.__PKG__;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
public class __CLASS_NAME__Application {
    public static void main(String[] args) {
        SpringApplication.run(__CLASS_NAME__Application.class, args);
    }
}
""",
    "Entity.java": """package com.medicare.__PKG__.model;

import lombok.*;
import jakarta.persistence.*;

@Entity
@Table(name = "__TABLE_NAME__")
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class __CLASS_NAME__ {
__FIELDS__
}
""",
    "Dto.java": """package com.medicare.__PKG__.dto;

import lombok.*;

@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class __CLASS_NAME__Dto {
__DTO_FIELDS__
}
""",
    "Repository.java": """package com.medicare.__PKG__.repository;

import com.medicare.__PKG__.model.__CLASS_NAME__;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface __CLASS_NAME__Repository extends JpaRepository<__CLASS_NAME__, Long> {
}
""",
    "Service.java": """package com.medicare.__PKG__.service;

import com.medicare.__PKG__.dto.__CLASS_NAME__Dto;
import com.medicare.__PKG__.model.__CLASS_NAME__;
import com.medicare.__PKG__.repository.__CLASS_NAME__Repository;
import org.springframework.stereotype.Service;
import java.util.List;
import java.util.stream.Collectors;

@Service
public class __CLASS_NAME__Service {

    private final __CLASS_NAME__Repository repository;

    public __CLASS_NAME__Service(__CLASS_NAME__Repository repository) {
        this.repository = repository;
    }

    public List<__CLASS_NAME__Dto> getAll() {
        return repository.findAll().stream()
                .map(this::convertToDto)
                .collect(Collectors.toList());
    }

    public __CLASS_NAME__Dto getById(Long id) {
        __CLASS_NAME__ entity = repository.findById(id)
                .orElseThrow(() -> new RuntimeException("__CLASS_NAME__ not found with id " + id));
        return convertToDto(entity);
    }

    public __CLASS_NAME__Dto create(__CLASS_NAME__Dto dto) {
        __CLASS_NAME__ entity = convertToEntity(dto);
        __CLASS_NAME__ saved = repository.save(entity);
        return convertToDto(saved);
    }

    public __CLASS_NAME__Dto update(Long id, __CLASS_NAME__Dto dto) {
        __CLASS_NAME__ existing = repository.findById(id)
                .orElseThrow(() -> new RuntimeException("__CLASS_NAME__ not found with id " + id));
__SERVICE_UPDATE_LOGIC__
        __CLASS_NAME__ saved = repository.save(existing);
        return convertToDto(saved);
    }

    public void delete(Long id) {
        if (!repository.existsById(id)) {
            throw new RuntimeException("__CLASS_NAME__ not found with id " + id);
        }
        repository.deleteById(id);
    }

    private __CLASS_NAME__Dto convertToDto(__CLASS_NAME__ entity) {
        __CLASS_NAME__Dto dto = new __CLASS_NAME__Dto();
__TO_DTO_MAPPING__
        return dto;
    }

    private __CLASS_NAME__ convertToEntity(__CLASS_NAME__Dto dto) {
        __CLASS_NAME__ entity = new __CLASS_NAME__();
__TO_ENTITY_MAPPING__
        return entity;
    }
}
""",
    "Controller.java": """package com.medicare.__PKG__.controller;

import com.medicare.__PKG__.dto.__CLASS_NAME__Dto;
import com.medicare.__PKG__.service.__CLASS_NAME__Service;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import java.util.List;

@RestController
@RequestMapping("/api/__PATH__")
@CrossOrigin(origins = "*")
public class __CLASS_NAME__Controller {

    private final __CLASS_NAME__Service service;

    public __CLASS_NAME__Controller(__CLASS_NAME__Service service) {
        this.service = service;
    }

    @GetMapping
    public ResponseEntity<List<__CLASS_NAME__Dto>> getAll() {
        return ResponseEntity.ok(service.getAll());
    }

    @GetMapping("/{id}")
    public ResponseEntity<__CLASS_NAME__Dto> getById(@PathVariable Long id) {
        return ResponseEntity.ok(service.getById(id));
    }

    @PostMapping
    public ResponseEntity<__CLASS_NAME__Dto> create(@RequestBody __CLASS_NAME__Dto dto) {
        return ResponseEntity.status(HttpStatus.CREATED).body(service.create(dto));
    }

    @PutMapping("/{id}")
    public ResponseEntity<__CLASS_NAME__Dto> update(@PathVariable Long id, @RequestBody __CLASS_NAME__Dto dto) {
        return ResponseEntity.ok(service.update(id, dto));
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<Void> delete(@PathVariable Long id) {
        service.delete(id);
        return ResponseEntity.noContent().build();
    }
}
"""
}

SERVICES_SPEC = {
    "patient-service": {
        "port": 8081,
        "db": "medicare_patient_db",
        "pkg": "patient",
        "className": "Patient",
        "tableName": "patients",
        "path": "patients",
        "fields": """    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    private String fullName;
    private String dateOfBirth;
    private String gender;
    private String phone;
    private String address;
    private String insuranceId;""",
        "dto_fields": """    private Long id;
    private String fullName;
    private String dateOfBirth;
    private String gender;
    private String phone;
    private String address;
    private String insuranceId;""",
        "service_update_logic": """        existing.setFullName(dto.getFullName());
        existing.setDateOfBirth(dto.getDateOfBirth());
        existing.setGender(dto.getGender());
        existing.setPhone(dto.getPhone());
        existing.setAddress(dto.getAddress());
        existing.setInsuranceId(dto.getInsuranceId());""",
        "to_dto_mapping": """        dto.setId(entity.getId());
        dto.setFullName(entity.getFullName());
        dto.setDateOfBirth(entity.getDateOfBirth());
        dto.setGender(entity.getGender());
        dto.setPhone(entity.getPhone());
        dto.setAddress(entity.getAddress());
        dto.setInsuranceId(entity.getInsuranceId());""",
        "to_entity_mapping": """        entity.setId(dto.getId());
        entity.setFullName(dto.getFullName());
        entity.setDateOfBirth(dto.getDateOfBirth());
        entity.setGender(dto.getGender());
        entity.setPhone(dto.getPhone());
        entity.setAddress(dto.getAddress());
        entity.setInsuranceId(dto.getInsuranceId());"""
    },
    "doctor-service": {
        "port": 8082,
        "db": "medicare_doctor_db",
        "pkg": "doctor",
        "className": "Doctor",
        "tableName": "doctors",
        "path": "doctors",
        "fields": """    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    private String fullName;
    private String specialty;
    private String phone;
    private String email;
    private String department;""",
        "dto_fields": """    private Long id;
    private String fullName;
    private String specialty;
    private String phone;
    private String email;
    private String department;""",
        "service_update_logic": """        existing.setFullName(dto.getFullName());
        existing.setSpecialty(dto.getSpecialty());
        existing.setPhone(dto.getPhone());
        existing.setEmail(dto.getEmail());
        existing.setDepartment(dto.getDepartment());""",
        "to_dto_mapping": """        dto.setId(entity.getId());
        dto.setFullName(entity.getFullName());
        dto.setSpecialty(entity.getSpecialty());
        dto.setPhone(entity.getPhone());
        dto.setEmail(entity.getEmail());
        dto.setDepartment(entity.getDepartment());""",
        "to_entity_mapping": """        entity.setId(dto.getId());
        entity.setFullName(dto.getFullName());
        entity.setSpecialty(entity.getSpecialty());
        entity.setPhone(entity.getPhone());
        entity.setEmail(entity.getEmail());
        entity.setDepartment(entity.getDepartment());"""
    },
    "appointment-service": {
        "port": 8083,
        "db": "medicare_appointment_db",
        "pkg": "appointment",
        "className": "Appointment",
        "tableName": "appointments",
        "path": "appointments",
        "fields": """    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    private Long patientId;
    private Long doctorId;
    private String appointmentDate;
    private String status;
    private String notes;""",
        "dto_fields": """    private Long id;
    private Long patientId;
    private Long doctorId;
    private String appointmentDate;
    private String status;
    private String notes;""",
        "service_update_logic": """        existing.setPatientId(dto.getPatientId());
        existing.setDoctorId(dto.getDoctorId());
        existing.setAppointmentDate(dto.getAppointmentDate());
        existing.setStatus(dto.getStatus());
        existing.setNotes(dto.getNotes());""",
        "to_dto_mapping": """        dto.setId(entity.getId());
        dto.setPatientId(entity.getPatientId());
        dto.setDoctorId(entity.getDoctorId());
        dto.setAppointmentDate(entity.getAppointmentDate());
        dto.setStatus(entity.getStatus());
        dto.setNotes(entity.getNotes());""",
        "to_entity_mapping": """        entity.setId(dto.getId());
        entity.setPatientId(dto.getPatientId());
        entity.setDoctorId(dto.getDoctorId());
        entity.setAppointmentDate(dto.getAppointmentDate());
        entity.setStatus(dto.getStatus());
        entity.setNotes(dto.getNotes());"""
    },
    "medical-record-service": {
        "port": 8084,
        "db": "medicare_medical_record_db",
        "pkg": "medicalrecord",
        "className": "MedicalRecord",
        "tableName": "medical_records",
        "path": "medical-records",
        "fields": """    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    private Long patientId;
    private Long doctorId;
    private String diagnosis;
    private String treatment;
    private String recordDate;""",
        "dto_fields": """    private Long id;
    private Long patientId;
    private Long doctorId;
    private String diagnosis;
    private String treatment;
    private String recordDate;""",
        "service_update_logic": """        existing.setPatientId(dto.getPatientId());
        existing.setDoctorId(dto.getDoctorId());
        existing.setDiagnosis(dto.getDiagnosis());
        existing.setTreatment(dto.getTreatment());
        existing.setRecordDate(dto.getRecordDate());""",
        "to_dto_mapping": """        dto.setId(entity.getId());
        dto.setPatientId(entity.getPatientId());
        dto.setDoctorId(entity.getDoctorId());
        dto.setDiagnosis(entity.getDiagnosis());
        dto.setTreatment(entity.getTreatment());
        dto.setRecordDate(entity.getRecordDate());""",
        "to_entity_mapping": """        entity.setId(dto.getId());
        entity.setPatientId(dto.getPatientId());
        entity.setDoctorId(dto.getDoctorId());
        entity.setDiagnosis(entity.getDiagnosis());
        entity.setTreatment(entity.getTreatment());
        entity.setRecordDate(entity.getRecordDate());"""
    },
    "pharmacy-service": {
        "port": 8085,
        "db": "medicare_pharmacy_db",
        "pkg": "pharmacy",
        "className": "Medication",
        "tableName": "medications",
        "path": "medications",
        "fields": """    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    private String name;
    private String description;
    private Double price;
    private Integer stockQuantity;""",
        "dto_fields": """    private Long id;
    private String name;
    private String description;
    private Double price;
    private Integer stockQuantity;""",
        "service_update_logic": """        existing.setName(dto.getName());
        existing.setDescription(dto.getDescription());
        existing.setPrice(dto.getPrice());
        existing.setStockQuantity(dto.getStockQuantity());""",
        "to_dto_mapping": """        dto.setId(entity.getId());
        dto.setName(entity.getName());
        dto.setDescription(entity.getDescription());
        dto.setPrice(entity.getPrice());
        dto.setStockQuantity(entity.getStockQuantity());""",
        "to_entity_mapping": """        entity.setId(dto.getId());
        entity.setName(dto.getName());
        entity.setDescription(dto.getDescription());
        entity.setPrice(dto.getPrice());
        entity.setStockQuantity(dto.getStockQuantity());"""
    }
}

def write_file(filepath, content):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"  [File sinh] {filepath}")

def generate_java_projects():
    print("[*] Đang tiến hành sinh toàn bộ 5 dự án Spring Boot (Gradle)...\n")
    for service_name, spec in SERVICES_SPEC.items():
        print(f"===> Đang tạo project: {service_name}")
        
        # 1. build.gradle
        write_file(f"{service_name}/build.gradle", JAVA_TEMPLATES["build.gradle"])
        
        # 2. application.yml
        app_yml_content = JAVA_TEMPLATES["application.yml"] \
            .replace("__PORT__", str(spec["port"])) \
            .replace("__APP_NAME__", service_name) \
            .replace("__DB_NAME__", spec["db"])
        write_file(f"{service_name}/src/main/resources/application.yml", app_yml_content)
        
        # Base package path
        package_path = f"{service_name}/src/main/java/com/medicare/{spec['pkg']}"
        
        # Helper lambda to substitute dynamic variables
        def fill_template(template_key):
            return JAVA_TEMPLATES[template_key] \
                .replace("__PKG__", spec["pkg"]) \
                .replace("__CLASS_NAME__", spec["className"]) \
                .replace("__TABLE_NAME__", spec["tableName"]) \
                .replace("__FIELDS__", spec["fields"]) \
                .replace("__DTO_FIELDS__", spec["dto_fields"]) \
                .replace("__SERVICE_UPDATE_LOGIC__", spec["service_update_logic"]) \
                .replace("__TO_DTO_MAPPING__", spec["to_dto_mapping"]) \
                .replace("__TO_ENTITY_MAPPING__", spec["to_entity_mapping"]) \
                .replace("__PATH__", spec["path"])
        
        # 3. Main Application
        write_file(f"{package_path}/{spec['className']}Application.java", fill_template("MainApplication.java"))
        
        # 4. Entity Class
        write_file(f"{package_path}/model/{spec['className']}.java", fill_template("Entity.java"))
        
        # 5. Dto Class
        write_file(f"{package_path}/dto/{spec['className']}Dto.java", fill_template("Dto.java"))
        
        # 6. Repository Class
        write_file(f"{package_path}/repository/{spec['className']}Repository.java", fill_template("Repository.java"))
        
        # 7. Service Class
        write_file(f"{package_path}/service/{spec['className']}Service.java", fill_template("Service.java"))
        
        # 8. Controller Class
        write_file(f"{package_path}/controller/{spec['className']}Controller.java", fill_template("Controller.java"))
        
        print(f"===> Đã sinh thành công dự án {service_name}!\n")
    print("[*] Quá trình sinh mã nguồn hoàn tất!")
    print("Bạn có thể mở từng thư mục dự án trong IntelliJ IDEA hoặc Eclipse để build bằng Gradle.")

def main():
    if len(sys.argv) < 2:
        print("HỆ THỐNG QUẢN LÝ MEDICARE MICROSERVICES")
        print("=========================================")
        print("Cú pháp sử dụng:")
        print("  python main.py --generate   : Sinh mã nguồn 5 dự án Spring Boot chuẩn cấu trúc")
        print("  python main.py --run-mock   : Khởi chạy 5 cổng API giả lập trên ports 8081-8085")
        sys.exit(0)
        
    mode = sys.argv[1]
    if mode == "--generate":
        generate_java_projects()
    elif mode == "--run-mock":
        print("[*] Khởi chạy Máy chủ Giả lập (Mock Server) cho các MediCare Microservices...")
        print("[*] Đang kết nối Cơ sở dữ liệu giả lập (RAM)...\n")
        
        threads = []
        for port in PORT_MAPPING.keys():
            t = threading.Thread(target=start_mock_server, args=(port,))
            t.daemon = True
            t.start()
            threads.append(t)
            
        print("\n[*] CẢ 5 SERVICES ĐÃ KHỞI CHẠY THÀNH CÔNG!")
        print("Nhấn Ctrl+C để tắt hệ thống máy chủ giả lập.\n")
        
        # Giữ luồng chính chạy
        try:
            while True:
                pass
        except KeyboardInterrupt:
            print("\n[!] Đang tắt hệ thống Máy chủ giả lập. Tạm biệt!")
    else:
        print(f"Lỗi: Tham số không xác định '{mode}'. Sử dụng --generate hoặc --run-mock.")

if __name__ == '__main__':
    main()
