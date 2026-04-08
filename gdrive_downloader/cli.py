import argparse
import sys

from colorama import init as colorama_init
from colorama import just_fix_windows_console

from .core import download
from .logger import get_logger
from .progress import CLIProgressReporter


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="gdrive-dl",
        description="Baixa arquivos ou pastas do Google Drive via links públicos.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Exemplos:\n"
            "  python main.py \"https://drive.google.com/file/d/ID/view\" -o C:\\Downloads\n"
            "  python main.py \"https://drive.google.com/drive/folders/ID\" -o C:\\Downloads\\Pasta\n"
            "  python main.py URL -o C:\\Downloads --speed 512 --resume\n"
        ),
    )
    parser.add_argument(
        "url",
        help="Link público do Google Drive (arquivo ou pasta)",
    )
    parser.add_argument(
        "-o", "--output",
        required=True,
        metavar="DIRETÓRIO",
        help="Diretório local de destino",
    )
    parser.add_argument(
        "--speed",
        type=int,
        default=None,
        metavar="KB/s",
        help="Limite de velocidade em KB/s (ex: 512 para 512 KB/s)",
    )
    parser.add_argument(
        "--resume",
        action="store_true",
        help="Retomar download interrompido",
    )
    parser.add_argument(
        "--log-dir",
        default="logs",
        metavar="DIRETÓRIO",
        help="Diretório para arquivos de log (padrão: logs/)",
    )
    parser.add_argument(
        "--no-color",
        action="store_true",
        help="Desativar saída colorida no terminal",
    )
    return parser


def run_cli(argv=None) -> int:
    """Ponto de entrada da CLI. Retorna 0 em sucesso, 1 em erro."""
    just_fix_windows_console()
    colorama_init(autoreset=True)

    # Garante saída UTF-8 no Windows (evita UnicodeEncodeError com símbolos)
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")

    parser = build_parser()
    args = parser.parse_args(argv)

    if args.no_color:
        import colorama
        colorama.deinit()

    logger = get_logger(log_dir=args.log_dir)
    reporter = CLIProgressReporter(logger)

    speed_bytes = args.speed * 1024 if args.speed else None

    result = download(
        url=args.url,
        output_dir=args.output,
        progress_reporter=reporter,
        speed_limit=speed_bytes,
        resume=args.resume,
        log_dir=args.log_dir,
    )

    if result["success"]:
        n = len(result["files_downloaded"])
        print(f"  {n} arquivo(s) salvo(s) em: {result['output_path']}")
        print(f"  Log: {args.log_dir}/gdrive_downloader.log")
        return 0
    else:
        print(f"  Verifique o log em: {args.log_dir}/gdrive_downloader.log")
        return 1
