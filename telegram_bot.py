"""FurniQuote Bot: a demonstrational Telegram bot for a simple quote workflow.

Prices and formula are illustrative only. Set TELEGRAM_BOT_TOKEN before running.
"""
from __future__ import annotations

import asyncio
import os
import sqlite3
from datetime import datetime, timezone

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

DB_PATH = os.getenv("QUOTE_DB_PATH", "quotes.sqlite3")
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()


class QuoteFlow(StatesGroup):
    width = State()
    height = State()
    material = State()


def init_db() -> None:
    with sqlite3.connect(DB_PATH) as db:
        db.execute("""CREATE TABLE IF NOT EXISTS quotes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT NOT NULL,
            telegram_user_id INTEGER NOT NULL,
            width_cm INTEGER NOT NULL,
            height_cm INTEGER NOT NULL,
            material TEXT NOT NULL,
            estimated_price REAL NOT NULL
        )""")


def save_quote(user_id: int, width: int, height: int, material: str, price: float) -> int:
    with sqlite3.connect(DB_PATH) as db:
        cursor = db.execute(
            "INSERT INTO quotes(created_at, telegram_user_id, width_cm, height_cm, material, estimated_price) VALUES (?, ?, ?, ?, ?, ?)",
            (datetime.now(timezone.utc).isoformat(), user_id, width, height, material, price),
        )
        return int(cursor.lastrowid)


def calculate_price(width_cm: int, height_cm: int, material: str) -> float:
    # Deliberately simple placeholder formula: not a real commercial quotation.
    coefficient = {"Базовый": 1.0, "Усиленный": 1.25, "Премиум": 1.6}[material]
    area = (width_cm / 100) * (height_cm / 100)
    return round((area * 18000 * coefficient + 2500) / 100) * 100


material_keyboard = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="Базовый"), KeyboardButton(text="Усиленный")], [KeyboardButton(text="Премиум")]],
    resize_keyboard=True,
    one_time_keyboard=True,
)


dp = Dispatcher()


@dp.message(CommandStart())
async def start(message: Message) -> None:
    await message.answer(
        "Привет! Я FurniQuote Bot — демонстрационный бот для сбора параметров заказа и расчёта предварительной стоимости.\n\n"
        "Нажмите /quote, чтобы создать тестовую заявку. Расчёт учебный и не является коммерческим предложением."
    )


@dp.message(Command("quote"))
async def quote_start(message: Message, state: FSMContext) -> None:
    await state.clear()
    await state.set_state(QuoteFlow.width)
    await message.answer("Введите ширину изделия в сантиметрах (от 20 до 500):", reply_markup=ReplyKeyboardRemove())


@dp.message(QuoteFlow.width)
async def set_width(message: Message, state: FSMContext) -> None:
    try:
        value = int((message.text or "").strip())
    except ValueError:
        await message.answer("Нужно целое число. Например: 120")
        return
    if not 20 <= value <= 500:
        await message.answer("Введите значение от 20 до 500 см.")
        return
    await state.update_data(width=value)
    await state.set_state(QuoteFlow.height)
    await message.answer("Введите высоту изделия в сантиметрах (от 20 до 300):")


@dp.message(QuoteFlow.height)
async def set_height(message: Message, state: FSMContext) -> None:
    try:
        value = int((message.text or "").strip())
    except ValueError:
        await message.answer("Нужно целое число. Например: 200")
        return
    if not 20 <= value <= 300:
        await message.answer("Введите значение от 20 до 300 см.")
        return
    await state.update_data(height=value)
    await state.set_state(QuoteFlow.material)
    await message.answer("Выберите условный материал:", reply_markup=material_keyboard)


@dp.message(QuoteFlow.material, F.text.in_({"Базовый", "Усиленный", "Премиум"}))
async def set_material(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    width, height, material = int(data["width"]), int(data["height"]), str(message.text)
    price = calculate_price(width, height, material)
    quote_id = save_quote(message.from_user.id, width, height, material, price)  # type: ignore[union-attr]
    await state.clear()
    await message.answer(
        f"Тестовая заявка #{quote_id} сохранена.\n"
        f"Размер: {width} × {height} см\nМатериал: {material}\n"
        f"Предварительный расчёт: {price:,.0f} ₽\n\n"
        "Это демонстрационная формула, а не реальная смета.",
        reply_markup=ReplyKeyboardRemove(),
    )


@dp.message(QuoteFlow.material)
async def invalid_material(message: Message) -> None:
    await message.answer("Пожалуйста, выберите один из предложенных вариантов кнопкой.", reply_markup=material_keyboard)


async def main() -> None:
    if not TOKEN:
        raise SystemExit("Set TELEGRAM_BOT_TOKEN environment variable first.")
    init_db()
    bot = Bot(TOKEN)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
