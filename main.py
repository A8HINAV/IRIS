import os
import sys
import json
import asyncio
import threading
import time
import platform
import urllib.request
import urllib.error
import webview
import keyboard
import ctypes

def get_asset_path(relative_path: str) -> str:
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), relative_path)

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from core.parser import parse_natural_query
from core.scraper import scrape_topic

class IrisAPI:
    def __init__(self):
        self._window = None
        # App now starts VISIBLE on boot to show the welcome screen
        self.is_visible = True 
        self.last_toggle = 0

    def set_window(self, window):
        self._window = window

    def send_feedback(self, feedback_text: str):
        webhook_url = "https://discord.com/api/webhooks/1547956619525099641/HhEWakLim3_8GRdV5k0uSOwjJWwtk6ojO-LO19WjWBXXgVqQMHs-VAqWH8ubiJm1jXJH"
        os_info = f"{platform.system()} {platform.release()} ({platform.machine()})"
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')

        payload = {
            "username": "IRIS Telemetry",
            "embeds": [{
                "title": "Incoming HUD Feedback",
                "color": 65535,
                "fields": [
                    {"name": "Transmission", "value": feedback_text, "inline": False},
                    {"name": "System Info", "value": os_info, "inline": True},
                    {"name": "Timestamp", "value": timestamp, "inline": True}
                ],
                "footer": {"text": "IRIS Desktop HUD"}
            }]
        }

        try:
            req = urllib.request.Request(webhook_url, data=json.dumps(payload).encode('utf-8'), headers={'Content-Type': 'application/json', 'User-Agent': 'Mozilla/5.0'})
            urllib.request.urlopen(req, timeout=5.0)
            return "SUCCESS"
        except urllib.error.URLError:
            return "NO_INTERNET"
        except Exception:
            return "ERROR"

    def submit_query(self, user_query: str):
        threading.Thread(target=self._execute_query, args=(user_query,), daemon=True).start()

    def _execute_query(self, user_query: str):
        parsed = parse_natural_query(user_query)
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            payload = loop.run_until_complete(scrape_topic(parsed))
        except Exception as e:
            payload = {
                "entity": "System Error", "category": "FAULT",
                "show_maps": False, "full_text": f"Telemetry failure: {e}",
                "images": [], "map_macro": "", "map_micro": ""
            }
        finally:
            loop.close()

        if self._window:
            safe_payload = json.dumps(payload)
            self._window.evaluate_js(f"window.renderIrisData({safe_payload});")

    def hide_window(self):
        if self._window:
            self._window.hide()
            self.is_visible = False
            self._window.evaluate_js("try { window.resetUI(); } catch(e) {}")

    def toggle_visibility(self):
        if time.time() - self.last_toggle < 0.5:
            return 
        self.last_toggle = time.time()
        
        if self._window:
            if self.is_visible:
                self.hide_window()
            else:
                self._window.evaluate_js("try { window.resetUI(); } catch(e) {}")
                self._window.show()
                self._window.restore() 
                self.is_visible = True

def register_hotkey(api):
    # Simply binds the hotkey quietly in the background
    time.sleep(0.5) 
    try:
        keyboard.add_hotkey('ctrl+space', api.toggle_visibility)
    except Exception as e:
        print(f"[HotKey Warning] Run terminal as Administrator: {e}")

if __name__ == '__main__':
    # Center the window calculation natively
    user32 = ctypes.windll.user32
    screen_width = user32.GetSystemMetrics(0)
    screen_height = user32.GetSystemMetrics(1)
    
    center_x = int((screen_width - 1000) / 2)
    center_y = int((screen_height - 650) / 2)

    api = IrisAPI()
    
    window = webview.create_window(
        title='I.R.I.S.',
        url=get_asset_path('ui/index.html'),
        js_api=api,
        transparent=True,
        frameless=True,
        on_top=True,
        hidden=False, # Starts visible
        x=center_x,   # Spawns perfectly centered
        y=center_y,
        width=1000,  
        height=650   
    )
    api.set_window(window)

    threading.Thread(target=register_hotkey, args=(api,), daemon=True).start()
    webview.start(debug=False)