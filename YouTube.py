import os
import random
import pickle
import pandas as pd
import numpy as np
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
key1 = 'AIzaSyDoAnzJYY5oro2WX4_3VQAqt3HeSncEwsg' #project 1 under eric.abel35@gmail.com personal account - limit: 10k
key2 = 'AIzaSyBLR-rq1OXLxo0Kvd0NYhWUU4nn9IfX-gE' #project 2 under eric.abel35@gmail.com personal account - limit: 10k

class YouTube():
    
    def __init__(self, api_key = key1, oauth = False, new_user = False):
        if oauth:
            credentials = None
            if os.path.exists('token.pickle') and not new_user:
                print('Loading Credentials From File...')
                with open('token.pickle', 'rb') as token:
                    credentials = pickle.load(token)
            if not credentials or not credentials.valid:
                if credentials and credentials.expired and credentials.refresh_token:
                        print('Refreshing Access Token...')
                        credentials.refresh(Request())
                else:
                    print('Fetching New Tokens...')
                    flow = InstalledAppFlow.from_client_secrets_file(
                        'client_secrets.json',
                        scopes=['https://www.googleapis.com/auth/youtube.force-ssl'])
                    flow.run_local_server(port=1234, prompt='consent', authorization_prompt_message='')
                    credentials = flow.credentials

        # Save the credentials for the next run
            with open('token.pickle', 'wb') as f:
                print('Saving Credentials for Future Use...')
                pickle.dump(credentials, f)
            print('done')
            
            self.yt = build('youtube', 'v3', credentials = credentials)
            
        else:
            self.key = api_key
            self.yt = build('youtube', 'v3', developerKey = self.key)
        
    #Use video id to pull video one of available meta data keys
    #returns either a single string value for a single id or a wrapped dictionary for list of ids with key value attached
    def video_meta(self, ids, key = 'title'):
        id_dic = {'ids': dict(zip(range(len(ids)), ids))}
        id_dic[key] = {}
        kwarg = ['publishedAt', 'channelId', 'title', 'description', 'thumbnails', 'channelTitle', 'tags', 'categoryId', 'liveBroadcastContent', 'localized', 'defaultAudioLanguage']
        if key not in kwarg:
            return str('This is not a valid key. Valid keys are:\n') + str(kwarg)
        else:
            if type(ids) == str:
                try:
                    return self.yt.videos().list(id = ids, part = 'snippet').execute().get('items', [])[0]['snippet'][key]
                except Exception as e:
                    return 'Your query resulted in this error: ' + str(e)
            else:
                for i in id_dic['ids']:
                    try:
                        id_dic[key][i] = self.yt.videos().list(id = i, part = 'snippet').execute().get('items', [])[0]['snippet'][key]
                    except Exception as e:
                        print('Your query resulted in this error: ' + str(e))
                        id_dic[key][i] = 'Error: No Data'
                return id_dic
    
    #returns all metadata for specified key
    def get_all(self, id = 'kJQP7kiw5Fk'):
        try:
            return self.yt.videos().list(id = id, part = 'snippet').execute().get('items', [])[0]
        except Exception as e:
            return 'Your query resulted in this error' + str(e)
    
    #returns search results from keyword and specified number of results
    #100 unit quota cost
    def search(self, query, num_results = 25):
        return self.yt.search().list(
            part="snippet",
            maxResults=num_results,
            q=query
            ).execute().get('items', [])
    
    #50 unit quota cost
    def insert_comment(self, id, text, contentOwner):
        return self.yt.commentThreads().insert(
            part="snippet",
            onBehalfOfContentOwner = contentOwner,
            body= {"snippet": {"videoId": id, 
                               "topLevelComment": {"snippet": {"textOriginal": text}}}}
            ).execute()
    
    #~55 unit quota cost
    def update(self, id, key, content, cms_usage = False):
        kwargs = ['title', 'description', 'tags']
        if key not in kwargs:
            return str('This is not a valid key. Valid keys are:\n') + str(kwarg)
        elif key == 'tags' and type(content) is not list:
            return str('tag update content must be in list format')
        elif cms_usage:
            current = self.get_all(id)
            channelId = current['snippet']['channelId']
            current['snippet'][key] = content
            self.yt.videos().update(
                part="snippet",
                onBehalfOfContentOwner= channelId,
                body={
                  "id": id,
                  "snippet": current['snippet']
                }).execute()
            return self.get_all(id)
        else:
            current = self.get_all(id)
            current['snippet'][key] = content
            self.yt.videos().update(
                part="snippet",
                body={
                  "id": id,
                  "snippet": current['snippet']
                }).execute()
            return self.get_all(id)
        
            
    
    def destroy():
        return 'Just Kidding'
    