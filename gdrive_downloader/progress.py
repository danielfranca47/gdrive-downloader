import collections
import logging
import queue
import threading
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from colorama import Fore, Style


@dataclass
class ProgressState:
    filename: str = ""
    total_bytes: int = 0
    downloaded_bytes: int = 0
    speed_bps: float = 0.0
    eta_seconds: float = 0.0
    percent: float = 0.0
    done: bool = False
    error: Optional[str] = None


class CLIProgressReporter:
    """
    Reporter para modo CLI.
    Imprime mensagens coloridas de início/fim e deixa o tqdm nativo
    do gdown exibir a barra de progresso (quiet=False).
    """

    def __init__(self, logger: logging.Logger):
        self._logger = logger

    def announce_start(self, url: str, output_path: str, is_folder: bool) -> None:
        tipo = "pasta" if is_folder else "arquivo"
        msg = f"Iniciando download de {tipo}:\n  Origem:  {url}\n  Destino: {output_path}"
        print(f"\n{Fore.CYAN}{msg}{Style.RESET_ALL}\n")
        self._logger.info(f"Download iniciado — {tipo} | destino: {output_path} | url: {url}")

    def announce_finish(self, output_path: str, elapsed: float) -> None:
        from .utils import format_eta
        msg = f"Download concluído em {format_eta(elapsed)} → {output_path}"
        print(f"\n{Fore.GREEN}[OK] {msg}{Style.RESET_ALL}\n")
        self._logger.info(f"Download concluído em {elapsed:.1f}s → {output_path}")

    def announce_error(self, error: str) -> None:
        print(f"\n{Fore.RED}[ERRO] {error}{Style.RESET_ALL}\n")
        self._logger.error(f"Erro no download: {error}")

    # Métodos no-op para manter a mesma interface do GUIProgressReporter
    def start_watching(self, output_path: str, drive_id: str) -> None:
        pass

    def stop_watching(self) -> None:
        pass


class GUIProgressReporter:
    """
    Reporter para modo GUI.
    Roda gdown com quiet=True e faz polling do arquivo .part a cada 250ms
    para inferir progresso, empurrando ProgressState para uma queue.Queue.
    """

    POLL_INTERVAL = 0.25  # segundos

    def __init__(self, update_queue: queue.Queue, logger: logging.Logger):
        self._queue = update_queue
        self._logger = logger
        self._stop_event = threading.Event()
        self._watch_thread: Optional[threading.Thread] = None
        self._output_path: Optional[Path] = None
        self._drive_id: str = ""
        self._speed_window: collections.deque = collections.deque(maxlen=5)

    def announce_start(self, url: str, output_path: str, is_folder: bool) -> None:
        tipo = "pasta" if is_folder else "arquivo"
        self._logger.info(f"Download iniciado — {tipo} | destino: {output_path} | url: {url}")
        state = ProgressState(
            filename=output_path,
            percent=0.0,
        )
        self._queue.put(("start", tipo, output_path, state))

    def announce_finish(self, output_path: str, elapsed: float) -> None:
        self._logger.info(f"Download concluído em {elapsed:.1f}s → {output_path}")
        state = ProgressState(done=True, percent=100.0)
        self._queue.put(("finish", output_path, elapsed, state))

    def announce_error(self, error: str) -> None:
        self._logger.error(f"Erro no download: {error}")
        state = ProgressState(done=True, error=error)
        self._queue.put(("error", error, state))

    def start_watching(self, output_path: str, drive_id: str) -> None:
        self._output_path = Path(output_path)
        self._drive_id = drive_id
        self._stop_event.clear()
        self._speed_window.clear()
        self._watch_thread = threading.Thread(
            target=self._watch_loop, daemon=True, name="gdrive-watcher"
        )
        self._watch_thread.start()

    def stop_watching(self) -> None:
        self._stop_event.set()
        if self._watch_thread and self._watch_thread.is_alive():
            self._watch_thread.join(timeout=2.0)

    def _watch_loop(self) -> None:
        """Poll o arquivo .part (ou final) a cada POLL_INTERVAL segundos."""
        output = self._output_path

        while not self._stop_event.is_set():
            try:
                downloaded = self._get_downloaded_bytes(output)
                speed = self._compute_speed(downloaded)

                state = ProgressState(
                    filename=str(output),
                    downloaded_bytes=downloaded,
                    speed_bps=speed,
                    percent=min(downloaded / max(1, downloaded) * 100, 99.0),
                )
                self._queue.put(("progress", state))
            except Exception:
                pass

            self._stop_event.wait(self.POLL_INTERVAL)

    def _get_downloaded_bytes(self, output: Path) -> int:
        """Retorna tamanho do .part se existir, senão do arquivo final."""
        part_file = Path(str(output) + ".part")
        if part_file.exists():
            return part_file.stat().st_size
        if output.exists():
            return output.stat().st_size
        # Para downloads de pasta, soma todos os arquivos no diretório
        if output.is_dir():
            return sum(f.stat().st_size for f in output.rglob("*") if f.is_file())
        return 0

    def _compute_speed(self, current_bytes: int) -> float:
        """Velocidade em bytes/s usando janela deslizante de 5 amostras."""
        now = time.monotonic()
        self._speed_window.append((now, current_bytes))
        if len(self._speed_window) < 2:
            return 0.0
        dt = self._speed_window[-1][0] - self._speed_window[0][0]
        db = self._speed_window[-1][1] - self._speed_window[0][1]
        if dt <= 0:
            return 0.0
        return max(0.0, db / dt)
