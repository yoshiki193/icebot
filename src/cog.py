import discord
from discord.ext import commands
import json
import logging

logging.basicConfig(
    level = logging.INFO,
    format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers = [
        logging.StreamHandler()
    ]
)

logger = logging.getLogger('discord')
logger.setLevel(logging.INFO)

class command(commands.Cog):
    def __init__(self, bot:commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message:discord.Message):
        if message.author != self.bot.user:
            with open('data.json') as f:
                data:dict = json.load(f)              
            if str(message.channel.id) in [i for i in data['announcement']]:
                last_message = await message.channel.fetch_message(data['announcement'][str(message.channel.id)]['messageId'])
                await last_message.delete()
                send_message = await message.channel.send(content=data['announcement'][str(message.channel.id)]['value'],silent=True)
                data['announcement'][str(message.channel.id)]['messageId'] = send_message.id
                with open('data.json', 'w') as f:
                    json.dump(data, f, indent = 2)
    
    @discord.app_commands.command(
        description = 'announcement'
    )
    @discord.app_commands.describe(mode='モードの指定')
    @discord.app_commands.choices(mode=[
        discord.app_commands.Choice(name='新規', value='new'),
        discord.app_commands.Choice(name='削除', value='delete'),
    ])
    async def announcement(self,interaction:discord.Interaction,mode:discord.app_commands.Choice[str],text:str = None):
        if mode.value == 'new' and text != None:
            with open('data.json') as f:
                data:dict = json.load(f)

            data['announcement'][interaction.channel_id] = {}
            data['announcement'][interaction.channel_id]['value'] = text
            last_message = await interaction.response.send_message(content=text)
            data['announcement'][interaction.channel_id]['messageId'] = last_message.message_id

            with open('data.json', 'w') as f:
                json.dump(data, f, indent = 2)
        elif mode.value == 'delete' and text == None:
            with open('data.json') as f:
                data:dict = json.load(f)
            
            if str(interaction.channel_id) in [i for i in data['announcement']]:
                data['announcement'].pop(str(interaction.channel_id))

                with open('data.json', 'w') as f:
                    json.dump(data, f, indent = 2)
                
                await interaction.response.send_message(content='complete',silent=True)
            else:
                await interaction.response.send_message(content='error',silent=True)
        else:
            await interaction.response.send_message(content='error',silent=True)

async def setup(bot:commands.Bot):
    await bot.add_cog(command(bot))