# zulipbot
Use Zulip to control the world.

## Rationale

This robot implements commands that the user can trigger on the Zulip chat.  
Those commands do things such as:
  - printing posts, pics, gifs from Reddit
  - playing music from Reddit
  - playing music from Youtube
  - making jokes
  - giving you a weather report

## Requirements

### Python Packages
```python
pip3 install -r requirements.txt
```
### Progams
  - **cvlc**: audio/video player
  - **pulseaudio**: manages volume and audio outputs

### Setup Files
Add the following files in this directory:
  - **zuliprc**, used by Zulip's client. Create a section called **zulipbot**. See [Zulip documentation](https://zulip.com/api/running-bots)
  - **praw.ini**, used by Reddit's client. See [praw documentation](https://praw.readthedocs.io/en/latest/getting_started/configuration/prawini.html)
  - **msg_filter.json**, used to filter Zulip messages the bot should respond to. See example below

```
{
    "type": "stream",
    "display_recipient": "MyChannel"
}
```

## Usage
```shell
./main.py
```
Then, in Zulip, type:
```
!help
```

## Acknowledgements

Thanks to my buddy T3lchar for letting me steal his bot: https://github.com/T3lchar/zulip_bot

## FAQ

Q: The command **!weather** fails with an SSL error, what's wrong?  
A: Take a look at this [issue](https://stackoverflow.com/questions/44649449/brew-installation-of-python-3-6-1-ssl-certificate-verify-failed-certificate/44649450#44649450) and execute ./bin/install_certifi.py
