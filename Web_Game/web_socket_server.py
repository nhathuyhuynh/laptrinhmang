import asyncio
import websockets
import json
import random

class Server:
    def __init__(self):
        self.clients = {}
        self.waiting = []
        self.rooms = {}
        
    async def handler(self, ws):
        try:
            async for msg in ws:
                data = json.loads(msg)
                
                if data['type'] == 'register':
                    self.clients[ws] = {'name': data['name'], 'choice': None, 'score': 0}
                    await self.send(ws, {'type': 'ok'})
                    
                elif data['type'] == 'find':
                    self.waiting.append(ws)
                    if len(self.waiting) >= 2:
                        p1, p2 = self.waiting.pop(0), self.waiting.pop(0)
                        room_id = f"r{len(self.rooms)}"
                        self.rooms[room_id] = [p1, p2]
                        
                        await self.send(p1, {'type': 'start', 'opp': self.clients[p2]['name']})
                        await self.send(p2, {'type': 'start', 'opp': self.clients[p1]['name']})
                    
                elif data['type'] == 'choice':
                    self.clients[ws]['choice'] = data['choice']
                    await self.check_result(ws)
                    
                elif data['type'] == 'ai':
                    ai = random.choice(['kéo', 'búa', 'bao'])
                    player = data['choice']
                    
                    if player == ai:
                        result = 'draw'
                    else:
                        wins = {'kéo': 'bao', 'búa': 'kéo', 'bao': 'búa'}
                        result = 'win' if wins[player] == ai else 'lose'
                    
                    await self.send(ws, {'type': 'ai_result', 'result': result, 
                                        'your': player, 'ai': ai})
        except websockets.exceptions.ConnectionClosed:
            pass
        except Exception as e:
            print(f"Lỗi: {e}")
        finally:
            if ws in self.clients:
                del self.clients[ws]
            if ws in self.waiting:
                self.waiting.remove(ws)
    
    async def check_result(self, ws):
        for room_id, players in self.rooms.items():
            if ws in players:
                if all(self.clients[p]['choice'] for p in players):
                    await self.calc_winner(players)
                break
    
    async def calc_winner(self, players):
        p1, p2 = players
        c1, c2 = self.clients[p1]['choice'], self.clients[p2]['choice']
        
        if c1 == c2:
            r1, r2 = 'draw', 'draw'
        else:
            wins = {'kéo': 'bao', 'búa': 'kéo', 'bao': 'búa'}
            if wins[c1] == c2:
                r1, r2 = 'win', 'lose'
                self.clients[p1]['score'] += 1
            else:
                r1, r2 = 'lose', 'win'
                self.clients[p2]['score'] += 1
        
        await self.send(p1, {'type': 'result', 'result': r1, 'your': c1, 'opp': c2,
                            'score': [self.clients[p1]['score'], self.clients[p2]['score']]})
        await self.send(p2, {'type': 'result', 'result': r2, 'your': c2, 'opp': c1,
                            'score': [self.clients[p2]['score'], self.clients[p1]['score']]})
        
        self.clients[p1]['choice'] = None
        self.clients[p2]['choice'] = None
    
    async def send(self, ws, msg):
        try:
            await ws.send(json.dumps(msg))
        except:
            pass

async def main():
    server = Server()
    print("="*50)
    print("  WEBSOCKET SERVER - GAME KÉO BÚA BAO")
    print("="*50)
    print("Server đang chạy tại: ws://localhost:8765")
    print("Để chơi với người khác trên cùng máy:")
    print("  1. Mở 2 tab trình duyệt")
    print("  2. Mở file index.html ở cả 2 tab")
    print("  3. Chọn 'Chơi Online' ở cả 2 tab")
    print("="*50)
    
    async with websockets.serve(server.handler, "localhost", 8765):
        await asyncio.Future()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nServer đã dừng!")