import socket
import threading
import json

class GameServer:
    def __init__(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind(('127.0.0.1', 5555))
        self.clients = {}
        self.waiting = []
        self.rooms = {}
        
    def start(self):
        self.server.listen()
        print("[SERVER] Đang chạy...")
        while True:
            conn, addr = self.server.accept()
            threading.Thread(target=self.handle_client, args=(conn,)).start()
    
    def handle_client(self, conn):
        try:
            # Nhận tên
            name = json.loads(conn.recv(1024).decode())['name']
            self.clients[conn] = {'name': name, 'choice': None, 'score': 0}
            self.send(conn, {'type': 'welcome'})
            
            # Thêm vào phòng chờ
            self.waiting.append(conn)
            if len(self.waiting) >= 2:
                p1, p2 = self.waiting.pop(0), self.waiting.pop(0)
                room_id = f"room_{len(self.rooms)}"
                self.rooms[room_id] = [p1, p2]
                
                self.send(p1, {'type': 'start', 'opponent': self.clients[p2]['name']})
                self.send(p2, {'type': 'start', 'opponent': self.clients[p1]['name']})
            
            # Nhận lựa chọn
            while True:
                data = json.loads(conn.recv(1024).decode())
                if data['type'] == 'choice':
                    self.clients[conn]['choice'] = data['choice']
                    self.check_result(conn)
        except:
            self.disconnect(conn)
    
    def check_result(self, conn):
        for room_id, players in self.rooms.items():
            if conn in players:
                if all(self.clients[p]['choice'] for p in players):
                    self.calc_winner(players)
                break
    
    def calc_winner(self, players):
        p1, p2 = players
        c1, c2 = self.clients[p1]['choice'], self.clients[p2]['choice']
        
        if c1 == c2:
            result = [0, 0]
        else:
            wins = {'kéo': 'bao', 'búa': 'kéo', 'bao': 'búa'}
            if wins[c1] == c2:
                result = [1, 0]
                self.clients[p1]['score'] += 1
            else:
                result = [0, 1]
                self.clients[p2]['score'] += 1
        
        self.send(p1, {'type': 'result', 'win': result[0], 'your': c1, 'opp': c2, 
                       'score': [self.clients[p1]['score'], self.clients[p2]['score']]})
        self.send(p2, {'type': 'result', 'win': result[1], 'your': c2, 'opp': c1,
                       'score': [self.clients[p2]['score'], self.clients[p1]['score']]})
        
        self.clients[p1]['choice'] = None
        self.clients[p2]['choice'] = None
    
    def send(self, conn, msg):
        try:
            conn.send(json.dumps(msg).encode())
        except:
            pass
    
    def disconnect(self, conn):
        if conn in self.clients:
            del self.clients[conn]
        if conn in self.waiting:
            self.waiting.remove(conn)
        conn.close()

if __name__ == "__main__":
    GameServer().start()