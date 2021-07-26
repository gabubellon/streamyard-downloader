# streamyeard-donwloader
Download Past Broadcast from StreamYard

# Install and use


* Copy env file and configure:

```shell
cp env.sample .env
```

* Variables:
  * LOCAL_DOWNLOAD_PATH = <STRING>
    * Local path to download directory files (e.g. ./files). Directory will be create if not exists
    * Default = './files'
  * MAX_THREADS = <INT>
    * Max threads to do simultaneus downloads. Use to download more then one file per time.
    * Default = 1
  * CHUNK_SIZE = <INT>
    * Size do chunk files to disk. Need be less for your memory and respect max threads
    * Default: 1024
  * FILTER_DATE= <STRING>
    * Date used to filter files to donwload, on this moment only one day can be donwload 
    * Format = 'YYYY-MM-DD'
  * NEW_LOGIN = <True|False>
    * Boolean parameter to make a new login, if False will check if has a cached login and reuse last session
    * Default = True
  * AUTO_UPLOAD = <True|False>
    * If True make a automatic upload do a S3 bucket **
    * Defaut = False
  * S3_PREFIX = <STRING>
    * S3 prefix to upload files **
  * S3_BUCKET = <STRING>
    * S3 bucket to upload file (e.g s3://my-bucket-name/) **

** To use auto upload to S3 bucket has necessary [AWS env vars](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-envvars.html) configured

* Run
  
```shell
pip install -r requirements.txt
python src/down_streamyard.py
```

When see this messsage on terminal `Insira o código de login enviado para <EMAIL>:` insert the login code received on your email.

After this all past broadcast (.mp3 and . mp4) will be download to `LOCAL_DOWNLOAD_PATH`

Can use make commands to help:

```shell
make install # Install all requirements
make format  # Format python files
make run # Run donwloader
```
