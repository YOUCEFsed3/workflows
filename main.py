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
            print("جاري الفحص الصامت لصفحة VFS...")
            page.goto(TARGET_URL, wait_until="domcontentloaded", timeout=60000)
            page.wait_for_timeout(5000)

            body_text = page.inner_text("body").lower()

            # الكلمات الدالة على فتح المواعيد
            keywords = ["earliest available slot", "available slot", "applicants is", "04-10-2026"]
            
            # إذا ظهرت أي كلمة دلت على موعد متاح ينطلق التنبيه فوراً
            if any(kw in body_text for kw in keywords):
                send_telegram(
                    f"🚨 *تنبيه عاجل: تم كشف مواعيد في VFS هولندا!*\n\n"
                    f"هناك تحديث أو موعد متاح حالياً على النظام.\n\n"
                    f"🔗 [افتح VFS وسجل دخولك فوراً للحجز]({TARGET_URL})"
                )
                print("✅ تم العثور على موعد وإرسال التنبيه!")
            else:
                print("⚙️ الفحص تم بنجاح: لا يوجد موعد متاح حالياً، البوت يعمل بصمت.")

        except Exception as e:
            # طباعة الخطأ في السجل الداخلي لـ GitHub فقط دون إزعاجك في تلغرام
            print(f"تنبيه خلفي: {e}")
        finally:
            browser.close()

if __name__ == "__main__":
    run()
