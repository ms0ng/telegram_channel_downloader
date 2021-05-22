import os
from time import sleep
import logging
import asyncio

from utils.ConfigHandler import ConfigHandler
from utils.TelegramClient import TelegramClient
from utils.Monitor import Monitor

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
    )
logger:logging.Logger=logging.getLogger("Downloader")

def update_monitor(monitors: list):
    tasks = [
        monitor.update()
        for monitor in monitors
    ]
    asyncio.get_event_loop().run_until_complete(asyncio.wait(tasks))


def instantiate_monitors(
    telegram_client: TelegramClient,
    config_handler: ConfigHandler
) -> list:
    monitor_info_list = config_handler.get_monitor_list()
    monitors: list = []
    for each in monitor_info_list:
        monitor = Monitor(
            telegram_client=telegram_client,
            config_handler=config_handler,
            chat_id=str(each),
        )
        monitors.append(monitor)
    return monitors


def main():
    if not os.path.isdir("Config"):
        os.mkdir("Config")
    if not os.path.isdir("Downloads"):
        os.mkdir("Downloads")
    # Read config
    config_file=os.path.join("Config","config.yaml")
    monitors_file=os.path.join("Config","monitors.yaml")
    config_handler = ConfigHandler(config_file,monitors_file)
    if not config_handler.get_config():
        logger.error(
            "[Config]: No config found.A template is generated,please check %s"
            %(str(config_file))
        )
        return
    
    # Create client
    tg_client = TelegramClient(
        api_id=config_handler.get_api_id(),
        api_hash=config_handler.get_api_hash(),
        proxy_addr=config_handler.get_config()["ProxyAddress"],
        proxy_port=config_handler.get_config()["ProxyPort"],
        proxy_user=config_handler.get_config()["ProxyUser"],
        proxy_pwd=config_handler.get_config()["ProxyPassword"]
    )
    # Create Monitors
    monitors: list = instantiate_monitors(
        config_handler=config_handler,
        telegram_client=tg_client
    )
    update_monitor(monitors=monitors)
    logger.info("Tasks All Done.Save data after 5s...")
    sleep(5)
    config_handler.save_config()

if __name__ == "__main__":
    main()
