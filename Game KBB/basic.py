
from random import randint

diem_nguoi = 0
diem_may = 0

print("=== GAME KÉO BÚA BAO ===")

while diem_nguoi < 2 and diem_may < 2:
    print(f"\nĐiểm hiện tại: Bạn {diem_nguoi} - Máy {diem_may}")

# Người chơi chọn
    nguoi = int(input('Chọn của bạn (1: Kéo, 2: Búa, 3: Bao): '))

    may = randint(1, 3)

    print(f"Bạn chọn: {nguoi} | Máy chọn: {may}")

    if may == 1:
        print('Máy chọn Kéo')
    elif may == 2:
        print('Máy chọn Búa')
    elif may == 3:
        print('Máy chọn Bao')

    if nguoi == may:
        print('--------- HÒA ---------')
    elif (nguoi - may) % 3 == 1:   
        diem_nguoi += 1
        print('--------- BẠN THẮNG ván này ---------')
    else:
        diem_may += 1
        print('--------- MÁY THẮNG ván này ---------')

# Khi thoát vòng lặp → đã có người thắng 2 ván
print("\n================ GAME KẾT THÚC ================")
print(f"Tổng điểm cuối: Bạn {diem_nguoi} - Máy {diem_may}")

if diem_nguoi == 2:
    print("🎉 CHÚC MỪNG! BẠN THẮNG CUỘC!")
else:
    print("😢 Máy thắng cuộc...")