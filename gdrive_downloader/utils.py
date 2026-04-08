import re
from pathlib import Path


def extract_id_from_url(url: str) -> tuple:
    """
    Extrai o ID e tipo de recurso de uma URL do Google Drive.
    Retorna (id, 'file'|'folder').
    Lança ValueError se a URL não for reconhecida.
    """
    # Formato: /drive/folders/{ID}
    match = re.search(r"/drive(?:/u/\d+)?/folders/([a-zA-Z0-9_-]+)", url)
    if match:
        return match.group(1), "folder"

    # Formato: /file/d/{ID}
    match = re.search(r"/file/d/([a-zA-Z0-9_-]+)", url)
    if match:
        return match.group(1), "file"

    # Formato: ?id={ID} ou &id={ID}
    match = re.search(r"[?&]id=([a-zA-Z0-9_-]+)", url)
    if match:
        return match.group(1), "file"

    raise ValueError(
        f"URL do Google Drive não reconhecida: {url}\n"
        "Formatos aceitos:\n"
        "  https://drive.google.com/file/d/ID/view\n"
        "  https://drive.google.com/drive/folders/ID\n"
        "  https://drive.google.com/open?id=ID"
    )


def is_folder_link(url: str) -> bool:
    """Retorna True se a URL aponta para uma pasta do Google Drive."""
    _, resource_type = extract_id_from_url(url)
    return resource_type == "folder"


def sanitize_output_path(path: str) -> Path:
    """
    Resolve, expande ~ e valida o diretório de destino.
    Cria o diretório se não existir.
    """
    resolved = Path(path).expanduser().resolve()
    resolved.mkdir(parents=True, exist_ok=True)
    # Verifica se o diretório é gravável
    test_file = resolved / ".write_test"
    try:
        test_file.touch()
        test_file.unlink()
    except OSError:
        raise PermissionError(f"Sem permissão de escrita em: {resolved}")
    return resolved


def format_bytes(size_bytes: int) -> str:
    """Converte bytes para string legível: '24.3 MB', '1.2 GB'."""
    if size_bytes < 0:
        return "0 B"
    units = ["B", "KB", "MB", "GB", "TB"]
    value = float(size_bytes)
    for unit in units[:-1]:
        if value < 1024:
            return f"{value:.1f} {unit}"
        value /= 1024
    return f"{value:.1f} TB"


def format_eta(seconds: float) -> str:
    """Converte segundos para string legível: '2m 30s', '1h 5m'."""
    if seconds <= 0 or seconds != seconds:  # <= 0 ou NaN
        return "--:--"
    seconds = int(seconds)
    if seconds < 60:
        return f"{seconds}s"
    minutes, secs = divmod(seconds, 60)
    if minutes < 60:
        return f"{minutes}m {secs:02d}s"
    hours, mins = divmod(minutes, 60)
    return f"{hours}h {mins:02d}m"
