import pymsteams
from datetime import datetime

def generate_teams_notification(rtr,interface,util,thresold):
    now = datetime.now()
    util_round = round(float(util),2)
    current_time = now.strftime("%d/%m/%Y %H:%M:%S")
    text_message = f"Interface {interface} util {util_round}% above theshold {thresold}% on router {rtr}"
    myMessageSection = pymsteams.cardsection()
    myMessageSection.title('LnetD Traffic above Thresold')

    myMessageSection.addFact("Date:", current_time)
    myMessageSection.addFact("Name:", rtr)
    myMessageSection.addFact("Interface:", interface)
    myMessageSection.addFact("Util %:", util_round )
    myMessageSection.addFact("Thresold %:", thresold )

    myMessageSection.text(text_message)

    return myMessageSection


def send_teams_notification_traffic(rtr,interface,util,thresold):
    myTeamsMessage = pymsteams.connectorcard("<change-me>")
    myTeamsMessage.addSection(generate_teams_notification(rtr,interface,util,thresold))
    summary_text = 'summary_text'
    myTeamsMessage.summary(summary_text)
    myTeamsMessage.printme()
    myTeamsMessage.send()
