import asyncio
import os
import requests
import importlib.util
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from flask import Flask
from threading import Thread
from pymongo import MongoClient

# ================= CONFIG =================
BOT_TOKEN = "8701988504:AAHgFsnTkV1n_Q_jv8iE93LSZSTn3OoqBSA"
ADMINS = [7793812954]

MONGO_URI = "mongodb+srv://f6388600_db_user:<db_password>@cluster0.k7ui3lf.mongodb.net/?appName=Cluster0"
GITHUB_RAW = "https://raw.githubusercontent.com/USERNAME/REPO/main/plugins/"

# ================= INIT =================
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

client = MongoClient(MONGO_URI)
db = client["bot"]
plugins_db = db["plugins"]

PLUGINS = {}
PLUGIN_ROUTERS = {}
UPLOAD_STATE = {}

# ================= KEEP ALIVE =================
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot Running ☠️"

def run_web():
    app.run(host="0.0.0.0", port=8080)

def keep_alive():
    Thread(target=run_web).start()

# ================= SECURITY =================
def is_admin(uid):
    return uid in ADMINS

# ================= GITHUB =================
def fetch_plugin(name):
    try:
        url = GITHUB_RAW + name + ".py"
        r = requests.get(url, timeout=10)

        if r.status_code == 200:
            os.makedirs("plugins", exist_ok=True)
            with open(f"plugins/{name}.py", "w", encoding="utf-8") as f:
                f.write(r.text)
            return True
    except:
        pass
    return False

# ================= HOT RELOAD ENGINE =================
def unload_plugin(name):
    try:
        if name in PLUGIN_ROUTERS:
            router = PLUGIN_ROUTERS[name]

            if router in dp._routers:
                dp._routers.remove(router)

            del PLUGIN_ROUTERS[name]

        if name in PLUGINS:
            del PLUGINS[name]

    except Exception as e:
        print("Unload error:", e)

def load_plugin(name):
    try:
        path = f"plugins/{name}.py"

        if not os.path.exists(path):
            return

        spec = importlib.util.spec_from_file_location(name, path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        if hasattr(module, "setup"):
            router = module.setup()
            dp.include_router(router)

            PLUGIN_ROUTERS[name] = router
            PLUGINS[name] = module

            print("Loaded:", name)

    except Exception as e:
        print("Load error:", name, e)

def reload_plugin(name):
    unload_plugin(name)
    fetch_plugin(name)
    load_plugin(name)

# ================= LOAD ALL =================
def load_all_plugins():
    os.makedirs("plugins", exist_ok=True)

    for p in plugins_db.find():
        name = p["name"]
        fetch_plugin(name)
        load_plugin(name)

# ================= COMMANDS =================

@dp.message(Command("start"))
async def start(msg: types.Message):
    await msg.answer("🤖 FULL BOT ONLINE\n⚡ PRO ENGINE ACTIVE")

@dp.message(Command("plugins"))
async def plugins(msg: types.Message):
    data = [p["name"] for p in plugins_db.find()]
    await msg.answer("📦 Plugins:\n" + "\n".join(data) if data else "No plugins")

@dp.message(Command("enable"))
async def enable(msg: types.Message):
    if not is_admin(msg.from_user.id):
        return await msg.answer("❌ Not allowed")

    try:
        name = msg.text.split()[1]

        plugins_db.update_one(
            {"name": name},
            {"$set": {"name": name}},
            upsert=True
        )

        reload_plugin(name)

        await msg.answer(f"✅ Enabled: {name}")

    except:
        await msg.answer("Usage: /enable name")

@dp.message(Command("delete"))
async def delete(msg: types.Message):
    if not is_admin(msg.from_user.id):
        return await msg.answer("❌ Not allowed")

    try:
        name = msg.text.split()[1]

        plugins_db.delete_one({"name": name})

        if os.path.exists(f"plugins/{name}.py"):
            os.remove(f"plugins/{name}.py")

        unload_plugin(name)

        await msg.answer(f"🗑 Deleted: {name}")

    except:
        await msg.answer("Usage: /delete name")

# -------- UPLOAD FLOW --------
@dp.message(Command("upload"))
async def upload_start(msg: types.Message):
    if not is_admin(msg.from_user.id):
        return await msg.answer("❌ Not allowed")

    UPLOAD_STATE[msg.from_user.id] = True
    await msg.answer("📤 Send cmd file (.py)")

@dp.message(lambda m: m.document)
async def receive_file(msg: types.Message):
    if not is_admin(msg.from_user.id):
        return

    if not UPLOAD_STATE.get(msg.from_user.id):
        return

    file = await bot.download(msg.document)
    name = msg.document.file_name

    if not name.endswith(".py"):
        return await msg.answer("❌ Only .py file")

    os.makedirs("plugins", exist_ok=True)

    path = f"plugins/{name}"
    with open(path, "wb") as f:
        f.write(file.read())

    plugin_name = name.replace(".py", "")

    plugins_db.update_one(
        {"name": plugin_name},
        {"$set": {"name": plugin_name}},
        upsert=True
    )

    reload_plugin(plugin_name)

    UPLOAD_STATE[msg.from_user.id] = False

    await msg.answer(f"""
✅ Plugin Uploaded
📄 {name}
⚡ Live Activated
""")

# ================= MAIN =================
async def main():
    print("🚀 BOT STARTING...")

    load_all_plugins()
    keep_alive()

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
