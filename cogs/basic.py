from discord.ext import commands
import re
from modules.prometheus_parser import PrometheusParser
from modules.aio_http import AioHttpCalls

class Basic(commands.Cog):
    def __init__(self, bot, config, logger):
        self.bot = bot
        self.config = config
        self.logger = logger
        self.prometheus_parser = PrometheusParser(logger=logger)
        self.alerts_channel = config.bot.alerts_channel
        self.announcement_monitoring_channel = config.bot.announcement_monitoring_channel
        self.enable_voice_calls = config.bot.enable_voice_calls
        self.users_to_ping = config.bot.users_to_ping

    @commands.Cog.listener()
    async def on_ready(self):
        print('\n------------------------------------------------------------------------')
        self.logger.info(f'{self.bot.user.name} STARTED')
        print('------------------------------------------------------------------------\n')

        self.bot.loop.create_task(self.bot.monitor_state_metrics())

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        if message.channel.id == self.announcement_monitoring_channel:

            if "ALL VALIDATOR OPERATORS" in message.content or "Commit Sha" in message.content:
                commit_sha_match = re.search(r'Commit Sha: ([^\n]+)', message.content)
                branch_match = re.search(r'Branch: ([^\n]+)', message.content)
                release_tag_match = re.search(r'Release Tag: ([^\n]+)', message.content)

                if commit_sha_match and branch_match and release_tag_match:
                    commit_sha = commit_sha_match.group(1)
                    branch = branch_match.group(1)
                    release_tag = release_tag_match.group(1)
                    message_content = f"""
**NEW VERSION IS OUT**
```ansi
[2;36mCommit: {commit_sha}[2;30m
[2;32mBranch: {branch}[2;30m
[2;33mRelease Tag: {release_tag}[2;30m
```
"""                
                else:
                    message_content = f"""
**NEW VERSION IS OUT**
Details are available here: <#{self.config.bot.announcement_monitoring_channel}>'
"""
            else:
                message_content = f"""
**NEW ANNOUNCEMENT IS OUT**
Details are available here: <#{self.config.bot.announcement_monitoring_channel}>'
"""
            
            for user in self.users_to_ping:
                message_content += f"<@{user}>" 
            channel = self.bot.get_channel(self.config.bot.alerts_channel)
            if channel:
                await channel.send(message_content)
            else:
                self.logger.error(f"Channel with ID {self.config.bot.alerts_channel} not found.")

    @commands.command()
    async def version(self, ctx):
        if ctx.author.bot:
            return
        if ctx.channel.id == self.config.bot.alerts_channel:
            async with AioHttpCalls(config=self.config, logger=self.logger) as session:
                data = await session.fetch_prometheus_metrics()
            if data:
                version = await self.prometheus_parser.get_version(data)
                if version:
                    message_content = f"""
:mag: **Your validator's version:**
```ansi
[2;36m{version}[2;30m
```
"""
                    await ctx.reply(content=message_content)
                    return
                
            await ctx.reply(content=":x:**Failed to fetch validator's version**")

async def setup(bot, config, logger):

    await bot.add_cog(Basic(bot, config, logger))