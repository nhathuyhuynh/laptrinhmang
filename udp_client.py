#!/usr/bin/env python3
"""
UDP Client đơn giản để test server
Có thể gửi nhiều loại message khác nhau
"""

import socket
import time
import threading
import random
from datetime import datetime

class UDPClient:
    def __init__(self, server_host='127.0.0.1', server_port=8888):
        """Khởi tạo UDP client"""
        self.server_address = (server_host, server_port)
        self.client_socket = None
        
        # Thống kê
        self.stats = {
            'packets_sent': 0,
            'packets_received': 0,
            'total_rtt': 0.0,  # Tổng thời gian round-trip
            'min_rtt': float('inf'),
            'max_rtt': 0.0,
            'errors': 0
        }
        
        print(f"[CLIENT] Kết nối đến server {server_host}:{server_port}")
    
    def connect(self):
        """Kết nối đến server"""
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.client_socket.settimeout(3.0)  # Timeout 3 giây
            return True
        except Exception as e:
            print(f"[CLIENT] Lỗi kết nối: {e}")
            return False
    
    def send_message(self, message, wait_for_response=True):
        """Gửi message đến server"""
        try:
            # Đo thời gian bắt đầu
            start_time = time.time()
            
            # Gửi message
            self.client_socket.sendto(message.encode('utf-8'), self.server_address)
            self.stats['packets_sent'] += 1
            
            print(f"[CLIENT] Đã gửi: {message[:50]}...")
            
            if wait_for_response:
                # Chờ phản hồi từ server
                response_data, _ = self.client_socket.recvfrom(4096)
                response = response_data.decode('utf-8', errors='ignore')
                
                # Tính RTT (Round-Trip Time)
                rtt = (time.time() - start_time) * 1000  # ms
                
                # Cập nhật thống kê
                self.stats['packets_received'] += 1
                self.stats['total_rtt'] += rtt
                self.stats['min_rtt'] = min(self.stats['min_rtt'], rtt)
                self.stats['max_rtt'] = max(self.stats['max_rtt'], rtt)
                
                print(f"[CLIENT] Nhận phản hồi (RTT: {rtt:.1f}ms): {response[:100]}...")
                
                return response, rtt
            else:
                return None, None
                
        except socket.timeout:
            print(f"[CLIENT] Timeout! Không nhận được phản hồi.")
            self.stats['errors'] += 1
            return None, None
        except Exception as e:
            print(f"[CLIENT] Lỗi: {e}")
            self.stats['errors'] += 1
            return None, None
    
    def send_multiple_messages(self, messages):
        """Gửi nhiều messages liên tiếp"""
        results = []
        
        for i, message in enumerate(messages):
            print(f"\n[CLIENT] Gửi message {i+1}/{len(messages)}")
            response, rtt = self.send_message(message)
            if response:
                results.append({
                    'message': message,
                    'response': response,
                    'rtt': rtt
                })
            
            # Delay ngẫu nhiên giữa các message
            time.sleep(random.uniform(0.1, 0.5))
        
        return results
    
    def test_performance(self, num_messages=10, message_size=100):
        """Test hiệu năng với nhiều messages"""
        print(f"\n[CLIENT] Bắt đầu test hiệu năng: {num_messages} messages")
        
        test_messages = []
        for i in range(num_messages):
            # Tạo message ngẫu nhiên
            message = f"Test message {i+1}: " + "Hi" * message_size
            test_messages.append(message)
        
        start_time = time.time()
        results = self.send_multiple_messages(test_messages)
        end_time = time.time()
        
        # Tính toán thống kê
        total_time = end_time - start_time
        
        print(f"\n{'='*50}")
        print("KẾT QUẢ TEST HIỆU NĂNG")
        print(f"{'='*50}")
        print(f"Tổng số messages: {num_messages}")
        print(f"Thời gian tổng: {total_time:.2f} giây")
        print(f"Messages/giây: {num_messages/total_time:.1f}")
        
        if self.stats['packets_received'] > 0:
            avg_rtt = self.stats['total_rtt'] / self.stats['packets_received']
            print(f"RTT trung bình: {avg_rtt:.1f} ms")
            print(f"RTT thấp nhất: {self.stats['min_rtt']:.1f} ms")
            print(f"RTT cao nhất: {self.stats['max_rtt']:.1f} ms")
        
        print(f"Tỷ lệ thành công: {self.stats['packets_received']}/{self.stats['packets_sent']}")
        print(f"Số lỗi: {self.stats['errors']}")
        
        return results
    
    def close(self):
        """Đóng kết nối"""
        if self.client_socket:
            self.client_socket.close()
            print("[CLIENT] Đã đóng kết nối")

# Các hàm tiện ích cho client
def send_single_message():
    """Gửi một message đơn giản"""
    client = UDPClient()
    if client.connect():
        message = input("Nhập message gửi đến server: ")
        client.send_message(message)
        client.close()

def run_performance_test():
    """Chạy test hiệu năng"""
    client = UDPClient()
    if client.connect():
        # Test với 20 messages
        client.test_performance(num_messages=20, message_size=50)
        client.close()

def interactive_client():
    """Client tương tác với server"""
    client = UDPClient()
    
    if not client.connect():
        print("Không thể kết nối đến server!")
        return
    
    print("\n" + "="*50)
    print("UDP CLIENT - Gõ lệnh để tương tác với server")
    print("="*50)
    print("Các lệnh đặc biệt:")
    print("  'stats'    - Xem thống kê server")
    print("  'time'     - Lấy thời gian từ server")
    print("  'ping'     - Kiểm tra kết nối")
    print("  'test'     - Chạy test hiệu năng")
    print("  'exit'     - Thoát client")
    print("="*50)
    
    while True:
        try:
            # Nhập lệnh từ người dùng
            user_input = input("\n>>> ").strip()
            
            if user_input.lower() == 'exit':
                break
            elif user_input.lower() == 'test':
                client.test_performance(num_messages=10, message_size=30)
            elif user_input.lower() == '':
                continue
            else:
                client.send_message(user_input)
                
        except KeyboardInterrupt:
            print("\n\nĐang thoát...")
            break
        except Exception as e:
            print(f"Lỗi: {e}")
    
    client.close()

if __name__ == "__main__":
    # Chạy client tương tác
    interactive_client()