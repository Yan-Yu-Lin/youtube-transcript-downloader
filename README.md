# YouTube 字幕下載工具

一個簡單易用的工具，可以下載 YouTube 影片的字幕並自動複製到剪貼簿，方便貼到 ChatGPT、Claude 等 LLM 進行摘要。

## 功能特色

- 🎯 支援 YouTube 自動生成字幕和手動上傳字幕
- 🌐 多語言支援（預設英文）
- 📋 自動複製到剪貼簿
- 🧹 清理字幕格式，移除時間戳記和 HTML 標籤
- 💡 簡單的命令列介面
- 🔍 可查看影片支援的所有字幕語言

## 安裝

### 前置需求

- Python 3.8+
- [uv](https://github.com/astral-sh/uv) (Python 套件管理工具)

### 安裝步驟

1. 確保已安裝 uv：
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

2. 進入專案目錄：
```bash
cd 23.01-youtube-transcript-downloader
```

3. 安裝相依套件（uv 會自動建立虛擬環境）：
```bash
uv sync
```

## 使用方法

### 基本使用

1. 互動模式：
```bash
uv run python main.py
```
然後輸入 YouTube 網址

2. 命令列參數模式：
```bash
uv run python main.py "https://www.youtube.com/watch?v=VIDEO_ID"
```

3. 指定語言：
```bash
uv run python main.py "https://www.youtube.com/watch?v=VIDEO_ID" --lang zh-Hant
```

4. 查看可用語言：
```bash
uv run python main.py "https://www.youtube.com/watch?v=VIDEO_ID" --list-langs
```

### 使用範例

```bash
# 下載英文字幕（預設）
uv run python main.py "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

# 下載繁體中文字幕
uv run python main.py "https://www.youtube.com/watch?v=dQw4w9WgXcQ" --lang zh-Hant

# 下載日文字幕
uv run python main.py "https://youtu.be/dQw4w9WgXcQ" --lang ja

# 查看影片有哪些語言的字幕
uv run python main.py "https://www.youtube.com/watch?v=dQw4w9WgXcQ" --list-langs
```

### 命令列參數

- `url` - YouTube 影片網址（可選，如果不提供會進入互動模式）
- `-l`, `--lang`, `--language` - 指定字幕語言代碼
- `--list-langs`, `--list-languages` - 列出影片所有可用的字幕語言

## 工作流程

1. 輸入 YouTube 影片網址
2. 工具會自動：
   - 獲取影片資訊
   - 尋找可用的字幕（預設英文）
   - 下載並解析字幕
   - 清理格式（移除時間戳記、HTML 標籤等）
   - 複製到剪貼簿

3. 直接到 LLM 貼上（Ctrl+V / Cmd+V）即可！

## 支援的語言

預設語言優先順序（英文優先）：
1. 英文 (en)
2. 美式英文 (en-US)
3. 英式英文 (en-GB)
4. 繁體中文 (zh-Hant)
5. 簡體中文 (zh-Hans)
6. 中文 (zh)

你可以使用 `--lang` 參數指定任何 YouTube 支援的語言代碼。

常見語言代碼：
- `en` - 英文
- `zh-Hant` - 繁體中文
- `zh-Hans` - 簡體中文
- `ja` - 日文
- `ko` - 韓文
- `es` - 西班牙文
- `fr` - 法文
- `de` - 德文
- `pt` - 葡萄牙文
- `ru` - 俄文

## 常見問題

### Q: 為什麼有些影片無法下載字幕？
A: 某些影片可能：
- 沒有開啟自動生成字幕功能
- 是私人影片或有地區限制
- 是直播影片

### Q: 如何知道影片支援哪些語言？
A: 使用 `--list-langs` 參數可以查看所有可用的字幕語言。

### Q: 複製到剪貼簿失敗怎麼辦？
A: 如果自動複製失敗，字幕內容會顯示在終端機中，可以手動選取複製。

### Q: 支援哪些作業系統？
A: 支援 Windows、macOS 和 Linux。

## 技術細節

使用的主要套件：
- `yt-dlp`: YouTube 影片資訊和字幕下載
- `pyperclip`: 跨平台剪貼簿操作
- `requests`: HTTP 請求處理

## License

MIT License