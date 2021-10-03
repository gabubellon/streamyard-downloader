from decouple import config

TOKEN_URL = "https://streamyard.com/login"
CODE_URL = "https://streamyard.com/api/user/login"
LOGIN_URL = "https://streamyard.com/api/user/otp_token"
CREATE_DOWNLOADS_URL = "https://streamyard.com/api/broadcasts/{stream_id}/vod"
DOWNLOAD_URL = "https://streamyard.com/api/broadcasts/{stream_id}/vod_download_urls"
LIST_PAST_URL = "https://streamyard.com/api/broadcasts?limit=99&isComplete=true"
BROAD_CAST_URL = "https://streamyard.com/api/broadcasts/"


S3_PREFIX = config("S3_PREFIX")
S3_BUCKET = config("S3_BUCKET")
EMAIL = config("EMAIL")
