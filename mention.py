import boto3
import requests
import os


def get_event_from_dynamo(event_id):
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('poor-webhook-events')

    res = table.get_item(
        Key={
            'X-Github-Delivery': event_id
        }
    )

    return res

def react(message, bot):
    """React to messages sent directly to the bot."""
    try:
        if 'get changelog' in message:
            filename = message.split('||')[1]
            filename = filename.split('||')[0]

            event_id = message.split('event ')[1]
            event_id = event_id.split('.')[0]

            event = (get_event_from_dynamo(event_id))

            url = "https://raw.githubusercontent.com/{org}/{repository}/{tree_id}/{filename}".format(
                org=event['Item']['organization']['login'],
                repository=event['Item']['repository']['name'],
                tree_id=event['Item']['head_commit']['id'],
                filename=filename
            )

            try:
                r = requests.get(url)
                F = open('/tmp/' + filename, 'w')
                F.write(r.text)
                F.close()
            except Exception as e:
                print('Could not write file because {e}'.format(e=e))

            try:
                content = os.popen("cat /tmp/" + filename).read()
                #os.popen("/usr/local/bin/grip /tmp/" + filename + ' --export ' + '/tmp/' + filename + '.html').read()
            except Exception as e:
                print(e)


            print(content)
            print(os.popen("ls /tmp").read())
            slack_message = "Here's the changelog you asked for: \n {changelog}".format(changelog=content)
            bot.message_channel(
                '#general',
                slack_message
            )

            response = {
                "statusCode": 200,
                "body": "",
                "headers": {
                    "Content-Type": "text/html",
                    "X-Slack-No-Retry": 1
                }
            }

            return response

    except Exception as e:
        print(e)
