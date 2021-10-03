import argparse
import calendar
from datetime import date, datetime

from streamyard_downloader import StreamYardDownload

parser = argparse.ArgumentParser(description="Donwload from StreamYard")

parser.add_argument(
    "-p",
    "--path",
    type=str,
    default="./files",
    help="Path local do save downaloads",
    dest="path",
)

parser.add_argument(
    "-s",
    "--start_date",
    type=date,
    help="Start Date to filter Videos",
    default=date(datetime.now().year, datetime.now().month, 1),
    dest="start_date",
)

parser.add_argument(
    "-e",
    "--end_date",
    type=date,
    help="End Date to filter Videos",
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
    help="Force a new login and ignore cache",
    dest="new_login",
)

parser.add_argument(
    "-u",
    "--upload",
    action="store_true",
    help="limit data to result",
    dest="upload",
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

if __name__ == "__main__":
    args = parser.parse_args()
    streamyardown = StreamYardDownload(**vars(args))
    streamyardown.start_download()
