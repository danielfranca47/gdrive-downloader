import sys


def main():
    if "--gui" in sys.argv:
        from gdrive_downloader.gui import run_gui
        run_gui()
    else:
        from gdrive_downloader.cli import run_cli
        sys.exit(run_cli())


if __name__ == "__main__":
    main()
