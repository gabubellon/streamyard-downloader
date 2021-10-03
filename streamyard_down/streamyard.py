import json
import os
import pickle
import re
import time
from concurrent import futures
from concurrent.futures import ProcessPoolExecutor

import boto3
import pandas as pd
import requests
from loguru import logger

import streamyard_down.config as cfg


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
        upload=False,
    ):
        self.email = email
        self.path = path
        self.threads = threads
        self.chuck_size = chuck_size
        self.new_login = new_login
        self.upload = upload
        self.start_date = start_date
        self.end_date = end_date
        self.request_session = self.create_session()

    def create_session(self):
        logger.info("Criando Sessão")
        return requests.session()

    def download_file(self, file_name, request_url):
        show_log = True
        previus_done = None
        os.makedirs(self.path, exist_ok=True)
        with open(os.path.join(self.path, file_name), "wb") as f:
            logger.info(
                f"Downloading {file_name} para {os.path.join(self.path,file_name)}"
            )

            response = self.request_session.get(request_url, stream=True)
            total_length = response.headers.get("content-length")

            if total_length is None:
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
                        logger.info(f"Donwload do arquivo {file_name} em {done}%")
                        show_log = False
                        previus_done = done

        if self.upload:
            self.send_to_s3(os.path.join(self.path, file_name))

    def get_cookie(self):
        logger.info("Carregando Cookie")
        self.request_session.get(cfg.TOKEN_URL)
        self.TOKEN = self.request_session.cookies["csrfToken"]

    @staticmethod
    def payload_token(token):
        return dict(email=self.email, csrfToken=token)

    def request_code(self):
        logger.info("Requisitando Código")

        self.request_session.post(
            cfg.CODE_URL,
            data=self.payload_token(self.TOKEN),
            headers=dict(Referer=cfg.CODE_URL),
        )

    @staticmethod
    def read_email_code():
        logger.info("Carregando Cookie")
        return input(f"Insira o código de login enviado para {self.email}:")

    @staticmethod
    def payload_login(token, email_code):
        return dict(email=self.email, csrfToken=token, otpToken=email_code)

    def login(self):
        logger.info("Acessando StreamYard")

        if self.new_login:
            logger.info("Novo Login")
            self.get_cookie()
            self.request_code()

            self.request_session.post(
                cfg.LOGIN_URL,
                data=self.payload_login(self.TOKEN, self.read_email_code()),
                headers=dict(Referer=cfg.LOGIN_URL),
            )
        elif os.path.exists("./cache_session.pkl"):
            logger.info("Carregando Cache")
            with open("./cache_session.pkl", "rb") as f:
                self.request_session.cookies.update(pickle.load(f))
        else:
            logger.info("Login Necessário")
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
            f"Carregando Broadcast entre os dias {self.start_date.strftime('%Y-%m-%d') } e {self.end_date.strftime('%Y-%m-%d') }"
        )
        last_broadcast = self.request_session.get(cfg.LIST_PAST_URL)

        stream_df = pd.DataFrame(json.loads(last_broadcast.text).get("broadcasts"))
        columns = [
            "date",
            "id",
            "title",
        ]
        stream_df["date"] = (
            pd.to_datetime(stream_df.startedAt)
            .dt.tz_convert("America/Sao_Paulo")
            .dt.date
        )
        stream_df = stream_df[columns]

        return stream_df.query(
            "date >= @self.start_date and date <= @self.end_date"
        ).to_dict(orient="records")

    def create_download_list(self):
        broadcasts = self.list_past_broadcast()
        logger.info("Separando Broadcast Para Download")
        broadcast_to_download = []
        for broadcast in broadcasts:
            file_name = re.sub("[\W]+", "", broadcast.get("title").replace(" ", "_"))
            broadcast_to_download.append(
                dict(
                    stream_id=broadcast.get("id"),
                    file_name=file_name,
                    audio_filename=f"{file_name}.mp3",
                    video_filename=f"{file_name}.mp4",
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
            logger.info(f"Download da stream {file_name} completo ")

    def download_broadcast(self, stream_info):
        stream_id = stream_info.get("stream_id")
        file_name = stream_info.get("file_name")
        video_filename = stream_info.get("video_filename")
        audio_filename = stream_info.get("audio_filename")

        logger.info(f"Download stream id:{stream_id} name:{file_name}")

        # ESSA CHAMADA NÃO FUNCIONA PELA API, APENAS ENTRANDO NO SITE E CLICANDO NO BOTÃO
        get_url = self.request_session.post(
            cfg.CREATE_DOWNLOADS_URL.format(stream_id=stream_id),
            data=dict(csrfToken=self.LOGGED_TOKEN),
            headers=dict(Referer=cfg.BROAD_CAST_URL),
        )

        logger.info(f"{get_url.text}")

        while True:
            logger.info(f"Gerando Links de download")

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

        download_url = self.request_session.get(
            cfg.DOWNLOAD_URL.format(stream_id=stream_id)
        )

        if json.loads(download_url.text).get("audioUrl"):
            logger.info(f"Download do audio")
            self.download_file(
                file_name=audio_filename,
                request_url=json.loads(download_url.text).get("audioUrl"),
            )

        if json.loads(download_url.text).get("videoUrl"):
            logger.info(f"Download do video")
            self.download_file(
                file_name=video_filename,
                request_url=json.loads(download_url.text).get("videoUrl"),
            )

        return file_name

    def start_download(self):
        self.login()
        self.dowload(self.create_download_list())

    def send_to_s3(self, sent_file):
        key = "{}/{}".format(cfg.S3_PREFIX, os.path.basename(sent_file))
        logger.info(f"Sending {sent_file} to bucket s3://{cfg.S3_BUCKET}/{key}")

        s3_client = boto3.client("s3")
        s3_client.upload_file(sent_file, cfg.S3_BUCKET, key)

        os.remove(sent_file)
