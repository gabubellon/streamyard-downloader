import argparse
import calendar
from datetime import date, datetime

parser = argparse.ArgumentParser(
    description="Download finished streamns from StreamYard"
)

streamyard_group = parser.add_argument_group("streamyard")
s3_group = parser.add_argument_group("s3")

streamyard_group.add_argument(
    "--email",
    type=str,
    help="registred email on streamyard ",
    dest="email",
    required=True,
)

streamyard_group.add_argument(
    "-lc",
    "--list_choise",
    action="store_true",
    help="Show a list of streamns to dowload",
    dest="list_choise",
)

streamyard_group.add_argument(
    "-p",
    "--path",
    type=str,
    default="./files",
    help="local path to save downloads (default: ./files)",
    dest="path",
)

streamyard_group.add_argument(
    "-s",
    "--start_date",
    type=str,
    help="start date to filter data on streamyard (default: first day of current month)",
    default=date(datetime.now().year, datetime.now().month, 1).strftime("%Y-%m-%d"),
    dest="start_date",
)

streamyard_group.add_argument(
    "-e",
    "--end_date",
    type=str,
    help="end date to filter data on streamyard (default: last day of current month)",
    default=date(
        datetime.now().year,
        datetime.now().month,
        calendar.monthrange(
            datetime.now().year,
            datetime.now().month,
        )[1],
    ).strftime("%Y-%m-%d"),
    dest="end_date",
)

streamyard_group.add_argument(
    "-nl",
    "--new_login",
    action="store_true",
    help="Force a new login and ignore cookie cache (default: False)",
    dest="new_login",
)

streamyard_group.add_argument(
    "-c",
    "--chuck_size",
    type=int,
    default=1024,
    help="size in MB of chunks to downloa files (default: 1024)",
    dest="chuck_size",
)

streamyard_group.add_argument(
    "-t",
    "--threads",
    type=int,
    default=1,
    help="number of threads to run simultaneos (default: 1)",
    dest="threads",
)

s3_group.add_argument(
    "-s3",
    "--upload_s3",
    action="store_true",
    help="automatic upload files to a s3 bucket (defaul: False)",
    dest="upload",
)

s3_group.add_argument(
    "--bucket",
    type=str,
    help="s3 bucket to save files on formart s3://bucket-name",
    dest="bucket",
)

s3_group.add_argument(
    "--prefix",
    type=str,
    help="s3 prefix to save file on bucket",
    dest="prefix",
)

args = parser.parse_args()


def get_args_dict():

    streamyard_keys = [
        "email",
        "list_choise",
        "path",
        "start_date",
        "end_date",
        "new_login",
        "chuck_size",
        "threads",
        "upload",
    ]

    streamyard_args = {}
    for arg in streamyard_keys:
        streamyard_args[arg] = vars(args)[arg]

    return streamyard_args
