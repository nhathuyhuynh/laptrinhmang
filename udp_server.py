#!/usr/bin/env python3
"""
UDP Echo Server đơn giản với kỹ thuật tối ưu
Server nhận dữ liệu và gửi lại (echo) cho client
"""

import socket
import time
import threading
from datetime import datetime

class SimpleUDPServer:
    def __init__(self, host='127.0.0.1', port=8888):
        """Khởi tạo UDP server"""
        self.host = host
        self.port = port
        self.server_socket = None
        self.running = False
        
        # Thống kê
        self.stats = {
            'start_time': time.time(),
            'packets_received': 0,
            'packets_sent': 0,
            'bytes_received': 0,
            'bytes_sent': 0,
            'clients': {}  # Lưu thông tin client
        }
        
        print(f"[SERVER] Đang khởi động UDP Server trên {host}:{port}")
    
    def start(self):
        """Bắt đầu server"""
        try:
            # 1. Tạo socket UDP
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            
            # 2. Cấu hình socket
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.settimeout(1.0)  # Timeout 1 giây
            
            # 3. Bind địa chỉ
            self.server_socket.bind((self.host, self.port))
            
            # 4. Bắt đầu lắng nghe
            self.running = True
            print(f"[SERVER] Đã sẵn sàng. Đang chờ kết nối...")
            
            # 5. Vòng lặp chính
            while self.running:
                try:
                    # Nhận dữ liệu từ client
                    data, client_address = self.server_socket.recvfrom(4096)
                    
                    # Cập nhật thống kê
                    self._update_stats(data, client_address)
                    
                    # Xử lý dữ liệu
                    self._handle_packet(data, client_address)
                    
                except socket.timeout:
                    # Timeout là bình thường, tiếp tục vòng lặp
                    continue
                except Exception as e:
                    print(f"[SERVER] Lỗi: {e}")
                    break
                    
        except KeyboardInterrupt:
            print("\n[SERVER] Đang dừng...")
        finally:
            self.stop()
    
    def _update_stats(self, data, client_address):
        """Cập nhật thống kê"""
        client_id = f"{client_address[0]}:{client_address[1]}"
        
        # Cập nhật client
        if client_id not in self.stats['clients']:
            self.stats['clients'][client_id] = {
                'first_seen': datetime.now().strftime("%H:%M:%S"),
                'packets_received': 0,
                'last_seen': datetime.now().strftime("%H:%M:%S")
            }
        
        self.stats['clients'][client_id]['packets_received'] += 1
        self.stats['clients'][client_id]['last_seen'] = datetime.now().strftime("%H:%M:%S")
        
        # Cập nhật tổng
        self.stats['packets_received'] += 1
        self.stats['bytes_received'] += len(data)
    
    def _handle_packet(self, data, client_address):
        """Xử lý packet từ client"""
        try:
            # 1. Giải mã dữ liệu
            message = data.decode('utf-8', errors='ignore')
            
            print(f"[SERVER] Nhận từ {client_address}: {message[:50]}...")
            
            # 2. Tùy chọn: Xử lý đặc biệt cho một số lệnh
            if message.strip().lower() == 'stats':
                # Client yêu cầu thống kê
                response = self._get_stats_response()
            elif message.strip().lower() == 'time':
                # Client yêu cầu thời gian
                response = f"Thời gian server: {datetime.now().strftime('%H:%M:%S')}"
            elif message.strip().lower() == 'ping':
                # Ping request
                response = "PONG"
            else:
                # Echo thông thường
                response = f"ECHO: {message}"
            
            # 3. Gửi phản hồi
            self.server_socket.sendto(response.encode('utf-8'), client_address)
            
            # 4. Cập nhật thống kê gửi
            self.stats['packets_sent'] += 1
            self.stats['bytes_sent'] += len(response.encode('utf-8'))
            
        except Exception as e:
            print(f"[SERVER] Lỗi xử lý packet: {e}")
            # Gửi lỗi về client
            error_msg = f"ERROR: {str(e)}"
            self.server_socket.sendto(error_msg.encode('utf-8'), client_address)
    
    def _get_stats_response(self):
        """Tạo response thống kê"""
        uptime = time.time() - self.stats['start_time']
        
        stats_text = f"""
=== THỐNG KÊ SERVER ===
Thời gian hoạt động: {uptime:.1f} giây
Số packet đã nhận: {self.stats['packets_received']}
Số packet đã gửi: {self.stats['packets_sent']}
Tổng bytes nhận: {self.stats['bytes_received']}
Tổng bytes gửi: {self.stats['bytes_sent']}
Số client đã kết nối: {len(self.stats['clients'])}
"""
        return stats_text
    
    def stop(self):
        """Dừng server"""
        self.running = False
        if self.server_socket:
            self.server_socket.close()
        
        # Hiển thị thống kê cuối
        print("\n=== THỐNG KÊ CUỐI ===")
        print(f"Tổng thời gian hoạt động: {time.time() - self.stats['start_time']:.1f}s")
        print(f"Tổng packet: {self.stats['packets_received']}")
        print(f"Tổng client: {len(self.stats['clients'])}")

# Hàm chạy server
def run_server():
    """Hàm chạy server - có thể gọi từ file khác"""
    server = SimpleUDPServer(host='127.0.0.1', port=8888)
    server.start()

if __name__ == "__main__":
    # Chạy server khi trực tiếp thực thi file
    run_server()