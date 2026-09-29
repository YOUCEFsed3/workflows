import os
import requests
from playwright.sync_api import sync_playwright

# بيانات تلغرام
BOT_TOKEN = "8292550162:AAGBLB4bX3xHnAaw9ftrpI2ZLvH5f1sTa08"
CHAT_ID = "1083698448"

# ضع بيانات حسابك في VFS هنا ليتسنى للسكربت فتح القوائم
VFS_EMAIL = "yayased10@gmail.com"
VFS_PASSWORD = "VISAvisa11**"

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
            print("جاري الدخول إلى موقع VFS...")
            page.goto(TARGET_URL, wait_until="networkidle", timeout=60000)
            page.wait_for_timeout(4000)

            # تسجيل الدخول
            if VFS_EMAIL != "ضع_إيميلك_هنا_بين_العلائم":
                print("تسجيل الدخول إلى الحساب...")
                page.fill("input[formcontrolname='username']", VFS_EMAIL)
                page.fill("input[formcontrolname='password']", VFS_PASSWORD)
                page.click("button[type='submit']")
                page.wait_for_timeout(6000)

            # الاتجاه لصفحة تفاصيل الموعد
            body_text = page.inner_text("body")

            # قراءة المواعيد المتاحة
            if "earliest available slot" in body_text.lower() or "available slot" in body_text.lower():
                send_telegram(f"🚨 *تنبيه موعد VFS متاح الآن!*\n\nتم العثور على موعد متاح في الحساب!\n🔗 [رابط VFS]({TARGET_URL})")
            else:
                # إرسال رسالة تجريبية لتأكيد الاتصال بالبوت
                send_telegram("✅ *اختبار البوت:* تم الاتصال بنجاح وفحص الصفحة، لا توجد مواعيد متاحة في الفئات غير المفتوحة حالياً.")

        except Exception as e:
            print(f"حدث خطأ أثناء التشغيل: {e}")
            send_telegram(f"⚠️ *خطأ في فحص VFS:* `{e}`")
        finally:
            browser.close()

if __name__ == "__main__":
    run()
