import cv2
import numpy as np
import pyautogui
import time
import keyboard
import tkinter as tk

def select_region():
    """Allows the user to select a region of the screen with a simple graphical interface."""
    print("Click and drag to select the red buoy region.")
    root = tk.Tk()
    root.withdraw()  # Hides the main window

    # Capture the entire screen
    screenshot = pyautogui.screenshot()
    screenshot = np.array(screenshot)
    screenshot = cv2.cvtColor(screenshot, cv2.COLOR_RGB2BGR)

    # Show the image for the user to select the region
    cv2.imshow('Select Region', screenshot)
    bbox = cv2.selectROI('Select Region', screenshot, fromCenter=False, showCrosshair=True)
    cv2.destroyAllWindows()
    
    x, y, w, h = bbox
    return (int(x), int(y), int(w), int(h))

def capture_screen(region):
    """Captures a part of the screen defined by the region."""
    screen = pyautogui.screenshot(region=region)
    screen = np.array(screen)
    return cv2.cvtColor(screen, cv2.COLOR_RGB2BGR)

def detect_red_region(image, reference_image, threshold=0.2):
    """Detects if the red color in the region has disappeared."""
    image_hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    reference_hsv = cv2.cvtColor(reference_image, cv2.COLOR_BGR2HSV)

    lower_red1 = np.array([0, 100, 100])
    upper_red1 = np.array([10, 255, 255])
    lower_red2 = np.array([160, 100, 100])
    upper_red2 = np.array([180, 255, 255])

    mask1 = cv2.inRange(image_hsv, lower_red1, upper_red1)
    mask2 = cv2.inRange(image_hsv, lower_red2, upper_red2)
    mask = mask1 | mask2

    reference_mask = cv2.inRange(reference_hsv, lower_red1, upper_red1) | cv2.inRange(reference_hsv, lower_red2, upper_red2)
    
    detected_area = np.sum(mask > 0)
    reference_area = np.sum(reference_mask > 0)

    return detected_area < reference_area * threshold

def double_click():
    """Simulates two mouse clicks at the current pointer position using pyautogui."""
    x, y = pyautogui.position()
    pyautogui.click(x=x, y=y, clicks=2, interval=0.1)

def main():
    print("Open the virtual keyboard and position the cursor over the Control key. Then run the script.")
    
    # Capture the red buoy region
    print("Select the red buoy area.")
    buoy_region = select_region()
    buoy_x, buoy_y, buoy_w, buoy_h = buoy_region

    # Capture the red buoy image for reference
    reference_image = capture_screen(buoy_region)

    print("Waiting for the red buoy to disappear...")

    last_click_time = 0
    delay_after_click = 6  # Wait time in seconds after clicking

    while True:
        screen_image = capture_screen(buoy_region)
        if detect_red_region(screen_image, reference_image):
            current_time = time.time()
            if current_time - last_click_time > delay_after_click or last_click_time == 0:
                print("The red buoy disappeared. Performing double-click at the current pointer position...")
                double_click()
                last_click_time = current_time
        else:
            print("The red buoy is still visible.")
        
        time.sleep(0.1)  # Reduce wait time to increase the frequency of checks

        # Check if the user pressed the F key to stop the script
        if keyboard.is_pressed('f'):
            print("Script stopped by the user.")
            break

if __name__ == "__main__":
    main()
