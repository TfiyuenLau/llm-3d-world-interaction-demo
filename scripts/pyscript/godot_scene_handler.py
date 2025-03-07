import time
import win32gui
import pyautogui
import pythoncom
import pygetwindow as gw
from win32com import client


def get_target_window():
    """
    获取所有窗口
    """
    windows = gw.getAllTitles()
    print("当前打开的窗口列表：")
    for index, window in enumerate(windows):
        print(f"{index + 1}: {window}")

    target_index = int(input("请输入窗口编号：")) - 1
    if target_index < 0 or target_index >= len(windows):
        print("无效的窗口编号！")
        return None
    return gw.getWindowsWithTitle(windows[target_index])[0]


def take_screenshot(window, save_path, crop_size=(800, 800)):
    """
    对指定的窗口进行截图并保存
    :param window: 窗口对象
    :param save_path: 保存路径
    :param crop_size: 裁剪尺寸，默认为640x640
    """
    # 查找窗口句柄并切换
    godot_wnd = win32gui.FindWindow(None, window.title)
    if not godot_wnd:
        raise Exception(f"Could not find a window with title '{window.title}'")

    # 修复BUG，详见https://blog.csdn.net/Katherine1029/article/details/125640361
    pythoncom.CoInitialize()
    shell = client.Dispatch("WScript.Shell")
    shell.SendKeys('%')
    win32gui.SetForegroundWindow(godot_wnd)

    # 获取窗口位置和尺寸
    left = window.left
    top = window.top
    width = window.width
    height = window.height

    # 裁剪截图，计算裁剪区域的左上角坐标，使得裁剪中心位于截图的中心
    time.sleep(0.5)
    img = pyautogui.screenshot(region=(left, top, width, height))
    center_x = width // 2
    center_y = height // 2
    left_crop = max(center_x - crop_size[0] // 2, 0)
    top_crop = max(center_y - crop_size[1] // 2, 0)
    right_crop = min(left_crop + crop_size[0], width)
    bottom_crop = min(top_crop + crop_size[1], height)
    cropped_img = img.crop((left_crop, top_crop, right_crop, bottom_crop))

    # 保存
    cropped_img.save(save_path)
    print("Screenshot saved.")


if __name__ == "__main__":
    window = get_target_window()
    if window:
        image_name = "SCENE_" + str(int(time.time())) + ".png"
        save_path = "image/scene/" + image_name
        take_screenshot(window, save_path)
