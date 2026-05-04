import asyncio
import os
import importlib
import traceback
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from flask import Flask
from threading import Thread

# ================= CONFIG =================
BOT_TOKEN = "8701988504:AAEMPtTE9elGanTZ-wYufGlpcF7hC8yMH-k"
ADMINS = [7793812954]

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

PLUGINS = {}

# ================= KEEP ALIVE =================
app = Flask(__name__)

@app.route("/")
def home():
    return "V5 Bot Alive ☠️"

def run_web():
    app.run(host="0.0.0.0", port=8080)

def keep_alive():
    Thread(target=run_web).start()

# ================= SECURITY =================
def is_admin(uid):
    return uid in ADMINS

# ================= CORE PLUGIN ENGINE =================
def load_all_plugins():
    if not os.path.exists("plugins"):
        os.mkdir("plugins")

    for file in os.listdir("plugins"):
        if file.endswith(".py"):
            name = file[:-3]
            load_plugin(name)

def load_plugin(name):
    try:
        path = f"plugins/{name}.py"
        module = {}

        with open(path, "r", encoding="utf-8") as f:
            code = f.read()

        exec(code, module)
        PLUGINS[name] = module

    except Exception as e:
        print(f"Plugin load error: {name}", e)

def reload_plugin(name):
    try:
        if name in PLUGINS:
            del PLUGINS[name]
        load_plugin(name)
    except:
        pass

# ================= COMMANDS =================

@dp.message(Command("start"))
async def start(msg: types.Message):
    await msg.answer("🤖 V5 BOT ONLINE\n⚡ Ultra Engine Active ☠️")

@dp.message(Command("plugins"))
async def plugins(msg: types.Message):
    files = [f[:-3] for f in os.listdir("plugins") if f.endswith(".py")]
    await msg.answer("📦 Plugins:\n" + "\n".join(files))

# -------- UPLOAD --------
@dp.message(Command("upload"))
async def upload(msg: types.Message):
    if not is_admin(msg.from_user.id):
        return await msg.answer("❌ Not allowed")

    if not msg.document:
        return await msg.answer("📎 Send .py file")

    file = await bot.download(msg.document)
    name = msg.document.file_name

    if not name.endswith(".py"):
        return await msg.answer("❌ Only .py allowed")

    path = f"plugins/{name}"

    try:
        with open(path, "wb") as f:
            f.write(file.read())

        reload_plugin(name[:-3])

        await msg.answer(f"""
✅ Plugin Installed
📄 {name}
⚡ Live Activated
""")

    except:
        await msg.answer("❌ Upload Failed")

# -------- DELETE --------
@dp.message(Command("delete"))
async def delete(msg: types.Message):
    if not is_admin(msg.from_user.id):
        return await msg.answer("❌ Not allowed")

    try:
        name = msg.text.split()[1]
        path = f"plugins/{name}.py"

        if os.path.exists(path):
            os.remove(path)
            PLUGINS.pop(name, None)
            await msg.answer(f"🗑 Deleted: {name}")
        else:
            await msg.answer("❌ Not found")

    except:
        await msg.answer("Usage: /delete name")

# ================= ERROR HANDLER =================
@dp.errors()
async def error_handler(update, exception):
    print("ERROR:", exception)
    traceback.print_exc()

# ================= MAIN =================
async def main():
    print("🚀 V5 BOT STARTING...")

    load_all_plugins()
    keep_alive()

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
