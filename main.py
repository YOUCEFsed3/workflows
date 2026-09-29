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
        print(f"Error sending Telegram message: {e}")

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        
        try:
            print("جاري فتح موقع VFS...")
            page.goto(TARGET_URL, wait_until="networkidle", timeout=60000)
            
            page.wait_for_timeout(5000)
            text = page.inner_text("body")

            if "Earliest available slot" in text or "available slot" in text:
                print("🚨 تم اكتشاف مواعيد متاحة!")
                send_telegram(f"🚨 *تنبيه VFS هولندا:*\nتم كشف مواعيد متاحة حالياً على الموقع عبر السحاب!\n🔗 [رابط VFS]({TARGET_URL})")
            else:
                print("⚙️ لا توجد مواعيد متاحة حالياً.")

        except Exception as e:
            print(f"حدث خطأ أثناء فحص الصفحة: {e}")
        finally:
            browser.close()

if __name__ == "__main__":
    run()
