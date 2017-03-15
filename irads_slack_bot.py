import os, time, requests, json, re, sqlite3, string
from slackclient import SlackClient
from datetime import datetime, timedelta

#----SECRET KEYS----#
BOT_ID = os.environ.get("BOT_ID")
SLACK_KEY = os.environ.get("SLACK_BOT_TOKEN")

#----COMMAND KEYS----#
AT_BOT = "<@" + BOT_ID + ">"
EXAMPLE_COMMAND = "do"
GREETING = "hey"
HELP = "help"
TOTAL_ENROLLMENT = "total enrollment"
UNDERGRADUATE_ENROLLMENT = "undergraduate enrollment"
GRADUATE_ENROLLMENT = "graduate enrollment"

#----SLACK CLIENT----#
#This is needed to interact with Slack.
slack_client = SlackClient(SLACK_KEY)

#----FUNCTIONS----#
#These functions create responses based on data.

#This function queries the database using a SQL command provided in the message
def sql_query(command):
    query = command
    #This connects to the database and prepares it for a query
    conn = sqlite3.connect("irads.sqlite")
    c = conn.cursor()

    #This block tries to execute the query. If an error is ever thrown, it responds with a failure message.
    try:
        #This executes the query and gets the response as a list of lists.
        c.execute(query)
        all_rows = c.fetchall()
        response = all_rows
        return response
    except:
        return "Unable to complete your query."

#This function searches the database for an entry by its objectid.
def get_total_enrollment(command):
    year = re.compile('\d+')
    queryyear = year.findall(command)
    qy = int(queryyear[0])
    #This pre-populates the SQL query and then sends that to the sql_query function.
    query = "SELECT Year, Total FROM enrollment_history WHERE Year >= %i" % qy
    response = sql_query(query)
    formatted_response = "Year  Enrollment\n"
    for item in response:
        formatted_response += "%s  %s\n" % (item[0], item[1])
    return formatted_response

def get_undergraduate_enrollment(command):
    year = re.compile('\d+')
    queryyear = year.findall(command)
    qy = int(queryyear[0])
    #This pre-populates the SQL query and then sends that to the sql_query function.
    query = "SELECT Year, Undergraduate FROM enrollment_history WHERE Year >= %i" % qy
    response = sql_query(query)
    formatted_response = "Year  Undergraduate Enrollment\n"
    for item in response:
        formatted_response += "%s  %s\n" % (item[0], item[1])
    return formatted_response

def get_graduate_enrollment(command):
    year = re.compile('\d+')
    queryyear = year.findall(command)
    qy = int(queryyear[0])
    #This pre-populates the SQL query and then sends that to the sql_query function.
    query = "SELECT Year, Graduate FROM enrollment_history WHERE Year >= %i" % qy
    response = sql_query(query)
    formatted_response = "Year  Graduate Enrollment\n"
    for item in response:
        formatted_response += "%s  %s\n" % (item[0], item[1])
    return formatted_response

#----COMMAND HANDLING----#
#This function parses the message and figures out how to respond.
#That response can be a simple text message or it can call a function.
def handle_command(command, channel):
    """
        Receives commands directed at the bot and determines if they
        are valid commands. If so, then acts on the commands. If not,
        returns back what it needs for clarification.
    """
    #This is the generic response. This will be sent if someone sends something that isn't recognized.
    #You should use this to guide users
    #Each of these checks to see if the command starts with a certain phrase or word.
    if command.startswith(EXAMPLE_COMMAND):
        response = "Sure...write some more code then I can do that!"
    elif command.startswith(GREETING) or command.startswith(HELP):
        response = "Howdy. I can tell you interesting things about UNL. Here's what I can do:\ntotal enrollment since [year]\nundergraduate enrollment since [year]\ngraduate enrollment since [year]\nchange [startyear] [endyear]\npercent change [startyear] [endyear]\nAnd I'm adding more all the time so check back."
    elif command.startswith(TOTAL_ENROLLMENT):
        response = get_total_enrollment(command)
    elif command.startswith(UNDERGRADUATE_ENROLLMENT):
        response = get_undergraduate_enrollment(command)
    elif command.startswith(GRADUATE_ENROLLMENT):
        response = get_graduate_enrollment(command)
    else:
        response = "Not sure what you mean. Try something else."

    #Finally, once a response is created, the slack_client posts it to the same channel the original message is in.
    slack_client.api_call("chat.postMessage", channel=channel, text=response, as_user=True)

#----PARSING OUTPUT----#
#This function takes the output and parses it. YOU SHOULDN'T NEED TO CHANGE ANYTHING.
#If the bot is named, it returns the channel id and the message with the username removed.
#If the bot is not named, it returns None and None.
def parse_slack_output(slack_rtm_output):
    """
        The Slack Real Time Messaging API is an events firehose.
        this parsing function returns None unless a message is
        directed at the Bot, based on its ID.
    """
    output_list = slack_rtm_output
    if output_list and len(output_list) > 0:
        for output in output_list:
            if output and 'text' in output and AT_BOT in output['text']:
                # return text after the @ mention, whitespace removed
                return output['text'].split(AT_BOT)[1].strip().lower(), output['channel']
    return None, None

#----CREATING THE TUNNEL----#
#This is called when the file is run from the terminal. YOU SHOULDN'T NEED TO CHANGE ANYTHING.
#It tries to connect to the slack client. If it fails, it prints a failure message.
if __name__ == "__main__":
    #This is how long the loop waits between checking for new messages.
    READ_WEBSOCKET_DELAY = 1
    if slack_client.rtm_connect():
        #Once the connection is successful, it starts a loop to constantly check for new messages.
        #It sends anything it finds to the parse_slack_output function.
        #If it receives a response from the parse_slack_output function, it sends those responses to the handle_command function.
        print("Bot connected and running!")
        while True:
            command, channel = parse_slack_output(slack_client.rtm_read())
            if command and channel:
                handle_command(command, channel)
            time.sleep(READ_WEBSOCKET_DELAY)
    else:
        print("Connection failed. Invalid Slack token or bot ID.")
