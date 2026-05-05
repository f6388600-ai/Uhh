import os
import asyncio
import importlib
import traceback
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, FSInputFile
from aiogram.filters import Command
from aiogram.enums import ParseMode

# ===================== CONFIG =====================
BOT_TOKEN = os.getenv("BOT_TOKEN", "8701988504:AAHgFsnTkV1n_Q_jv8iE93LSZSTn3OoqBSA)
ADMIN_ID = int(os.getenv("ADMIN_ID", "7793812954"))

PLUGIN_FOLDER = "plugins"
LOG_FILE = "bot.log"

# ===================== INIT =====================
bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()

plugins = {}
plugin_status = {}

# ===================== LOGGER =====================
def log(text: str):
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(text + "\n")
    print(text)

# ===================== SECURITY =====================
def is_admin(user_id: int):
    return user_id == ADMIN_ID

# ===================== PLUGIN SYSTEM =====================
def load_plugins():
    global plugins, plugin_status
    plugins = {}

    if not os.path.exists(PLUGIN_FOLDER):
        os.makedirs(PLUGIN_FOLDER)

    for file in os.listdir(PLUGIN_FOLDER):
        if file.endswith(".py"):
            name = file[:-3]
            try:
                module = importlib.import_module(f"{PLUGIN_FOLDER}.{name}")
                importlib.reload(module)

                if hasattr(module, "setup"):
                    module.setup(dp, bot)

                plugins[name] = module
                plugin_status[name] = True
                log(f"[PLUGIN LOADED] {name}")

            except Exception as e:
                log(f"[PLUGIN ERROR] {name} -> {e}")

def reload_plugins():
    global plugins
    try:
        importlib.invalidate_caches()
        load_plugins()
        return True
    except Exception as e:
        log(f"[RELOAD ERROR] {e}")
        return False

# ===================== START =====================
@dp.message(Command("start"))
async def start(msg: Message):
    await msg.answer("🤖 Bot is running!\nUse /help")

# ===================== HELP =====================
@dp.message(Command("help"))
async def help_cmd(msg: Message):
    await msg.answer(
        "📌 Commands:\n"
        "/upload - upload plugin file (admin)\n"
        "/plugins - list plugins\n"
        "/reload - reload plugins\n"
        "/logs - view logs"
    )

# ===================== UPLOAD SYSTEM =====================
@dp.message(Command("upload"))
async def upload_cmd(msg: Message):
    if not is_admin(msg.from_user.id):
        return await msg.answer("❌ Not allowed")

    await msg.answer("📤 Send a .py plugin file")

@dp.message(F.document)
async def handle_upload(msg: Message):
    if not is_admin(msg.from_user.id):
        return

    file = msg.document
    if not file.file_name.endswith(".py"):
        return await msg.answer("❌ Only .py files allowed")

    path = os.path.join(PLUGIN_FOLDER, file.file_name)

    await bot.download(file, destination=path)

    await msg.answer("⚙️ Installing plugin...")

    try:
        reload_plugins()
        await msg.answer(f"✅ Plugin installed: {file.file_name}")
    except Exception as e:
        await msg.answer(f"❌ Error: {e}")

# ===================== PLUGINS LIST =====================
@dp.message(Command("plugins"))
async def list_plugins(msg: Message):
    if not is_admin(msg.from_user.id):
        return

    text = "🧩 Plugins:\n"
    for p, status in plugin_status.items():
        text += f"- {p} : {'🟢' if status else '🔴'}\n"

    await msg.answer(text)

# ===================== RELOAD =====================
@dp.message(Command("reload"))
async def reload_cmd(msg: Message):
    if not is_admin(msg.from_user.id):
        return

    ok = reload_plugins()
    if ok:
        await msg.answer("🔄 Plugins reloaded")
    else:
        await msg.answer("❌ Reload failed")

# ===================== LOGS =====================
@dp.message(Command("logs"))
async def logs_cmd(msg: Message):
    if not is_admin(msg.from_user.id):
        return

    if not os.path.exists(LOG_FILE):
        return await msg.answer("No logs yet")

    with open(LOG_FILE, "rb") as f:
        await msg.answer_document(FSInputFile(LOG_FILE))

# ===================== HOT RELOAD WATCHER =====================
async def watcher():
    last_state = set()

    while True:
        try:
            current = set(os.listdir(PLUGIN_FOLDER))
            if current != last_state:
                reload_plugins()
                last_state = current
                log("[HOT RELOAD] changes detected")

        except Exception as e:
            log(f"[WATCHER ERROR] {e}")

        await asyncio.sleep(5)

# ===================== ERROR HANDLER =====================
@dp.errors()
async def error_handler(update, exception):
    err = traceback.format_exc()
    log(f"[BOT ERROR]\n{err}")
    return True

# ===================== MAIN =====================
async def main():
    log("Bot starting...")

    load_plugins()
    asyncio.create_task(watcher())

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
