import os
import json
import random
import time
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, CallbackContext

TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
DATA_FILE = "bank_data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {"users": {}, "cooldown": {}}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

data = load_data()
jobs = ["مبرمج", "طيار", "طبيب", "مهندس", "معلم", "تاجر", "فلاح", "عامل"]

def random_job():
    return random.choice(jobs)

def random_salary():
    return random.randint(500, 25000)

def check_cooldown(user_id, command_name):
    now = time.time()
    key = f"{user_id}_{command_name}"
    if key in data["cooldown"]:
        last_used = data["cooldown"][key]
        if now - last_used < 180:
            remaining = int(180 - (now - last_used))
            return False, remaining
    return True, 0

def set_cooldown(user_id, command_name):
    key = f"{user_id}_{command_name}"
    data["cooldown"][key] = time.time()
    save_data(data)

async def handle_message(update: Update, context: CallbackContext):
    text = update.message.text.strip()
    user_id = str(update.effective_user.id)

    if text in ["إنشاء حساب", "انشاء حساب"]:
        if user_id in data["users"]:
            await update.message.reply_text("⚠️ لديك حساب مسبقاً.")
            return
        job = random_job()
        balance = random_salary()
        account_number = str(random.randint(100000, 999999))
        data["users"][user_id] = {
            "balance": balance,
            "job": job,
            "account_number": account_number,
            "username": update.effective_user.username or update.effective_user.first_name
        }
        save_data(data)
        await update.message.reply_text(
            f"✅ تم إنشاء حسابك!\nالوظيفة: {job}\n💰 الرصيد: {balance} جنيه\n🏦 رقم الحساب: {account_number}"
        )

    elif text == "راتب":
        if user_id not in data["users"]:
            await update.message.reply_text("❌ أنشئ حسابك أولاً (أرسل: إنشاء حساب)")
            return
        ok, remaining = check_cooldown(user_id, "salary")
        if not ok:
            await update.message.reply_text(f"⏳ انتظر {remaining} ثانية قبل طلب الراتب مرة أخرى.")
            return
        amount = random_salary()
        data["users"][user_id]["balance"] += amount
        save_data(data)
        set_cooldown(user_id, "salary")
        await update.message.reply_text(f"💰 استلمت راتبك: {amount} جنيه\nالرصيد الآن: {data['users'][user_id]['balance']}")

    elif text == "استثمار":
        if user_id not in data["users"]:
            await update.message.reply_text("❌ أنشئ حسابك أولاً.")
            return
        ok, remaining = check_cooldown(user_id, "invest")
        if not ok:
            await update.message.reply_text(f"⏳ انتظر {remaining} ثانية قبل الاستثمار مرة أخرى.")
            return
        percent = random.randint(3, 25)
        win = random.choice([True, False])
        balance = data["users"][user_id]["balance"]
        if win:
            gain = int(balance * percent / 100)
            data["users"][user_id]["balance"] += gain
            msg = f"📈 استثمار ناجح! ربح {percent}% = {gain} جنيه"
        else:
            loss = int(balance * percent / 100)
            data["users"][user_id]["balance"] -= loss
            msg = f"📉 استثمار خاسر! خسارة {percent}% = {loss} جنيه"
        save_data(data)
        set_cooldown(user_id, "invest")
        await update.message.reply_text(f"{msg}\nالرصيد الجديد: {data['users'][user_id]['balance']}")

    elif text == "مضاربة":
        if user_id not in data["users"]:
            await update.message.reply_text("❌ أنشئ حسابك أولاً.")
            return
        ok, remaining = check_cooldown(user_id, "gamble")
        if not ok:
            await update.message.reply_text(f"⏳ انتظر {remaining} ثانية قبل المضاربة مرة أخرى.")
            return
        percent = random.choice([50, 75])
        win = random.choice([True, False])
        balance = data["users"][user_id]["balance"]
        if win:
            gain = int(balance * percent / 100)
            data["users"][user_id]["balance"] += gain
            msg = f"🎲 مضاربة ناجحة! ربح {percent}% = {gain} جنيه"
        else:
            loss = int(balance * percent / 100)
            data["users"][user_id]["balance"] -= loss
            msg = f"💥 مضاربة خاسرة! خسارة {percent}% = {loss} جنيه"
        save_data(data)
        set_cooldown(user_id, "gamble")
        await update.message.reply_text(f"{msg}\nالرصيد الجديد: {data['users'][user_id]['balance']}")

    elif text == "حظ":
        if user_id not in data["users"]:
            await update.message.reply_text("❌ أنشئ حسابك أولاً.")
            return
        ok, remaining = check_cooldown(user_id, "luck")
        if not ok:
            await update.message.reply_text(f"⏳ انتظر {remaining} ثانية قبل استخدام الحظ مرة أخرى.")
            return
        win = random.choice([True, False])
        balance = data["users"][user_id]["balance"]
        if win:
            gain = balance
            data["users"][user_id]["balance"] += gain
            msg = f"🍀 حظ سعيد! ربحت {gain} جنيه إضافية!"
        else:
            loss = balance
            data["users"][user_id]["balance"] = 0
            msg = f"💔 حظ سيء! خسرت كل رصيدك ({loss} جنيه)"
        save_data(data)
        set_cooldown(user_id, "luck")
        await update.message.reply_text(f"{msg}\nالرصيد الجديد: {data['users'][user_id]['balance']}")

    elif text in ["رصيدي", "رصيد"]:
        if user_id not in data["users"]:
            await update.message.reply_text("❌ أنشئ حسابك أولاً.")
            return
        u = data["users"][user_id]
        await update.message.reply_text(
            f"👤 {u['username']}\n💼 وظيفة: {u['job']}\n💰 الرصيد: {u['balance']}\n🏦 رقم الحساب: {u['account_number']}"
        )

    elif text.startswith("إرسال"):
        parts = text.split()
        if len(parts) != 3:
            await update.message.reply_text("استخدم: إرسال [رقم_الحساب] [المبلغ]\nمثال: إرسال 123456 500")
            return
        if user_id not in data["users"]:
            await update.message.reply_text("❌ أنشئ حسابك أولاً.")
            return
        to_account = parts[1]
        try:
            amount = int(parts[2])
        except:
            await update.message.reply_text("المبلغ يجب أن يكون رقماً.")
            return
        sender = data["users"][user_id]
        if sender["balance"] < amount:
            await update.message.reply_text(f"❌ رصيدك غير كافٍ. رصيدك: {sender['balance']} جنيه")
            return
        target_id = None
        for uid, info in data["users"].items():
            if info["account_number"] == to_account:
                target_id = uid
                break
        if not target_id:
            await update.message.reply_text("❌ رقم الحساب غير صحيح.")
            return
        sender["balance"] -= amount
        data["users"][target_id]["balance"] += amount
        save_data(data)
        await update.message.reply_text(f"✅ تم إرسال {amount} جنيه إلى الحساب {to_account}")

    elif text == "/start":
        await update.message.reply_text(
            "✨ مرحباً بك في البوت البنكي! ✨\n\n"
            "الأوامر المتاحة:\n"
            "🔹 إنشاء حساب\n"
            "🔹 راتب\n"
            "🔹 استثمار\n"
            "🔹 مضاربة\n"
            "🔹 حظ\n"
            "🔹 رصيدي\n"
            "🔹 إرسال [رقم_الحساب] [المبلغ]\n\n"
            "أرسل 'إنشاء حساب' لتبدأ!"
        )

def main():
    print("🎮 تشغيل البوت البنكي...")
    app = Application.builder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("✅ البوت يعمل الآن...")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()