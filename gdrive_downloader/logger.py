import logging
from pathlib import Path

_logger_instance = None


def get_logger(log_dir: str = "logs", name: str = "gdrive_downloader") -> logging.Logger:
    """
    Retorna um logger singleton com FileHandler (DEBUG) e StreamHandler (WARNING).
    O StreamHandler usa WARNING para não conflitar com a barra de progresso do tqdm.
    """
    global _logger_instance
    if _logger_instance is not None:
        return _logger_instance

    log_path = Path(log_dir)
    log_path.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # Evita adicionar handlers duplicados se chamado múltiplas vezes
    if logger.handlers:
        _logger_instance = logger
        return logger

    fmt = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(funcName)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Handler para arquivo — nível DEBUG (tudo)
    file_handler = logging.FileHandler(
        log_path / "gdrive_downloader.log", encoding="utf-8"
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(fmt)

    # Handler para console — apenas WARNING+ (não polui o terminal com tqdm)
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.WARNING)
    stream_handler.setFormatter(fmt)

    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)

    _logger_instance = logger
    return logger


def reset_logger() -> None:
    """Remove o singleton — usado em testes."""
    global _logger_instance
    _logger_instance = None
