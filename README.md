# Telegram Channel Downloader
Download all media stuff from telegram, support for multiple channels.Using Python 3.8

## Quick Start

Install Python3.8 then:
``` sh
$ pip3 install -r requirements.txt
```
Run once and the programe will generate config files at ` ./Config `:
``` sh
$ Python3 downloader.py
```

Configurate `./Config/config.yaml`, here is an example
``` yaml
ProxyAddress: 127.0.0.1
ProxyPort: 7890
ProxyPassword: null
ProxyUser: null
api_hash: your_api_hash
api_id: your_api_id
chat_ids:
- channel_name01
- channel_name02
#...copy one or more chat id here, channel name is also okey
```

> [This is a way to find Chat id](https://gist.github.com/mraaroncruz/e76d19f7d61d59419002db54030ebe35). I recommend [@getidsbot](https://t.me/getidsbot) tho.

> `config.yaml` will be **DELETED** when the program spot something error.Be sure backup your file before you start the program!

Run again and login to your telegram, the program will start download all media from the channel.

You can edit `./Config/monitors.yaml` to define where to start download:
``` yaml
channel_name01:
  ids_to_retry: # failed downloads, will re-download them after all media downloads complete, don't edit
  - 2086
  - 2612
  - 6980
  last_read_message_id: 21149 #message id where to start download
channel_name02:
  ids_to_retry: []
  last_read_message_id: 10056 
```

Files will be downloaded at `./Downloads/{channel_name}/{media_type}/`

{media_type} can be `Photo`, `Video`, `Animation`, `Document`, `Audio`

## Special Thanks
Checkout these links and see how they inspire me.

[Dineshkarthik/telegram_media_downloader](https://github.com/Dineshkarthik/telegram_media_downloader)

[snow922841/telegram_channel_downloader](https://github.com/snow922841/telegram_channel_downloader)
