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
            print("جاري فتح صفحة VFS...")
            page.goto(TARGET_URL, wait_until="networkidle", timeout=60000)
            page.wait_for_timeout(6000)

            # محاولة محاكاة اختيار القوائم المنسدلة
            try:
                # اختيار المركز
                selects = page.locator("mat-select")
                if selects.count() > 0:
                    selects.nth(0).click()
                    page.wait_for_timeout(1000)
                    page.locator("mat-option").first.click()
                    page.wait_for_timeout(2000)

                # اختيار الفئة العامة
                if selects.count() > 1:
                    selects.nth(1).click()
                    page.wait_for_timeout(1000)
                    page.locator("mat-option").filter(has_text="Short Stay-Visa").click()
                    page.wait_for_timeout(2000)
            except Exception as opt_err:
                print(f"تنبيه: تعذر التنقل الكامل بين القوائم الخفية: {opt_err}")

            # قراءة محتوى الصفحة بالكامل
            body_text = page.inner_text("body")

            # البحث عن أي نص يحتوي على توفر مواعيد
            keywords = ["earliest available slot", "available slot", "applicants is"]
            found_slot = any(kw in body_text.lower() for kw in keywords)

            if found_slot:
                # استخراج السطر المكتوب فيه الموعد
                lines = [line.strip() for line in body_text.split('\n') if any(k in line.lower() for k in keywords)]
                details = lines[0] if lines else "تم اكتشاف موعد متاح على الموقع!"

                message = (
                    f"🚨 *تنبيه موعد VFS هولندا متاح الآن!*\n\n"
                    f"📅 *التفاصيل الكترونية:* {details}\n\n"
                    f"🔗 [سجل دخولك فوراً للحجز]({TARGET_URL})"
                )
                send_telegram(message)
                print("✅ تم إرسال التنبيه بنجاح إلى تلغرام!")
            else:
                print("⚙️ لا توجد مواعيد متاحة في الفحص الحالي.")

        except Exception as e:
            print(f"حدث خطأ أثناء تنفيذ الفحص: {e}")
        finally:
            browser.close()

if __name__ == "__main__":
    run()
