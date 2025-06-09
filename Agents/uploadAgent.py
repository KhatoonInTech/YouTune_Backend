import os
from dotenv import load_dotenv
import pickle
import pprint
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

scopes = ["https://www.googleapis.com/auth/youtube.upload"]
credentials = None
token_path = "token.pickle"

# Load saved credentials if they exist
if os.path.exists(token_path):
    with open(token_path, "rb") as token_file:
        credentials = pickle.load(token_file)

# If no valid credentials available, run the OAuth flow
if not credentials or not credentials.valid:
    if credentials and credentials.expired and credentials.refresh_token:
        credentials.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file("client_secret.json", scopes)
        credentials = flow.run_local_server(port=0)
    # Save the credentials for next time
    with open(token_path, "wb") as token_file:
        pickle.dump(credentials, token_file)

youtube = build("youtube", "v3", credentials=credentials)

def upload_api_call(video_file, title, description, tags):
    """Upload a video to YouTube using the YouTube Data API."""
    request = youtube.videos().insert(
        part="snippet,status",
        body={
            "snippet": {
                "title": title,
                "description": description,
                "tags": tags,
                "categoryId": "22"  # Category ID for People & Blogs
            },
            "status": {
                "privacyStatus": "public"  # Change to 'private' or 'unlisted' as needed
            }
        },
        media_body=video_file
    )
    response = request.execute()
    return response.id


# r=upload_api_call(
#     video_file=r'C:\Users\Super\OneDrive\Desktop\Youtube Automation\Projects\Laptop_Maintenance_Tips_for_Beginners\Laptop_Maintenance_Tips_for_Beginners.mp4', 
#  title="Laptop Maintenance Tips for Beginners",
#  description="This video explains Laptop Maintenance Tips for Beginners", 
#  tags=["laptop", "maintenance", "tips", "beginners"])   
# # pprint.pprint(r)
# if r is None:
#     print("Error: Video upload failed.")
# else:
#     print(f"\n\nSuccess: your video is live at  https://www.youtube.com/watch?v={r}")