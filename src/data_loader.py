import pandas as pd


def load_service_data(service_name: str) -> dict[str, pd.DataFrame]:
    """
    Сканирует папки data/{service_name}/ и загружает CSV в память.
    Пока это заглушка, возвращающая тестовый DataFrame.
    """
    # TODO: Здесь Участник 2 напишет логику обхода файлов через os.walk или pathlib

    # Возвращаем фейковые данные для тестирования
    mock_df = pd.DataFrame({"id": [1, 2, 3], "value": [100.5, 200.0, 350.2]})

    return {"mock_table": mock_df}
