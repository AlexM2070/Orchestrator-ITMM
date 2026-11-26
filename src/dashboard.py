from __future__ import annotations

import queue
import re
import threading
from typing import Callable, Optional

import customtkinter as ctk
import pandas as pd


class OrchestratorUI(ctk.CTk):
    """Окно управления запуском пайплайна и просмотра его результатов."""

    def __init__(self, start_callback: Callable[[], None]):
        super().__init__()

        self.start_callback = start_callback
        self._events: queue.Queue = queue.Queue()
        self._running = False
        self._closing = False

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.title("Оркестратор бизнес-процессов — MVP")
        self.geometry("1100x760")
        self.minsize(850, 620)
        self.configure(fg_color=("#eef2f7", "#111827"))
        self.protocol("WM_DELETE_WINDOW", self._on_close)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self.grid_rowconfigure(3, weight=1)

        self._build_header()
        self._build_controls()
        self._build_logs()
        self._build_results()

        self.after(100, self._process_events)

    def _build_header(self) -> None:
        header = ctk.CTkFrame(self, corner_radius=14)
        header.grid(row=0, column=0, padx=18, pady=(18, 10), sticky="ew")
        header.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            header,
            text="ПАНЕЛЬ УПРАВЛЕНИЯ ОРКЕСТРАТОРОМ",
            font=ctk.CTkFont(size=22, weight="bold"),
        ).grid(row=0, column=0, padx=20, pady=(18, 4), sticky="w")

        ctk.CTkLabel(
            header,
            text="Единый запуск расчётов рыночного риска и кредитной экспозиции",
            text_color=("gray40", "gray70"),
            font=ctk.CTkFont(size=13),
        ).grid(row=1, column=0, padx=20, pady=(0, 18), sticky="w")

    def _build_controls(self) -> None:
        panel = ctk.CTkFrame(self, corner_radius=14)
        panel.grid(row=1, column=0, padx=18, pady=8, sticky="ew")
        panel.grid_columnconfigure(1, weight=1)

        self.start_btn = ctk.CTkButton(
            panel,
            text="▶  Запустить сквозной процесс",
            command=self._start_pipeline,
            height=42,
            font=ctk.CTkFont(size=14, weight="bold"),
        )
        self.start_btn.grid(row=0, column=0, padx=16, pady=14)

        self.status_label = ctk.CTkLabel(
            panel,
            text="● Ожидание запуска",
            text_color="#60a5fa",
            font=ctk.CTkFont(size=13, weight="bold"),
        )
        self.status_label.grid(row=0, column=1, padx=12, pady=14, sticky="w")

        self.process_label = ctk.CTkLabel(
            panel,
            text="Process ID: —",
            font=ctk.CTkFont(size=12, family="Consolas"),
        )
        self.process_label.grid(row=0, column=2, padx=16, pady=14, sticky="e")

    def _build_logs(self) -> None:
        section = ctk.CTkFrame(self, corner_radius=14)
        section.grid(row=2, column=0, padx=18, pady=8, sticky="nsew")
        section.grid_columnconfigure(0, weight=1)
        section.grid_rowconfigure(1, weight=1)

        top = ctk.CTkFrame(section, fg_color="transparent")
        top.grid(row=0, column=0, padx=14, pady=(12, 4), sticky="ew")
        ctk.CTkLabel(
            top, text="Журнал выполнения",
            font=ctk.CTkFont(size=16, weight="bold"),
        ).pack(side="left")
        ctk.CTkButton(
            top, text="Очистить", width=90, height=28,
            command=self.clear_logs, fg_color="gray",
        ).pack(side="right")

        self.log_box = ctk.CTkTextbox(
            section, wrap="word", font=ctk.CTkFont(size=12, family="Consolas"),
            activate_scrollbars=True,
        )
        self.log_box.grid(row=1, column=0, padx=14, pady=(4, 14), sticky="nsew")
        self.log_box.configure(state="disabled")

    def _build_results(self) -> None:
        section = ctk.CTkFrame(self, corner_radius=14)
        section.grid(row=3, column=0, padx=18, pady=(8, 18), sticky="nsew")
        section.grid_columnconfigure(0, weight=1)
        section.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(
            section, text="Итоговый отчёт",
            font=ctk.CTkFont(size=16, weight="bold"),
        ).grid(row=0, column=0, padx=14, pady=(12, 4), sticky="w")

        self.result_box = ctk.CTkTextbox(
            section, wrap="none", font=ctk.CTkFont(size=12, family="Consolas"),
            activate_scrollbars=True,
        )
        self.result_box.grid(row=1, column=0, padx=14, pady=(4, 14), sticky="nsew")
        self.result_box.configure(state="disabled")
        self._set_text(self.result_box, "Результаты появятся после выполнения расчётов.")

    @staticmethod
    def _set_text(widget, value: str) -> None:
        widget.configure(state="normal")
        widget.delete("1.0", "end")
        widget.insert("end", value)
        widget.configure(state="disabled")

    def _start_pipeline(self) -> None:
        if self._running:
            return

        self._running = True
        self.start_btn.configure(state="disabled", text="Выполняется…")
        self.status_label.configure(text="● Выполнение процесса", text_color="#fbbf24")
        self.process_label.configure(text="Process ID: формируется…")
        self._set_text(self.result_box, "Расчёт выполняется. Ожидайте итоговый отчёт.")
        self.append_log("=" * 72)
        self.append_log("Запуск сквозного процесса…")

        # Callback выполняется в отдельном потоке, чтобы окно не зависало.
        # Методы append_log/show_result_table безопасно передают данные в UI через очередь.
        threading.Thread(target=self._run_callback, daemon=True).start()

    def _run_callback(self) -> None:
        try:
            self.start_callback()
            self._events.put(("finished", None))
        except Exception as exc:
            self._events.put(("log", f"[ERROR] Ошибка выполнения пайплайна: {type(exc).__name__}: {exc}"))
            self._events.put(("failed", None))

    def append_log(self, message: str) -> None:
        """Добавляет строку в журнал; метод можно вызывать из рабочего потока."""
        self._events.put(("log", str(message)))

    def show_result_table(self, df: pd.DataFrame) -> None:
        """Отображает итоговый DataFrame; метод можно вызывать из рабочего потока."""
        if not isinstance(df, pd.DataFrame):
            self.append_log("[ERROR] show_result_table: ожидался pandas.DataFrame.")
            return
        self._events.put(("result", df.copy()))

    def clear_logs(self) -> None:
        self._set_text(self.log_box, "")

    def _process_events(self) -> None:
        if self._closing:
            return

        try:
            while True:
                event, payload = self._events.get_nowait()

                if event == "log":
                    self._append_log_to_widget(payload)
                    match = re.search(r"Process ID:\s*([0-9a-fA-F-]{8,})", payload)
                    if match:
                        self.process_label.configure(text=f"Process ID: {match.group(1)}")
                    # В текущем main.py ID может быть записан в формате
                    # "[*] Сгенерирован Сквозной Process ID: <uuid>".
                    match = re.search(r"Process ID:\s*([0-9a-fA-F-]{8,})", payload, re.I)
                    if match:
                        self.process_label.configure(text=f"Process ID: {match.group(1)}")

                elif event == "result":
                    self._set_text(self.result_box, self._format_dataframe(payload))

                elif event == "finished":
                    self._running = False
                    self.start_btn.configure(state="normal", text="▶  Запустить сквозной процесс")
                    self.status_label.configure(text="● Процесс завершён", text_color="#34d399")

                elif event == "failed":
                    self._running = False
                    self.start_btn.configure(state="normal", text="▶  Повторить запуск")
                    self.status_label.configure(text="● Ошибка выполнения", text_color="#f87171")

        except queue.Empty:
            pass

        self.after(100, self._process_events)

    def _append_log_to_widget(self, message: str) -> None:
        self.log_box.configure(state="normal")
        self.log_box.insert("end", message + "\n")
        self.log_box.see("end")
        self.log_box.configure(state="disabled")

        # Поддержка фактического формата Process ID из main.py в PDF.
        match = re.search(r"Process ID:\s*([0-9a-fA-F-]{8,})", message, re.I)
        if match:
            self.process_label.configure(text=f"Process ID: {match.group(1)}")

    @staticmethod
    def _format_dataframe(df: pd.DataFrame) -> str:
        if df.empty:
            return "Расчёт завершён, но итоговая таблица пуста."
        return f"Строк: {len(df)} | Столбцов: {len(df.columns)}\n\n{df.to_string(index=False)}"

    def _on_close(self) -> None:
        self._closing = True
        self.destroy()
