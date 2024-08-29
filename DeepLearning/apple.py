import os
import cv2
import pyautogui
import numpy as np
import time
import keyboard

# 숫자 이미지 파일의 경로
image_folder = 'data'


# 파일 경로가 올바른지 확인하는 함수
def check_file_exists(file_path):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")


# 숫자 이미지를 미리 로드하여 딕셔너리에 저장
def load_number_images():
    number_images = {}
    for i in range(1, 10):  # 1부터 9까지
        image_path = os.path.join(image_folder, f'{i}.png')
        check_file_exists(image_path)  # 파일 존재 여부 확인
        number_images[i] = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    return number_images


# 스크린샷 찍기 및 OpenCV 형식으로 변환
def screenshot_and_process():
    screenshot = pyautogui.screenshot()
    screenshot = np.array(screenshot)
    screenshot = cv2.cvtColor(screenshot, cv2.COLOR_RGB2BGR)
    return screenshot


# 숫자 이미지와 화면을 비교하여 숫자 위치를 찾기
def find_number_positions(screenshot, number_images):
    positions = []
    for number, template in number_images.items():
        result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
        threshold = 0.8  # 매칭 정확도 임계값 설정
        loc = np.where(result >= threshold)
        for pt in zip(*loc[::-1]):
            positions.append((number, pt))
    return positions


# 합이 10이 되는 조합을 찾기
def find_combinations(positions):
    combinations = []
    for i in range(len(positions)):
        for j in range(i + 1, len(positions)):
            if positions[i][0] + positions[j][0] == 10:
                combinations.append((positions[i][1], positions[j][1]))
    return combinations


# 지정된 위치 클릭
def click_on_positions(combinations):
    for (pos1, pos2) in combinations:
        pyautogui.click(pos1[0], pos1[1])
        pyautogui.click(pos2[0], pos2[1])


# 메인 루프
def main():
    number_images = load_number_images()

    print("매크로 실행 중... ESC 키를 누르면 종료됩니다.")

    while True:
        if keyboard.is_pressed('esc'):
            print("매크로가 종료되었습니다.")
            break

        screenshot = screenshot_and_process()
        positions = find_number_positions(screenshot, number_images)
        combinations = find_combinations(positions)
        click_on_positions(combinations)

        time.sleep(1)  # 1초 대기 후 반복


if __name__ == "__main__":
    main()
