import json
import os
import re
import sys
import time
from concurrent import futures
from concurrent.futures import ProcessPoolExecutor

import requests
from loguru import logger

import config


class StreamYardDownload:
    def __init__(self):
        self.request_session = self.create_session()

    def create_session(self):
        logger.info("Criando Sessão")
        return requests.session()

    def download_file(self, file_name, request_url):
        show_log = True
        previus_done = None
        with open(os.path.join(config.LOCAL_DOWNLOAD_PATH, file_name), "wb") as f:
            print(
                f"Downloading {file_name} para {os.path.join(config.LOCAL_DOWNLOAD_PATH,file_name)}"
            )

            response = self.request_session.get(request_url, stream=True)
            total_length = response.headers.get("content-length")

            if total_length is None:
                f.write(response.content)
            else:
                dl = 0
                total_length = int(total_length)
                for data in response.iter_content(chunk_size=config.CHUNK_SIZE):
                    dl += len(data)
                    f.write(data)
                    done = int(100 * dl / total_length)

                    if done != previus_done:
                        show_log = True
                    if done in range(0, 100, 5) and show_log:
                        logger.info(f"Donwload do arquivo {file_name} em {done}%")
                        show_log = False
                        previus_done = done

    def get_cookie(self):
        logger.info("Carregando Cookie")
        self.request_session.get(config.TOKEN_URL)
        self.TOKEN = self.request_session.cookies["csrfToken"]

    @staticmethod
    def payload_token(token):
        return dict(email=config.EMAIL, csrfToken=token)

    def request_code(self):
        logger.info("Requisitando Código")

        self.request_session.post(
            config.CODE_URL,
            data=self.payload_token(self.TOKEN),
            headers=dict(Referer=config.CODE_URL),
        )

    @staticmethod
    def read_email_code():
        logger.info("Carregando Cookie")
        return input(f"Insira o código de login enviado para {config.EMAIL}:")

    @staticmethod
    def payload_login(token, email_code):
        return dict(email=config.EMAIL, csrfToken=token, otpToken=email_code)

    def login(self):
        logger.info("Acessando StreamYard")

        self.get_cookie()
        self.request_code()

        self.request_session.post(
            config.LOGIN_URL,
            data=self.payload_login(self.TOKEN, self.read_email_code()),
            headers=dict(Referer=config.LOGIN_URL),
        )

    def list_past_broadcast(self):
        logger.info("Carregando Broadcast")
        last_broadcast = self.request_session.get(config.LIST_PAST_URL)
        return json.loads(last_broadcast.text).get("broadcasts")

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

    def dowload(self,broadcast_to_download):

        with ProcessPoolExecutor(max_workers=int(config.MAX_THREADS)) as executor:
            future_executor = {
                executor.submit(
                    self.download_broadcast,
                    item
                ): item.get("stream_id")
                for item in broadcast_to_download[:2]
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

        while True:
            logger.info(f"Gerando Links de donwload")

            make_urls = self.request_session.get(
                config.CREATE_DOWNLOADS_URL.format(stream_id=stream_id)
            )
            status = json.loads(make_urls.text).get("status")

            logger.info(f"Status: {status}")

            if status != "creating":
                break

            time.sleep(10)

        download_url = self.request_session.get(
            config.DOWNLOAD_URL.format(stream_id=stream_id)
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


if __name__ == "__main__":
    streamyardown = StreamYardDownload()
    streamyardown.start_download()
