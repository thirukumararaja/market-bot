import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.auth.exceptions import RefreshError

# -----------------------------
# CONFIG
# -----------------------------
SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
CLIENT_SECRETS_FILE = "client_secret.json"
TOKEN_FILE = "token.pickle"


# -----------------------------
# AUTHENTICATION
# -----------------------------
def get_authenticated_service():
    creds = None

    # Load token if exists
    if os.path.exists(TOKEN_FILE):
        try:
            with open(TOKEN_FILE, "rb") as f:
                creds = pickle.load(f)
        except Exception:
            creds = None

    # If token invalid or expired → force re-login
    if not creds:
        print("🔐 Starting YouTube OAuth flow...")
        flow = InstalledAppFlow.from_client_secrets_file(
            CLIENT_SECRETS_FILE,
            SCOPES
        )

        creds = flow.run_local_server(
            port=0,
            prompt="select_account"
        )

        with open(TOKEN_FILE, "wb") as f:
            pickle.dump(creds, f)

    return build("youtube", "v3", credentials=creds)


# -----------------------------
# VIDEO UPLOAD
# -----------------------------
def upload_video(
    file_path: str,
    title: str,
    description: str,
    tags=None,
    categoryId="28",
    privacyStatus="public"
):
    """
    Uploads a video safely.
    Will NOT crash the app if auth fails.
    """
    try:
        youtube = get_authenticated_service()

        media = MediaFileUpload(
            file_path,
            chunksize=-1,
            resumable=True
        )

        request = youtube.videos().insert(
            part="snippet,status",
            body={
                "snippet": {
                    "title": title,
                    "description": description,
                    "tags": tags or [],
                    "categoryId": categoryId
                },
                "status": {
                    "privacyStatus": privacyStatus,
                    "selfDeclaredMadeForKids": False
                }
            },
            media_body=media
        )

        response = request.execute()
        print("✅ Upload successful!")
        print("🎥 Video ID:", response["id"])
        return response["id"]

    except RefreshError:
        print("❌ YouTube token expired or revoked.")
        print("➡️ Delete token.pickle and re-run to re-authenticate.")
        return None

    except Exception as e:
        print("❌ YouTube upload failed:", e)
        return None
