import os
import requests
from playwright.sync_api import sync_playwright

BOT_TOKEN = "8292550162:AAGBLB4bX3xHnAaw9ftrpI2ZLvH5f1sTa08"
CHAT_ID = "1083698448"
TARGET_URL = "https://visa.vfsglobal.com/dza/en/nld/login"

def send_telegram_msg(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"}
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print(f"Error sending msg: {e}")

def send_telegram_photo(photo_path, caption=""):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
    try:
        with open(photo_path, "rb") as photo:
            requests.post(url, data={"chat_id": CHAT_ID, "caption": caption}, files={"photo": photo}, timeout=20)
    except Exception as e:
        print(f"Error sending photo: {e}")

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-blink-features=AutomationControlled"
            ]
        )
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
            viewport={'width': 1280, 'height': 720},
            locale="en-US"
        )
        page = context.new_page()

        try:
            print("جاري الاتصال بصفحة VFS...")
            page.goto(TARGET_URL, wait_until="domcontentloaded", timeout=60000)
            page.wait_for_timeout(7000)

            # قبول الكوكيز إن وجدت
            try:
                page.click("#onetrust-accept-btn-handler", timeout=3000)
            except:
                pass

            # قراءة جميع النصوص
            body_text = page.inner_text("body").lower()

            # أخذ صورة الشاشة الحالية
            screenshot_path = "vfs_current.png"
            page.screenshot(path=screenshot_path, full_page=True)

            keywords = ["earliest available slot", "available slot", "applicants is", "04-10-2026"]
            found = any(kw in body_text for kw in keywords)

            if found:
                send_telegram_msg(f"🚨 *تنبيه موعد VFS هولندا متاح الآن!*\n\n🔗 [افتح الموقع للحجز]({TARGET_URL})")
                send_telegram_photo(screenshot_path, "صورة الموعد المتاح")
            else:
                send_telegram_msg("ℹ️ *تأكيد فحص دوري:* تم فحص الموقع بنجاح. حالة الصفحة الحالية:")
                send_telegram_photo(screenshot_path, "صورة صفحة VFS الحالية")

        except Exception as e:
            print(f"خطأ أثناء العملية: {e}")
            send_telegram_msg(f"⚠️ *خطأ في فحص VFS:* `{e}`")
        finally:
            browser.close()

if __name__ == "__main__":
    run()
