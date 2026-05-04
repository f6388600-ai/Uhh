from aiogram import types
import asyncio, os
from loader import reload_plugin
from utils.parser import extract_commands
from utils.logger import logger

async def upload_handler(message: types.Message, dp):

    msg = await message.reply("📤 Initializing upload...")

    for step in ["Checking file...", "Validating...", "Extracting data..."]:
        await asyncio.sleep(0.7)
        await msg.edit_text(f"⏳ {step}")

    if not message.document:
        return await msg.edit_text("❌ No file detected")

    file = await message.bot.download(message.document)
    filename = message.document.file_name

    if not filename.endswith(".py"):
        return await msg.edit_text("❌ Only .py plugins allowed")

    path = f"plugins/{filename}"

    with open(path, "wb") as f:
        f.write(file.read())

    code = open(path).read()
    cmds = extract_commands(code)

    info = f"""
✅ Plugin Uploaded

📄 File: {filename}
⚡ Commands: {", ".join(cmds) if cmds else "None"}
📦 Size: {round(len(code)/1024,2)} KB
"""

    await msg.edit_text(info)

    # 🔄 HOT LOAD (NO RESTART)
    name = filename.replace(".py", "")
    reload_plugin(name, dp)

    logger.info(f"Uploaded & Loaded: {filename}")
