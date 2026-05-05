import asyncio
import os
import importlib.util
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from flask import Flask
from threading import Thread
from pymongo import MongoClient

# ================= CONFIG =================
BOT_TOKEN = "8701988504:AAHgFsnTkV1n_Q_jv8iE93LSZSTn3OoqBSA"
ADMIN_IDS = [7793812954]

MONGO_URI = "mongodb+srv://f6388600_db_user:<db_password>@cluster0.k7ui3lf.mongodb.net/?appName=Cluster0"

GITHUB_RAW = "https://raw.githubusercontent.com/USERNAME/REPO/main/plugins/"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

client = MongoClient(MONGO_URI)
db = client["bot"]
plugins_db = db["plugins"]

PLUGINS = {}
ROUTERS = {}
UPLOAD_STATE = {}

# ================= KEEP ALIVE =================
app = Flask(__name__)

@app.route("/")
def home():
    return "BOT RUNNING"

def run_web():
    app.run(host="0.0.0.0", port=8080)

def keep_alive():
    Thread(target=run_web).start()

# ================= ADMIN CHECK =================
def is_admin(uid):
    return uid in ADMIN_IDS

# ================= GITHUB FETCH =================
def fetch_plugin(name):
    try:
        url = GITHUB_RAW + name + ".py"
        r = requests.get(url)

        if r.status_code == 200:
            os.makedirs("plugins", exist_ok=True)

            with open(f"plugins/{name}.py", "w", encoding="utf-8") as f:
                f.write(r.text)

            return True
    except:
        pass
    return False

# ================= PLUGIN SYSTEM =================
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

            PLUGINS[name] = module
            ROUTERS[name] = router

            print("Loaded:", name)

    except Exception as e:
        print("Load error:", e)


def unload_plugin(name):
    try:
        if name in ROUTERS:
            try:
                dp._routers.remove(ROUTERS[name])
            except:
                pass

            del ROUTERS[name]
            del PLUGINS[name]
    except:
        pass


def reload_plugin(name):
    unload_plugin(name)
    fetch_plugin(name)
    load_plugin(name)

# ================= LOAD ALL =================
def load_all():
    os.makedirs("plugins", exist_ok=True)

    for file in os.listdir("plugins"):
        if file.endswith(".py"):
            load_plugin(file[:-3])

# ================= START =================
@dp.message(Command("start"))
async def start(msg: types.Message):
    await msg.answer("🤖 BOT ONLINE + PRO ENGINE ACTIVE")

# ================= PLUGINS LIST =================
@dp.message(Command("plugins"))
async def plugins(msg: types.Message):
    data = [p for p in plugins_db.find()]
    names = "\n".join([d["name"] for d in data]) if data else "No plugins"
    await msg.answer(names)

# ================= ENABLE PLUGIN =================
@dp.message(Command("enable"))
async def enable(msg: types.Message):
    if not is_admin(msg.from_user.id):
        return

    try:
        name = msg.text.split()[1]

        plugins_db.update_one(
            {"name": name},
            {"$set": {"name": name}},
            upsert=True
        )

        reload_plugin(name)

        await msg.answer(f"Enabled {name}")

    except:
        await msg.answer("Usage: /enable name")

# ================= DELETE PLUGIN =================
@dp.message(Command("delete"))
async def delete(msg: types.Message):
    if not is_admin(msg.from_user.id):
        return

    try:
        name = msg.text.split()[1]

        plugins_db.delete_one({"name": name})

        unload_plugin(name)

        try:
            os.remove(f"plugins/{name}.py")
        except:
            pass

        await msg.answer(f"Deleted {name}")

    except:
        await msg.answer("Usage: /delete name")

# ================= UPLOAD =================
@dp.message(Command("upload"))
async def upload(msg: types.Message):
    if not is_admin(msg.from_user.id):
        return

    UPLOAD_STATE[msg.from_user.id] = True
    await msg.answer("📤 Send .py plugin file")

@dp.message(lambda m: m.document)
async def file_handler(msg: types.Message):
    if not is_admin(msg.from_user.id):
        return

    if not UPLOAD_STATE.get(msg.from_user.id):
        return

    file = await bot.download(msg.document)
    name = msg.document.file_name

    if not name.endswith(".py"):
        return await msg.answer("Only .py allowed")

    os.makedirs("plugins", exist_ok=True)

    path = f"plugins/{name}"
    with open(path, "wb") as f:
        f.write(file.read())

    plugin_name = name.replace(".py", "")

    reload_plugin(plugin_name)

    UPLOAD_STATE[msg.from_user.id] = False

    await msg.answer(f"Uploaded + Active: {plugin_name}")

# ================= MAIN =================
async def main():
    print("BOT STARTING...")

    keep_alive()
    load_all()

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
