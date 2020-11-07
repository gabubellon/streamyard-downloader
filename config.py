from decouple import config

TOKEN_URL = "https://streamyard.com/login"
CODE_URL = "https://streamyard.com/api/user/login"
LOGIN_URL = "https://streamyard.com/api/user/otp_token"
CREATE_DOWNLOADS_URL = "https://streamyard.com/api/broadcasts/{stream_id}/vod"
DOWNLOAD_URL = "https://streamyard.com/api/broadcasts/{stream_id}/vod_download_urls"
LIST_PAST_URL = "https://streamyard.com/api/broadcasts?isComplete=true"

EMAIL = config("EMAIL")
LOCAL_DOWNLOAD_PATH = config("LOCAL_DOWNLOAD_PATH")
TOKEN = ""
CODE = ""
