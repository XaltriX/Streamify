# (©)NextGenBotz

from aiohttp import web
from plugins import web_server

import pyromod.listen
import pyrogram
from pyrogram import Client
from pyrogram.enums import ParseMode
import sys
from datetime import datetime

from config import API_HASH, APP_ID, LOGGER, TG_BOT_TOKEN, TG_BOT_WORKERS, FORCE_SUB_CHANNEL, FORCE_SUB_CHANNEL2, CHANNEL_ID, PORT

# Minimum IDs adjust for pyrogram
pyrogram.utils.MIN_CHAT_ID = -999999999999
pyrogram.utils.MIN_CHANNEL_ID = -100999999999999


class Bot(Client):
    def __init__(self):
        super().__init__(
            name="Bot",
            api_hash=API_HASH,
            api_id=APP_ID,
            plugins={"root": "plugins"},
            workers=TG_BOT_WORKERS,
            bot_token=TG_BOT_TOKEN
        )
        self.LOGGER = LOGGER

    async def start(self):
        try:
            await super().start()
            usr_bot_me = await self.get_me()
            self.uptime = datetime.now()

            # Handle Force Subscription for first channel
            if FORCE_SUB_CHANNEL:
                try:
                    link = (await self.get_chat(FORCE_SUB_CHANNEL)).invite_link
                    if not link:
                        await self.export_chat_invite_link(FORCE_SUB_CHANNEL)
                        link = (await self.get_chat(FORCE_SUB_CHANNEL)).invite_link
                    self.invitelink = link
                except Exception as error:
                    self.LOGGER(__name__).warning(f"Error while getting invite link for {FORCE_SUB_CHANNEL}: {error}")
                    self.LOGGER(__name__).warning("Bot can't Export Invite link from Force Sub Channel!")
                    self.LOGGER(__name__).warning(f"Check FORCE_SUB_CHANNEL value and bot permissions, Current Value: {FORCE_SUB_CHANNEL}")
                    self.LOGGER(__name__).info("\nBot Stopped. Join https://t.me/nextgenbotz for support")
                    sys.exit()

            # Handle Force Subscription for second channel
            if FORCE_SUB_CHANNEL2:
                try:
                    link = (await self.get_chat(FORCE_SUB_CHANNEL2)).invite_link
                    if not link:
                        await self.export_chat_invite_link(FORCE_SUB_CHANNEL2)
                        link = (await self.get_chat(FORCE_SUB_CHANNEL2)).invite_link
                    self.invitelink2 = link
                except Exception as error:
                    self.LOGGER(__name__).warning(f"Error while getting invite link for {FORCE_SUB_CHANNEL2}: {error}")
                    self.LOGGER(__name__).warning("Bot can't Export Invite link from Force Sub Channel 2!")
                    self.LOGGER(__name__).warning(f"Check FORCE_SUB_CHANNEL2 value and bot permissions, Current Value: {FORCE_SUB_CHANNEL2}")
                    self.LOGGER(__name__).info("\nBot Stopped. Join https://t.me/nextgenbotz for support")
                    sys.exit()

            # Validate DB Channel
            try:
                db_channel = await self.get_chat(CHANNEL_ID)
                self.db_channel = db_channel
                test = await self.send_message(chat_id=db_channel.id, text="Test Message")
                await test.delete()
            except Exception as error:
                self.LOGGER(__name__).warning(f"Error while checking DB Channel with ID {CHANNEL_ID}: {error}")
                self.LOGGER(__name__).warning("Ensure bot is Admin in DB Channel.")
                self.LOGGER(__name__).info("\nBot Stopped. Join https://t.me/nextgenbotz for support")
                sys.exit()

            self.set_parse_mode(ParseMode.HTML)
            self.LOGGER(__name__).info(f"Bot Running Successfully!\n\nCreated by\nhttps://t.me/nextgenbotz")
            self.LOGGER(__name__).info(
                """
███╗░░██╗███████╗██╗░░██╗████████╗░██████╗░███████╗███╗░░██╗██████╗░░█████╗░████████╗███████╗
████╗░██║██╔════╝╚██╗██╔╝╚══██╔══╝██╔════╝░██╔════╝████╗░██║██╔══██╗██╔══██╗╚══██╔══╝╚════██║
██╔██╗██║█████╗░░░╚███╔╝░░░░██║░░░██║░░██╗░█████╗░░██╔██╗██║██████╦╝██║░░██║░░░██║░░░░░███╔═╝
██║╚████║██╔══╝░░░██╔██╗░░░░██║░░░██║░░╚██╗██╔══╝░░██║╚████║██╔══██╗██║░░██║░░░██║░░░██╔══╝░░
██║░╚███║███████╗██╔╝╚██╗░░░██║░░░╚██████╔╝███████╗██║░╚███║██████╦╝╚█████╔╝░░░██║░░░███████╗
╚═╝░░╚══╝╚══════╝╚═╝░░╚═╝░░░╚═╝░░░░╚═════╝░╚══════╝╚═╝░░╚══╝╚═════╝░░╚════╝░░░░╚═╝░░░╚══════╝
            """
            )
            self.username = usr_bot_me.username

            # Start web server
            app = web.AppRunner(await web_server())
            await app.setup()
            bind_address = "0.0.0.0"
            await web.TCPSite(app, bind_address, PORT).start()

        except Exception as error:
            self.LOGGER(__name__).error(f"Error while starting the bot: {error}")
            sys.exit("Bot initialization failed. Please check logs for details.")

    async def stop(self, *args):
        try:
            await super().stop()
            self.LOGGER(__name__).info("Bot stopped successfully.")
        except Exception as error:
            self.LOGGER(__name__).error(f"Error while stopping the bot: {error}")
