import os
import sqlite3
import pandas as pd

import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
from joblib import dump, load

scopes = ["https://www.googleapis.com/auth/youtube.readonly"]

con = sqlite3.connect("data.db")

def update_youtube_subscriptions():
    data = get_list_of_subscribed_channels()

    try:
        df = pd.read_sql('select * from youtube', con)
        youtube = pd.DataFrame(columns=list(df.columns))
        for channel in data:
            
            channelId = channel['snippet']['resourceId']['channelId']

            if channelId not in df['channel_id'].tolist():
                item = {
                        "channel_id": channelId,
                        "title": channel['snippet']['title'],
                        "description": channel['snippet']['description'],
                        "thumbnail_url": channel['snippet']['thumbnails']['high']['url']
                        }
                youtube = youtube.append(item, ignore_index=True)

        youtube.to_sql("youtube", con, if_exists='append', index=False)

    except pd.errors.DatabaseError as e:
        channelId = []
        title = []
        description = []
        thumbnail_url = []

        for channel in data:
            channelId.append(channel['snippet']['resourceId']['channelId'])
            title.append(channel['snippet']['title'])
            description.append(channel['snippet']['description'])
            thumbnail_url.append(channel['snippet']['thumbnails']['high']['url'])

        items = {
                "channel_id": channelId,
                "title": title,
                "description": description,
                "thumbnail_url": thumbnail_url
                }
        youtube = pd.DataFrame(items, columns=list(items.keys())) 

        youtube.to_sql("youtube", con, index=False)



def get_list_of_subscribed_channels():
    # Disable OAuthlib's HTTPS verification when running locally.
    # *DO NOT* leave this option enabled in production.
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    api_service_name = "youtube"
    api_version = "v3"
    client_secrets_file = "client_secret_youtube.json"

    # Get credentials and create an API client
    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
        client_secrets_file, scopes)
    credentials = flow.run_local_server()
    youtube = googleapiclient.discovery.build(
        api_service_name, api_version, credentials=credentials)

    data = []
    pageToken = ""
    while True:
        res = youtube.subscriptions().list(
        part="snippet,contentDetails",
        mine=True,
        maxResults=50,
        pageToken=pageToken if pageToken != "" else ""
        ).execute()
        v = res.get('items', [])
        if v:
            data.extend(v)
        pageToken = res.get('nextPageToken')
        if not pageToken:
            break

    return data    

update_youtube_subscriptions()
