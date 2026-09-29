import os
import requests
from playwright.sync_api import sync_playwright

BOT_TOKEN = "8292550162:AAGBLB4bX3xHnAaw9ftrpI2ZLvH5f1sTa08"
CHAT_ID = "1083698448"

# ضع بيانات حسابك في VFS هنا
VFS_EMAIL = "yayased10@gmail.com"
VFS_PASSWORD = "VISAvisa11**"

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
                "--disable-blink-features=AutomationControlled",
                "--start-maximized"
            ]
        )
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
            viewport={'width': 1366, 'height': 768},
            locale="en-US"
        )
        page = context.new_page()

        try:
            print("جاري فتح صفحة VFS...")
            page.goto(TARGET_URL, wait_until="networkidle", timeout=60000)
            page.wait_for_timeout(5000)

            # قبول الكوكيز
            try:
                page.click("#onetrust-accept-btn-handler", timeout=3000)
                page.wait_for_timeout(1000)
            except:
                pass

            # تعبئة بيانات الدخول إن توفرت
            if VFS_EMAIL != "your_email@example.com":
                print("تعبئة بيانات الحساب...")
                page.type("input[formcontrolname='username']", VFS_EMAIL, delay=100)
                page.type("input[formcontrolname='password']", VFS_PASSWORD, delay=100)
                page.wait_for_timeout(2000)
                
                # الضغط على زر الدخول إن لم يكن هناك كابتشا مانعة
                submit_btn = page.locator("button[type='submit']")
                if submit_btn.is_enabled():
                    submit_btn.click()
                    page.wait_for_timeout(8000)

            # قراءة النص والصورة بعد التفاعل
            body_text = page.inner_text("body").lower()
            screenshot_path = "vfs_result.png"
            page.screenshot(path=screenshot_path, full_page=True)

            keywords = ["earliest available slot", "available slot", "applicants is", "04-10-2026"]
            found = any(kw in body_text for kw in keywords)

            if found:
                send_telegram_msg(f"🚨 *تنبيه: تم العثور على موعد VFS هولندا!*\n\n🔗 [افتح الموقع للحجز]({TARGET_URL})")
                send_telegram_photo(screenshot_path, "صورة الموعد المتاح")
            else:
                send_telegram_msg("ℹ️ *تحديث الفحص:* تم تنفيذ الفحص وإليك صورة الشاشة الحالية:")
                send_telegram_photo(screenshot_path, "حالة الصفحة الحالية")

        except Exception as e:
            print(f"خطأ: {e}")
            send_telegram_msg(f"⚠️ *خطأ أثناء الفحص:* `{e}`")
        finally:
            browser.close()

if __name__ == "__main__":
    run()
