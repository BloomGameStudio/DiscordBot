# -*- coding: UTF-8 -*-
import discord, asyncio, os
from dotenv import load_dotenv
from discord.ext import commands, tasks
from controllers.appearance_manager import *
from controllers.command_manager import *
from controllers.data_manager import *
from controllers.settings import *

class DiscordClient(discord.Client):
    __command_manager = CommandManager()
    __appearance_manager = AppearanceManager()
    __data_manager = DataManager()
    __settings = Settings()
    __bot_user = None

    async def on_ready(self):
        print('Logged in as\n{0}\n{1}\n------'.format(self.user.name,self.user.id))
        # self.__appearance_manager.load_settings(self.__settings)
        self.__assign_bot_user()
        # await self.__refresh_name()
        # await self.start_looped_info()

    #received message
    async def on_message(self, message):
        await self.__command_manager.process_message_as_command(message,self.__data_manager,self.__settings)

    async def on_member_join(self,member):
        await self.__command_manager.process_new_member(member,self.__general_channel,self.__rules_channel)

    async def on_raw_reaction_add(self, payload):
        if payload.message_id == RULES_MESSAGE_ID:
            await self.__command_manager.process_reaction_add(payload, self.__general_channel)

    def __assign_bot_user(self):
        for guild in self.guilds:
            if guild.name.startswith(GUILD_TRIGGER):
                for member in guild.members:
                    if member.id == self.user.id:
                        self.__bot_user = member
                        return

    @property
    def __rules_channel(self):
        for guild in self.guilds:
            if guild.name.startswith(GUILD_TRIGGER):
                for channel in guild.channels:
                    if "rules" in channel.name:
                        return channel
        return None

    @property
    def __general_channel(self):
        for guild in self.guilds:
            if guild.name.startswith(GUILD_TRIGGER):
                for channel in guild.channels:
                    if "general" in channel.name:
                        return channel
        return None



    # async def start_looped_info(self):
    #     self.loop.create_task(self.start_looping_status())
    #     self.loop.create_task(self.start_looping_requests())

    # async def start_looping_status(self):
    #     while True:
    #         await self.__refresh_status()
    #         await asyncio.sleep(self.__settings.cycle_length)

    # async def start_looping_requests(self):
    #     while True:
    #         self.__data_manager.update_all_token_prices()
    #         await self.__refresh_name()
    #         await asyncio.sleep(self.__settings.request_frequency)

    # async def start_looping_ens_requests(self):
    #     while True:
    #         await self.__data_manager.load_ens()
    #         await asyncio.sleep(2000)

    # async def start_looping_nft_requests(self):
    #     while True:
    #         await self.__data_manager.get_collections()
    #         await asyncio.sleep(2000)




    async def __refresh_name(self):
        await self.__appearance_manager.refresh_title_state(self,self.__data_manager,self.__bot_user,self.__settings)
        new_momentum = self.__data_manager.token_manager.bitcoin.price_momentum
        if not self.__settings.momentum == new_momentum:
            self.__settings.update_momentum(new_momentum)

    async def __refresh_status(self):
        await self.__appearance_manager.refresh_status(self,self.__data_manager,self.__bot_user,self.__settings)






load_dotenv()
bot_key = os.getenv('DISCORD_BOT_KEY')
if bot_key:
    intents = discord.Intents.default()
    intents.messages = True
    intents.reactions = True
    intents.members = True
    client = DiscordClient(intents=intents)
    client.run(bot_key)
else:
    print("Bot key is missing")