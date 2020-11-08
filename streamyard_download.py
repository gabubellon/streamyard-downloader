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


def download_file(file_name, request_session, request_url):
    show_log = True
    previus_done = None
    with open(os.path.join(config.LOCAL_DOWNLOAD_PATH, file_name), "wb") as f:
        print(
            f"Downloading {file_name} para {os.path.join(config.LOCAL_DOWNLOAD_PATH,file_name)}"
        )

        response = request_session.get(request_url, stream=True)
        total_length = response.headers.get("content-length")

        if total_length is None:
            f.write(response.content)
        else:
            dl = 0
            total_length = int(total_length)
            for data in response.iter_content(chunk_size=4096):
                dl += len(data)
                f.write(data)
                done = int(100 * dl / total_length)

                if done != previus_done:
                    show_log = True
                if done in range(0, 100, 5) and show_log:
                    logger.info(f"Donwload do arquivo {file_name} em {done}%")
                    show_log = False
                    previus_done = done

def create_session():
    logger.info("Criando Sessão")
    return requests.session()


def get_cookie(request_session):
    logger.info("Carregando Cookie")
    request_session.get(config.TOKEN_URL)
    config.TOKEN = request_session.cookies["csrfToken"]


def payload_token():
    return dict(email=config.EMAIL, csrfToken=config.TOKEN)


def request_code(request_session):
    logger.info("Requisitando Código")
    request_session.post(
        config.CODE_URL, data=payload_token(), headers=dict(Referer=config.CODE_URL)
    )


def read_email_code():
    logger.info("Carregando Cookie")
    return input(f"Insira o código de login enviado para {config.EMAIL}:")


def payload_login(email_code):
    return dict(email=config.EMAIL, csrfToken=config.TOKEN, otpToken=email_code)


def login_streamyard(request_session):
    logger.info("Acessando StreamYard")
    request_session.post(
        config.LOGIN_URL,
        data=payload_login(read_email_code()),
        headers=dict(Referer=config.LOGIN_URL),
    )


def list_past_broadcast(request_session):
    logger.info("Carregando Broadcast")
    last_broadcast = request_session.get(config.LIST_PAST_URL)
    return json.loads(last_broadcast.text).get("broadcasts")


def create_download_list(request_session):
    broadcasts = list_past_broadcast(request_session)
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


def start_donwload(request_session):
    broadcast_to_download = create_download_list(request_session)

    with ProcessPoolExecutor(max_workers=int(config.MAX_THREADS)) as executor:
        future_executor = {
            executor.submit(download_broadcast, request_session, item): item.get(
                "stream_id"
            )
            for item in broadcast_to_download
        }

    for future in futures.as_completed(future_executor):
        file_name = future.result()
        logger.info(f"Download da stream {file_name} completo ")


def download_broadcast(request_session, stream_info):
    stream_id = stream_info.get("stream_id")
    file_name = stream_info.get("file_name")
    video_filename = stream_info.get("video_filename")
    audio_filename = stream_info.get("audio_filename")

    logger.info(f"Download stream id:{stream_id} name:{file_name}")

    while True:
        logger.info(f"Gerando Links de donwload")

        make_urls = request_session.get(
            config.CREATE_DOWNLOADS_URL.format(stream_id=stream_id)
        )
        status = json.loads(make_urls.text).get("status")

        logger.info(f"Status: {status}")

        if status != "creating":
            break

        time.sleep(10)

    download_url = request_session.get(config.DOWNLOAD_URL.format(stream_id=stream_id))

    logger.info(f"Download do audio")
    download_file(
        file_name=audio_filename,
        request_session=request_session,
        request_url=json.loads(download_url.text).get("audioUrl"),
    )
    
    logger.info(f"Download do video")
    download_file(
        file_name=video_filename,
        request_session=request_session,
        request_url=json.loads(download_url.text).get("videoUrl"),
    )

    return file_name


if __name__ == "__main__":
    request_session = create_session()
    get_cookie(request_session)
    request_code(request_session)
    login_streamyard(request_session)
    start_donwload(request_session)
