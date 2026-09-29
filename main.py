import os
import requests
from playwright.sync_api import sync_playwright

BOT_TOKEN = "8292550162:AAGBLB4bX3xHnAaw9ftrpI2ZLvH5f1sTa08"
CHAT_ID = "1083698448"
TARGET_URL = "https://visa.vfsglobal.com/dza/en/nld/login"

# الفئات المطلوبة
CATEGORIES = [
    "Business Visa",
    "Tourism",
    "Other Category"
]

def send_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"}
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print(f"Error sending Telegram message: {e}")

def check_sub_category(page, sub_cat_name):
    try:
        # تحديد واختيار الفئة الفرعية من القائمة
        sub_cat_dropdown = page.locator("mat-select[formcontrolname='subCategory']").or_(
            page.locator("mat-select").nth(2)
        )
        sub_cat_dropdown.click()
        page.wait_for_timeout(1000)

        # الضغط على خيار الفئة المحدد
        page.locator("mat-option").filter(has_text=sub_cat_name).click()
        page.wait_for_timeout(4000)

        # قراءة النص الظاهر في مربع النتيجة
        body_text = page.inner_text("body")

        if "earliest available slot" in body_text.lower() or "available slot" in body_text.lower():
            lines = [line.strip() for line in body_text.split('\n') if "earliest available slot" in line.lower()]
            slot_info = lines[0] if lines else "موعد متاح!"
            
            message = (
                f"🚨 *تنبيه موعد VFS هولندا جديد!*\n\n"
                f"📌 *الفئة الفرعية:* `{sub_cat_name}`\n"
                f"📅 *التفاصيل:* {slot_info}\n\n"
                f"🔗 [تسجيل الدخول وحجز الموعد الآن]({TARGET_URL})"
            )
            send_telegram(message)
            print(f"✅ تم العثور على موعد للفئة: {sub_cat_name}")
        else:
            print(f"❌ لا توجد مواعيد حالياً للفئة: {sub_cat_name}")

    except Exception as e:
        print(f"⚠️ خطأ أثناء اختيار الفئة {sub_cat_name}: {e}")

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
            page.wait_for_timeout(5000)

            # اختيار المركز
            centre_dropdown = page.locator("mat-select[formcontrolname='itemCategory']").or_(
                page.locator("mat-select").nth(0)
            )
            if centre_dropdown.is_visible():
                centre_dropdown.click()
                page.wait_for_timeout(1000)
                page.locator("mat-option").first.click()
                page.wait_for_timeout(2000)

            # اختيار الفئة الرئيسية Short Stay-Visa
            cat_dropdown = page.locator("mat-select[formcontrolname='selectedCategory']").or_(
                page.locator("mat-select").nth(1)
            )
            if cat_dropdown.is_visible():
                cat_dropdown.click()
                page.wait_for_timeout(1000)
                page.locator("mat-option").filter(has_text="Short Stay-Visa").click()
                page.wait_for_timeout(2000)

            # فحص كل فئة فرعية من الفئات الثلاث
            for sub_cat in CATEGORIES:
                print(f"جاري فحص فئة: {sub_cat}...")
                check_sub_category(page, sub_cat)

        except Exception as e:
            print(f"حدث خطأ أثناء تنفيذ الفحص: {e}")
        finally:
            browser.close()

if __name__ == "__main__":
    run()
