# -*- coding: utf-8 -*-
"""
Python Slack Bot class for use with the pythOnBoarding app
"""
import boto3
import os

from slackclient import SlackClient

# To remember which teams have authorized your app and what tokens are
# associated with each team, we can store this information in memory on
# as a global object. When your bot is out of development, it's best to
# save this in a more persistant memory store.
authed_teams = {}


class Bot(object):
    """ Instantiates a Bot object to handle Slack onboarding interactions."""
    def __init__(self):
        super(Bot, self).__init__()
        self.name = "poorwebhook"
        self.emoji = ":robot_face:"
        # When we instantiate a new bot object, we can access the app
        # credentials we set earlier in our local development environment.
        self.oauth = {"client_id": os.environ.get("CLIENT_ID"),
                      "client_secret": os.environ.get("CLIENT_SECRET"),
                      # Scopes provide and limit permissions to what our app
                      # can access. It's important to use the most restricted
                      # scope that your app will need.
                      "scope": "bot"}
        self.verification = os.environ.get("VERIFICATION_TOKEN")

        # NOTE: Python-slack requires a client connection to generate
        # an oauth token. We can connect to the client without authenticating
        # by passing an empty string as a token and then reinstantiating the
        # client with a valid OAuth token once we have one.
        self.client = SlackClient('')
        # We'll use this dictionary to store the state of each message object.
        # In a production environment you'll likely want to store this more
        # persistently in a database.
        self.messages = {}

        self.dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        self.table = self.dynamodb.Table('poor-webhook-tokens')

    def get_auth_code(self):
        try:
            response = self.table.get_item(
                Key={
                    'account_id': '207437628164'
                },
                AttributesToGet=[
                    'token'
                ]
            )

            return response['Item']['token']
        except Exception as e:
            print(e)
            return None

    def update_auth(self):
        auth_response = self.client.api_call(
            "oauth.access",
            client_id=self.oauth.get('client_id'),
            client_secret=self.oauth.get('client_secret'),
            code=self.get_auth_code()
        )

        response = self.table.put_item(
            Item={
                'account_id': '207437628164',
                'access_token': auth_response.get('access_token'),
                'bot_token': auth_response['bot']['bot_access_token']
            }
        )
        print(auth_response)
        return None

    def auth_info(self):
        try:
            response = self.table.get_item(
                Key={
                    'account_id': '207437628164'
                },
                AttributesToGet=[
                    'access_token',
                    'bot_token'
                ]
            )

            return response['Item']
        except Exception as e:
            print(e)
            return None

    def message_channel(self, channel, message):
        creds = self.auth_info()
        self.client = SlackClient(creds['bot_token'])
        response = message
        res = self.client.api_call(
            "chat.postMessage",
            channel=channel,
            text=response,
            attachments=None
        )
        print(res)
