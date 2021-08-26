
from datetime import datetime
import pyrogram
import asyncio
import os
import logging

from utils.TelegramClient import TelegramClient
from utils.ConfigHandler import ConfigHandler

logger: logging.Logger = logging.getLogger("Downloader")

class Monitor:
    downloadingCount=0

    @property
    def default_accept_media(self):
        return {
            "animation": ["all"],
            "audio": ["all"],
            "document": ["all"],
            "photo": ["jpg", "png"],
            "video": ["mp4", "mov"],
            "voice": ["all"]
        }

    def __init__(self, telegram_client: TelegramClient, config_handler:ConfigHandler, chat_id: str) -> None:
        self.__TG_CLIENT: pyrogram.Client
        self.__CONFIGHANDLER: ConfigHandler
        self.__CHAT_ID: str
        self.__LAST_READ_MESSAGE_ID: int
        self.__IDS_TO_RETRY: list
        self.__ACCEPT_MEDIA: dict
        self.__CUSTOM_ACCEPT_MEDIA: dict
        self.__ACCEPT_MEDIA_TYPES: list

        self.__TG_CLIENT = telegram_client.get_client()
        self.__CONFIGHANDLER=config_handler
        self.__CHAT_ID = chat_id
        self.__LAST_READ_MESSAGE_ID = self.__CONFIGHANDLER.get_monitor(self.__CHAT_ID).get("last_read_message_id",0)
        self.__IDS_TO_RETRY = self.__CONFIGHANDLER.get_monitor(self.__CHAT_ID).get("ids_to_retry",[])
        self.__CUSTOM_ACCEPT_MEDIA = self.__CONFIGHANDLER.get_monitor(self.__CHAT_ID).get("accept_media",None)

        if self.__CUSTOM_ACCEPT_MEDIA:
            self.__ACCEPT_MEDIA = self.__CUSTOM_ACCEPT_MEDIA
        else:
            self.__ACCEPT_MEDIA = self.default_accept_media

        self.__ACCEPT_MEDIA_TYPES = list(self.__ACCEPT_MEDIA.keys())
        logger.info(
            "[%s]: Init success.Last Message id %s"
            %(str(self),str(self.__LAST_READ_MESSAGE_ID))
            )

    def __str__(self) -> str:
        return "Monitor(" + self.__CHAT_ID + ")"

    def get_status(self) -> dict:
        sdict = {
            "last_read_message_id": self.__LAST_READ_MESSAGE_ID,
            "ids_to_retry": list(self.__IDS_TO_RETRY)
        }
        if self.__CUSTOM_ACCEPT_MEDIA:
            sdict["accept_media"] = self.__CUSTOM_ACCEPT_MEDIA
        return sdict

    async def __download_media(
        self,
        message:pyrogram.types.Message,
    ):
        
        async def _filename(message:pyrogram.types.Message)->str:
            _download_path="Downloads"
            _date=str(datetime.fromtimestamp(message.date).strftime("%Y-%m-%d_%H-%M-%S"))
            _type:str
            _filename:str
            if msg := message.animation:
                _type = "Animation"
                _filename = "{}_{}.{}".format(
                    _date,
                    str(getattr(msg, "file_name", msg.file_unique_id)).split(".")[0][0:100],
                    msg.mime_type.split("/")[-1],
                )
            elif msg := message.audio:
                _type = "Audio"
                _filename = "{}_{}.{}".format(
                    _date,
                    str(getattr(msg, "file_name", msg.file_unique_id)).split(".")[0][0:100],
                    msg.mime_type.split("/")[-1],
                )
            elif msg := message.document:
                _type = "Document"
                _filename = "{}_{}.{}".format(
                    _date,
                    str(getattr(msg, "file_name", msg.file_unique_id)).split(".")[0][0:100],
                    msg.mime_type.split("/")[-1],
                )
            elif msg := message.photo:
                _type = "Photo"
                _filename = "{}_{}.{}".format(
                    _date,
                    str(getattr(msg, "file_unique_id"))[0:10],
                    "jpg",
                )
            elif msg := message.video:
                _type = "Video"
                _filename = "{}_{}.{}".format(
                    _date,
                    str(getattr(msg, "file_name", msg.file_unique_id)).split(".")[0][0:100],
                    msg.mime_type.split("/")[-1],
                )
            elif msg := message.voice:
                _type = "Voice"
                _filename = "{}_{}.{}".format(
                    _date,
                    str(getattr(msg, "file_unique_id"))[0:100],
                    msg.mime_type.split("/")[-1],
                )
            else:
                _type = "Unknown"
                _filename = "{}_{}.{}".format(
                    _date,
                    str(message.message_id),
                    "unknownfile"
                )
            return os.path.join(
                _download_path, 
                self.__CHAT_ID, 
                _type,
                _filename,
                )


        if not message:return
        if not message.media : return
        filename=await _filename(message)
        if os.path.exists(filename):
            logger.warning(
                "[%s]: Media %s exists,download skipped.At %s"
                %(str(self),str(message.message_id),filename)
            )
            return

        #Wait for other downloading
        while Monitor.downloadingCount>3:
            await asyncio.sleep(3)
        Monitor.downloadingCount+=1

        retry:int =3
        for i in range(retry):
            try:
                download_path=await self.__TG_CLIENT.download_media(
                    message=message,
                    file_name=filename
                )
                if download_path:
                    logger.info(
                        "[%s]: Downloaded media (%s) at %s"
                        %(str(self),str(message.message_id),download_path)
                    )
                    break
                else:
                    raise Exception("Download failed")
            except ValueError:
                logger.debug("This message doesn't contain any media.")
                break
            except Exception as e:
                logger.error(
                    "[%s]: Download failed due to an exception:\n%s"
                    %(str(self),e),
                    exc_info=True
                    )
                if i==retry-1:
                    logger.warning("[%s]: Add message id %s to failed list, download skipped" %(str(self),str(message.message_id)))
                    self.__IDS_TO_RETRY.append(message.message_id)
                    break
                await asyncio.sleep(5)

        Monitor.downloadingCount-=1
        if self.__LAST_READ_MESSAGE_ID<message.message_id:
            self.__LAST_READ_MESSAGE_ID=message.message_id

    async def update(self):
        """main call"""
        
        if self.__CHAT_ID[0]=="-":
            chatid:int=int(self.__CHAT_ID)
        else:
            chatid:str=self.__CHAT_ID
        msg_iter=self.__TG_CLIENT.iter_history(
            chat_id=chatid,
            offset_id=self.__LAST_READ_MESSAGE_ID,
            reverse=True,
        )
        dl_list:list=[]
        async for message in msg_iter: 
            #asyncio.run_coroutine_threadsafe(self.__download_media(message,sema),asyncio.get_running_loop())  #too fast
            dl_list.append(self.__download_media(message))
            if len(dl_list) >= 8:
                await asyncio.wait(dl_list.copy())
                dl_list.clear()
                self.__CONFIGHANDLER.set_monitor(self.__CHAT_ID, self.get_status())
        if dl_list:
            await asyncio.wait(dl_list.copy())
            dl_list.clear()
        if self.__IDS_TO_RETRY:
            logger.info(
                "[%s]: Start to redownload failed downloads."
                %(str(self))
            )
            failed_list:list=await self.__TG_CLIENT.get_messages(
                chat_id=self.__CHAT_ID,
                message_ids=self.__IDS_TO_RETRY,
            )
            self.__IDS_TO_RETRY.clear()
            for failed in failed_list:
                await self.__download_media(failed)
                self.__CONFIGHANDLER.set_monitor(self.__CHAT_ID, self.get_status())
        logger.info(
            "[%s]: Download all done.Last download id %s"
            %(str(self),str(self.__LAST_READ_MESSAGE_ID))
        )



    def __del__(self):
        logger.debug(
            "[%s]: Shutdown.Final status:\n%s"
            %(str(self),str(self.get_status()))
        )
        self.__CONFIGHANDLER.set_monitor(self.__CHAT_ID, self.get_status())
        self.__CONFIGHANDLER.save_config()

