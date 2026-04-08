import time
from pathlib import Path
from typing import Optional, Union

import gdown

from .api_downloader import DriveAPIError, download_file as api_download_file
from .api_downloader import download_folder as api_download_folder
from .logger import get_logger
from .progress import CLIProgressReporter, GUIProgressReporter
from .utils import extract_id_from_url, sanitize_output_path


def download(
    url: str,
    output_dir: str,
    progress_reporter: Optional[Union[CLIProgressReporter, GUIProgressReporter]] = None,
    speed_limit: Optional[int] = None,
    resume: bool = False,
    fuzzy: bool = True,
    log_dir: str = "logs",
    api_key: str = "",
) -> dict:
    """
    Função central de download. Chamada da mesma forma por CLI e GUI.

    Retorna dict com:
      success, output_path, elapsed_seconds, error, files_downloaded
    """
    logger = get_logger(log_dir=log_dir)
    result = {
        "success": False,
        "output_path": output_dir,
        "elapsed_seconds": 0.0,
        "error": None,
        "files_downloaded": [],
    }

    try:
        # 1. Valida URL
        drive_id, resource_type = extract_id_from_url(url)
        is_folder = resource_type == "folder"

        # 2. Valida e cria diretório de saída
        output_path = sanitize_output_path(output_dir)
        result["output_path"] = str(output_path)

        # 3. Anuncia início
        if progress_reporter:
            progress_reporter.announce_start(url, str(output_path), is_folder)

        is_gui = isinstance(progress_reporter, GUIProgressReporter)
        quiet = is_gui  # GUI usa quiet=True; CLI deixa tqdm do gdown aparecer

        t_start = time.monotonic()

        # 4. Executa download
        if is_folder:
            watch_target = str(output_path / drive_id)
            if progress_reporter:
                progress_reporter.start_watching(watch_target, drive_id)
            try:
                if api_key:
                    # Usa Google Drive API v3 — confiável para pastas públicas
                    def _status(msg):
                        logger.info(msg)

                    downloaded = api_download_folder(
                        folder_id=drive_id,
                        output_dir=output_path,
                        api_key=api_key,
                        resume=resume,
                        status_cb=_status,
                    )
                else:
                    downloaded = gdown.download_folder(
                        url=url,
                        output=str(output_path),
                        quiet=quiet,
                        resume=resume,
                        remaining_ok=True,
                    )
            finally:
                if progress_reporter:
                    progress_reporter.stop_watching()

            if downloaded:
                result["files_downloaded"] = downloaded if isinstance(downloaded, list) else [downloaded]
                result["success"] = True
            else:
                if api_key:
                    result["error"] = "Nenhum arquivo encontrado na pasta. Verifique o link e as permissões."
                else:
                    result["error"] = (
                        "gdown não conseguiu baixar a pasta. O Google bloqueou o acesso automático.\n"
                        "Solução: adicione uma Google API Key no campo correspondente da aplicação.\n"
                        "Veja o guia-de-uso.md para instruções de como obter a chave."
                    )

        else:
            if progress_reporter:
                progress_reporter.start_watching(str(output_path), drive_id)
            try:
                if api_key:
                    file_path = api_download_file(
                        file_id=drive_id,
                        dest_path=output_path,
                        api_key=api_key,
                        resume=resume,
                    )
                    downloaded = str(file_path) if file_path else None
                else:
                    output_file_hint = str(output_path) + "/"
                    downloaded = gdown.download(
                        url=url,
                        output=output_file_hint,
                        quiet=quiet,
                        fuzzy=fuzzy,
                        resume=resume,
                    )
            finally:
                if progress_reporter:
                    progress_reporter.stop_watching()

            if downloaded:
                result["files_downloaded"] = [downloaded]
                result["success"] = True
            else:
                result["error"] = "Não foi possível baixar o arquivo. Verifique se o link é público."

        elapsed = time.monotonic() - t_start
        result["elapsed_seconds"] = elapsed

        # 5. Anuncia resultado
        if result["success"]:
            if progress_reporter:
                progress_reporter.announce_finish(str(output_path), elapsed)
        else:
            if progress_reporter:
                progress_reporter.announce_error(result["error"])

    except DriveAPIError as e:
        result["error"] = str(e)
        logger.error(f"Erro na API do Google Drive: {e}")
        if progress_reporter:
            progress_reporter.stop_watching()
            progress_reporter.announce_error(str(e))

    except ValueError as e:
        result["error"] = str(e)
        logger.error(f"URL inválida: {e}")
        if progress_reporter:
            progress_reporter.stop_watching()
            progress_reporter.announce_error(str(e))

    except PermissionError as e:
        result["error"] = str(e)
        logger.error(f"Erro de permissão: {e}")
        if progress_reporter:
            progress_reporter.stop_watching()
            progress_reporter.announce_error(str(e))

    except Exception as e:
        result["error"] = str(e)
        logger.exception(f"Erro inesperado no download: {e}")
        if progress_reporter:
            progress_reporter.stop_watching()
            progress_reporter.announce_error(str(e))

    return result
