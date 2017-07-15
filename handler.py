# -*- coding: utf-8 -*-
"""
A routing layer for the onboarding bot tutorial built using
[Slack's Events API](https://api.slack.com/events-api) in Python
"""


import bot
import boto3
import json
import mention

pyBot = bot.Bot()
slack = pyBot.client

def store_token(token):
    try:
        res = boto3.resource('dynamodb', region_name='us-east-1')
        table = res.Table('poor-webhook-tokens')
        response = table.put_item(
            Item={
                'account_id': token.split('.')[0],
                'token': token
            }
        )

        pyBot.update_auth()
        return response
    except Exception as e:
        print(e)

def thanks(event, context):
    message = """
    <!doctype html>
    <title>Install pythOnBoarding</title>
    <br>
    <br>
    <br>
    <center>
        <h1>Thanks for installing!</h1>
    </center>
    """

    print(event)
    print(context)
    try:
        store_token(event['queryStringParameters']['code'])

        response = {
            "statusCode": 200,
            "body": message,
            "headers": {
                "Content-Type": "text/html"
            }
        }
    except Exception as e:
        print(e)
        message = 'Could not store token.'
        response = {
            "statusCode": 500,
            "body": message,
            "headers": {
                "Content-Type": "text/html"
            }
        }
    return response

def install(event, context):

    scope = pyBot.oauth["scope"]
    client_id = pyBot.oauth["client_id"]


    message = """
        <!doctype html>
        <title>Install pythOnBoarding</title>
        <br>
        <br>
        <br>
        <center>
            <h1>Click the button to install pythOnBoarding Bot</h1>
            <a href="https://slack.com/oauth/authorize?scope={scope}&client_id={client_id}">
                <img alt="Add to Slack" height="40" width="139" src="https://platform.slack-edge.com/img/add_to_slack.png" srcset="https://platform.slack-edge.com/img/add_to_slack.png 1x, https://platform.slack-edge.com/img/add_to_slack@2x.png 2x" />
            </a>
        </center>
    """.format(
        scope=scope,
        client_id=client_id
    )

    response = {
        "statusCode": 200,
        "body": message,
        "headers": {
            "Content-Type": "text/html"
        }
    }
    return response

def _event_handler(event_type, slack_event):
    """
    A helper function that routes events from Slack to our Bot
    by event type and subtype.
    Parameters
    ----------
    event_type : str
        type of event received from Slack
    slack_event : dict
        JSON response from a Slack reaction event
    Returns
    ----------
    obj
        Response object with 200 - ok or 500 - No Event Handler error
    """
    team_id = slack_event["team_id"]
    # ================ Team Join Events =============== #
    # When the user first joins a team, the type of event will be team_join
    if event_type == "team_join":
        pass
    else:
        pass

def hears(event, context):
    """
    This route listens for incoming events from Slack and uses the event
    handler helper function to route events to our Bot.
    """

    slack_event = event.get('body')



    if slack_event is not None:
        slack_event = json.loads(slack_event)
        # ============= Slack URL Verification ============ #
        # In order to verify the url of our endpoint, Slack will send a challenge
        # token in a request and check for this token in the response our endpoint
        # sends back.
        #       For more info: https://api.slack.com/events/url_verification


        # TBD handle this
        """
        { 
            "token": "QSNFm4OA5WD9jr8v5MAlJOky", "team_id": "T63CVJG4U", 
            "api_app_id": "A63ELGLVB", 
            "event": { 
            "type": "message", "user": "U62M7T83A", 
            "text": "@poor-webhook get changelog boo.md for commit for 
            commit bff6b7dcda5cb723908c514d814ca4fbbe558912", 
            "ts": "1499662208.370661", "channel": "C646H1UBZ", "event_ts": "1499662208.370661" }, 
            "type": "event_callback", "authed_users": [ "U62M7T83A" ], "event_id": "Ev661M0Q11", 
            "event_time": 1499662208 
        }
        """
        #print(slack_event['event']['text'].split(' ')[0])

        try:
            if slack_event['event']['text'].split(' ')[0] == "@poor-webhook":
                """If this is a direct message to the bot in the channel react appropriately."""
                print('Message sent directly to slack bot, reacting now.')
                mention.react(slack_event['event'].get('text'), pyBot)
        except:
            pass


        if "challenge" in slack_event:
        #   return make_response(slack_event["challenge"], 200, {"content_type":
        #                                                         "application/json"
        #                                                         })
            response = {
                "statusCode": 200,
                "body": slack_event.get('challenge'),
                "headers": {
                    "Content-Type": "application/json"
                }
            }

            return response


        # ============ Slack Token Verification =========== #
        # We can verify the request is coming from Slack by checking that the
        # verification token in the request matches our app's settings
        if pyBot.verification != slack_event.get("token"):
            message = "Invalid Slack verification token: %s \npyBot has: \
                       %s\n\n" % (slack_event["token"], pyBot.verification)
            # By adding "X-Slack-No-Retry" : 1 to our response headers, we turn off
            # Slack's automatic retries during development.

            response = {
                "statusCode": 403,
                "body": message,
                "headers": {
                    "Content-Type": "text/html",
                    "X-Slack-No-Retry": 1
                }
            }

            return response
        # ====== Process Incoming Events from Slack ======= #
        # If the incoming request is an Event we've subcribed to
        if "event" in slack_event:
            event_type = slack_event["event"]["type"]
            # Then handle the event by event_type and have your bot respond
            return _event_handler(event_type, slack_event)
    # If our bot hears things that are not events we've subscribed to,
    # send a quirky but helpful error response

    message = "[NO EVENT IN SLACK REQUEST] These are not the droids you're looking for."
    response = {
        "statusCode": 404,
        "body": message,
        "headers": {
            "Content-Type": "text/html",
            "X-Slack-No-Retry": 1
        }
    }
    return

def clean_empty(d):
    if not isinstance(d, (dict, list)):
        return d
    if isinstance(d, list):
        return [v for v in (clean_empty(v) for v in d) if v]
    return {k: v for k, v in ((k, clean_empty(v)) for k, v in d.items()) if v}

def github_webhook(event, context):
    """Fires anytime github webhook content comes in."""
    try:
        # Parse the headers for convenience.
        event_id = event['headers']['X-GitHub-Delivery']
        event_type = event['headers']['X-GitHub-Event']
        event_body = json.loads(event['body'])

        # Add our event_id to the body.
        event_body['X-Github-Delivery'] = event_id
        event_body['X-GitHub-Event'] = event_type

        # Remove any keys whose value is empty string.
        event_body = clean_empty(event_body)

        print(event_body)

        # Store the event in DynamoDb for use later.
        res = boto3.resource('dynamodb', region_name='us-east-1')
        table = res.Table('poor-webhook-events')
        response = table.put_item(
            Item=event_body
        )
    except Exception as e:
        print(e)

    if event_type == 'push':
        """Handle pushes to any branch"""
        slack_message = "A commit has landed in the {branch} of {repository}. Message is : {message}. "\
            "For a copy of the changelog you can say @poor-webhook get changelog ||filename|| "\
            "for event {event_id}.".format(
            branch=event_body['ref'].split('/')[2],
            message=event_body['head_commit']['message'],
            event_id=event_id,
            repository=event_body['repository']['full_name']
        )

        pyBot.message_channel(
            '#general',
            slack_message
        )
        pass
    elif event_type == 'pull_request':
        """Handle PRs"""
        pass
    elif event_type == 'issue':
        pass

    response = {
        "statusCode": 200,
        "body": "",
        "headers": {
            "Content-Type": "text/html",
            "X-Slack-No-Retry": 1
        }
    }

    return response