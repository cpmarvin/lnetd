import os,sys
import slack
from datetime import datetime

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
def generate_alarm_text(base_template,rtr,interface):
    now = datetime.now()
    date = now.strftime("%d/%m/%Y %H:%M:%S")
    base_template[2]['elements'][0]['text'] = f"*{rtr}* - *{interface}* is *DOWN* or *SNMP not enabled* , checked at : *{date}*"
    return base_template

def generate_util_text(base_template,rtr,interface,threshold,util):
    now = datetime.now()
    date = now.strftime("%d/%m/%Y %H:%M:%S")
    base_template[2]['elements'][0]['text'] = f"*{rtr}* - *{interface}* util *{util}%* *greater* than *{threshold} %*, checked at : *{date}*"
    return base_template

def send_slack_notification(rtr,interface,type,threshold=None,util=None):
    try:
        client = slack.WebClient(token='slack-token')
        channel='UTF656E8K'
        text='LnetD - Alert '
        if type=='down':
            print(generate_alarm_text(base_template,rtr,interface))
            response = client.chat_postMessage(
             channel=channel,
             text=text,
             blocks = generate_alarm_text(base_template,rtr,interface),
             as_user = True)
        elif type=='util':
            print(generate_util_text(base_template,rtr,interface,threshold,util))
            response = client.chat_postMessage(
             channel=channel,
             text=text,
             blocks = generate_util_text(base_template,rtr,interface,threshold,util),
             as_user = True)
    except Exception as e:
        print(e)
