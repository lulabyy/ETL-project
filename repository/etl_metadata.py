"""
etl_metadata.py

This module implements the ETL (Extract, Transform, Load) pipeline for metadata used in the portfolio analytics dashboard.

It defines the MetadataETL class, which is responsible for:
- Extracting raw metadata from source(s)
- Transforming and cleaning the metadata
- Loading the processed metadata into the appropriate storage or dataframes

etl_metadata.py is called by main_etl.py during the ETL process. It should not be executed directly.

To run the full ETL pipeline, use:
    python main_etl.py

See main_streamlit.py for launching the Streamlit dashboard using the processed data.
"""

import pandas as pd
import os

from model.model_config import Config

from helpers import helpers_logger
from helpers import helpers_export

class MetadataETL():
    def __init__(self, config: Config):
        """
        Initialize the MetadataETL object.

        Args:
            config (EtlConfig): Configuration object for the ETL process.
        """
        self.logger = helpers_logger.initLogger(config.metadata.logger.logname, config.log_path, config.metadata.logger.filename)
        self.config = config
        self.df_raw = None
        self.df_transformed = None

    def extract(self) -> None:
        """
        Extract metadata from the configured CSV file.

        This method loads the metadata from a CSV file defined in the configuration
        and stores the raw DataFrame in self.df_raw.

        Raises:
            Exception: If reading the CSV file fails.
        """
        # on récupere le path du csv des metadatas
        absolute_data_path = os.path.join(self.config.root_path, self.config.metadata.dir, self.config.metadata.file)
        self.logger.info(f"Extracting data from: {os.path.relpath(absolute_data_path, start=self.config.root_path)}")

        try:
            self.df_raw = pd.read_csv(absolute_data_path)
            self.logger.info(f"Raw data shape: {self.df_raw.shape}")
        except Exception as e:
            self.logger.exception(f"Error while extracting: {e}")
            raise

    def transform(self) -> None:
        """
        Transform the extracted metadata into a clean format.

        This method drops unnecessary columns, converts types, renames columns,
        and stores the result in self.df_transformed.

        Raises:
            ValueError: If extract() was not called before transform().
            Exception: If an error occurs during data transformation.
        """
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

    def load(self) -> None:
        if self.df_transformed is None:
            self.logger.error("Data not transformed. transform() must be called before load().")
            raise ValueError("No data to load.")

        self.logger.info("Loading data")
        export = {self.config.etl_output.excel.metadata_sheet: self.df_transformed}

        try:
            if self.config.main_parameters.to_excel:
                excel_path = os.path.join(self.config.root_path, self.config.etl_output.excel.dir,
                                          self.config.etl_output.excel.file.format(self.config.main_parameters.output_version))
                os.makedirs(os.path.dirname(excel_path), exist_ok=True)

                self.logger.info(f"Exporting data to Excel | path={excel_path}")
                helpers_export.dataframes_to_excel(export, excel_path)
                self.logger.info(f"sheets={helpers_export.get_excel_sheet_names(excel_path)}")

            if self.config.main_parameters.to_sqlite:
                sqlite_path = os.path.join(self.config.root_path, self.config.database.dir, 
                                           self.config.database.file.format(self.config.main_parameters.output_version))
                os.makedirs(os.path.dirname(sqlite_path), exist_ok=True)

                self.logger.info(f"Exporting data to SQLite | path={sqlite_path}")
                helpers_export.dataframes_to_db(export, db_path=sqlite_path, drop_all_tables=True)
                self.logger.info(f"tables={helpers_export.get_sqlite_table_names(sqlite_path)}")
        except Exception as e:
            self.logger.exception(f"Error while loading: {e}")
            raise
