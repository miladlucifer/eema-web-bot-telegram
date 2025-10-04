import logging
import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from db import get_connection
import os
from dotenv import load_dotenv
load_dotenv()


logging.basicConfig(level=logging.INFO)

TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=TOKEN)
dp = Dispatcher()

# مراحل پروژه
PROJECT_STEPS = [
    "انتخاب نوع سایت",
    "تعداد صفحات تقریبی",
    "انتخاب امکانات مورد نیاز",
    "انتخاب سبک طراحی",
    "بودجه تقریبی",
    "زمان تحویل"
]

# ذخیره موقت پاسخ‌ها در حافظه
user_data = {}

# خوش‌آمدگویی
@dp.message(Command("start"))
async def start_handler(message: Message):
    user_data[message.from_user.id] = {}
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="شروع ثبت پروژه", callback_data="start_project")]
    ])
    await message.answer(
        "سلام 👋\nبه ربات حرفه‌ای طراحی سایت خوش آمدید!\n"
        "با چند سوال کوتاه، نیازهای سایت شما رو جمع‌آوری می‌کنم.", 
        reply_markup=keyboard
    )

# پاسخ به دکمه‌ها
@dp.callback_query(F.data == "start_project")
async def start_project(callback):
    await ask_step(callback.message, callback.from_user.id, 0)

# تابع پرسش مرحله‌ای
async def ask_step(message: Message, user_id: int, step: int):
    if step == 0:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="فروشگاهی", callback_data="type_shop")],
            [InlineKeyboardButton(text="شرکتی", callback_data="type_corp")],
            [InlineKeyboardButton(text="شخصی", callback_data="type_personal")],
            [InlineKeyboardButton(text="آموزشی", callback_data="type_edu")]
        ])
        await message.answer("لطفا نوع سایت خود را انتخاب کنید:", reply_markup=keyboard)
    else:
        await message.answer(f"مرحله {step+1}: لطفا پاسخ خود را وارد کنید:")

# پاسخ دکمه نوع سایت
@dp.callback_query(F.data.startswith("type_"))
async def handle_type(callback):
    user_id = callback.from_user.id
    user_data[user_id]["type"] = callback.data.replace("type_", "")
    await callback.message.answer(f"✅ نوع سایت شما: {user_data[user_id]['type']}")
    # ادامه مرحله بعد
    await ask_step(callback.message, user_id, 1)

# ذخیره دیتابیس
def save_to_db(user_id):
    conn = get_connection()
    cur = conn.cursor()
    data = user_data[user_id]
    cur.execute(
        "INSERT INTO projects (user_id, type, pages, features, style, budget, deadline) VALUES (%s, %s, %s, %s, %s, %s, %s)",
        (
            user_id,
            data.get("type"),
            data.get("pages"),
            data.get("features"),
            data.get("style"),
            data.get("budget"),
            data.get("deadline")
        )
    )
    conn.commit()
    cur.close()
    conn.close()

# اجرا
if __name__ == "__main__":
    asyncio.run(dp.start_polling(bot))
