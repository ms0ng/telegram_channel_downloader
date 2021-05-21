from logging import info
import logging
from typing import Tuple
import yaml
from datetime import date, datetime
import time

logger: logging.Logger = logging.getLogger("Downloader")

class ConfigHandler:
    __CONFIG: dict
    __CONFIG_FILE_NAME: str
    __MONITORS: dict
    __MONITORS_SAVENAME: str
    __LAST_TIME_SAVE:float

    default_monitor = {
        "ids_to_retry": [],
        "last_read_message_id": 0,
    }
    default_monitor_full = {
        "ids_to_retry": [],
        "last_read_message_id": 0,
        "accept_media": {
            "animation": ["all"],
            "audio": ["all"],
            "document": ["all"],
            "photo": ["jpg", "png"],
            "video": ["mp4", "mov"],
            "voice": ["all"]
        }
    }

    def __init__(self, file_name: str = "config.yaml", monitors_save_name: str = "monitors.yaml") -> None:
        self.__CONFIG_FILE_NAME=file_name
        self.__MONITORS_SAVENAME=monitors_save_name
        self.__CONFIG , self.__MONITORS = self.__load(self.__CONFIG_FILE_NAME,self.__MONITORS_SAVENAME)
        self.__LAST_TIME_SAVE=time.time()

    def get_config(self) -> dict:
        return self.__CONFIG

    def get_api_hash(self)->str:
        return str(self.__CONFIG["api_hash"])

    def get_api_id(self)->str:
        return str(self.__CONFIG["api_id"])

    def get_monitor_list(self)->list:
        return self.__CONFIG["chat_ids"]

    def get_monitor(self,chat_id:str)->dict:
        return self.__MONITORS.setdefault(chat_id,self.default_monitor)

    def set_monitor(self, chat_id: str, monitor_status:dict):
        self.__MONITORS[chat_id] = monitor_status
        self.save_config()

    def __load(self,config_filename: str,monitors_savename:str)-> Tuple[dict,dict] :
        
        #1.load config file
        config: dict
        try:
            with open(config_filename, "r") as f:
                config = yaml.safe_load(f)
            if config["api_hash"]:
                pass
            if config["api_id"]:
                pass
            if config["chat_ids"]:
                pass
            if config["ProxyAddress"]:
                pass
        except:
            default_config = {
                "ProxyAddress":"",
                "ProxyPort": 1080,
                "ProxyUser": None,
                "ProxyPassword": None,
                "api_hash": "your_api_hash_like_this_12345678abcd12345678abcdfe123c",
                "api_id": 123456,
                "chat_ids": ["chat_id_01", "chat_id_02", "chat_id_03"],
                "Note_1": "Replace api_hash and api_id to yours.",
                "Note_2": "You can copy one or more chat id to download its media.",
                "Note_3": "Backup this config file after you edit it!The program will rewrite this file if something go wrong.Check ConfigHandler.__load().",
                "Note_4": "These Note can be delete.",
            }
            try:
                with open(config_filename, "w") as yaml_file:
                    yaml.dump(default_config, yaml_file)
            except:
                return None,None
        #2.load monitors' info
        monitors: dict
        try:
            with open(monitors_savename, "r") as f:
                monitors = yaml.safe_load(f)
            if monitors:
                pass
            if len(monitors):
                pass
        except:
            default_monitors:dict={
                "chat_id": self.default_monitor,
                #"chat_id_full":self.default_monitor_full
            }
            try:
                with open(monitors_savename,"w") as yaml_file:
                    yaml.dump(default_monitors, yaml_file)
            except:
                pass
            return None,None
        #3.update monitors
        id_config:set=set(config["chat_ids"])
        id_monitors:set=set(monitors.keys())
        for id in id_config-id_monitors:
            monitors.setdefault(str(id),self.default_monitor)
        #for id in id_monitors-id_config:
        #    monitors.pop(str(id))
        return config,monitors

    def __save_config(self):
        try:
            with open(self.__CONFIG_FILE_NAME, "w") as yaml_file:
                yaml.dump(self.__CONFIG, yaml_file, default_flow_style=False)
            with open(self.__MONITORS_SAVENAME, "w") as yaml_file:
                yaml.dump(self.__MONITORS, yaml_file, default_flow_style=False)
        except:
            logger.error(
                "Save config files failed.Please check if other proccess is using the files."
                )
        
    def save_config(self):
        now = time.time()
        if now-self.__LAST_TIME_SAVE>5:
            logger.info(
                "[Config]: Update config."
                )
            self.__save_config()
            self.__LAST_TIME_SAVE=now
