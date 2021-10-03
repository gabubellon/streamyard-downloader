import argparse
import calendar
from datetime import date, datetime

parser = argparse.ArgumentParser(description="Downlods from StreamYard")

parser.add_argument(
    "--email",
    type=str,
    help="registred email on streamyard",
    dest="email",
    required=True,
)

parser.add_argument(
    "-p",
    "--path",
    type=str,
    default="./files",
    help="local path to save downloads",
    dest="path",
)

parser.add_argument(
    "-s",
    "--start_date",
    type=date,
    help="start date to filter data on streamyard",
    default=date(datetime.now().year, datetime.now().month, 1),
    dest="start_date",
)

parser.add_argument(
    "-e",
    "--end_date",
    type=date,
    help="end date to filter data on streamyard",
    default=date(
        datetime.now().year,
        datetime.now().month,
        calendar.monthrange(
            datetime.now().year,
            datetime.now().month,
        )[1],
    ),
    dest="end_date",
)

parser.add_argument(
    "-nl",
    "--new_login",
    action="store_true",
    help="Force a new login and ignore cookie cache",
    dest="new_login",
)

parser.add_argument(
    "-c",
    "--chuck_size",
    type=int,
    default=1024,
    help="Size of chunks do Donwload files",
    dest="chuck_size",
)

parser.add_argument(
    "-t",
    "--threads",
    type=int,
    default=1,
    help="Number of threads to run simultaneos",
    dest="threads",
)

parser.add_argument(
    "-s3",
    "--upload_s3",
    action="store_true",
    help="limit data to result",
    dest="upload",
)

args = parser.parse_args()


def get_args_dict():
    return vars(args)
