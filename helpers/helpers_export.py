import os
from typing import Dict, Literal, List

import numpy as np
import pandas as pd
from sqlalchemy import create_engine, MetaData, inspect

IfExists = Literal["fail", "replace", "append"]

def dataframes_to_excel(
    dataframes: Dict[str, pd.DataFrame], excel_full_path: str
) -> None:
    """
    Export DataFrames to an Excel file from a dict like keys=sheet names and values=DataFrame
    :param dataframes: DataFrames as Dict[sheet_name, data]
    :param excel_full_path: full path of the Excel File
    :return: None
    """
    os.makedirs(os.path.dirname(excel_full_path), exist_ok=True)
    
    if os.path.exists(excel_full_path):
        mode = "a"
        if_sheet_exists = "replace"
    else:
        mode = "w"
        if_sheet_exists = None  

    with pd.ExcelWriter(excel_full_path, engine="openpyxl", mode=mode, if_sheet_exists=if_sheet_exists) as writer:
        for sheet, df in dataframes.items():
            if isinstance(df.columns, pd.MultiIndex):
                df.to_excel(writer, sheet_name=sheet, merge_cells=False)
            elif df.index.dtype == np.int64 and df.index.nlevels == 1:
                df.to_excel(writer, sheet_name=sheet, merge_cells=False, index=False)
            else:
                df.to_excel(writer, sheet_name=sheet, merge_cells=False, index=True)


def dataframes_to_db(
    dataframes: Dict[str, pd.DataFrame],
    db_path: str,
    drop_all_tables: bool = False,
    append_data: bool = False,
):
    """
    Create a SQLite database from a dict like keys=sheet names and values=DataFrame
    If the SQLite database already exists, current data (before this new insertion) could be kept or erased with the
    drop_all_tables parameter
    :param dataframes: DataFrames as Dict(sheet_name, Data)
    :param db_path: full database path
    :param drop_all_tables: if true, all tables will be deleted
    :param append_data: if True, data will be added to the current table. If False, current data will be erased before
    the insertion
    :return: None
    """
    path, _ = os.path.split(db_path)
    os.makedirs(path, exist_ok=True)

    engine = create_engine(f"sqlite:///{db_path}", echo=True)
    con = engine.connect()
    meta = MetaData()

    if drop_all_tables:
        meta.drop_all(con)

    if append_data:
        if_exists: IfExists = "append"
    else:
        if_exists: IfExists = "replace"

    for sh, df in dataframes.items():
        df.to_sql(name=sh, con=con, if_exists=if_exists, index=False)


def get_sqlite_table_names(db_path: str) -> List[str]:
    engine = create_engine(f"sqlite:///{db_path}", echo=False)
    inspector = inspect(engine)
    return inspector.get_table_names()


def get_excel_sheet_names(path: str) -> List[str]:
    xl_file = pd.ExcelFile(path)
    return list(xl_file.sheet_names)
