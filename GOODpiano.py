"""virtual_piano_full.py
────────────────────────────────────────────────────────────────
Virtual Piano PRO — Mediapipe × CustomTkinter
(Hand-Only Detection + Polyphonic Audio)
────────────────────────────────────────────────────────────────
• 即時鏡頭畫面 + 霧白琴鍵 GUI 同窗呈現。
• 手指尖低於手腕 ⇒ 琴鍵 (C‧D‧E‧F‧G) 亮藍並發出多音音符。
• 僅使用 Mediapipe Hands 模組，移除臉部偵測。
依賴：
    pip install customtkinter mediapipe opencv-python numpy pillow simpleaudio
────────────────────────────────────────────────────────────────
"""

from __future__ import annotations
import cv2
import mediapipe as mp
import customtkinter as ctk
from PIL import Image, ImageTk
import threading
import numpy as np
import simpleaudio as sa
import time
import sys

# Mediapipe Hands 初始化
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.5,
)

drawing_utils = mp.solutions.drawing_utils

# 音頻參數
SAMPLE_RATE = 44100
DURATION = 0.3  # seconds
NOTE_FREQS = {"C": 261.63, "D": 293.66, "E": 329.63, "F": 349.23, "G": 392.00}
# 產生 PCM 資料並建立 WaveObject
AUDIO_OBJ: dict[str, sa.WaveObject] = {}
for note, freq in NOTE_FREQS.items():
    t = np.linspace(0, DURATION, int(SAMPLE_RATE * DURATION), False)
    wave = 0.5 * np.sin(freq * t * 2 * np.pi)
    pcm = np.int16(wave * 32767)
    AUDIO_OBJ[note] = sa.WaveObject(pcm.tobytes(), 1, 2, SAMPLE_RATE)

# 手指關鍵點對應 (5 根手指)
FINGER_TIPS = [4, 8, 12, 16, 20]           # Thumb, Index, Middle, Ring, Pinky
FINGER_LABELS = ["C", "D", "E", "F", "G"]
WRIST_ID = 0

class PianoApp(ctk.CTk):
    CAM_W, CAM_H = 640, 480  # 相機解析度

    def __init__(self) -> None:
        super().__init__()
        self.title("🎹 Virtual Piano PRO")
        self.geometry("960x640")
        self.resizable(False, False)
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")

        # 共享狀態
        self.pressed: list[str] = []
        self.current_frame: np.ndarray | None = None
        self._fps = 0.0
        self._last_pressed: set[str] = set()

        # 建立 UI
        self._build_ui()

        # 啟動偵測執行緒
        self._run_flag = True
        threading.Thread(target=self._detector_loop, daemon=True).start()
        self.after(15, self._refresh_ui)
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _build_ui(self) -> None:
        # 標題文字
        ctk.CTkLabel(self, text="Virtual Piano PRO", font=("SF Pro", 28, "bold")).pack(pady=(10, 0))

        # 主體分區
        body = ctk.CTkFrame(self, fg_color="transparent")
        body.pack(expand=True, fill="both", padx=20, pady=10)
        body.grid_columnconfigure(0, weight=3)
        body.grid_columnconfigure(1, weight=2)

        # 左側：攝影機預覽
        self.video_label = ctk.CTkLabel(body, text="Initializing camera…")
        self.video_label.grid(row=0, column=0, sticky="nsew", padx=(0, 20))

        # 右側：琴鍵面板
        keys_frame = ctk.CTkFrame(body, corner_radius=12)
        keys_frame.grid(row=0, column=1, sticky="nsew")
        keys_frame.grid_columnconfigure(tuple(range(5)), weight=1)

        self.key_buttons: dict[str, ctk.CTkButton] = {}
        for i, lbl in enumerate(FINGER_LABELS):
            btn = ctk.CTkButton(
                keys_frame,
                text=lbl,
                width=80,
                height=240,
                corner_radius=8,
                fg_color="#ffffff",
                hover_color="#e5e7eb",
                text_color="#000000",
                font=("Helvetica", 24, "bold"),
                state="disabled"
            )
            btn.grid(row=0, column=i, padx=6, pady=10, sticky="ns")
            self.key_buttons[lbl] = btn

        # 底部：FPS 顯示
        self.status = ctk.CTkLabel(self, text="FPS: 0", font=("Menlo", 12))
        self.status.pack(pady=(0, 6))

    def _detector_loop(self) -> None:
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            self.video_label.configure(text="❌ Camera not found")
            return
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.CAM_W)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.CAM_H)

        prev_t = time.time()
        while self._run_flag:
            ret, frame = cap.read()
            if not ret:
                continue

            # 鏡像翻轉與色彩
            frame = cv2.flip(frame, 1)
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # 手部偵測
            results = hands.process(rgb)
            pressed: list[str] = []
            if results.multi_hand_landmarks:
                lm = results.multi_hand_landmarks[0].landmark
                wrist_y = lm[WRIST_ID].y
                for idx, tip in enumerate(FINGER_TIPS):
                    if lm[tip].y > wrist_y:
                        pressed.append(FINGER_LABELS[idx])
                # 畫手部骨架 (選用)
                drawing_utils.draw_landmarks(frame, results.multi_hand_landmarks[0], mp_hands.HAND_CONNECTIONS)

            # 播放新按鍵音（Polyphony）
            new_keys = set(pressed) - self._last_pressed
            for key in new_keys:
                AUDIO_OBJ[key].play()
            self._last_pressed = set(pressed)

            # 更新狀態
            self.pressed = pressed
            self.current_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            curr_t = time.time()
            self._fps = 1 / (curr_t - prev_t + 1e-5)
            prev_t = curr_t

        cap.release()

    def _refresh_ui(self) -> None:
        if self.current_frame is not None:
            img = Image.fromarray(self.current_frame)
            img = img.resize((self.CAM_W * 3 // 2, self.CAM_H * 3 // 2), Image.BILINEAR)
            imgtk = ImageTk.PhotoImage(img)
            self.video_label.configure(image=imgtk, text="")
            self.video_label.image = imgtk

        for lbl, btn in self.key_buttons.items():
            btn.configure(fg_color="#60a5fa" if lbl in self.pressed else "#ffffff")

        self.status.configure(text=f"FPS: {self._fps:.1f}")
        if self._run_flag:
            self.after(15, self._refresh_ui)

    def _on_close(self) -> None:
        self._run_flag = False
        self.after(200, self.destroy)

if __name__ == "__main__":
    try:
        PianoApp().mainloop()
    except KeyboardInterrupt:
        sys.exit(0)
