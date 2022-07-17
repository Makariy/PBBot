import asyncio
import random
from uuid import uuid4

import telegram
from telegram import Update, InputMediaPhoto, InlineQueryResultArticle, InputTextMessageContent
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, InlineQueryHandler

from services.database.services import *
from services.extern.loader import load_file_data


class PBBot:
    def __init__(self, token: str):
        self.chat_id = None
        self.application = ApplicationBuilder().token(token).build()
        self.application.add_handler(CommandHandler("start", self.command_start))
        self.application.add_handler(CommandHandler("stop", self.command_stop))
        self.application.add_handler(CommandHandler("set", self.command_set_interval))
        self.application.add_handler(CommandHandler("model", self.command_model))
        self.application.add_handler(InlineQueryHandler(self.command_list_models))
        self.interval = 60 * 60
        self.job = None

    def start(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        self.application.run_polling(close_loop=False)

    def _pick_random_model(self, models: List[OFModel]):
        return random.choice(models)

    async def _send_pics(self, bot: telegram.Bot,
                        chat_id: int,
                        images: List[Image]):
        await bot.send_media_group(
            chat_id=chat_id,
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
        await self._send_pics(context.bot, context.job.chat_id, await get_images_by_model(model))

    async def command_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        context.job_queue.run_once(self.send_pics, 0, chat_id=update.effective_message.chat_id)
        self.job = context.job_queue.run_repeating(self.send_pics, self.interval, chat_id=update.effective_message.chat_id)

    async def command_stop(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        self.job.job.remove()

    async def set_interval(self, number: int):
        self.interval = number * 60

    async def command_set_interval(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            await self.set_interval(int(context.args[0]))
            self.job.job.remove()
            self.job = context.job_queue.run_repeating(self.send_pics, self.interval,
                                                       chat_id=update.effective_message.chat_id)

        except (IndexError, ValueError):
            await update.effective_message.reply_text("Usage: /set <time in seconds>")

    async def command_list_models(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        name = update.inline_query.query
        models = await get_all_ofmodels(name)
        model_names = [model.name for model in models]

        results = [
            InlineQueryResultArticle(
                id=str(uuid4()),
                title=name,
                input_message_content=InputTextMessageContent("/model " + name),
            ) for name in model_names[:10]
        ]
        await update.inline_query.answer(results)

    async def command_model(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        bot = update.effective_chat.get_bot()
        chat_id = update.effective_message.chat_id
        model_name = " ".join(context.args)
        model = await get_ofmodel_by_name(model_name)
        if model is None:
            await bot.send_message(chat_id=chat_id, text="Не удаётся найти такую модель, программист идиот, (или ты...)")
            return
        images = await get_images_by_model(model)
        await self._send_pics(bot, chat_id, images)

