import queue
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from tkinter.scrolledtext import ScrolledText
from typing import Optional

from .config import get_api_key, set_api_key
from .core import download
from .logger import get_logger
from .progress import GUIProgressReporter
from .utils import format_bytes, format_eta


class DownloadApp(tk.Tk):
    """Janela principal da aplicação GUI de download do Google Drive."""

    def __init__(self):
        super().__init__()
        self.title("Google Drive Downloader")
        self.geometry("720x540")
        self.minsize(600, 480)
        self.resizable(True, True)

        self._update_queue: queue.Queue = queue.Queue()
        self._download_thread: Optional[threading.Thread] = None
        self._is_downloading = False

        self._build_widgets()
        self._poll_queue()

    # ------------------------------------------------------------------ #
    #  Construção de widgets                                               #
    # ------------------------------------------------------------------ #

    def _build_widgets(self) -> None:
        self.columnconfigure(0, weight=1)
        self.rowconfigure(5, weight=1)  # área de log expande

        pad = {"padx": 12, "pady": 4}

        # Título
        title_frame = ttk.Frame(self)
        title_frame.grid(row=0, column=0, sticky="ew", padx=12, pady=(12, 6))
        ttk.Label(
            title_frame,
            text="Google Drive Downloader",
            font=("Segoe UI", 14, "bold"),
        ).pack(anchor="w")
        ttk.Label(
            title_frame,
            text="Downloads de links públicos do Google Drive",
            foreground="#555",
        ).pack(anchor="w")

        ttk.Separator(self, orient="horizontal").grid(
            row=1, column=0, sticky="ew", padx=12, pady=4
        )

        # Formulário de entrada
        form = ttk.Frame(self)
        form.grid(row=2, column=0, sticky="ew", **pad)
        form.columnconfigure(1, weight=1)

        # Link
        ttk.Label(form, text="Link do Drive:").grid(row=0, column=0, sticky="w", pady=3)
        self.url_var = tk.StringVar()
        ttk.Entry(form, textvariable=self.url_var, width=60).grid(
            row=0, column=1, columnspan=2, sticky="ew", padx=(8, 0), pady=3
        )

        # Pasta de destino
        ttk.Label(form, text="Pasta de destino:").grid(row=1, column=0, sticky="w", pady=3)
        self.folder_var = tk.StringVar()
        ttk.Entry(form, textvariable=self.folder_var, width=50).grid(
            row=1, column=1, sticky="ew", padx=(8, 4), pady=3
        )
        ttk.Button(form, text="Procurar...", command=self._browse_folder).grid(
            row=1, column=2, pady=3
        )

        # Google API Key
        ttk.Label(form, text="Google API Key:").grid(row=2, column=0, sticky="w", pady=3)
        self.api_key_var = tk.StringVar(value=get_api_key())
        api_entry = ttk.Entry(form, textvariable=self.api_key_var, width=50, show="*")
        api_entry.grid(row=2, column=1, sticky="ew", padx=(8, 4), pady=3)
        ttk.Button(form, text="?", width=3, command=self._show_api_key_help).grid(
            row=2, column=2, pady=3
        )

        # Opções
        opts = ttk.Frame(self)
        opts.grid(row=3, column=0, sticky="ew", **pad)

        ttk.Label(opts, text="Velocidade máxima:").pack(side="left")
        self.speed_var = tk.StringVar()
        ttk.Entry(opts, textvariable=self.speed_var, width=8).pack(side="left", padx=4)
        ttk.Label(opts, text="KB/s   ").pack(side="left")

        self.resume_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(opts, text="Retomar download interrompido", variable=self.resume_var).pack(
            side="left", padx=8
        )

        # Botão de download
        btn_frame = ttk.Frame(self)
        btn_frame.grid(row=4, column=0, sticky="ew", padx=12, pady=6)
        self.download_btn = ttk.Button(
            btn_frame,
            text="⬇  Baixar",
            command=self._on_download_click,
            width=20,
        )
        self.download_btn.pack()

        ttk.Separator(self, orient="horizontal").grid(
            row=4, column=0, sticky="ew", padx=12, pady=(40, 0)
        )

        # Progresso
        prog_frame = ttk.Frame(self)
        prog_frame.grid(row=5, column=0, sticky="ew", padx=12, pady=(6, 2))
        prog_frame.columnconfigure(0, weight=1)

        self.progress_bar = ttk.Progressbar(prog_frame, mode="indeterminate", length=400)
        self.progress_bar.grid(row=0, column=0, sticky="ew", pady=(0, 4))

        self.status_var = tk.StringVar(value="Aguardando...")
        ttk.Label(prog_frame, textvariable=self.status_var, foreground="#333").grid(
            row=1, column=0, sticky="w"
        )

        # Área de log
        log_frame = ttk.LabelFrame(self, text="Log")
        log_frame.grid(row=6, column=0, sticky="nsew", padx=12, pady=(4, 12))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        self.rowconfigure(6, weight=1)

        self.log_text = ScrolledText(
            log_frame, height=8, state="disabled",
            font=("Consolas", 9), bg="#1e1e1e", fg="#d4d4d4",
            insertbackground="white",
        )
        self.log_text.grid(row=0, column=0, sticky="nsew", padx=4, pady=4)
        self.log_text.tag_config("info", foreground="#d4d4d4")
        self.log_text.tag_config("success", foreground="#4ec9b0")
        self.log_text.tag_config("error", foreground="#f44747")
        self.log_text.tag_config("warn", foreground="#dcdcaa")

    # ------------------------------------------------------------------ #
    #  Ações do usuário                                                    #
    # ------------------------------------------------------------------ #

    def _browse_folder(self) -> None:
        path = filedialog.askdirectory(title="Selecione a pasta de destino")
        if path:
            self.folder_var.set(path)

    def _show_api_key_help(self) -> None:
        msg = (
            "A Google API Key é necessária para baixar pastas do Google Drive de forma confiável.\n\n"
            "Como obter gratuitamente:\n"
            "1. Acesse: console.cloud.google.com\n"
            "2. Crie um projeto (ou selecione um existente)\n"
            "3. Vá em APIs e Serviços → Biblioteca\n"
            "4. Ative a 'Google Drive API'\n"
            "5. Vá em APIs e Serviços → Credenciais\n"
            "6. Clique em 'Criar credenciais' → 'Chave de API'\n"
            "7. Copie a chave gerada e cole aqui\n\n"
            "A chave é gratuita e permite até 1.000 downloads/dia."
        )
        messagebox.showinfo("Como obter a Google API Key", msg)

    def _on_download_click(self) -> None:
        url = self.url_var.get().strip()
        folder = self.folder_var.get().strip()

        if not url:
            messagebox.showerror("Campo obrigatório", "Informe o link do Google Drive.")
            return
        if not folder:
            messagebox.showerror("Campo obrigatório", "Selecione a pasta de destino.")
            return

        speed_kb = None
        if self.speed_var.get().strip():
            try:
                speed_kb = int(self.speed_var.get().strip()) * 1024
            except ValueError:
                messagebox.showerror("Valor inválido", "Velocidade deve ser um número inteiro em KB/s.")
                return

        api_key = self.api_key_var.get().strip()
        if api_key:
            set_api_key(api_key)

        self._is_downloading = True
        self.download_btn.configure(state="disabled", text="Baixando...")
        self.progress_bar.configure(mode="indeterminate")
        self.progress_bar.start(10)
        self.status_var.set("Iniciando download...")
        self._append_log(f"Iniciando: {url}", "info")

        self._download_thread = threading.Thread(
            target=self._run_download,
            args=(url, folder, speed_kb, self.resume_var.get(), api_key),
            daemon=True,
            name="gdrive-download",
        )
        self._download_thread.start()

    # ------------------------------------------------------------------ #
    #  Download em thread separada                                         #
    # ------------------------------------------------------------------ #

    def _run_download(self, url: str, folder: str, speed_limit, resume: bool, api_key: str = "") -> None:
        """Roda na thread de background — nunca toca widgets diretamente."""
        logger = get_logger()
        reporter = GUIProgressReporter(self._update_queue, logger)

        download(
            url=url,
            output_dir=folder,
            progress_reporter=reporter,
            speed_limit=speed_limit,
            resume=resume,
            api_key=api_key,
        )

    # ------------------------------------------------------------------ #
    #  Polling da fila (main thread)                                       #
    # ------------------------------------------------------------------ #

    def _poll_queue(self) -> None:
        """Drena a fila a cada 100ms no main thread e atualiza a UI."""
        try:
            while True:
                item = self._update_queue.get_nowait()
                self._handle_queue_item(item)
        except queue.Empty:
            pass
        self.after(100, self._poll_queue)

    def _handle_queue_item(self, item: tuple) -> None:
        event_type = item[0]

        if event_type == "start":
            _, tipo, output_path, _ = item
            self._append_log(f"Download de {tipo} iniciado → {output_path}", "info")
            self.status_var.set(f"Baixando {tipo}...")

        elif event_type == "status":
            _, msg = item
            self.status_var.set(msg)
            tag = "warn" if msg.startswith("[SKIP]") else "info"
            self._append_log(msg, tag)

        elif event_type == "progress":
            _, state = item
            speed_str = format_bytes(int(state.speed_bps)) + "/s" if state.speed_bps > 0 else "--"
            dl_str = format_bytes(state.downloaded_bytes)
            self.status_var.set(f"Baixado: {dl_str}  |  Velocidade: {speed_str}")

        elif event_type == "finish":
            _, output_path, elapsed, _ = item
            self.progress_bar.stop()
            self.progress_bar.configure(mode="determinate", value=100)
            self.status_var.set(f"Concluído em {format_eta(elapsed)} → {output_path}")
            self._append_log(f"✔ Download concluído em {format_eta(elapsed)}", "success")
            self._reset_download_state()

        elif event_type == "error":
            _, error_msg, _ = item
            self.progress_bar.stop()
            self.progress_bar.configure(mode="determinate", value=0)
            self.status_var.set(f"Erro: {error_msg}")
            self._append_log(f"✘ Erro: {error_msg}", "error")
            messagebox.showerror("Erro no download", error_msg)
            self._reset_download_state()

    def _reset_download_state(self) -> None:
        self._is_downloading = False
        self.download_btn.configure(state="normal", text="⬇  Baixar")

    # ------------------------------------------------------------------ #
    #  Log visual                                                          #
    # ------------------------------------------------------------------ #

    def _append_log(self, message: str, tag: str = "info") -> None:
        import datetime
        ts = datetime.datetime.now().strftime("%H:%M:%S")
        line = f"[{ts}] {message}\n"
        self.log_text.configure(state="normal")
        self.log_text.insert("end", line, tag)
        self.log_text.see("end")
        self.log_text.configure(state="disabled")


def run_gui() -> None:
    app = DownloadApp()
    app.mainloop()
