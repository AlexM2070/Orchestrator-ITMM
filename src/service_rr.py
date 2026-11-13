import pandas as pd


def process_rr_calc(process_id: str, tables: dict[str, pd.DataFrame]) -> tuple[pd.DataFrame, list[str]]:
    """
    Бизнес-логика расчета пруденциального рыночного риска (rr_calc).
    """
    logs = []
    logs.append(f"[{process_id}] rr_calc: Начало обработки данных...")
    logs.append(f"[{process_id}] rr_calc: Получено таблиц: {len(tables)}")

    # TODO: Здесь Участник 3 напишет логику объединения таблиц из словаря tables (pd.merge)

    # Имитация результата расчетов
    result_df = pd.DataFrame({"Метрика": ["Рыночный риск (rr_calc)"], "Сумма (RUB)": [450000.00]})

    logs.append(f"[{process_id}] rr_calc: Раскладка данных успешно завершена.")

    return result_df, logs
