import pandas as pd
import os

from model.model_config import EtlConfig

from helpers import helpers_logger
from helpers import helpers_export

class MetadataETL():
    def __init__(self, config: EtlConfig, root_path: str):
        self.logger = helpers_logger.initLogger("etl_metadata_logger", "etl_metadata")
        self.root_path = root_path
        self.config = config
        self.df_raw = None
        self.df_transformed = None

    def extract(self):
        absolute_data_path = os.path.join(self.root_path, self.config.metadata.dir, self.config.metadata.file)
        self.logger.info(f"Extracting data from: {os.path.relpath(absolute_data_path, start=self.root_path)}")

        try:
            self.df_raw = pd.read_csv(absolute_data_path)
            self.logger.info(f"Raw data shape: {self.df_raw.shape}")
        except Exception as e:
            self.logger.exception(f"Error while extracting: {e}")
            raise

    def transform(self):
        if self.df_raw is None:
            self.logger.error("Data not extracted. extract() must be called before transform().")
            raise ValueError("No data to transform.")
        
        self.logger.info("Transforming data")
        df = self.df_raw.copy(deep=True)

        try:
            # 1. Drop useless columns.
            for col in self.config.metadata.columns.columns_to_drop:
                if col in df.columns:
                     df.drop(col, axis=1, inplace=True)

            # 2. Change string format to datetime.
            for col in self.config.metadata.columns.columns_date:
                if col in df.columns:
                    df[col] = pd.to_datetime(df[col])

            # 3. Change string format to numeric
            for col in self.config.metadata.columns.columns_numeric:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col])

            # 4. Force string type
            for col in self.config.metadata.columns.columns_string:
                new_col = self.config.metadata.columns.columns_new_names.get(col, col)
                if new_col in df.columns:
                    df[new_col] = df[new_col].astype(str)

            # 5. Rename columns
            df.rename(columns=self.config.metadata.columns.columns_new_names, inplace=True)

            self.df_transformed = df

            self.logger.info(f"Transformed data shape: {self.df_transformed.shape}")

        except Exception as e:
            self.logger.exception(f"Error while transforming: {e}")
            raise    

    def load(self):
        if self.df_transformed is None:
            self.logger.error("Data not transformed. transform() must be called before load().")
            raise ValueError("No data to load.")

        self.logger.info("Loading data")
        export = {"metadata": self.df_transformed}

        try:
            if self.config.main_parameters.to_excel:
                excel_path = os.path.join(self.root_path, self.config.etl_output.excel.dir,
                                          self.config.etl_output.excel.file.format(self.config.main_parameters.output_version))
                os.makedirs(os.path.dirname(excel_path), exist_ok=True)

                self.logger.info(f"Exporting data to Excel | path={excel_path}")
                helpers_export.dataframes_to_excel(export, excel_path)
                self.logger.info(f"sheets={helpers_export.get_excel_sheet_names(excel_path)}")

            if self.config.main_parameters.to_sqlite:
                sqlite_path = os.path.join(self.root_path, self.config.database.dir, 
                                           self.config.database.file.format(self.config.main_parameters.output_version))
                os.makedirs(os.path.dirname(sqlite_path), exist_ok=True)

                self.logger.info(f"Exporting data to SQLite | path={sqlite_path}")
                helpers_export.dataframes_to_db(export, db_path=sqlite_path, drop_all_tables=True)
                self.logger.info(f"tables={helpers_export.get_sqlite_table_names(sqlite_path)}")
        except Exception as e:
            self.logger.exception(f"Error while loading: {e}")
            raise
