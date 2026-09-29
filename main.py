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
        browser = p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-setuid-sandbox"]
        )
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            viewport={'width': 1280, 'height': 720}
        )
        page = context.new_page()

        try:
            print("جاري فتح موقع VFS...")
            page.goto(TARGET_URL, wait_until="networkidle", timeout=60000)
            page.wait_for_timeout(5000)

            # التعامل مع حماية أو كوكيز إذا ظهرت
            try:
                cookie_btn = page.locator("#onetrust-accept-btn-handler")
                if cookie_btn.is_visible(timeout=3000):
                    cookie_btn.click()
            except:
                pass

            # قراءة النص كاملاً
            body_text = page.inner_text("body")

            # كلمات البحث الدالة على المواعيد المتاحة
            keywords = ["earliest available slot", "available slot", "applicants is"]
            
            # التحقق من وجود تواريخ أو مواعيد
            if any(kw in body_text.lower() for kw in keywords) or "04-10-2026" in body_text:
                # استخراج السطر الذي يحتوي التنبيه
                lines = [line.strip() for line in body_text.split('\n') if any(k in line.lower() for k in keywords)]
                details = lines[0] if lines else "تم كشف موعد متاح في الصفحة!"

                send_telegram(
                    f"🚨 *تنبيه موعد VFS هولندا متاح الآن!*\n\n"
                    f"📅 *التفاصيل:* {details}\n\n"
                    f"🔗 [حجز الموعد عبر VFS]({TARGET_URL})"
                )
            else:
                # إرسال تأكيد التشغيل التلقائي دورياً
                print("فحص ناجح: لا يوجد تغيير حالياً.")

        except Exception as e:
            print(f"خطأ أثناء العملية: {e}")
            send_telegram(f"⚠️ *خطأ في فحص VFS:* `{e}`")
        finally:
            browser.close()

if __name__ == "__main__":
    run()
