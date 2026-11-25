import pandas as pd
import os

def load_service_data(service_name: str) -> dict[str, pd.DataFrame]:

    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    base_path = os.path.join(project_root, "data", service_name)

    tables = {}

    if not os.path.exists(base_path):
        print(f"[ОШИБКА] Папка {base_path} не найдена!")
        return tables

    for root, dirs, files in os.walk(base_path):
        for filename in files:
            # Нас интересуют только CSV-файлы (игнорируем скрытые файлы вроде .DS_Store)
            if filename.endswith(".csv"):
                file_path = os.path.join(root, filename)
                table_name = os.path.splitext(filename)[0]

                try:
                    # Читаем CSV с автоопределением разделителя (запятая, табуляция, точка с запятой)
                    df = pd.read_csv(file_path, sep=None, engine='python')
                    tables[table_name] = df
                    print(f"  [OK] Загружена таблица: {table_name} (из {file_path})")
                except Exception as e:
                    print(f"  [ОШИБКА] Не удалось прочитать {file_path}: {e}")

    return tables


