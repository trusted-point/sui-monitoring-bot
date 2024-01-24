import discord
from discord.ext import commands
from sys import exit
from yaml import safe_load
from os import listdir
from inspect import iscoroutinefunction, signature
from importlib import import_module
import asyncio
from utils.get_bot_token import get_bot_token
from utils.logger_setup import setup_logger
from utils.config_datatype import Config
from modules.prometheus_parser import PrometheusParser
from modules.aio_http import AioHttpCalls

with open('config.yaml', 'r') as config_file:
    yaml_config = safe_load(config_file)

config = Config(**yaml_config)
bot_token = get_bot_token()

logger = setup_logger(log_level =  config.logs.level, enable_logs_save = config.logs.enable_log_save, log_file = config.logs.file, log_rotation_size = config.logs.rotation_size)

class MyBot(commands.Bot):
    def __init__(self, intents, config, logger):
        self.config = config
        self.logger = logger
        self.prometheus_parser = PrometheusParser(logger=logger)
        self.alert_channel_id = config.bot.alerts_channel
        self.users_to_ping = config.bot.users_to_ping
        self.alerts_thresholds = {
                    'global_failed_attempts': 0,
                    'max_global_attempts': 3,
                    'metrics': {
                        'current_round':{ 'last_value': 0, 'stuck_attempts': 0, 'max_stuck_attempts': 3, 'cahnge_rate': 10},
                        'last_committed_round':{ 'last_value': 0, 'stuck_attempts': 0, 'max_stuck_attempts': 3, 'cahnge_rate': 10},
                        'last_executed_checkpoint':{ 'last_value': 0, 'stuck_attempts': 0, 'max_stuck_attempts': 3, 'cahnge_rate': 10},
                        'highest_synced_checkpoint':{ 'last_value': 0, 'stuck_attempts': 0, 'max_stuck_attempts': 3, 'cahnge_rate': 10},
                    }
                    }

        super().__init__(
            command_prefix="!",
            intents=intents
        )

    async def setup_hook(self) -> None:
        await self.load_cogs()

    async def load_cogs(self):
        cog_dir = './cogs'
        cog_params_mapping = {
            'basic': {'config': self.config, 'logger': self.logger},
            }
        
        for filename in listdir(cog_dir):
            if filename.endswith('.py'):
                cog_name = filename[:-3]
                cog_module = f'cogs.{cog_name}'
                cog = import_module(cog_module)
                
                if hasattr(cog, 'setup') and iscoroutinefunction(cog.setup):
                    setup_params = signature(cog.setup).parameters

                    if cog_name in cog_params_mapping and all(param in setup_params for param in cog_params_mapping[cog_name]):
                        
                        await cog.setup(self, **cog_params_mapping[cog_name])
                        print('\n------------------------------------------------------------------------')
                        logger.info(f"Cog {cog_name.upper()} has been loaded successfully")
                        print('------------------------------------------------------------------------')
                    else:
                        logger.error(f"Error: Incorrect parameters for setup function in {cog_module}")
                        logger.error(f"Expected parameters: {setup_params}, Provided parameters: {cog_params_mapping[cog_name]}")

    async def monitor_state_metrics(self):
        while not self.is_closed():
            self.logger.info(f"Fetching metrics")

            try:
                async with AioHttpCalls(config=self.config, logger=self.logger) as session:
                    data = await session.fetch_prometheus_metrics()

                if data is None:
                    self.alerts_thresholds['global_failed_attempts'] += 1
                    if self.alerts_thresholds['global_failed_attempts'] >= self.alerts_thresholds['max_global_attempts']:
                        await self.send_global_alert()
                        self.logger.error(f"Validator is down. Metrics are not presented")
                        self.alerts_thresholds['global_failed_attempts'] = 0

                else:
                    metric_functions = {
                        'current_round': self.prometheus_parser.get_current_round,
                        'last_committed_round': self.prometheus_parser.get_last_committed_round,
                        'last_executed_checkpoint': self.prometheus_parser.get_last_executed_checkpoint,
                        'highest_synced_checkpoint': self.prometheus_parser.get_highest_synced_checkpoint,
                        }
                    
                    for metric_name, metric_function in metric_functions.items():
                        current_metric_value = await metric_function(data)
                        if current_metric_value == 0 or current_metric_value - self.alerts_thresholds['metrics'][metric_name]['last_value'] < self.alerts_thresholds['metrics'][metric_name]['cahnge_rate']:
                            self.logger.warn(f"Metric {metric_name} is not advancing. Adding stuck_attempt")

                            self.alerts_thresholds['metrics'][metric_name]['stuck_attempts'] += 1
                            if self.alerts_thresholds['metrics'][metric_name]['stuck_attempts'] >= self.alerts_thresholds['metrics'][metric_name]['max_stuck_attempts']:
                                self.logger.warn(f"Stuck_attempt for {metric_name} reached")

                                await self.send_metric_stuck_alert(metric_name=metric_name, metric_value=current_metric_value)
                                self.alerts_thresholds['metrics'][metric_name]['stuck_attempts'] = 0
                        else:
                            self.logger.info(f"{metric_name} is okay")

                        self.alerts_thresholds['metrics'][metric_name]['last_value'] = current_metric_value

                await asyncio.sleep(30)
            except Exception as e:
                self.logger.error(f"An unexpected error occurred: {e}")

    async def send_metric_stuck_alert(self, metric_name: str, metric_value):
        message_content = f"""
:no_entry: **EMERGENCY ALERT**

`{metric_name}` is stuck
Fetch attempts: {self.alerts_thresholds['metrics'][metric_name]['max_stuck_attempts']}
```ansi
[2;31m {metric_name} : {metric_value}
```
"""
        for user in self.users_to_ping:
            message_content += f"<@{user}>" 
        alert_channel = self.get_channel(self.alert_channel_id)
        if alert_channel:
            await alert_channel.send(content=message_content)
            self.logger.info(f"Sending {metric_name} alert")
        else:
            self.logger.error(f"Channel with ID {config.bot.gov_channel_id} not found.")

    async def send_global_alert(self):
        message_content = f"""
:no_entry: **EMERGENCY ALERT**
```ansi
[2;31m VALIDATOR IS NOT RESPONDING
```
Fetch attempts: {self.alerts_thresholds['max_global_attempts']}
"""
        for user in self.users_to_ping:
            message_content += f"<@{user}>"
        alert_channel = self.get_channel(self.alert_channel_id)
        if alert_channel:
            await alert_channel.send(content=message_content)
            self.logger.info(f"Sending global alert")
        else:
            self.logger.error(f"Channel with ID {config.bot.gov_channel_id} not found.")

intents = discord.Intents.default()
intents.typing = True
intents.presences = False
intents.message_content = True
bot = MyBot(intents=intents, config=config, logger=logger)

async def main():
    tasks = [
        bot.start(token=bot_token)
    ]

    await asyncio.gather(*tasks)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        asyncio.run(bot.close())
        print('\n------------------------------------------------------------------------')
        logger.info("Bot was stopped")
        print('------------------------------------------------------------------------\n')
        exit()