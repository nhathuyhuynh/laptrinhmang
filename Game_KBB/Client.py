import socket
import threading
import json
import random
import os

class GameClient:
    def __init__(self):
        self.sock = None
        self.mode = None
        self.scores = [0, 0]  # [player, opponent]
        
    def menu(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        print("=" * 40)
        print("    GAME KÉO BÚA BAO")
        print("=" * 40)
        print("1. Chơi với Máy")
        print("2. Chơi với Người khác")
        print("3. Thoát")
        return input("\nChọn (1-3): ")
    
    def play(self):
        while True:
            choice = self.menu()
            if choice == '1':
                self.play_ai()
            elif choice == '2':
                self.play_online()
            elif choice == '3':
                break
    
    def play_ai(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        name = input("Tên của bạn: ") or "Player"
        self.scores = [0, 0]
        
        while True:
            print(f"\n{name} vs AI | Tỷ số: {self.scores[0]} - {self.scores[1]}")
            print("1.Kéo  2.Búa  3.Bao  (q=thoát)")
            
            c = input("Chọn: ")
            if c == 'q': break
            if c not in ['1','2','3']: continue
            
            choices = ['kéo', 'búa', 'bao']
            player = choices[int(c)-1]
            ai = random.choice(choices)
            
            print(f"\nBạn: {player} vs AI: {ai}")
            
            if player == ai:
                print("HÒA!")
            else:
                wins = {'kéo': 'bao', 'búa': 'kéo', 'bao': 'búa'}
                if wins[player] == ai:
                    print("BẠN THẮNG!")
                    self.scores[0] += 1
                else:
                    print("BẠN THUA!")
                    self.scores[1] += 1
            
            input("\nEnter để tiếp tục...")
    
    def play_online(self):
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect(('127.0.0.1', 5555))
        except:
            print("\nKhông kết nối được server!")
            input("Enter để tiếp tục...")
            return
        
        name = input("Tên của bạn: ") or "Player"
        self.sock.send(json.dumps({'name': name}).encode())
        self.scores = [0, 0]
        
        threading.Thread(target=self.receive, daemon=True).start()
        
        while True:
            print("\n1.Kéo  2.Búa  3.Bao")
            c = input("Chọn: ")
            if c not in ['1','2','3']: continue
            
            choice = ['kéo', 'búa', 'bao'][int(c)-1]
            self.sock.send(json.dumps({'type': 'choice', 'choice': choice}).encode())
            print("Đang đợi đối thủ...")
    
    def receive(self):
        while True:
            try:
                data = json.loads(self.sock.recv(1024).decode())
                
                if data['type'] == 'welcome':
                    print("\nĐang tìm đối thủ...")
                    
                elif data['type'] == 'start':
                    print(f"\nĐối thủ: {data['opponent']}")
                    
                elif data['type'] == 'result':
                    print(f"\n{'='*40}")
                    print(f"Bạn: {data['your']} vs Đối thủ: {data['opp']}")
                    
                    if data['win'] == 1:
                        print("BẠN THẮNG!")
                    elif data['win'] == 0:
                        if data['your'] == data['opp']:
                            print("HÒA!")
                        else:
                            print("BẠN THUA!")
                    
                    self.scores = data['score']
                    print(f"Tỷ số: {self.scores[0]} - {self.scores[1]}")
                    print("="*40)
            except:
                break

if __name__ == "__main__":
    GameClient().play()