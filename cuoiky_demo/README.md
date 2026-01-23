# WebSocket Chat Server với SSL/TLS - High Performance Application

Ứng dụng chat realtime sử dụng WebSocket + SSL/TLS, đáp ứng yêu cầu **"Xây dựng ứng dụng có khả năng chịu tải cao"**

# Tính năng

#  Đáp ứng yêu cầu đề bài:
-  WebSocket - Công nghệ được yêu cầu trong đề
-  SSL/TLS - Bảo mật và mã hóa
-  Chịu tải cao - Hỗ trợ nhiều clients đồng thời
-  Async I/O - Sử dụng asyncio để xử lý bất đồng bộ
-  Realtime Communication - Giao tiếp thời gian thực

# Chức năng:
- Chat realtime giữa nhiều users
- Mã hóa SSL/TLS (wss://)
- Broadcast tin nhắn đến tất cả clients
- Lịch sử tin nhắn (50 messages gần nhất)
- Hiển thị số users online
- Thông báo join/leave
- Giao diện web đẹp mắt
- Auto-reconnect khi mất kết nối
- Fallback từ SSL sang non-SSL nếu cần

## Cấu trúc thư mục

```
elearning5/
├── certs/
│   ├── server.crt              # SSL Certificate
│   └── server.key              # SSL Private Key
├── websocket_server_ssl.py     # WebSocket server với SSL/TLS
├── chat_client.html            # Web client với SSL support
├── load_test.py               # Script test hiệu năng
└── README.md                  # File này
```

# Cài đặt

### 1. Cài đặt Python dependencies:
```bash
pip install websockets
```

### 2. Kiểm tra Python version (cần >= 3.7):
```bash
python --version
```

### 3. Kiểm tra certificates:
```bash
# Phải có 2 file này trong thư mục certs/
dir certs             # Windows
ls certs              # Mac/Linux
```

# Hướng dẫn chạy

# Bước 1: Chạy WebSocket Server với SSL/TLS

```bash
cd elearning5
python websocket_server_ssl.py
```

**Output với SSL:**
```
================================================================================
 HIGH-PERFORMANCE WEBSOCKET CHAT SERVER WITH SSL/TLS
================================================================================
[✓] SSL/TLS ENABLED
    Certificate: certs/server.crt
    Private Key: certs/server.key
[+] Host: 0.0.0.0
[+] Port: 8765
[+] Protocol: wss://
[+] URL: wss://localhost:8765
[+] Security: 🔒 ENCRYPTED
================================================================================
[✓] Server running! Waiting for connections...
[*] SSL/TLS: ENABLED ✅
[*] Press Ctrl+C to stop
```

# Bước 2: Mở Web Client

1. Mở file `chat_client.html` bằng trình duyệt (Chrome/Firefox/Edge)
2. Client sẽ tự động thử kết nối SSL trước
3. Nếu SSL fail → tự động fallback sang non-SSL

# Hoặc mở nhiều tab/cửa sổ để test multi-user:
- Tab 1: Alice
- Tab 2: Bob  
- Tab 3: Charlie

### Bước 3: Test Load với nhiều clients

```bash
python load_test.py
```

# Lưu ý: Load test script kết nối qua `ws://` (non-SSL) để test nhanh hơn.

## 🔐 SSL/TLS Configuration

# Bật/Tắt SSL:

Trong file `websocket_server_ssl.py`:**
```python
USE_SSL = True   # Bật SSL/TLS
USE_SSL = False  # Tắt SSL/TLS
```

# Khi SSL ENABLED:
- Protocol: `wss://` (WebSocket Secure)
- Port: 8765
- Certificate: `certs/server.crt`
- Private Key: `certs/server.key`
- Encryption: TLS 1.2+
- Cipher Suite: Tự động chọn cipher mạnh nhất

# Khi SSL DISABLED:
- Protocol: `ws://` (WebSocket)
- Port: 8765
- No encryption (plaintext)

# Kết quả Load Test Mẫu

```
============================================================
📊 LOAD TEST RESULTS
============================================================
Total duration: 25.43 seconds
Total clients: 50
Successful connections: 50
Failed connections: 0

Total messages sent: 500
Total messages received: 550
Messages per second: 19.66 msg/s

Success rate: 100.0%

Performance Rating:
⭐⭐⭐ Good! Acceptable performance
============================================================
```

# Web Client hiển thị:
- SSL Badge: 
  - 🔒 Green = SSL/TLS Enabled
  - 🔓 Orange = Non-SSL Connection
- Status Indicator: 
  - 🟢 Green dot = Connected
  - 🔴 Red dot = Disconnected
- Online Users: Số users đang online
- Stats Panel: Tổng số messages và peak concurrent users
- Encrypted Badge: 🔒 trên mỗi message nếu dùng SSL

# Message Layout:
- Tin nhắn của bạn: Bên phải, màu tím
- Tin nhắn người khác: Bên trái, màu trắng
- System messages: Giữa, màu xám

# Kiến trúc & Công nghệ

# Server Side:
- Python 3.7+
- asyncio - Async I/O framework
- websockets - WebSocket protocol
- ssl - SSL/TLS encryption
- JSON - Data serialization

# Client Side:
- HTML5 - Structure
- CSS3 - Styling với gradient và animations
- JavaScript - WebSocket API
- Auto SSL Fallback - Thử SSL trước, fallback nếu fail

# Security:
- TLS 1.2+ protocol
- Self-signed certificate (development)
- Certificate verification disabled (development mode)
- Production: Cần certificate từ CA (Let's Encrypt, etc.)

# Design Pattern:
- **Pub/Sub Pattern** - Broadcast to subscribers
- **Event-Driven Architecture** - Async event handling
- **Auto-reconnect** - Client tự động kết nối lại

# Bật/tắt SSL:
```python
USE_SSL = True   # hoặc False
```

# certificate path:
CERT_FILE = "certs/server.crt"
KEY_FILE = "certs/server.key"


# Thay đổi số lượng lịch sử:
"messages": message_history[-50:]  # Đổi 50 thành số khác

# Lỗi "Connection refused":
- Kiểm tra server đã chạy chưa
- Kiểm tra port 8765 có bị block không
- Kiểm tra firewall

# Client không kết nối được (SSL):
- Client sẽ tự động fallback sang non-SSL
- Xem Console browser (F12) để check lỗi
- Refresh trang (F5)

# Load test fail:
- Tăng timeout trong code
- Giảm số clients hoặc messages
- Kiểm tra server có đủ resources không

# Các kiến thức Lập trình mạng đã áp dụng

# 1. WebSocket Protocol
- Full-duplex communication
- Handshake upgrade từ HTTP
- Frame-based messaging
- ws:// và wss:// protocols

# 2. SSL/TLS Security
- TLS protocol stack
- Certificate management
- Public/Private key encryption
- Cipher suite selection

# 3. Asyncio Programming
- Event loop
- Coroutines (async/await)
- Non-blocking I/O
- Concurrent task execution

# 4. Socket Programming
- TCP/IP networking
- Socket binding và listening
- Connection management
- Client-server architecture

# 5. Broadcast Pattern
- Pub/Sub messaging
- One-to-many communication
- Concurrent message distribution

# Đáp ứng các yêu cầu hướng dẫn bài tập 5:
- [x] Code server với SSL/TLS
- [x] Code client hỗ trợ wss://
- [x] Script load testing
- [x] README đầy đủ
- [x] Certificates trong thư mục certs/
- [x] Screenshot server chạy với SSL
- [x] Screenshot client UI
- [x] Screenshot load test results
- [x] Đáp ứng "chịu tải cao" + "SSL/TLS"


# So với yêu cầu đề bài:
- WebSocket - Đúng công nghệ
- SSL/TLS - Bảo mật nâng cao
- Chịu tải cao - Asyncio + concurrent handling
- Code đầy đủ - Server + Client + Load test
- Hình ảnh - UI đẹp để demo

# So với hướng dẫn lý thuyết:
- Tích hợp SSL/TLS vào dự án Chat
- Quản lý certificates
- Hiểu về cipher suites
- Xử lý connections an toàn


**Bài tập 5: Xây dựng ứng dụng có khả năng chịu tải cao với SSL/TLS**
- Công nghệ: WebSocket + SSL/TLS
- Ngôn ngữ: Python + HTML/CSS/JS
- Framework: asyncio, websockets, ssl

---