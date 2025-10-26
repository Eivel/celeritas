import asyncio
import logging
import threading
from telethon import TelegramClient
from telethon.tl.functions.messages import AddChatUserRequest
from telethon.tl.functions.channels import InviteToChannelRequest
from telethon.errors import ChatAdminRequiredError, UserAdminInvalidError
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from config.provider import TelegramConfig, ChannelTravelConfig

class ChannelTravel():
    MODULE_PREFIX = "channel_travel::"

    def __init__(self, telegram_config: TelegramConfig, ct_config: ChannelTravelConfig):
        self.logger = logging.getLogger(__name__)
        self.channels = ct_config.channels
        self.ids = ct_config.whitelist
        self.message_text = ct_config.message
        self.telegram_client = TelegramClient(
            telegram_config.telegram_api_session_name,
            telegram_config.telegram_api_id,
            telegram_config.telegram_api_hash
        )
        self.logger.info("Starting Telethon client for session '%s'", telegram_config.telegram_api_session_name)
        self.telegram_client.start()
        self.loop = self.telegram_client.loop
        me = self.loop.run_until_complete(self.telegram_client.get_me())
        identity = f"@{me.username}" if getattr(me, "username", None) else me.id
        self.logger.info("Telethon client authenticated as %s", identity)
        self._loop_ready = threading.Event()
        self.loop_thread = threading.Thread(target=self._loop_worker, name="telethon-loop", daemon=True)
        self.loop_thread.start()
        if not self._loop_ready.wait(timeout=30):
            raise RuntimeError("Telethon event loop thread failed to start within timeout")
        self.logger.info("Loaded %d channels and %d whitelisted users", len(self.channels), len(self.ids))

    def _loop_worker(self):
        asyncio.set_event_loop(self.loop)
        self._loop_ready.set()
        self.logger.info("Telethon loop thread running")
        try:
            self.loop.run_forever()
        finally:
            self.logger.info("Telethon loop thread exiting")

    def command_channels(self, update, context):
        user_id = update.message.from_user.id
        self.logger.info("Received /channels from user_id=%s chat_id=%s chat_type=%s", user_id, update.message.chat.id, update.message.chat.type)
        if not update.message.from_user.id in self.ids:
            self.logger.warning("Unauthorized /channels attempt by user_id=%s", user_id)
            update.message.reply_text("Nie masz uprawnień do korzystania z tej komendy.")
            return

        if update.message.chat.type != "private":
            self.logger.info("Ignored /channels from non-private chat_id=%s", update.message.chat.id)
            update.message.reply_text("Zapytaj mnie o kanały na PW: @DraconisCeleritasBot")
            return

        keyboard = []
        for c in self.channels:
            channel_name = c["name"]
            channel_id = c["id"]
            buttons = [
                InlineKeyboardButton(f"{channel_name}", callback_data="blep"),
                InlineKeyboardButton(f"+", callback_data=f"{self.MODULE_PREFIX}join_{channel_id}"),
                InlineKeyboardButton(f"-", callback_data=f"{self.MODULE_PREFIX}leave_{channel_id}")
            ]
            keyboard.append(buttons)

        reply_markup = InlineKeyboardMarkup(keyboard)

        self.logger.info("Sending channel dashboard to user_id=%s", user_id)
        update.message.reply_text(self.message_text, reply_markup=reply_markup, parse_mode="markdown")


    def callback_channels(self, update, context):
        user_id = update.callback_query.from_user.id
        query = update.callback_query
        self.logger.info("Received callback '%s' from user_id=%s", query.data, user_id)

        if not user_id in self.ids:
            self.logger.warning("Unauthorized callback attempt by user_id=%s", user_id)
            return

        if not query.data.startswith(self.MODULE_PREFIX):
            self.logger.info("Ignoring callback without module prefix: %s", query.data)
            return

        _, query_data = query.data.split('::')
        instruction, chat_id = query_data.split("_")

        if instruction == 'join':
            self.logger.info("Processing join for user_id=%s chat_id=%s", user_id, chat_id)
            future = asyncio.run_coroutine_threadsafe(self._invite_to_channel(chat_id, user_id), self.loop)
            try:
                invited = future.result()
                if invited:
                    self.logger.info("Invite request completed for user_id=%s chat_id=%s", user_id, chat_id)
                else:
                    self.logger.info("User_id=%s already joined chat_id=%s", user_id, chat_id)
            except Exception as exc:
                self.logger.exception("Failed to invite user_id=%s to chat_id=%s: %s", user_id, chat_id, exc)
        else:
            self.logger.info("Processing leave for user_id=%s chat_id=%s", user_id, chat_id)
            future = asyncio.run_coroutine_threadsafe(self._remove_from_channel(chat_id, user_id), self.loop)
            try:
                removal_result = future.result()
                if removal_result == "removed":
                    self.logger.info("Removal via Telethon succeeded for user_id=%s chat_id=%s", user_id, chat_id)
                elif removal_result == "not_found":
                    self.logger.info("User_id=%s already absent from chat_id=%s", user_id, chat_id)
                elif removal_result == "needs_bot":
                    self.logger.info("Falling back to Bot API kick for user_id=%s chat_id=%s", user_id, chat_id)
                    try:
                        context.bot.kick_chat_member(chat_id=int(chat_id), user_id=user_id)
                        self.logger.info("Bot API kick succeeded for user_id=%s chat_id=%s", user_id, chat_id)
                    except Exception as exc:
                        self.logger.exception("Bot API kick failed for user_id=%s chat_id=%s: %s", user_id, chat_id, exc)
                else:
                    self.logger.warning("Unexpected removal result '%s' for user_id=%s chat_id=%s", removal_result, user_id, chat_id)
            except Exception as exc:
                self.logger.exception("Failed to remove user_id=%s from chat_id=%s: %s", user_id, chat_id, exc)


    async def _invite_to_channel(self, chat_id, user_id):
        participants = await self.telegram_client.get_participants(int(chat_id))
        if user_id not in [o.id for o in participants]:
            group = await self.telegram_client.get_entity(int(chat_id))
            if group.__class__.__name__ == 'Channel':
                self.logger.info("Inviting user_id=%s to channel_id=%s", user_id, chat_id)
                await self.telegram_client(InviteToChannelRequest(group, [user_id]))
            else:
                self.logger.info("Adding user_id=%s to chat_id=%s", user_id, chat_id)
                await self.telegram_client(AddChatUserRequest(group, user_id, fwd_limit=10))
            return True
        else:
            self.logger.info("User_id=%s already present in chat_id=%s", user_id, chat_id)
        return False

    async def _remove_from_channel(self, chat_id, user_id):
        participants = await self.telegram_client.get_participants(int(chat_id))
        if user_id not in [o.id for o in participants]:
            self.logger.info("User_id=%s not found in chat_id=%s; skipping kick", user_id, chat_id)
            return "not_found"

        try:
            await self.telegram_client.kick_participant(int(chat_id), user_id)
            return "removed"
        except (ChatAdminRequiredError, UserAdminInvalidError) as exc:
            self.logger.warning("Telethon account lacks rights to remove user_id=%s from chat_id=%s: %s", user_id, chat_id, exc)
            return "needs_bot"
