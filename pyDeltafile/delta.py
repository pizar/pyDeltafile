import hashlib
from typing import Callable

import pandas as pd
from pandas import DataFrame

HASH_ALL_COLUMNS_KEY = 'UID'
HASH_KEY_COLUMNS_KEY = 'RID'

def _read_file_csv(file_path: str, key_columns: [], skip_rows=0) -> DataFrame:
    dataframe = pd.read_csv(file_path, skiprows=skip_rows)
    dataframe = _add_hash_all_columns(dataframe)
    dataframe = _add_hash_key_columns(dataframe, key_columns)
    return dataframe

def _add_to_head(file_path:str, head:list[str]):
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

def _add_hash_all_columns(dataframe:DataFrame) -> DataFrame:
    dataframe[HASH_ALL_COLUMNS_KEY] = dataframe.apply(lambda row: _calculate_uid(row), axis=1)
    return dataframe

def _add_hash_key_columns(dataframe:DataFrame, keys) -> DataFrame:
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

def _save_dataframe(file_path:str, dataframe: DataFrame):
    dataframe.to_csv(file_path, index=False)

def delta_csv(
        old_data_file:str, new_data_file:str, delta_data_file:str='delta.csv', key_columns:[]=None, skip_rows:int=0,
        delete_callback:Callable[[DataFrame], DataFrame]=None,
        add_callback:Callable[[DataFrame], DataFrame]=None,
        update_callback:Callable[[DataFrame], DataFrame]=None
    ) -> None:
    """
    Confronta due file CSV utilizzando Pandas.

    Args:
        file1 (str): Percorso del primo file CSV.
        file2 (str): Percorso del secondo file CSV.
        colonne_chiave (list, optional): Elenco di colonne da utilizzare come chiave per il confronto.

    Returns:
        pandas.DataFrame: Un DataFrame contenente le differenze tra i file.
        :param add_callback:
        :param delete_callback:
        :param old_data_file:
        :param new_data_file:
        :param delta_data_file:
        :param key_columns:
        :param skip_rows:
    """

    old_dataframe = _read_file_csv(old_data_file, key_columns, skip_rows)
    new_data_file = _read_file_csv(new_data_file, key_columns, skip_rows)

    to_delete = _get_line_to_delete(old_dataframe, new_data_file, key_columns)
    if delete_callback:
        to_delete = delete_callback(to_delete)

    to_add = _get_line_to_add(old_dataframe, new_data_file, key_columns)
    if add_callback:
        to_add = add_callback(to_add)

    to_update = _get_line_to_update(old_dataframe, new_data_file, key_columns)
    if add_callback:
        to_update = update_callback(to_update)

    delta = pd.concat([to_delete, to_add, to_update])
    delta.drop(HASH_ALL_COLUMNS_KEY, axis=1, inplace=True)
    delta.drop(HASH_KEY_COLUMNS_KEY, axis=1, inplace=True)
    delta.to_csv(delta_data_file, index=False)

    if skip_rows > 0:
        head_line = _get_head(old_data_file, skip_rows)
        _add_to_head(delta_data_file, head_line)
