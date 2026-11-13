import uuid

import pandas as pd

from src.dashboard import OrchestratorUI

# Импорт наших локальных модулей
from src.data_loader import load_service_data
from src.service_krs import process_krs_load
from src.service_rr import process_rr_calc


def run_pipeline(ui: OrchestratorUI):
    """
    Главная функция оркестрации. Запускается при нажатии кнопки в дашборде.
    """
    ui.append_log("-" * 60)

    # 1. Генерация сквозного ID
    process_id = str(uuid.uuid4())[:8]
    ui.append_log(f"[*] Сгенерирован Сквозной Process ID: {process_id}")

    # 2. Вызов микросервиса rr_calc
    ui.append_log(f"[{process_id}] Извлечение сырых данных для rr_calc...")
    data_rr = load_service_data("rr_calc")
    result_rr, logs_rr = process_rr_calc(process_id, data_rr)

    for log in logs_rr:
        ui.append_log(log)

    # 3. Вызов микросервиса krs_load
    ui.append_log(f"[{process_id}] Извлечение сырых данных для krs_load...")
    data_krs = load_service_data("krs_load")
    result_krs, logs_krs = process_krs_load(process_id, data_krs)

    for log in logs_krs:
        ui.append_log(log)

    # 4. Агрегация и вывод результатов
    ui.append_log(f"[{process_id}] Оркестрация успешно завершена!")

    # Объединяем результаты двух сервисов в одну сводную таблицу
    final_report = pd.concat([result_rr, result_krs], ignore_index=True)
    ui.show_result_table(final_report)


if __name__ == "__main__":
    # Инициализируем UI и передаем ссылку на него внутрь коллбэка с помощью lambda
    app = OrchestratorUI(start_callback=lambda: run_pipeline(app))

    # Запускаем бесконечный цикл отрисовки окна
    app.mainloop()
