import asyncio
import logging
import sys
import requests
import re
import os
import tempfile
import subprocess
from aiogram import Bot, Dispatcher, types, F, Router
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command, Filter
from aiogram.types import Message, URLInputFile, FSInputFile, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage
from aiohttp import web
import database
from flask import Flask
from threading import Thread
from yt_dlp import YoutubeDL

# Flask
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is alive!"

def run_flask():
    app.run(host='0.0.0.0', port=55555)

flask_thread = Thread(target=run_flask)
flask_thread.start()

load_dotenv()
TOKEN = os.getenv("TOKEN")  
CHANNEL_USERNAME = os.getenv("CHANNEL_USERNAME")
FFMPEG_PATH = "/usr/bin/ffmpeg"

bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(storage=MemoryStorage())

database.create_table_users()
database.create_table_convertations()

class LinkFilter(Filter):
    async def __call__(self, message: Message) -> bool:
        return message.text.startswith("http")

async def check_subscription(bot: Bot, user_id: int) -> bool:
    try:
        member = await bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return member.status in ['member', 'administrator', 'creator']
    except Exception as e:
        print(f"Ошибка проверки подписки: {e}")
        return False

def sanitize_filename(name):
    return re.sub(r'[\\/*?:"<>|]', "", name)

def get_video_resolution(file_path):
    import time

    ffprobe_path = FFMPEG_PATH.replace("ffmpeg", "ffprobe")

    for _ in range(10):
        if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
            break
        time.sleep(0.5)
    else:
        raise FileNotFoundError(f"Файл {file_path} не найден или пустой.")

    cmd = [
        ffprobe_path,
        "-v", "error",
        "-select_streams", "v:0",
        "-show_entries", "stream=width,height",
        "-of", "csv=s=x:p=0",
        file_path
    ]
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    output = result.stdout.strip()

    if not output or "x" not in output:
        raise ValueError("ffprobe не смог получить разрешение видео.")

    width, height = map(int, output.split('x'))
    return width, height


def pad_video_if_needed(input_path):
    width, height = get_video_resolution(input_path)
    aspect_ratio = width / height
    logging.info(f"Оригинальное разрешение: {width}x{height}, Аспект: {aspect_ratio:.2f}")

    if abs(aspect_ratio - (9/16)) < 0.03:
        logging.info("[FFMPEG] Видео уже 9:16 — паддинг и перекодирование не требуется.")
        return input_path

    if abs(aspect_ratio - (16/9)) < 0.01:
        logging.info("[FFMPEG] Видео уже 16:9 — паддинг не нужен.")
        return input_path

    output_path = input_path.replace(".mp4", "_padded.mp4")
    cmd = [
        FFMPEG_PATH, "-i", input_path,
        "-vf", "scale=-2:720:force_original_aspect_ratio=decrease,pad=ceil(iw/2)*2:720:(ow-iw)/2:(oh-ih)/2",
        "-c:a", "copy", output_path
    ]

    logging.info("[FFMPEG] Видео будет вписано в 1280x720 с боковыми и верх/низ полосами")
    try:
        subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=120, check=True)
        return output_path
    except subprocess.TimeoutExpired:
        logging.error("FFmpeg: Обработка заняла слишком много времени")
        return input_path
    except subprocess.CalledProcessError as e:
        logging.error(f"FFmpeg: Ошибка обработки — {e}")
        return input_path

async def download_tiktok(url):
    tmpdir = tempfile.mkdtemp()
    output_template = os.path.join(tmpdir, "%(title).50s.%(ext)s")

    ydl_opts = {
        'outtmpl': output_template,
        'format': 'mp4',
        'quiet': True,
        'no_warnings': True,
    }

    def _download():
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            path = ydl.prepare_filename(info)
            new_path = os.path.join(tmpdir, sanitize_filename(os.path.basename(path)))
            os.rename(path, new_path)
            return pad_video_if_needed(new_path)

    padded_path = await asyncio.to_thread(_download)
    return padded_path, tmpdir


    def _download():
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            path = ydl.prepare_filename(info)
            new_path = os.path.join(tempfile.gettempdir(), sanitize_filename(os.path.basename(path)))
            os.rename(path, new_path)
            return pad_video_if_needed(new_path)

    padded_path = await asyncio.to_thread(_download)
    return padded_path

@dp.message(LinkFilter())
async def Link_handler(message: Message) -> None:
    is_subscribed = await check_subscription(message.bot, message.from_user.id)

    if not is_subscribed:
        buttons = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Подписаться🔗", url="https://t.me/your_channel_name")],
            [InlineKeyboardButton(text="Я подписался✅", callback_data="check_sub")]
        ])
        await message.answer("Чтобы использовать бота, нужно подписаться на наш канал!", reply_markup=buttons)
        return

    msg = await message.answer("Пожалуйста, подождите, мы обрабатываем ваш запрос...")

    try:
        video_path, tmpdir = await download_tiktok(message.text)
        size_mb = os.path.getsize(video_path) / 1024 / 1024

        if size_mb > 50:
            await msg.edit_text(f"⚠️ Видео слишком большое: {size_mb:.1f} МБ. Максимум — 50 МБ.")
            return

        await msg.edit_text("Отправляем видео...")
        file = FSInputFile(video_path)
        await message.answer_video(
            file,
            caption="Скачано с помощью:\n\n[@TikTokDownloader_yourbot](https://t.me/TikTokDownloader_yourbot)",
            parse_mode=ParseMode.MARKDOWN
        )
        database.add_convertation(message.from_user.id, status='Done')

    except Exception as e:
        await msg.edit_text(f"Ошибка: {e}")
        database.add_convertation(message.from_user.id, status='Failed')

    finally:
        import shutil
        if 'tmpdir' in locals() and os.path.exists(tmpdir):
            shutil.rmtree(tmpdir)

@dp.callback_query(F.data == "check_sub")
async def check_sub_callback(callback: CallbackQuery):
    if await check_subscription(callback.bot, callback.from_user.id):
        await callback.message.edit_text("Спасибо за подписку!✅\n\nТеперь отправьте ссылку ещё раз.")
    else:
        await callback.answer("Вы еще не подписаны на канал!", show_alert=True)

@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    await message.answer(
        f"Привет {message.from_user.full_name}!\n\nЭто загрузчик видео из TikTok без водяных знаков.\n\nОтправь мне ссылку на видео.")
    database.add_user(message.from_user.id, message.from_user.username)

@dp.message(Command("restart"))
async def command_restart_handler(message: Message) -> None:
    await message.delete()
    await message.answer("Бот успешно перезапущен!🔄\n\nТеперь можешь снова отправить ссылку на видео из TikTok.")
    database.add_user(message.from_user.id, message.from_user.username)

@dp.message(Command('admin'))
async def admin_stats(message: Message) -> None:
    users = database.get_users()
    convertations = database.get_convertations()
    with open('info.txt', 'w') as file:
        file.write(f'USERS\n{users}\nCONVERTATIONS\n{convertations}')
    await message.answer_document(document=FSInputFile('info.txt'))

@dp.message()
async def echo_handler(message: Message) -> None:
    await message.answer("Я не понимаю.\n\nОтправьте ссылку на видео из TikTok.")

async def main() -> None:
    await bot.set_my_commands([
        types.BotCommand(command="start", description="Запустить бота"),
        types.BotCommand(command="restart", description="Перезапустить бота")
    ])
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
