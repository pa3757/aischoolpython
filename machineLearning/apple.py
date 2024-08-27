import pyautogui
import time
import math
import os

class apple:
    def __init__(self, num, x, y, wid, hei):
        self.num = num
        self.x = x
        self.y = y
        self.endx = x + wid
        self.endy = y + hei

    def cut(self):
        self.num = 0

applelist = []

def is_ten(appletable, sx, sy, ex, ey):  # 해당구역 합 10 확인함수
    result = 0
    for a in range(ey - sy + 1):
        for b in range(ex - sx + 1):
            result = result + appletable[sx + b][sy + a].num
    return result == 10

def print_table(appletable):  # 사과테이블 출력함수
    print()
    for b in range(10):
        for c in range(17):
            if appletable[c][b].num == 0:  # 사과가 0점이라면 지워진걸로 간주
                print(' ', end=' ')
            else:
                print(appletable[c][b].num, end=' ')
        print()

def drag(appletable, sx, sy, ex, ey):  # 드래그함수
    pyautogui.moveTo(appletable[sx][sy].x, appletable[sx][sy].y)
    pyautogui.dragTo(appletable[ex][ey].endx + 20, appletable[ex][ey].endy + 20, math.sqrt(((ex - sx) ** 2) + ((ey - sy) ** 2)) * 0.5, button='left')  # 드래그씹힘 방지로 x y 각각 20씩 더 움직임

def rm_apple(appletable, sx, sy, w, h):
    for b in range(h + 1):  # 테이블에서 해당부분 0점처리
        for c in range(w + 1):
            appletable[sx + c][sy + b].cut()
    return appletable

def check_file_exists(file_path):
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    if not os.access(file_path, os.R_OK):
        raise PermissionError(f"File cannot be read: {file_path}")

a = 0
for b in range(9):  # 화면에서 숫자사진 찾기
    file_path = f"{b + 1}.png"
    check_file_exists(file_path)
    pos = pyautogui.locateAllOnScreen(file_path, confidence=0.5)  # 일치도 조정
    for i in pos:
        applelist.append(0)
        applelist[a] = apple(b + 1, i.left, i.top, i.width, i.height)
        a = a + 1

for b in range(len(applelist)):  # 사과목록 출력
    print("(" + str(applelist[b].x) + ", " + str(applelist[b].y) + ")")
print(len(applelist))

for d in range(10):  # 사과 중복제거 #확실하게 중복을 제거하기 위해 여러번 돌림
    end = 0
    for b in range(170):
        for c in range(170):  # 중복검사할 최대개수:170
            if b + 1 == len(applelist):
                end = 1
                break
            if b + c + 1 >= len(applelist):
                break
            if abs(applelist[b].x - applelist[b + c + 1].x) < 10 and abs(applelist[b].y - applelist[b + c + 1].y) < 10:  # 다음원소와 x,y 차이가 7 미만이라면 중복이라 간주
                del applelist[b + c + 1]
                c = c - 1
        if end == 1:
            break

for b in range(len(applelist)):  # 중복제거 후 사과목록 출력
    print("(" + str(applelist[b].x) + ", " + str(applelist[b].y) + ")")
print(len(applelist))

applelist2 = []  # y좌표 기준으로 정렬
for b in range(170):
    least = 0
    for c in range(170):
        if c == len(applelist):
            break
        if applelist[c].y < applelist[least].y:
            least = c
    applelist2.append(applelist[least])
    del applelist[least]

applelist3 = []  # 열마다 x좌표 기준으로 정렬
for b in range(10):
    for c in range(17):
        least = 0
        for d in range(17 - c):
            if d >= len(applelist2):
                break
            if applelist2[d].x < applelist2[least].x:
                least = d
        applelist3.append(applelist2[least])
        del applelist2[least]

for b in range(len(applelist3)):  # 정렬 후 사과목록 출력
    print("(" + str(applelist3[b].x) + ", " + str(applelist3[b].y) + ")")
print(len(applelist3))

appletable = [[0 for col in range(10)] for row in range(17)]  # 사과 2차원배열 생성
for b in range(10):  # 2차원배열에 사과 정리
    for c in range(17):
        appletable[c][b] = applelist3[b * 17 + c]

print_table(appletable)  # 초기 사과테이블 출력

for d in range(20):  # 한번해서 안나오면 여러번한다, 20번
    for sy in range(10):  # 무차별 대입
        for sx in range(17):
            for h in range(10 - sy):
                for w in range(17 - sx):
                    if is_ten(appletable, sx, sy, sx + w, sy + h):  # 모두 합해 10이라면
                        appletable = rm_apple(appletable, sx, sy, w, h)
                        print("--------------------------------------------------")
                        print("find 10: (" + str(sx) + ", " + str(sy) + ") -> (" + str(sx + w) + ", " + str(sy + h) + ")")
                        print_table(appletable)
                        drag(appletable, sx, sy, sx + w, sy + h)