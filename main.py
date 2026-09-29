import os
import requests
from playwright.sync_api import sync_playwright

BOT_TOKEN = "8292550162:AAGBLB4bX3xHnAaw9ftrpI2ZLvH5f1sTa08"
CHAT_ID = "1083698448"
TARGET_URL = "https://visa.vfsglobal.com/dza/en/nld/login"

def send_telegram(message):
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
            args=["--no-sandbox", "--disable-setuid-sandbox", "--disable-blink-features=AutomationControlled"]
        )
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        try:
            print("جاري فتح VFS...")
            page.goto(TARGET_URL, wait_until="networkidle", timeout=60000)
            page.wait_for_timeout(5000)

            # التقاط الصورة الحالية
            screenshot_path = "vfs_state.png"
            page.screenshot(path=screenshot_path, full_page=True)
            body_text = page.inner_text("body")

            # فحص وجود نص الموعد أو التاريخ المحدد
            if "04-10-2026" in body_text or "earliest available slot" in body_text.lower():
                send_telegram(
                    "🚨 *تنبيه عاجل: موعد متاح في VFS هولندا!*\n\n"
                    "📌 *الفئة:* Other Category / Short Stay\n"
                    "📅 *الموعد الكاشف:* `04-10-2026`\n\n"
                    f"🔗 [سجل دخولك فوراً للحجز]({TARGET_URL})"
                )
                send_telegram_photo(screenshot_path, "صورة الموعد المتاح")
            else:
                send_telegram("ℹ️ *تحديث الفحص:* البوت متصل ومستعد، وفي انتظار ظهور تحديث المواعيد داخل النظام.")
                send_telegram_photo(screenshot_path, "حالة الشاشة الحالية")

        except Exception as e:
            print(f"خطأ: {e}")
            send_telegram(f"⚠️ *خطأ فحص:* `{e}`")
        finally:
            browser.close()

if __name__ == "__main__":
    run()
