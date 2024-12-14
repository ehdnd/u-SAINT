from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import os

class SlackNotifier:
    def __init__(self, token, channel_id):
        self.client = WebClient(token=token)
        self.channel_id = channel_id
    
    def send_message(self, text):
        try:
            self.client.chat_postMessage(channel=self.channel_id, text=text)
        except SlackApiError as e:
            print(f"Slack API error occurred: {e.response['error']}")