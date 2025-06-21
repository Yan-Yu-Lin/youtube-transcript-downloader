#!/usr/bin/env python3
"""
YouTube 字幕下載工具
自動下載 YouTube 影片的字幕並複製到剪貼簿
"""

import yt_dlp
import pyperclip
import requests
import re
import sys
import json
import argparse
from typing import Optional, Dict, List


class YouTubeTranscriptDownloader:
    def __init__(self):
        self.ydl_opts = {
            'writeautomaticsub': True,
            'skip_download': True,
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
        }
    
    def extract_video_id(self, url: str) -> Optional[str]:
        """從 YouTube URL 提取影片 ID"""
        patterns = [
            r'(?:v=|\/)([0-9A-Za-z_-]{11}).*',
            r'(?:embed\/)([0-9A-Za-z_-]{11})',
            r'(?:youtu\.be\/)([0-9A-Za-z_-]{11})'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None
    
    def get_transcript(self, video_url: str, preferred_lang: Optional[str] = None, list_langs: bool = False) -> str:
        """取得字幕文字"""
        print(f"正在處理影片: {video_url}")
        
        with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
            try:
                # 提取影片資訊
                print("正在獲取影片資訊...")
                info = ydl.extract_info(video_url, download=False)
                
                # 取得影片標題
                title = info.get('title', 'Unknown')
                print(f"影片標題: {title}")
                
                # 檢查自動字幕
                auto_captions = info.get('automatic_captions', {})
                
                if not auto_captions:
                    # 檢查手動字幕
                    subtitles = info.get('subtitles', {})
                    if subtitles:
                        auto_captions = subtitles
                        print("找到手動上傳的字幕")
                    else:
                        return "錯誤：此影片沒有可用的字幕"
                
                # 如果要列出語言
                if list_langs:
                    available_langs = list(auto_captions.keys())
                    lang_list = "\n".join([f"  - {lang}" for lang in available_langs])
                    return f"可用的字幕語言:\n{lang_list}"
                
                # 決定要使用的語言
                selected_lang = None
                
                if preferred_lang:
                    # 使用者指定的語言
                    if preferred_lang in auto_captions:
                        selected_lang = preferred_lang
                    else:
                        # 嘗試部分匹配
                        for lang in auto_captions:
                            if preferred_lang.lower() in lang.lower() or lang.lower() in preferred_lang.lower():
                                selected_lang = lang
                                break
                        
                        if not selected_lang:
                            available_langs = list(auto_captions.keys())
                            return f"錯誤：找不到語言 '{preferred_lang}'。\n可用的語言: {', '.join(available_langs)}"
                else:
                    # 預設語言優先順序 (英文優先)
                    languages = ['en', 'en-US', 'en-GB', 'zh-Hant', 'zh-Hans', 'zh']
                    
                    # 尋找可用語言
                    for lang in languages:
                        if lang in auto_captions:
                            selected_lang = lang
                            break
                    
                    # 如果沒有找到優先語言，使用第一個可用語言
                    if not selected_lang and auto_captions:
                        selected_lang = list(auto_captions.keys())[0]
                
                if not selected_lang:
                    return "錯誤：找不到任何語言的字幕"
                
                print(f"使用語言: {selected_lang}")
                
                # 取得字幕 URL (優先取得 vtt 格式)
                caption_url = None
                caption_format = None
                
                # 優先嘗試取得 vtt 格式
                for caption in auto_captions[selected_lang]:
                    if caption.get('ext') == 'vtt':
                        caption_url = caption['url']
                        caption_format = 'vtt'
                        break
                
                # 如果沒有 vtt，嘗試其他格式
                if not caption_url:
                    for caption in auto_captions[selected_lang]:
                        ext = caption.get('ext')
                        if ext in ['srv1', 'srv2', 'srv3', 'json3']:
                            caption_url = caption['url']
                            caption_format = ext
                            break
                
                if not caption_url:
                    return "錯誤：無法取得字幕 URL"
                
                # 下載字幕
                print(f"正在下載字幕... (格式: {caption_format})")
                response = requests.get(caption_url)
                response.raise_for_status()
                
                # 根據格式解析字幕
                if caption_format == 'json3':
                    return self.parse_json3_subtitle(response.text, title)
                else:
                    return self.parse_subtitle(response.text, title)
                
            except yt_dlp.utils.DownloadError as e:
                return f"下載錯誤：{str(e)}"
            except Exception as e:
                return f"發生錯誤：{str(e)}"
    
    def parse_subtitle(self, subtitle_text: str, video_title: str) -> str:
        """解析字幕，提取純文字"""
        # 檢查是否為 M3U8 播放列表
        if subtitle_text.startswith('#EXTM3U'):
            # 嘗試從 M3U8 中提取實際的字幕 URL 並下載
            urls = re.findall(r'https://[^\s]+', subtitle_text)
            if urls:
                try:
                    # 下載第一個 URL 的內容
                    response = requests.get(urls[0])
                    response.raise_for_status()
                    subtitle_text = response.text
                except:
                    pass
        
        lines = subtitle_text.split('\n')
        transcript = []
        
        # 加入影片標題
        transcript.append(f"=== {video_title} ===\n")
        
        # 檢查是否為 VTT 格式
        is_vtt = 'WEBVTT' in subtitle_text
        
        for i, line in enumerate(lines):
            # 跳過 VTT 標頭
            if line.startswith('WEBVTT'):
                continue
            
            # 跳過時間戳記
            if '-->' in line:
                continue
            
            # 跳過空行和時間索引
            if not line.strip() or line.strip().isdigit():
                continue
            
            # 移除 HTML 標籤
            clean_line = re.sub('<[^>]+>', '', line)
            # 移除特殊字符
            clean_line = clean_line.replace('&nbsp;', ' ')
            clean_line = clean_line.replace('&amp;', '&')
            clean_line = clean_line.replace('&lt;', '<')
            clean_line = clean_line.replace('&gt;', '>')
            clean_line = clean_line.replace('&quot;', '"')
            
            if clean_line.strip():
                transcript.append(clean_line.strip())
        
        # 合併重複的句子（有時字幕會重複）
        final_transcript = []
        prev_line = None
        for line in transcript:
            if line != prev_line:
                final_transcript.append(line)
                prev_line = line
        
        if len(final_transcript) <= 1:  # 只有標題
            return f"{final_transcript[0]}\n\n無法解析字幕內容，可能是格式問題或影片太短。"
        
        return '\n'.join(final_transcript)
    
    def parse_json3_subtitle(self, json_text: str, video_title: str) -> str:
        """解析 JSON3 格式的字幕"""
        try:
            data = json.loads(json_text)
            transcript = [f"=== {video_title} ===\n"]
            
            # JSON3 格式包含事件列表
            if 'events' in data:
                for event in data['events']:
                    # 跳過非文字事件
                    if 'segs' not in event:
                        continue
                    
                    # 組合片段
                    text_parts = []
                    for seg in event.get('segs', []):
                        if 'utf8' in seg:
                            text_parts.append(seg['utf8'])
                    
                    if text_parts:
                        line = ''.join(text_parts).strip()
                        if line:
                            transcript.append(line)
            
            # 移除重複
            final_transcript = []
            prev_line = None
            for line in transcript:
                if line != prev_line:
                    final_transcript.append(line)
                    prev_line = line
            
            return '\n'.join(final_transcript)
            
        except json.JSONDecodeError:
            # 如果不是 JSON，嘗試作為普通文字處理
            return self.parse_subtitle(json_text, video_title)
    
    def copy_to_clipboard(self, text: str):
        """複製到剪貼簿"""
        try:
            pyperclip.copy(text)
            print("\n✅ 字幕已複製到剪貼簿！")
            print("您現在可以貼到 ChatGPT、Claude 或其他 LLM 進行摘要。")
        except Exception as e:
            print(f"\n⚠️  無法複製到剪貼簿：{str(e)}")
            print("請手動複製上方的字幕內容。")


def main() -> int:
    # 設定命令列參數
    parser = argparse.ArgumentParser(
        description='YouTube 字幕下載工具 - 自動下載 YouTube 影片字幕並複製到剪貼簿',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
範例:
  %(prog)s "https://www.youtube.com/watch?v=VIDEO_ID"
  %(prog)s "https://youtu.be/VIDEO_ID" --lang zh-Hant
  %(prog)s "https://www.youtube.com/watch?v=VIDEO_ID" --list-langs
        """
    )
    
    parser.add_argument('url', nargs='?', help='YouTube 影片網址')
    parser.add_argument('-l', '--lang', '--language', 
                        help='指定字幕語言 (例如: en, zh-Hant, zh-Hans, ja, ko)')
    parser.add_argument('--list-langs', '--list-languages', 
                        action='store_true',
                        help='列出影片可用的字幕語言')
    
    args = parser.parse_args()
    
    print("YouTube 字幕下載工具")
    print("=" * 50)
    
    # 取得 YouTube URL
    if args.url:
        url = args.url
    else:
        url = input("請輸入 YouTube 網址: ").strip()
    
    if not url:
        print("錯誤：請提供有效的 YouTube 網址")
        return 1
    
    # 建立下載器
    downloader = YouTubeTranscriptDownloader()
    
    # 驗證 URL
    video_id = downloader.extract_video_id(url)
    if not video_id:
        print("錯誤：無效的 YouTube 網址")
        return 1
    
    # 取得字幕
    transcript = downloader.get_transcript(url, preferred_lang=args.lang, list_langs=args.list_langs)
    
    # 如果是列出語言，直接顯示並結束
    if args.list_langs:
        print("\n" + transcript)
        return 0
    
    # 顯示結果
    print("\n" + "=" * 50)
    print("字幕內容：")
    print("=" * 50)
    
    # 如果字幕太長，只顯示前面部分
    if len(transcript) > 1000 and not transcript.startswith("錯誤"):
        print(transcript[:1000] + "\n...\n[字幕內容太長，已截斷顯示]")
        print(f"\n完整字幕長度：{len(transcript)} 字")
    else:
        print(transcript)
    
    # 複製到剪貼簿
    if not transcript.startswith("錯誤") and not transcript.startswith("下載錯誤") and not transcript.startswith("可用的字幕語言"):
        downloader.copy_to_clipboard(transcript)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())