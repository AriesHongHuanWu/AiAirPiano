# 🎹 Virtual Piano PRO — Mediapipe × CustomTkinter

> 即時手勢鋼琴：使用 **Mediapipe Hands** 偵測手部動作，在畫面中即時顯示與發出多音（Polyphonic）鋼琴聲。  
> 支援五鍵音階 (C, D, E, F, G)，透過攝影機即可彈奏。

---

## 📘 專案簡介

此專案為互動式「虛擬鋼琴」應用，透過攝影機偵測使用者手部位置：  
當手指尖低於手腕時，即代表「按下琴鍵」，程式將同時：
- 高亮對應琴鍵（亮藍色）  
- 播放對應音符（C, D, E, F, G）  

整體介面為單一視窗，包含：
- 即時鏡頭畫面  
- 琴鍵按鈕區塊  
- FPS 狀態列  

---

## 🧩 系統架構

```
main.py
│
├── Mediapipe 偵測模組
│   ├── Hands (單手模式，移除臉部辨識)
│   └── drawing_utils：用於顯示關節骨架
│
├── 音訊系統
│   ├── 生成 C–G 音階正弦波（44100 Hz, 0.3s）
│   ├── simpleaudio 播放多音（Polyphonic）
│
├── CustomTkinter 介面
│   ├── 即時顯示攝影機畫面
│   ├── 琴鍵高亮 (白→藍)
│   ├── 顯示 FPS
│
└── 執行邏輯
    ├── 偵測每根手指 y 座標 vs 手腕
    ├── 若指尖低於手腕 → 琴鍵觸發
    └── 新按下的音符立即播放
```

---

## ⚙️ 安裝需求

| 套件名稱 | 功能 | 安裝指令 |
|-----------|------|-----------|
| `customtkinter` | GUI 介面 | `pip install customtkinter` |
| `mediapipe` | 手部偵測 | `pip install mediapipe` |
| `opencv-python` | 攝影機影像處理 | `pip install opencv-python` |
| `numpy` | 聲波生成 | `pip install numpy` |
| `pillow` | 顯示攝影機畫面 | `pip install pillow` |
| `simpleaudio` | 音訊播放 | `pip install simpleaudio` |

---

## 🧠 運作原理

| 功能 | 機制說明 |
|------|-----------|
| **手指偵測** | Mediapipe Hands 取 21 個關鍵點；比對 `finger_tip.y` 與 `wrist.y` |
| **琴鍵判定** | 當 `tip_y > wrist_y` 時 → 視為按下該鍵 |
| **即時畫面** | OpenCV + Pillow 將影像轉換成 Tkinter 可顯示格式 |
| **音訊輸出** | 以 NumPy 生成正弦波 PCM，simpleaudio 同時播放多音 |
| **介面刷新** | 每 15ms 更新畫面與琴鍵狀態，顯示 FPS |

---

## 🧮 鍵位與音高對應

| 鍵位 | 指尖關鍵點 ID | 音符 | 頻率 (Hz) |
|------|----------------|------|------------|
| 拇指 | 4 | C | 261.63 |
| 食指 | 8 | D | 293.66 |
| 中指 | 12 | E | 329.63 |
| 無名指 | 16 | F | 349.23 |
| 小指 | 20 | G | 392.00 |

---

## 🚀 執行方式

```bash
python main.py
```

啟動後將開啟視窗顯示鏡頭畫面與琴鍵。  
手掌出現在畫面中即可互動彈奏。  

---

## 💡 視覺介面

| 區域 | 說明 |
|------|------|
| 左側 | 攝影機畫面（鏡像翻轉） |
| 右側 | 五鍵琴盤（C–G） |
| 底部 | FPS 狀態列 |

琴鍵顏色變化：  
- 白色 → 未按下  
- 藍色 → 按下並發聲  

---

## 🔧 自訂參數

| 名稱 | 預設值 | 說明 |
|------|--------|------|
| `SAMPLE_RATE` | 44100 | 聲音取樣率 |
| `DURATION` | 0.3 | 單音長度 (秒) |
| `max_num_hands` | 1 | 同時偵測手數 |
| `min_detection_confidence` | 0.7 | 偵測信心閾值 |
| `min_tracking_confidence` | 0.5 | 追蹤信心閾值 |

---

## ⚠️ 注意事項

- 執行前請確保攝影機權限開啟。  
- 使用「手心朝向鏡頭」效果最佳。  
- 若音訊延遲，請關閉其他音效程式。  
- 不建議於低階 CPU 上執行（需即時影像 + 音訊生成）。  

---

## 🧱 專案結構

```
📂 VirtualPianoPRO
├── main.py
└── README.md
```

---

## 👨‍💻 作者

**Aries Wu**  
AI × Robotics × Music 技術創作者  
📧 arieswu001@gmail.com  
