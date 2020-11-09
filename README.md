# streamyeard-donwloader
Download Past Broadcast from StreamYard

# Install and use


* Set varibles

```shell
cp env.sample .env
```

Edit `EMAIL` to your StreamYard email and `LOCAL_DOWNLOAD_PATH` to a local path.

* Run
  
```shell
pip install -r requirements.txt
python src/streamyard_download.py
```

When see this messsage on terminal `Insira o código de login enviado para <EMAIL>:` insert the login code received on your email.

After this all past broadcast (.mp3 and . mp4) will be download to `LOCAL_DOWNLOAD_PATH`
