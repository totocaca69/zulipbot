# zulipbot

## Requirements

### Python Packages
```python
pip3 install -r requirements.txt
```
### Setup Files
Add the following files in this directory:
  - **zuliprc**, used by Zulip's client. See [Zulip documentation](https://zulip.com/api/running-bots)
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
Thanks to my buddy T3lchar for letting me still his bot: https://github.com/T3lchar/zulip_bot
