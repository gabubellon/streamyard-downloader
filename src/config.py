from datetime import datetime

from decouple import config

TOKEN_URL = "https://streamyard.com/login"
CODE_URL = "https://streamyard.com/api/user/login"
LOGIN_URL = "https://streamyard.com/api/user/otp_token"
CREATE_DOWNLOADS_URL = "https://streamyard.com/api/broadcasts/{stream_id}/vod"
DOWNLOAD_URL = "https://streamyard.com/api/broadcasts/{stream_id}/vod_download_urls"
LIST_PAST_URL = "https://streamyard.com/api/broadcasts?limit=99&isComplete=true"
BROAD_CAST_URL = "https://streamyard.com/api/broadcasts/"

NEW_LOGIN = config("NEW_LOGIN", cast=bool, default=True)
AUTO_UPLOAD = config("AUTO_UPLOAD", cast=bool, default=False)
S3_PREFIX = config("S3_PREFIX")
S3_BUCKET = config("S3_BUCKET")
EMAIL = config("EMAIL")
LOCAL_DOWNLOAD_PATH = config("LOCAL_DOWNLOAD_PATH", default="./files")
CHUNK_SIZE = config("CHUNK_SIZE", default=1024, cast=int)
MAX_THREADS = config("MAX_THREADS", default=1, cast=int)
FILTER_DATE = datetime.strptime(config("FILTER_DATE"), "%Y-%m-%d").date()
