import os,sys
import slack
from datetime import datetime

def generate_alarm_text(rtr,interface):
    now = datetime.now()
    date = now.strftime("%d/%m/%Y %H:%M:%S")
    base_template = [
  {
    "type": "context",
    "elements": [
      {
        "type": "mrkdwn",
        "text": "LnetD - Link Alert"
      }
    ]
  },
  {
    "type": "divider"
  },
  {
    "type": "context",
    "elements": [
      {
        "type": "mrkdwn",
        "text": " *{}* - *{}* has *0* traffic at: *{}*"
      }
    ]
  }
]
    base_template[2]['elements'][0]['text'] = f"*{rtr}* - *{interface}* is *DOWN* or *SNMP not enabled* , checked at : *{date}*"
    return base_template


def send_slack_notification(rtr,interface):
    client = slack.WebClient(token='xoxb-3738957452-1000578228822-xouk7yjHeKz2OEm16XjYRudb11111')
    print(generate_alarm_text(rtr,interface))
    response = client.chat_postMessage(
        channel='UTF656E8K',
        text='LnetD - Alert ',
        blocks = generate_alarm_text(rtr,interface),
        as_user = True)
