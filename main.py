# Script to search someone's coments in Youtube
# Inspired by https://python.gotrained.com/youtube-api-extracting-comments/

import os
import csv 
import google.oauth2.credentials
 
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google_auth_oauthlib.flow import InstalledAppFlow
 
# The CLIENT_SECRETS_FILE variable specifies the name of a file that contains
# the OAuth 2.0 information for this application, including its client_id and
# client_secret.
CLIENT_SECRETS_FILE = "client_secret.json"

# This OAuth 2.0 access scope allows for full read/write access to the
# authenticated user's account and requires requests to use an SSL connection.
SCOPES = ['https://www.googleapis.com/auth/youtube.force-ssl']
API_SERVICE_NAME = 'youtube'
API_VERSION = 'v3'

def get_authenticated_service():
    flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
    credentials = flow.run_console()
    return build(API_SERVICE_NAME, API_VERSION, credentials = credentials)

def get_all_videos_comments(service, **kwargs):
    comments = []
    results = service.commentThreads().list(**kwargs).execute()
 
    cantidad = 0
    answer = 's'
    while results:
        for item in results['items']:
            cantidad = cantidad + 1
            name = item['snippet']['topLevelComment']['snippet']['authorDisplayName']
            author_url = item['snippet']['topLevelComment']['snippet']['authorChannelUrl']
            if author_url == "http://www.youtube.com/channel/UCg7fzx4PEk96-7Ec2Ol2dJA": # Test Susan (Youtube CEO) Channel ID
                print("\nFound!!!")
                video_id = item['snippet']['topLevelComment']['snippet']['videoId']
                comment = item['snippet']['topLevelComment']['snippet']['textDisplay']
                comment_id = item['snippet']['topLevelComment']['id']
                print([comment, video_id, comment_id])
                link = f'https://www.youtube.com/watch?v={video_id}&lc={comment_id}'
                comments.append([comment, link])
            else:
                print(f'\rVerificando {cantidad}... {name}                 ', end='')
                if cantidad % 100 == 0:
                    answer = input('Too many search, youtube can block you, Wanna continue? (y/n): ')
                    if answer == 'n':
                        break

        # Check if another page exists
        if answer == 'n':
            break
        elif 'nextPageToken' in results:
            kwargs['pageToken'] = results['nextPageToken']
            results = service.commentThreads().list(**kwargs).execute()
        else:
            break
 
    return comments

def write_to_csv(comments):
    with open('example_file.csv', 'a') as comments_file:
        comments_writer = csv.writer(comments_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        comments_writer.writerow(['Channel', 'Comment', 'Link'])
        for row in comments:
            comments_writer.writerow(list(row))

if __name__ == '__main__':
    # When running locally, disable OAuthlib's HTTPs verification. When
    # running in production *do not* leave this option enabled.
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
    service = get_authenticated_service()
    while True:
        canal_id = input('Youtube Channel ID: ')
        busqueda = input('Search term: ')
        final_result = []
        comments = get_all_videos_comments(service, part='snippet', allThreadsRelatedToChannelId=canal_id, searchTerms=busqueda, textFormat='plainText')
        final_result.extend([(canal_id, comment[0], comment[-1]) for comment in comments]) 
        write_to_csv(final_result)
        print("\nReady!, open the CSV file to see data")
        answer = input("Try again? (y/n): ")
        if answer == "n":
            break

