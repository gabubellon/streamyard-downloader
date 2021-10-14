# streamyard-downloader
Download Finished Broadcast from StreamYard

 # Install

```shell
pip install git+https://github.com/gabubellon/streamyard-downloader
```

# Usage

Call python script with `streamyard-downloader --email some@email.com`, `--email` has the unique necessary parameter.

When see this messsage on terminal `Insira o código de login enviado para <EMAIL>:` insert the login code received on your email.

After this all past broadcast (.mp3 and . mp4) will be download to `PATH` (./file by default)

Run `streamyard-downloader  -h` show all parameters can be used:

```shell
$ Download finished streamns from StreamYard
>
> optional arguments:
>  -h, --help            show this help message and exit
>  --email EMAIL         registred email on streamyard
>  -p PATH, --path PATH  local path to save downloads (default: ./files)
>  -s START_DATE, --start_date START_DATE
>                        start date to filter data on streamyard (default: first day of current month)
>  -e END_DATE, --end_date END_DATE
>                        end date to filter data on streamyard (default: last day of current month)
>  -nl, --new_login      Force a new login and ignore cookie cache (default: False)
>  -c CHUCK_SIZE, --chuck_size CHUCK_SIZE
>                        size in MB of chunks to downloa files (default: 1024)
>  -t THREADS, --threads THREADS
>                        number of threads to run simultaneos (default: 1)
>  -s3, --upload_s3      automatic upload files to a s3 bucket (defaul: False)
```

** To use auto upload to S3 bucket has necessary [AWS env vars](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-envvars.html) configured

## Make

Can use make commands to help:

```shell
make install # Install all requirements
make format  # Format python files
```
