import customtkinter as ctk
import pandas as pd


class OrchestratorUI(ctk.CTk):
    def __init__(self, start_callback):
        super().__init__()
        self.start_callback = start_callback

        # Настройка окна
        self.title("Оркестратор Бизнес-Процессов (MVP)")
        self.geometry("800x600")
        ctk.set_appearance_mode("dark")

        # UI Элементы
        self.title_label = ctk.CTkLabel(self, text="Панель управления микросервисами", font=("Arial", 20, "bold"))
        self.title_label.pack(pady=15)

        self.start_btn = ctk.CTkButton(self, text="Запустить сквозной процесс", command=self.start_callback, height=40)
        self.start_btn.pack(pady=10)

        # Консоль логов
        self.log_box = ctk.CTkTextbox(self, width=750, height=250, state="disabled", font=("Consolas", 13))
        self.log_box.pack(pady=10)

        # Поле для итоговой таблицы
        self.result_box = ctk.CTkTextbox(self, width=750, height=150, state="disabled", font=("Consolas", 14))
        self.result_box.pack(pady=10)

    def append_log(self, message: str):
        """Добавляет новую строку в окно логов"""
        self.log_box.configure(state="normal")
        self.log_box.insert("end", message + "\n")
        self.log_box.see("end")  # Автопрокрутка вниз
        self.log_box.configure(state="disabled")
        self.update()  # Принудительно обновляем UI, чтобы текст появлялся в реальном времени

    def show_result_table(self, df: pd.DataFrame):
        """Выводит итоговый DataFrame в текстовое поле"""
        self.result_box.configure(state="normal")
        self.result_box.delete("1.0", "end")
        self.result_box.insert("end", "ИТОГОВЫЙ ОТЧЕТ:\n")
        self.result_box.insert("end", "-" * 40 + "\n")
        self.result_box.insert("end", df.to_string(index=False))
        self.result_box.configure(state="disabled")
        self.update()
