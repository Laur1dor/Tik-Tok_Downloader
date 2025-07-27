# TikTok Video Downloader Telegram Bot

Этот проект представляет собой **Telegram-бота**, который позволяет скачивать видео из TikTok **без водяных знаков** и отправляет их пользователю прямо в Telegram. Бот разработан на **Python** с использованием **Aiogram 3**, **yt-dlp**, **FFmpeg**, **PostgreSQL** и **Flask** (для пинга и поддержания активности).

---

## 📌 Функционал бота

✅ Скачивает **видео из TikTok без водяных знаков**  
✅ Проверяет **подписку пользователя** на указанный канал  
✅ Обрабатывает видео, чтобы не было растяжений или обрезки (FFmpeg добавляет отступы при необходимости)  
✅ **Хранит статистику**:
- Пользователи (ID, username, дата регистрации)
- Конвертации (ID, статус, время)  
✅ Ограничение размера видео: **50 МБ**  
✅ Команды для админов:
- `/admin` — выгружает статистику пользователей и скачиваний  
✅ Встроенный **Flask-сервер** для пинга (**UptimeRobot**)  
✅ Поддержка PostgreSQL  

---

## 📦 Структура проекта

```
project/
│
├── main.py          # Основной код бота
├── database.py      # Работа с PostgreSQL
├── requirements.txt # Зависимости
├── .env             # Переменные окружения
└── README.md        # Документация (этот файл)
```

---

## 🛠 Требования

- **Python** ≥ 3.9
- **PostgreSQL**
- **FFmpeg**
- **UptimeRobot** (для мониторинга, опционально)
- **Виртуальное окружение (рекомендуется)**

---

## 🔧 Установка и запуск

### 1. Клонировать репозиторий
```bash
git clone https://github.com/Laur1dor/Tik-Tok_Downloader.git
cd Tik-Tok_Downloader
```

### 2. Создать виртуальное окружение и активировать
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Установить зависимости
```bash
pip install -r requirements.txt
```

### 4. Установить FFmpeg
#### Ubuntu / Debian:
```bash
sudo apt update && sudo apt install ffmpeg -y
```
#### Windows:
[Скачать FFmpeg](https://ffmpeg.org/download.html), добавить в `PATH`.

---

## 🗄 Настройка базы данных

### 1. Установить PostgreSQL:
```bash
sudo apt install postgresql postgresql-contrib -y
```

### 2. Создать базу данных и пользователя:
```bash
sudo -u postgres psql
CREATE DATABASE tiktok_bot;
CREATE USER bot_user WITH PASSWORD 'yourpassword';
GRANT ALL PRIVILEGES ON DATABASE tiktok_bot TO bot_user;
\q
```

### 3. В файле `.env` указать параметры:
```env
TOKEN = "ваш_telegram_token"
CHANNEL_USERNAME = "@ваш_канал"

DB_NAME=tiktok_bot
DB_USER=bot_user
DB_PASSWORD=yourpassword
DB_HOST=localhost
DB_PORT=5432
```

---

## ▶️ Запуск бота

```bash
python main.py
```

---

## 🚀 Деплой на VPS (Ubuntu 24.04)

### 1. Установить зависимости:
```bash
sudo apt update
sudo apt install python3-pip ffmpeg postgresql postgresql-contrib -y
```

### 2. Настроить виртуальное окружение и зависимости:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Настроить `.env` и базу данных как выше.

### 4. Запустить с автозапуском (через `systemd`):
Создать файл:
```bash
sudo nano /etc/systemd/system/tiktok-bot.service
```

Вставить:
```
[Unit]
Description=TikTok Telegram Bot
After=network.target

[Service]
User=root
WorkingDirectory=/path/to/project
ExecStart=/path/to/project/venv/bin/python /path/to/project/main.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Активировать:
```bash
sudo systemctl daemon-reload
sudo systemctl enable tiktok-bot
sudo systemctl start tiktok-bot
```

Проверить статус:
```bash
sudo systemctl status tiktok-bot
```

---

## ⚙️ Основные команды бота

- `/start` — Запуск
- `/restart` — Перезапуск
- `/admin` — Статистика (для админов)
- **Ссылка на TikTok** — скачивание видео

---

## 🔒 Проверка подписки

Перед скачиванием бот проверяет, подписан ли пользователь на ваш канал. Если нет:
- Показывает кнопку **«Подписаться»**
- После подписки пользователь нажимает **«Я подписался»**

---

## ✅ Поддерживаемые технологии

- **Python** (Aiogram 3)
- **Flask** (для пинга)
- **yt-dlp** (скачивание TikTok-видео)
- **FFmpeg** (корректировка видео)
- **PostgreSQL** (база данных)

---

## 🛡 Возможные проблемы и решения

### 1. **Ошибка подключения к БД**
- Проверьте `.env`
- Проверьте `systemctl status postgresql`

### 2. **Видео не отправляется**
- Проверьте размер (макс. 50 МБ)
- Проверьте `FFmpeg` в логах output'а

### 3. **Проблема с yt-dlp**
- Обновите:
```bash
pip install -U yt-dlp
```

---

## 🌐 Мониторинг (UptimeRobot)

Добавьте ваш VPS URL с портом 55555:
```
http://ваш_IP:55555/
```
или используйте домен.

---

## 🖼 Обработка видео (FFmpeg)

Бот использует `ffmpeg`:
- Проверяет пропорции видео
- Если не 9:16 — добавляет паддинг
- Сохраняет аудио без перекодирования

---

## 🔍 Логирование

- **INFO** и **ERROR** логи выводятся в консоль
- При деплое можно добавить лог-файл:
```bash
ExecStart=/path/to/venv/bin/python /path/to/main.py >> /var/log/tiktok_bot.log 2>&1
```

---

## 📜 Лицензия
MIT License — свободно используйте и модифицируйте.
