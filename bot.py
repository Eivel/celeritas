import logging
import telegram
from dotenv import load_dotenv
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler
from mods.channel_travel import ChannelTravel
from config.provider import TelegramConfig, ChannelTravelConfig


load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def error(update, context):
    logger.exception('Update "%s" caused error "%s"', update, context.error)


def main():
    telegram_config = TelegramConfig()
    ct_config = ChannelTravelConfig()

    logger.info("Bootstrapping bot with session '%s'", telegram_config.telegram_api_session_name)

    bot = telegram.Bot(token=telegram_config.bot_token)
    logger.info("Authenticated bot user: %s", bot.get_me().username)

    updater = Updater(token=telegram_config.bot_token, use_context=True)

    channel_travel = ChannelTravel(telegram_config, ct_config)

    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler('channels', channel_travel.command_channels))
    dispatcher.add_handler(CallbackQueryHandler(channel_travel.callback_channels))
    dispatcher.add_error_handler(error)

    logger.info("Starting polling loop")
    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
