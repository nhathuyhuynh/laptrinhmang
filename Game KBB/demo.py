import tkinter as tk
from tkinter import messagebox
import random

class RPSGame:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Kéo Búa Bao - Best of 3")
        self.root.geometry("800x650")          
        self.root.resizable(False, False)
        self.root.configure(bg="#E3F2FD")
        
        self.p1_score = 0
        self.ai_score = 0
        self.choices = {'p1': None, 'ai': None}
        
        self.setup_menu()
        
    def setup_menu(self):
        self.clear_frame()
        title = tk.Label(self.root, text="KÉO - BÚA - BAO", font=("Arial", 38, "bold"), 
                         bg="#E3F2FD", fg="#1976D2")
        title.pack(pady=140)
        
        subtitle = tk.Label(self.root, text="Best of 3 - Chơi với AI", font=("Arial", 20), 
                            bg="#E3F2FD", fg="#424242")
        subtitle.pack(pady=20)
        
        btn_start = tk.Button(self.root, text="BẮT ĐẦU CHƠI", font=("Arial", 22, "bold"), 
                              command=self.start_game, bg="#4CAF50", fg="white", 
                              height=2, width=25, relief="raised", bd=6)
        btn_start.pack(pady=80)
        
    def clear_frame(self):
        for widget in self.root.winfo_children():
            widget.destroy()
            
    def start_game(self):
        self.p1_score = 0
        self.ai_score = 0
        self.show_game_screen()
        
    def show_game_screen(self):
        self.clear_frame()
        
        title = tk.Label(self.root, text="KÉO - BÚA - BAO", font=("TimeNewsRoman", 34, "bold"), 
                         bg="#E3F2FD", fg="#1976D2")
        title.grid(row=0, column=0, columnspan=3, pady=(40, 10))
        
        self.score_label = tk.Label(self.root, text=f"Bạn: {self.p1_score}   |   AI: {self.ai_score}", 
                                    font=("Arial", 24, "bold"), bg="#E3F2FD", fg="#333")
        self.score_label.grid(row=1, column=0, columnspan=3, pady=25)
        
        self.instruct_label = tk.Label(self.root, text="Chọn của bạn:", font=("Arial", 24, "bold"), 
                                       bg="#E3F2FD", fg="#424242")
        self.instruct_label.grid(row=2, column=0, columnspan=3, pady=30)
        
        btn_frame = tk.Frame(self.root, bg="#E3F2FD")
        btn_frame.grid(row=3, column=0, columnspan=3, pady=40, padx=60)
        
        button_style = {
            "font": ("TimeNewsRoman", 24, "bold"),
            "width": 10,          # Giảm width để vừa hơn
            "height": 2,
            "relief": "raised",
            "bd": 6
        }
        
        self.btn_keo = tk.Button(btn_frame, text="KÉO", bg="#EF1D1D", fg="black", 
                                 command=lambda: self.make_choice('keo'), **button_style)
        self.btn_keo.grid(row=0, column=0, padx=10)
        
        self.btn_bua = tk.Button(btn_frame, text="BÚA", bg="#FFE711", fg="black", 
                                 command=lambda: self.make_choice('bua'), **button_style)
        self.btn_bua.grid(row=0, column=1, padx=15)
        
        self.btn_bao = tk.Button(btn_frame, text="BAO", bg="#53FF19", fg="black", 
                                 command=lambda: self.make_choice('bao'), **button_style)
        self.btn_bao.grid(row=0, column=2, padx=15)
        
        self.result_label = tk.Label(self.root, text="", font=("Arial", 24, "bold"), bg="#E3F2FD")
        self.result_label.grid(row=4, column=0, columnspan=3, pady=50)
        
        back_btn = tk.Button(self.root, text="Menu chính", font=("Arial", 14), 
                             command=self.setup_menu, bg="#F44336", fg="white", width=15)
        back_btn.grid(row=5, column=0, columnspan=3, pady=30)
        
        self.next_round()
        
    def make_choice(self, choice):
        if self.choices['p1'] is not None:
            return
        
        self.choices['p1'] = choice
        self.choices['ai'] = random.choice(['keo', 'bua', 'bao'])
        
        self.instruct_label.config(text="AI đang chọn...", fg="blue")
        self.root.update()
        
        self.show_round_result()
        
    def show_round_result(self):
        p1 = self.choices['p1'].upper()
        ai = self.choices['ai'].upper()
        
        if self.choices['p1'] == self.choices['ai']:
            result = "HÒA!"
            color = "orange"
        elif (self.choices['p1'] == 'keo' and self.choices['ai'] == 'bao') or \
             (self.choices['p1'] == 'bua' and self.choices['ai'] == 'keo') or \
             (self.choices['p1'] == 'bao' and self.choices['ai'] == 'bua'):
            result = "BẠN THẮNG VÁN!"
            self.p1_score += 1
            color = "green"
        else:
            result = "AI THẮNG VÁN!"
            self.ai_score += 1
            color = "red"
            
        self.result_label.config(text=f"{p1}  VS  {ai}\n{result}", fg=color)
        self.score_label.config(text=f"Bạn: {self.p1_score}   |   AI: {self.ai_score}")
        
        self.btn_keo.config(state=tk.DISABLED)
        self.btn_bua.config(state=tk.DISABLED)
        self.btn_bao.config(state=tk.DISABLED)
        
        self.check_game_end()
        
        if self.p1_score < 2 and self.ai_score < 2:
            self.root.after(1800, self.next_round)
            
    def check_game_end(self):
        if self.p1_score >= 2 or self.ai_score >= 2:
            if self.p1_score >= 2:
                msg = "CHÚC MỪNG! BẠN THẮNG CUỘC!"
            else:
                msg = "AI THẮNG CUỘC! Thử lại nhé!"
            messagebox.showinfo("KẾT THÚC", 
                                f"{msg}\n\nTổng điểm: Bạn {self.p1_score} - AI {self.ai_score}")
            self.setup_menu()
            
    def next_round(self):
        self.choices = {'p1': None, 'ai': None}
        self.result_label.config(text="")
        self.btn_keo.config(state=tk.NORMAL)
        self.btn_bua.config(state=tk.NORMAL)
        self.btn_bao.config(state=tk.NORMAL)
        self.instruct_label.config(text="Chọn của bạn:", fg="black")
        
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    game = RPSGame()
    game.run()