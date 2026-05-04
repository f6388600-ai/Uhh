from aiogram import types
from config import ADMINS
from utils.uploader import upload_handler
import os

def register(dp):

    # 🚀 START
    @dp.message(commands=["start"])
    async def start(msg: types.Message):
        await msg.reply("🤖 Bot Online • Plugin System Active")

    # 📤 UPLOAD (MAIN CMD)
    @dp.message(commands=["upload"])
    async def upload(msg: types.Message):
        if msg.from_user.id not in ADMINS:
            return await msg.reply("❌ Access Denied")

        await upload_handler(msg, dp)

    # 🗑 DELETE PLUGIN
    @dp.message(commands=["delete"])
    async def delete(msg: types.Message):
        if msg.from_user.id not in ADMINS:
            return await msg.reply("❌ Access Denied")

        try:
            name = msg.text.split()[1]
            path = f"plugins/{name}.py"

            if not os.path.exists(path):
                return await msg.reply("❌ Plugin not found")

            os.remove(path)
            await msg.reply(f"🗑 Deleted: {name}")

        except:
            await msg.reply("Usage: /delete plugin_name")

    # 📦 LIST
    @dp.message(commands=["plugins"])
    async def list_plugins(msg: types.Message):
        files = [f[:-3] for f in os.listdir("plugins") if f.endswith(".py")]
        await msg.reply("📦 Active Plugins:\n" + "\n".join(files))
