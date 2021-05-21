import pyrogram

class TelegramClient:
    __CLIENT: pyrogram.Client
    __API_ID: str
    __API_HASH: str

    def __init__(self, api_id: str, api_hash: str, proxy_addr: str = None, proxy_port: int = 1080, proxy_user: str = "", proxy_pwd: str = "") -> None:
        self.__API_ID = api_id
        self.__API_HASH = api_hash
        proxy = dict(
            hostname=proxy_addr,
            port=proxy_port,
            username=proxy_user,
            password=proxy_pwd
        )
        self.__create_client(proxy)

    def __create_client(self,proxy:dict):
        if proxy.get("hostname"):
            self.__CLIENT = pyrogram.Client(
                "telegram_monitor",
                api_id=self.__API_ID,
                api_hash=self.__API_HASH,
                proxy=proxy
            )
        else :
            self.__CLIENT = pyrogram.Client(
            "telegram_monitor",
            api_id=self.__API_ID,
            api_hash=self.__API_HASH,
            )
        pyrogram.session.Session.notice_displayed = True
        self.__CLIENT.start()

    def __del__(self):
        self.__CLIENT.stop()

    def get_client(self) -> pyrogram.Client:
        return self.__CLIENT
