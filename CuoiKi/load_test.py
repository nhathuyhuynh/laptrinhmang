import asyncio
import websockets
import json
import time

# Cấu hình load test
SERVER_URL = "ws://localhost:8765"
NUM_CLIENTS = 50  # Số lượng clients đồng thời
MESSAGES_PER_CLIENT = 10  # Số tin nhắn mỗi client gửi
MESSAGE_DELAY = 0.5  # Delay giữa các tin nhắn (giây)

# Thống kê
stats = {
    "total_clients": 0,
    "connected_clients": 0,
    "total_messages_sent": 0,
    "total_messages_received": 0,
    "failed_connections": 0,
    "start_time": None,
    "end_time": None
}


async def client_worker(client_id):
    """
    Mô phỏng một client kết nối và gửi tin nhắn
    """
    try:
        # Kết nối đến server
        async with websockets.connect(SERVER_URL) as websocket:
            stats["connected_clients"] += 1
            print(f"[+] Client {client_id} connected")
            
            # Nhận lịch sử (nếu có)
            try:
                history = await asyncio.wait_for(websocket.recv(), timeout=2.0)
                stats["total_messages_received"] += 1
            except asyncio.TimeoutError:
                pass
            
            # Gửi tin nhắn
            for i in range(MESSAGES_PER_CLIENT):
                message = {
                    "username": f"LoadTest-Client{client_id}",
                    "message": f"Test message {i+1} from client {client_id}"
                }
                
                await websocket.send(json.dumps(message))
                stats["total_messages_sent"] += 1
                
                print(f"[→] Client {client_id} sent message {i+1}/{MESSAGES_PER_CLIENT}")
                
                # Nhận response
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=2.0)
                    stats["total_messages_received"] += 1
                except asyncio.TimeoutError:
                    print(f"[!] Client {client_id} timeout receiving message")
                
                # Delay giữa các tin nhắn
                await asyncio.sleep(MESSAGE_DELAY)
            
            print(f"[-] Client {client_id} finished")
            stats["connected_clients"] -= 1
            
    except Exception as e:
        stats["failed_connections"] += 1
        print(f"[!] Client {client_id} error: {e}")


async def run_load_test():
    """
    Chạy load test với nhiều clients đồng thời
    """
    print("="*70)
    print("🚀 WEBSOCKET LOAD TEST")
    print("="*70)
    print(f"Server URL: {SERVER_URL}")
    print(f"Number of concurrent clients: {NUM_CLIENTS}")
    print(f"Messages per client: {MESSAGES_PER_CLIENT}")
    print(f"Total messages: {NUM_CLIENTS * MESSAGES_PER_CLIENT}")
    print("="*70)
    print()
    
    # Bắt đầu đếm thời gian
    stats["start_time"] = time.time()
    stats["total_clients"] = NUM_CLIENTS
    
    # Tạo tasks cho tất cả clients
    tasks = []
    for i in range(NUM_CLIENTS):
        task = asyncio.create_task(client_worker(i+1))
        tasks.append(task)
        
        # Delay nhỏ giữa các client để tránh overwhelm server
        await asyncio.sleep(0.1)
    
    # Đợi tất cả clients hoàn thành
    await asyncio.gather(*tasks, return_exceptions=True)
    
    # Kết thúc đếm thời gian
    stats["end_time"] = time.time()
    
    # In kết quả
    print_results()


def print_results():
    """
    In kết quả load test
    """
    duration = stats["end_time"] - stats["start_time"]
    messages_per_second = stats["total_messages_sent"] / duration if duration > 0 else 0
    
    print()
    print("="*70)
    print("📊 LOAD TEST RESULTS")
    print("="*70)
    print(f"Total duration: {duration:.2f} seconds")
    print(f"Total clients: {stats['total_clients']}")
    print(f"Successful connections: {stats['total_clients'] - stats['failed_connections']}")
    print(f"Failed connections: {stats['failed_connections']}")
    print()
    print(f"Total messages sent: {stats['total_messages_sent']}")
    print(f"Total messages received: {stats['total_messages_received']}")
    print(f"Messages per second: {messages_per_second:.2f} msg/s")
    print()
    
    # Tính success rate
    success_rate = ((stats['total_clients'] - stats['failed_connections']) / stats['total_clients'] * 100) if stats['total_clients'] > 0 else 0
    
    print(f"Success rate: {success_rate:.1f}%")
    
    # Đánh giá performance
    print()
    print("Performance Rating:")
    if messages_per_second > 100:
        print("⭐⭐⭐⭐⭐ Excellent! Very high throughput")
    elif messages_per_second > 50:
        print("⭐⭐⭐⭐ Great! Good performance")
    elif messages_per_second > 20:
        print("⭐⭐⭐ Good! Acceptable performance")
    else:
        print("⭐⭐ Fair. Consider optimization")
    
    print("="*70)


async def main():
    """
    Entry point
    """
    try:
        await run_load_test()
    except KeyboardInterrupt:
        print("\n[!] Load test interrupted by user")
    except Exception as e:
        print(f"\n[!] Load test error: {e}")


if __name__ == "__main__":
    asyncio.run(main())