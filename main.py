import requests
import json
import time
from playwright.sync_api import sync_playwright

BOT_TOKEN = "8292550162:AAGBLB4bX3xHnAaw9ftrpI2ZLvH5f1sTa08"
CHAT_ID = "1083698448"
LOGIN_URL = "https://visa.vfsglobal.com/dza/en/nld/login"

# الفئات المطلوب فحصها
TARGET_CATEGORIES = ["Business Visa", "Tourism", "Other Category"]

def send_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"}
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print(f"Error sending Telegram message: {e}")

def run():
    with sync_playwright() as p:
        # تشغيل المتصفح ببيئة مموهة لتفادي كشف BOTS
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
            viewport={'width': 1366, 'height': 768}
        )
        page = context.new_page()

        slots_found = []

        # التقاط استجابات الشبكة الداخلية (Network Interception)
        def handle_response(response):
            try:
                # فحص استجابات API الخاصة بالمواعيد
                if "appointment" in response.url.lower() or "slots" in response.url.lower():
                    if response.status == 200:
                        data = response.json()
                        data_str = json.dumps(data)
                        if "earliest" in data_str.lower() or "date" in data_str.lower():
                            slots_found.append(data_str)
            except:
                pass

        page.on("response", handle_response)

        try:
            print("جاري فتح VFS واستخراج البيانات...")
            page.goto(LOGIN_URL, wait_until="networkidle", timeout=60000)
            page.wait_for_timeout(6000)

            # قراءة النص البرمجي الكامل للصفحة
            body_text = page.inner_text("body")

            # البحث عن وجود تواريخ أو كلمات المواعيد
            keywords = ["earliest available slot", "available slot", "04-10-2026"]
            found_in_text = any(kw in body_text.lower() for kw in keywords)

            if found_in_text or len(slots_found) > 0:
                # استخراج السطر المكتوب فيه الموعد
                lines = [line.strip() for line in body_text.split('\n') if any(k in line.lower() for k in keywords)]
                slot_detail = lines[0] if lines else "تم اكتشاف توفر مواعيد في النظام!"

                msg = (
                    f"🚨 *تنبيه قوي: تم كشف موعد متاح في VFS هولندا!*\n\n"
                    f"📌 *التفاصيل:* `{slot_detail}`\n"
                    f"🎯 *الفئات المستهدفة:* Business / Tourism / Other Category\n\n"
                    f"🔗 [سجل دخولك فوراً للحجز]({LOGIN_URL})"
                )
                send_telegram(msg)
                print("✅ تم العثور على موعد وإرسال التنبيه!")
            else:
                print("⚙️ اكتمل الفحص: لا توجد مواعيد متاحة في هذا الاستعلام.")

        except Exception as e:
            print(f"خطأ أثناء الفحص: {e}")
        finally:
            browser.close()

if __name__ == "__main__":
    run()
