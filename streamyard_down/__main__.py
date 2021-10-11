import streamyard_down.args as args
from streamyard_down.streamyard import StreamYardDownload


def main():
    streamyardown = StreamYardDownload(**args.get_args_dict())
    streamyardown.start_download()

if __name__ == "__main__":
    main()
   
