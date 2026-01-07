"""
Script test tự động cho UDP Server và Client
Chạy test và hiển thị kết quả
"""

import subprocess
import time
import threading
import sys
import os

def run_server_in_thread():
    """Chạy server trong một thread riêng"""
    def server_thread():
        try:
            import udp_server
            udp_server.run_server()
        except Exception as e:
            print(f"[TEST] Lỗi server: {e}")
    
    thread = threading.Thread(target=server_thread, daemon=True)
    thread.start()
    return thread

def test_basic_communication():
    """Test giao tiếp cơ bản giữa client và server"""
    print("\n" + "="*60)
    print("TEST 1: GIAO TIẾP CƠ BẢN")
    print("="*60)
    
    try:
        import udp_client
        
        client = udp_client.UDPClient()
        
        if not client.connect():
            print(" Không thể kết nối đến server!")
            return False
        
        test_cases = [
            ("Hello Server!", "Thông điệp thông thường"),
            ("ping", "Ping request"),
            ("time", "Request thời gian"),
            ("stats", "Request thống kê"),
        ]
        
        success_count = 0
        for message, description in test_cases:
            print(f"\nTesting: {description} ('{message}')")
            
            response, rtt = client.send_message(message)
            
            if response:
                print(f"✓ Thành công! RTT: {rtt:.1f}ms")
                print(f"  Server response: {response[:80]}...")
                success_count += 1
            else:
                print(f"✗ Thất bại!")
        
        client.close()
        
        print(f"\n{'='*40}")
        result_text = f"KẾT QUẢ: {success_count}/{len(test_cases)} tests thành công"
        if success_count == len(test_cases):
            print(result_text)
        else:
            print(result_text)
        
        return success_count == len(test_cases)
        
    except Exception as e:
        print(f" Lỗi trong test: {e}")
        return False

def test_performance():
    """Test hiệu năng với nhiều messages"""
    print("\n" + "="*60)
    print("TEST 2: HIỆU NĂNG VỚI NHIỀU MESSAGES")
    print("="*60)
    
    try:
        import udp_client
        
        client = udp_client.UDPClient()
        
        if not client.connect():
            return False
        
        print("\nĐang chạy test hiệu năng...")
        
        results = client.test_performance(
            num_messages=15,
            message_size=40
        )
        
        client.close()
        
        if results:
            print("✓ Test hiệu năng hoàn tất!")
            return True
        else:
            print("✗ Test hiệu năng thất bại!")
            return False
            
    except Exception as e:
        print(f" Lỗi test hiệu năng: {e}")
        return False

def test_concurrent_clients():
    """Test nhiều clients đồng thời"""
    print("\n" + "="*60)
    print("TEST 3: NHIỀU CLIENTS ĐỒNG THỜI")
    print("="*60)
    
    def client_worker(client_id):
        """Mỗi client chạy trong thread riêng"""
        try:
            import udp_client
            client = udp_client.UDPClient()
            
            if client.connect():
                for i in range(5):
                    message = f"Client {client_id}, message {i+1}"
                    response, rtt = client.send_message(message, wait_for_response=True)
                    
                    if response and rtt:
                        print(f"[Client {client_id}] Message {i+1}: RTT {rtt:.1f}ms")
                    else:
                        print(f"[Client {client_id}] Message {i+1}: Failed")
                    
                    time.sleep(0.1)
                
                client.close()
                return True
            return False
            
        except Exception as e:
            print(f"[Client {client_id}] Error: {e}")
            return False
    
    threads = []
    for i in range(3):
        thread = threading.Thread(target=client_worker, args=(i+1,))
        threads.append(thread)
        thread.start()
    
    for thread in threads:
        thread.join(timeout=10)
    
    print("✓ Test nhiều clients hoàn tất!")
    return True

def run_all_tests():
    """Chạy tất cả các tests"""
    print("\n" + "="*70)
    print("BẮT ĐẦU CHẠY TẤT CẢ TESTS")
    print("="*70)
    
    test_results = []
    
    result1 = test_basic_communication()
    test_results.append(("Giao tiếp cơ bản", result1))
    
    time.sleep(1)
    
    result2 = test_performance()
    test_results.append(("Hiệu năng", result2))
    
    time.sleep(1)
    
    result3 = test_concurrent_clients()
    test_results.append(("Nhiều clients đồng thời", result3))
    
    print("\n" + "="*70)
    print("TỔNG KẾT KẾT QUẢ TEST")
    print("="*70)
    
    passed = sum(1 for _, result in test_results if result)
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✓ PASSED" if result else "✗ FAILED"
        print(f"{test_name:30} {status}")
    
    print(f"\nĐã hoàn thành: {passed}/{total} tests")
    
    if passed == total:
        print("\n TẤT CẢ TESTS ĐÃ THÀNH CÔNG!")
    else:
        print(f"\n  Có {total - passed} test thất bại")
    
    return passed == total

def quick_demo():
    """Chạy demo nhanh tất cả trong một"""
    print("\n" + "="*70)
    print("UDP SERVER & CLIENT DEMO - BẮT ĐẦU")
    print("="*70)
    
    print("\n[1/3] Đang khởi động server...")
    server_thread = run_server_in_thread()
    time.sleep(2)
    
    print("\n[2/3] Đang chạy tests...")
    success = run_all_tests()
    
    print("\n[3/3] Đang kết thúc demo...")
    
    time.sleep(1)
    
    if success:
        print("\n DEMO HOÀN TẤT THÀNH CÔNG!")
    else:
        print("\n DEMO HOÀN TẤT VỚI MỘT SỐ LỖI")
    
    print("\nĐể chạy lại, nhấn: python test.py")
    print("Hoặc chạy riêng server/client:")
    print("  python udp_server.py  (trong terminal riêng)")
    print("  python udp_client.py  (trong terminal riêng)")

if __name__ == "__main__":
    if sys.version_info < (3, 6):
        print("  Yêu cầu Python 3.6 hoặc cao hơn!")
        sys.exit(1)
    
    print("\n" + "="*70)
    print("UDP OPTIMIZATION DEMO")
    print("="*70)
    print("Cấu trúc thư mục:")
    print("  udp_server.py - Máy chủ UDP với kỹ thuật tối ưu")
    print("  udp_client.py - Máy khách UDP để test")
    print("  test.py       - Script test tự động")
    print("="*70)
    
    try:
        quick_demo()
    except KeyboardInterrupt:
        print("\n\n  Đã dừng demo bởi người dùng")
    except Exception as e:
        print(f"\n Lỗi không mong muốn: {e}")
    
    input("\nNhấn Enter để kết thúc...")