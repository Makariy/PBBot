import asyncio
import random

from telegram import Update, InputMediaPhoto
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters

from services.database.services import *
from services.extern.loader import load_file_data


class PBBot:
    def __init__(self, token: str):
        self.chat_id = None
        self.application = ApplicationBuilder().token(token).build()
        self.application.add_handler(CommandHandler("start", self.command_start))
        self.application.add_handler(CommandHandler("set", self.command_set_interval))
        self.interval = 60 * 60

    def start(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        self.application.run_polling(close_loop=False)

    def _pick_random_model(self, models: List[OFModel]):
        return random.choice(models)

    async def _send_pics(self, context: ContextTypes.DEFAULT_TYPE,
                        model: OFModel,
                        images: List[Image]):
        await context.bot.send_media_group(
            chat_id=context.job.chat_id,
            media=[
                InputMediaPhoto(load_file_data(image.file))
                for image in images[:10]
            ]
        )

    async def send_pics(self, context: ContextTypes.DEFAULT_TYPE):
        model = self._pick_random_model(await get_all_ofmodels())
        await context.bot.send_message(
            context.job.chat_id,
            rf"Кидаю {model.name}",
        )
        await self._send_pics(context, model, await get_images_by_model(model))

    async def command_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        context.job_queue.run_once(self.send_pics, 0, chat_id=update.effective_message.chat_id)
        context.job_queue.run_repeating(self.send_pics, self.interval, chat_id=update.effective_message.chat_id)

    async def set_interval(self, number: int):
        self.interval = number * 60

    async def command_set_interval(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            await self.set_interval(int(context.args[0]))
        except (IndexError, ValueError):
            await update.effective_message.reply_text("Usage: /set <time in seconds>")


