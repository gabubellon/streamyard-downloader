import json
import os
import pickle
import re
import time
from concurrent import futures
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime

import pandas as pd
import requests
from loguru import logger

import streamyard_down.config as cfg
import streamyard_down.s3 as s3


class StreamYardDownload:
    def __init__(
        self,
        email,
        path,
        start_date,
        end_date,
        new_login=False,
        threads=1,
        chuck_size=1024,
        list_choise=False,
        upload=False,
        bucket=None,
        prefix=None

    ):
        self.email = email
        self.path = path
        self.threads = threads
        self.chuck_size = chuck_size
        self.new_login = new_login
        self.upload = upload
        self.bucket = bucket
        self.prefix = prefix
        self.start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
        self.end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
        self.request_session = self.create_session()
        self.list_choise = list_choise
        self._types=["individualAudio","video"]
        self.quit = False

    def create_session(self):
        logger.info("Creating session...")
        return requests.session()

    def download_file(self, file_name, request_url,zip=False):
        show_log = True
        previus_done = None
        os.makedirs(self.path, exist_ok=True)
        full_file = os.path.join(self.path, file_name)
        with open(full_file, "wb") as f:
            logger.info(
                f"Downloading {file_name} to {full_file}"
            )

            response = self.request_session.get(request_url, stream=True)
            total_length = response.headers.get("content-length")

            if total_length is None or zip:
                f.write(response.content)
            else:
                dl = 0
                total_length = int(total_length)
                for data in response.iter_content(chunk_size=self.chuck_size):
                    dl += len(data)
                    f.write(data)
                    done = int(100 * dl / total_length)

                    if done != previus_done:
                        show_log = True
                    if done in range(0, 100, 5) and show_log:
                        logger.info(f"Download progress of file {file_name} is at {done}%")
                        show_log = False
                        previus_done = done

        # TODO implement upload
        if self.upload:
            s3.send_to_s3(full_file,self.bucket,self.prefix)

    def get_cookie(self):
        logger.info("Loading cookie...")
        self.request_session.get(cfg.TOKEN_URL)
        self.TOKEN = self.request_session.cookies["csrfToken"]


    def payload_token(self,token):
        return dict(email=self.email, csrfToken=token)

    def request_code(self):
        logger.info("Requesting code...")

        self.request_session.post(
            cfg.CODE_URL,
            data=self.payload_token(self.TOKEN),
            headers=dict(Referer=cfg.CODE_URL),
        )

    def read_email_code(self):
        logger.info("Loading cookie...")
        return input(f"Insert the login code sent to {self.email}:")


    def payload_login(self,token, email_code):
        return dict(email=self.email, csrfToken=token, otpToken=email_code)

    def login(self):
        logger.info("Acessing StreamYard...")

        if self.new_login:
            logger.info("New login")
            self.get_cookie()
            self.request_code()

            self.request_session.post(
                cfg.LOGIN_URL,
                data=self.payload_login(self.TOKEN, self.read_email_code()),
                headers=dict(Referer=cfg.LOGIN_URL),
            )
        elif os.path.exists("./cache_session.pkl"):
            logger.info("Loading cache...")
            with open("./cache_session.pkl", "rb") as f:
                self.request_session.cookies.update(pickle.load(f))
        else:
            logger.info("Login is necessary")
            self.get_cookie()
            self.request_code()

            self.request_session.post(
                cfg.LOGIN_URL,
                data=self.payload_login(self.TOKEN, self.read_email_code()),
                headers=dict(Referer=cfg.LOGIN_URL),
            )

        # TOKEN SECUNDARIO POS DONWLOAD
        self.LOGGED_TOKEN = self.request_session.cookies["csrfToken"]
        with open("./cache_session.pkl", "wb") as f:
            pickle.dump(self.request_session.cookies, f)

    def list_past_broadcast(self):
        logger.info(
            f"Loading broadcasts between {self.start_date.strftime('%Y-%m-%d') } and {self.end_date.strftime('%Y-%m-%d') }"
        )
        last_broadcast = self.request_session.get(cfg.LIST_PAST_URL)

        stream_df = pd.DataFrame(json.loads(last_broadcast.text).get("broadcasts"))
        columns = [
            "date",
            "datetime",
            "id",
            "title",
        ]
        stream_df["date"] = (
            pd.to_datetime(stream_df.startedAt)
            .dt.tz_convert("America/Sao_Paulo")
            .dt.date
        )
        stream_df["datetime"] = (
            pd.to_datetime(stream_df.startedAt)
            .dt.tz_convert("America/Sao_Paulo").dt.strftime('%Y%m%d_%H%M%S')
        )

        stream_df = stream_df[columns]

        return stream_df.query(
            "date >= @self.start_date and date <= @self.end_date"
        ).to_dict(orient="records")


    def create_download_list(self):
        broadcasts = self.list_past_broadcast()
        logger.info("Gathering broadcasts to download...")
        broadcast_to_download = []
        for broadcast in broadcasts:
            file_name = re.sub('[\W]+', '', broadcast.get('title').replace(' ', '_')).rstrip().lstrip()
            file_name = (f"{file_name}_{broadcast.get('datetime')}").lower()
            broadcast_to_download.append(
                dict(
                    stream_id=broadcast.get("id"),
                    stream_date=broadcast.get("date"),
                    stream_datetime=broadcast.get("datetime"),
                    file_name=file_name,
                    audio_filename=f"{file_name}.mp3",
                    video_filename=f"{file_name}.mp4",
                    indivial_filename=f"{file_name}.zip"
                )
            )
        return broadcast_to_download

    def dowload(self, broadcast_to_download):
        with ProcessPoolExecutor(max_workers=int(self.threads)) as executor:
            future_executor = {
                executor.submit(self.download_broadcast, item): item.get("stream_id")
                for item in broadcast_to_download
            }

        for future in futures.as_completed(future_executor):
            file_name = future.result()
            logger.info(f"Download of stream {file_name} is now complete")

    def download_broadcast(self, stream_info):
        while not self.quit:
            stream_id = stream_info.get("stream_id")
            file_name = stream_info.get("file_name")
            video_filename = stream_info.get("video_filename")
            audio_filename = stream_info.get("audio_filename")
            indivial_filename = stream_info.get("indivial_filename")

            logger.info(f"Download stream id:{stream_id} name:{file_name}")

            # ESSA CHAMADA NÃO FUNCIONA PELA API, APENAS ENTRANDO NO SITE E CLICANDO NO BOTÃO
            get_url = self.request_session.post(
                cfg.CREATE_DOWNLOADS_URL.format(stream_id=stream_id),
                data=dict(csrfToken=self.LOGGED_TOKEN),
                headers=dict(Referer=cfg.BROAD_CAST_URL),
            )

            logger.info(f"{get_url.text}")

            while True:
                logger.info(f"Generating download links...")

                # COMO A CHAMADA NEM SEMPRE FUNCIONA ESSE REQUEST RETORNA ESSE
                make_urls = self.request_session.get(
                    cfg.CREATE_DOWNLOADS_URL.format(stream_id=stream_id)
                )

                logger.info(f"{make_urls.text}")
                status = json.loads(make_urls.text).get("status")

                logger.info(f"Status: {status}")

                if status != "creating":
                    break

                time.sleep(10)

            for type in self._types:
                download_url = self.request_session.get(
                    cfg.DOWNLOAD_URL.format(stream_id=stream_id,type=type)
                )
                
                if type=="individualAudio" and json.loads(download_url.text).get("audioUrl"):
                    logger.info(f"Downloading .zip file...")
                    self.download_file(
                        file_name=indivial_filename,
                        request_url=json.loads(download_url.text).get("audioUrl"),
                        zip=False
                    )

                if type=="video": 

                    if json.loads(download_url.text).get("videoUrl"):
                        logger.info(f"Downloading video file...")
                        self.download_file(
                            file_name=video_filename,
                            request_url=json.loads(download_url.text).get("videoUrl"),
                        )

                    if json.loads(download_url.text).get("audioUrl"):
                        logger.info(f"Downloading audio file...")
                        self.download_file(
                            file_name=audio_filename,
                            request_url=json.loads(download_url.text).get("audioUrl"),
                        )
            return file_name
        return

    def start_download(self):
        self.login()
        download_list = self.create_download_list()
        options = """"""
        for index, item in enumerate(download_list):
            options += f"** ID:{index} - STREAM:{item.get('file_name')} - DATE:{item.get('stream_datetime')}\n    "

        to_download = []
        if self.list_choise:
            message = f"""
            ############################
            LISTING STREAMS BETWEEN {self.start_date.strftime('%Y-%m-%d') } AND {self.end_date.strftime('%Y-%m-%d') }
            CHOOSE WHICH FILES YOU WISH TO DOWNLOAD INFORMING THEIR IDs SEPARATED BY COMMA (",")
            EXAMPLES:
                0,1,2,3  # to download files with IDs 0, 1, 2 and 3
                1  # to download only the file with ID 1

            IDs to download:

            ##### STREAM LIST #####:

            {options}

            Select IDs:
            """
            ids = input(message)

            to_download = []
            escolhas = ""
            for id in ids.split(","):

                data = download_list[int(id)]
                escolhas += f"** ID:{id} - STREAM:{data.get('file_name')} - DATE:{data.get('stream_date')}\n"
                to_download.append(data)
            print(f"The following IDs will be downloaded: {ids}\n{escolhas}")
        else:
            to_download = download_list

        try:
            self.dowload(to_download)
        except KeyboardInterrupt:
            self.quit = True
