import argparse
import calendar
from datetime import date, datetime

parser = argparse.ArgumentParser(description="Download finished streamns from StreamYard")

parser.add_argument(
    "--email",
    type=str,
    help="registred email on streamyard ",
    dest="email",
    required=True,
)

parser.add_argument(
    "-lc",
    "--list_choise",
    action="store_true",
    help="Show a list of streamns to dowload",
    dest="list_choise",
)

parser.add_argument(
    "-p",
    "--path",
    type=str,
    default="./files",
    help="local path to save downloads (default: ./files)",
    dest="path",
)

parser.add_argument(
    "-s",
    "--start_date",
    type=date,
    help="start date to filter data on streamyard (default: first day of current month)",
    default=date(datetime.now().year, datetime.now().month, 1),
    dest="start_date",
)

parser.add_argument(
    "-e",
    "--end_date",
    type=date,
    help="end date to filter data on streamyard (default: last day of current month)",
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
    help="Force a new login and ignore cookie cache (default: False)",
    dest="new_login",
)

parser.add_argument(
    "-c",
    "--chuck_size",
    type=int,
    default=1024,
    help="size in MB of chunks to downloa files (default: 1024)",
    dest="chuck_size",
)

parser.add_argument(
    "-t",
    "--threads",
    type=int,
    default=1,
    help="number of threads to run simultaneos (default: 1)",
    dest="threads",
)

parser.add_argument(
    "-s3",
    "--upload_s3",
    action="store_true",
    help="automatic upload files to a s3 bucket (defaul: False)",
    dest="upload",
)

args = parser.parse_args()


def get_args_dict():
    return vars(args)
