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
        self.application.add_handler(CommandHandler("models", self.command_models))
        self.application.add_handler(CommandHandler("help", self.command_help))
        self.application.add_handler(InlineQueryHandler(self.inline_list_models))

        self.interval = 60 * 60

    def start(self):
        self.application.run_polling(close_loop=False)

    def _pick_random_model(self, models: List[OFModel]):
        return random.choice(models)

    async def _send_pics(self, bot: telegram.Bot,
                        chat_id: int,
                        images: List[Image]):
        _images = list(images)
        random.shuffle(_images)
        await bot.send_media_group(
            chat_id=chat_id,
            media=[
                InputMediaPhoto(load_file_data(image.file))
                for image in _images[:10]
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

    async def purge_jobs(self, context: ContextTypes.DEFAULT_TYPE):
        jobs = context.job_queue.jobs()
        if len(jobs) > 0:
            jobs[0].job.remove()

    async def command_stop(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await self.purge_jobs(context)

    async def set_interval(self, number: float):
        self.interval = number * 60

    async def command_set_interval(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            await self.set_interval(float(context.args[0]))
            await self.purge_jobs(context)
            if self.job is not None:
                self.job.job.remove()
            context.job_queue.run_repeating(self.send_pics, self.interval,
                                                       chat_id=update.effective_message.chat_id)

        except (IndexError, ValueError):
            await update.effective_message.reply_text("Usage: /set <time in seconds>")

    async def inline_list_models(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
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

    async def command_models(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        bot = update.effective_chat.get_bot()
        chat_id = update.effective_message.chat_id
        models = await get_all_ofmodels()
        await bot.send_message(chat_id=chat_id, text="\n".join([model.name for model in models]))

    async def command_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.effective_message.reply_text(
            text="""
Используйте следующие команды для взаимодействия с ботом, приятных ощущений.
/help - показать это сообщение 
/start - начать отправку моделей
/stop - прекратить отправку моделей
/set <время> - установить период отправки моделей в секундах
@<Имя бота> <имя> - отправить модель по имени  
            """
        )

