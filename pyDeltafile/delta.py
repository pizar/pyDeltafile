import hashlib
import json
from typing import Callable

import pandas as pd
from pandas import DataFrame

HASH_ALL_COLUMNS_KEY = 'UID'
HASH_KEY_COLUMNS_KEY = 'RID'


def _write_generic_file(file_path: str, data: str):
    f = open(file_path, "w")
    f.write(data)
    f.close()

def _read_file_csv(file_path: str, key_columns: [], skip_rows=0) -> DataFrame:
    dataframe = pd.read_csv(file_path, skiprows=skip_rows)
    dataframe = _add_hash_all_columns(dataframe)
    dataframe = _add_hash_key_columns(dataframe, key_columns)
    return dataframe

def _read_file_excel(file_path: str, sheet_name='MySheet', key_columns:list[str]=None, skip_rows=0) -> DataFrame:
    dataframe = pd.read_excel(file_path, sheet_name=sheet_name, skiprows=skip_rows)
    dataframe = _add_hash_all_columns(dataframe)
    dataframe = _add_hash_key_columns(dataframe, key_columns)
    return dataframe

def _read_file_json(file_path: str, key_columns:list[str]=None) -> DataFrame:
    dataframe = pd.read_json(file_path)
    dataframe = _add_hash_all_columns(dataframe)
    dataframe = _add_hash_key_columns(dataframe, key_columns)
    return dataframe

def _add_to_head(file_path: str, head: list[str]):
    try:
        # Read the existing file content
        with open(file_path, 'r') as file:
            existing_content = file.read()
        # Create the new content
        new_content = '\n'.join(head) + existing_content
        # Write the new content back to the file
        with open(file_path, 'w') as file:
            file.write(new_content)
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
    except Exception as e:
        print(f"An error occurred: {e}")


def _calculate_uid(row):
    row_values = ','.join(map(str, row.values))  # Concatenate all values as strings
    md5_hash = hashlib.md5(row_values.encode('utf-8')).hexdigest()
    return md5_hash


def _calculate_rid(row, keys):
    selected_values = [str(row[col]) for col in keys]
    row_values = ','.join(selected_values)

    md5_hash = hashlib.md5(row_values.encode('utf-8')).hexdigest()
    return md5_hash


def _add_hash_all_columns(dataframe: DataFrame) -> DataFrame:
    dataframe[HASH_ALL_COLUMNS_KEY] = dataframe.apply(lambda row: _calculate_uid(row), axis=1)
    return dataframe


def _add_hash_key_columns(dataframe: DataFrame, keys) -> DataFrame:
    dataframe[HASH_KEY_COLUMNS_KEY] = dataframe.apply(lambda row: _calculate_rid(row, keys), axis=1)
    return dataframe


def _get_head(file_path: str, num_of_line: int) -> list[str]:
    try:
        with open(file_path, 'r') as file:
            head = file.readlines()[:num_of_line]
            return head
    except FileNotFoundError:
        print(f"Errore: il file '{file_path}' non è stato trovato.")
        return None
    except Exception as e:
        print(f"Si è verificato un errore: {e}")
        return None


def _get_line_to_delete(old_dataframe, new_dataframe, key_columns=None) -> DataFrame:
    return old_dataframe[~old_dataframe[HASH_KEY_COLUMNS_KEY].isin(new_dataframe[HASH_KEY_COLUMNS_KEY])]


def _get_line_to_add(old_dataframe, new_dataframe, key_columns=None) -> DataFrame:
    return new_dataframe[~new_dataframe[HASH_KEY_COLUMNS_KEY].isin(old_dataframe[HASH_KEY_COLUMNS_KEY])]


def _del_identical_line(old_dataframe, new_dataframe, key_columns=None) -> DataFrame:
    return new_dataframe[~new_dataframe[HASH_ALL_COLUMNS_KEY].isin(old_dataframe[HASH_ALL_COLUMNS_KEY])]


def _get_line_to_update(old_dataframe, new_dataframe, key_columns=None) -> DataFrame:
    filtered = _del_identical_line(old_dataframe, new_dataframe, key_columns)
    return filtered[filtered[HASH_KEY_COLUMNS_KEY].isin(old_dataframe[HASH_KEY_COLUMNS_KEY])]


def _save_dataframe(file_path: str, dataframe: DataFrame):
    dataframe.to_csv(file_path, index=False)



def _delta_dataframe(
        old_dataframe: DataFrame, new_dataframe: DataFrame, key_columns: [] = None,
        skip_rows: int = 0,
        delete_callback: Callable[[DataFrame], DataFrame] = None,
        add_callback: Callable[[DataFrame], DataFrame] = None,
        update_callback: Callable[[DataFrame], DataFrame] = None
) -> DataFrame:
    """
    Confronta due file CSV utilizzando Pandas.

    Args:
        old_data_file (str): Percorso del vecchio file  CSV.
        new_data_file (str): Percorso del nuovo file CSV.
        delta_data_file (str): Percorso del file di delta CSV.
        key_columns (list[]): elenco delle colonne chiave.
        skip_rows (int): numero di linee da saltare dalla testata.
        delete_callback (Callable): funzione di callback per l'elenco di righe da cancellare.
        add_callback (Callable): funzione di callback per l'elenco di righe da aggiungere.
        update_callback (Callable): funzione di callback per l'elenco di righe da aggiornare.

    Returns:
        pandas.DataFrame: Un DataFrame contenente le differenze tra i file.

        :param old_dataframe:
        :param new_dataframe:
        :param key_columns:
        :param skip_rows:
        :param delete_callback:
        :param add_callback:
        :param update_callback:
    """

    # calculate the line to delete and apply the callback if needed
    to_delete = _get_line_to_delete(old_dataframe, new_dataframe, key_columns)
    if delete_callback:
        to_delete = delete_callback(to_delete)

    # calculate the line to add and apply the callback if needed
    to_add = _get_line_to_add(old_dataframe, new_dataframe, key_columns)
    if add_callback:
        to_add = add_callback(to_add)

    # calculate the line to update and apply the callback if needed
    to_update = _get_line_to_update(old_dataframe, new_dataframe, key_columns)
    if update_callback:
        to_update = update_callback(to_update)

    # compose the delta and write the file
    delta = pd.concat([to_delete, to_add, to_update])
    delta.drop(HASH_ALL_COLUMNS_KEY, axis=1, inplace=True)
    delta.drop(HASH_KEY_COLUMNS_KEY, axis=1, inplace=True)

    return delta

def delta_csv(
        old_data_file: str,
        new_data_file: str,
        delta_data_file: str = 'delta.csv',
        key_columns: [] = None,
        skip_rows: int = 0,
        delete_callback: Callable[[DataFrame], DataFrame] = None,
        add_callback: Callable[[DataFrame], DataFrame] = None,
        update_callback: Callable[[DataFrame], DataFrame] = None
) -> None:
    """
    Confronta due file CSV utilizzando Pandas.

    Args:
        old_data_file (str): Percorso del vecchio file  CSV.
        new_data_file (str): Percorso del nuovo file CSV.
        delta_data_file (str): Percorso del file di delta CSV.
        key_columns (list[]): elenco delle colonne chiave.
        skip_rows (int): numero di linee da saltare dalla testata.
        delete_callback (Callable): funzione di callback per l'elenco di righe da cancellare.
        add_callback (Callable): funzione di callback per l'elenco di righe da aggiungere.
        update_callback (Callable): funzione di callback per l'elenco di righe da aggiornare.

    Returns:
        pandas.DataFrame: Un DataFrame contenente le differenze tra i file.

        :param old_data_file:
        :param new_data_file:
        :param delta_data_file:
        :param key_columns:
        :param skip_rows:
        :param delete_callback:
        :param add_callback:
        :param update_callback:
    """
    # read the data file
    old_dataframe = _read_file_csv(old_data_file, key_columns, skip_rows)
    new_dataframe = _read_file_csv(new_data_file, key_columns, skip_rows)

    delta = _delta_dataframe(old_dataframe, new_dataframe, key_columns, skip_rows, delete_callback, add_callback, update_callback)

    delta.to_csv(delta_data_file, index=False)
    if skip_rows > 0:
        head_line = _get_head(old_data_file, skip_rows)
        _add_to_head(delta_data_file, head_line)


def delta_excel(
        old_data_file: str,
        new_data_file: str,
        delta_data_file: str = 'delta.xlsx',
        sheet_name:str='MySheet',
        key_columns: [] = None,
        skip_rows: int = 0,
        delete_callback: Callable[[DataFrame], DataFrame] = None,
        add_callback: Callable[[DataFrame], DataFrame] = None,
        update_callback: Callable[[DataFrame], DataFrame] = None
) -> None:
    """
    Confronta due file CSV utilizzando Pandas.

    Args:
        old_data_file (str): Percorso del vecchio file  CSV.
        new_data_file (str): Percorso del nuovo file CSV.
        delta_data_file (str): Percorso del file di delta CSV.
        key_columns (list[]): elenco delle colonne chiave.
        skip_rows (int): numero di linee da saltare dalla testata.
        delete_callback (Callable): funzione di callback per l'elenco di righe da cancellare.
        add_callback (Callable): funzione di callback per l'elenco di righe da aggiungere.
        update_callback (Callable): funzione di callback per l'elenco di righe da aggiornare.

    Returns:
        pandas.DataFrame: Un DataFrame contenente le differenze tra i file.

        :param old_data_file:
        :param new_data_file:
        :param delta_data_file:
        :param key_columns:
        :param skip_rows:
        :param delete_callback:
        :param add_callback:
        :param update_callback:
    """
    # read the data file
    old_dataframe = _read_file_excel(old_data_file, sheet_name, key_columns, skip_rows)
    new_dataframe = _read_file_excel(new_data_file, sheet_name, key_columns, skip_rows)

    delta = _delta_dataframe(old_dataframe, new_dataframe, key_columns, skip_rows, delete_callback, add_callback, update_callback)

    delta.to_csv(delta_data_file, index=False)
    if skip_rows > 0:
        head_line = _get_head(old_data_file, skip_rows)
        _add_to_head(delta_data_file, head_line)



def delta_json(
        old_data_file: str,
        new_data_file: str,
        delta_data_file: str = 'delta.json',
        key_columns: [] = None,
        delete_callback: Callable[[DataFrame], DataFrame] = None,
        add_callback: Callable[[DataFrame], DataFrame] = None,
        update_callback: Callable[[DataFrame], DataFrame] = None
) -> None:
    """
    Confronta due file CSV utilizzando Pandas.

    Args:
        old_data_file (str): Percorso del vecchio file  CSV.
        new_data_file (str): Percorso del nuovo file CSV.
        delta_data_file (str): Percorso del file di delta CSV.
        key_columns (list[]): elenco delle colonne chiave.
        skip_rows (int): numero di linee da saltare dalla testata.
        delete_callback (Callable): funzione di callback per l'elenco di righe da cancellare.
        add_callback (Callable): funzione di callback per l'elenco di righe da aggiungere.
        update_callback (Callable): funzione di callback per l'elenco di righe da aggiornare.

    Returns:
        pandas.DataFrame: Un DataFrame contenente le differenze tra i file.

        :param old_data_file:
        :param new_data_file:
        :param delta_data_file:
        :param key_columns:
        :param skip_rows:
        :param delete_callback:
        :param add_callback:
        :param update_callback:
    """
    # read the data file
    old_dataframe = _read_file_json(old_data_file, key_columns)
    new_dataframe = _read_file_json(new_data_file, key_columns)

    delta = _delta_dataframe(old_dataframe, new_dataframe, key_columns, 0, delete_callback, add_callback, update_callback)
    # Converti il DataFrame di nuovo in una lista di dizionari (come l'input originale)
    result = delta.to_dict(orient='records')
    # Stampa il risultato per verificare che sia identico all'input
    data = json.dumps(result, indent=4)
    _write_generic_file(delta_data_file, data)

