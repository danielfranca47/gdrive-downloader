"""
Downloader usando Google Drive API v3 com API key.
Alternativa confiável ao gdown para pastas públicas.
"""
import time
from pathlib import Path
from typing import Callable, List, Optional


def _human_size(n: int) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024:
            return f"{n:.0f} {unit}"
        n /= 1024
    return f"{n:.1f} GB"

import requests

DRIVE_API = "https://www.googleapis.com/drive/v3"
CHUNK_SIZE = 4 * 1024 * 1024  # 4 MB


class DriveAPIError(Exception):
    pass


def _get(url: str, params: dict, timeout: int = 30) -> dict:
    resp = requests.get(url, params=params, timeout=timeout)
    if resp.status_code == 403:
        data = resp.json()
        msg = data.get("error", {}).get("message", "Acesso negado")
        raise DriveAPIError(f"API Key inválida ou sem permissão: {msg}")
    if resp.status_code == 400:
        data = resp.json()
        msg = data.get("error", {}).get("message", "Requisição inválida")
        raise DriveAPIError(f"Erro na API: {msg}")
    resp.raise_for_status()
    return resp.json()


def list_folder(folder_id: str, api_key: str) -> List[dict]:
    """Lista todos os itens (arquivos e subpastas) de uma pasta do Drive."""
    items = []
    page_token = None
    while True:
        params = {
            "q": f"'{folder_id}' in parents and trashed = false",
            "fields": "nextPageToken, files(id, name, size, mimeType)",
            "key": api_key,
            "pageSize": 1000,
        }
        if page_token:
            params["pageToken"] = page_token
        data = _get(f"{DRIVE_API}/files", params)
        items.extend(data.get("files", []))
        page_token = data.get("nextPageToken")
        if not page_token:
            break
    return items


def download_file(
    file_id: str,
    dest_path: Path,
    api_key: str,
    resume: bool = False,
    progress_cb: Optional[Callable[[int, int], None]] = None,
) -> Path:
    """Baixa um único arquivo do Drive para dest_path (diretório ou arquivo)."""
    # Obtém metadata
    meta = _get(
        f"{DRIVE_API}/files/{file_id}",
        {"fields": "name,size", "key": api_key},
    )
    name = meta.get("name", file_id)
    total = int(meta.get("size") or 0)

    if dest_path.is_dir():
        out_file = dest_path / name
    else:
        out_file = dest_path

    # Suporte a resume
    start = 0
    headers = {}
    if resume and out_file.exists():
        start = out_file.stat().st_size
        if start >= total > 0:
            return out_file  # já completo
        headers["Range"] = f"bytes={start}-"

    download_url = f"{DRIVE_API}/files/{file_id}?alt=media&key={api_key}"
    resp = requests.get(download_url, headers=headers, stream=True, timeout=60)
    if resp.status_code == 416:  # Range Not Satisfiable → arquivo já completo
        return out_file
    resp.raise_for_status()

    mode = "ab" if start > 0 else "wb"
    downloaded = start
    with open(out_file, mode) as fh:
        for chunk in resp.iter_content(chunk_size=CHUNK_SIZE):
            if chunk:
                fh.write(chunk)
                downloaded += len(chunk)
                if progress_cb:
                    progress_cb(downloaded, total)

    return out_file


def download_folder(
    folder_id: str,
    output_dir: Path,
    api_key: str,
    resume: bool = False,
    status_cb: Optional[Callable[[str], None]] = None,
    progress_cb: Optional[Callable[[int, int], None]] = None,
) -> List[str]:
    """
    Baixa recursivamente todos os arquivos de uma pasta pública do Google Drive.
    Retorna lista de caminhos baixados.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    items = list_folder(folder_id, api_key)

    if not items:
        return []

    downloaded = []
    for item in items:
        mime = item.get("mimeType", "")
        name = item.get("name", item["id"])

        if mime == "application/vnd.google-apps.folder":
            # Subpasta: recursão
            sub_dir = output_dir / name
            if status_cb:
                status_cb(f"Entrando em subpasta: {name}")
            sub_files = download_folder(
                folder_id=item["id"],
                output_dir=sub_dir,
                api_key=api_key,
                resume=resume,
                status_cb=status_cb,
                progress_cb=progress_cb,
            )
            downloaded.extend(sub_files)

        elif mime.startswith("application/vnd.google-apps."):
            # Arquivos Google Workspace (Docs, Sheets…) — exportação não implementada
            if status_cb:
                status_cb(f"Ignorando arquivo Google Workspace: {name}")

        else:
            out_file = output_dir / name
            api_size = int(item.get("size") or 0)

            if out_file.exists():
                existing_size = out_file.stat().st_size
                if api_size > 0 and existing_size >= api_size:
                    # Arquivo completo — pula sem baixar
                    if status_cb:
                        status_cb(f"[SKIP] {name} ({_human_size(existing_size)})")
                    downloaded.append(str(out_file))
                    continue
                elif existing_size > 0 and resume:
                    # Arquivo parcial e resume ativado — retoma
                    if status_cb:
                        status_cb(
                            f"[RETOMANDO] {name} "
                            f"({_human_size(existing_size)} de {_human_size(api_size)})"
                        )
                else:
                    # Arquivo parcial sem resume, ou tamanho desconhecido — baixa do zero
                    if status_cb:
                        status_cb(f"[BAIXANDO] {name}")
            else:
                if status_cb:
                    status_cb(f"[BAIXANDO] {name}")

            path = download_file(
                file_id=item["id"],
                dest_path=output_dir,
                api_key=api_key,
                resume=resume,
                progress_cb=progress_cb,
            )
            downloaded.append(str(path))
            time.sleep(0.1)  # Pequena pausa para não estourar quota

    return downloaded
