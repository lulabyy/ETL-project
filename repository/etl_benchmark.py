"""
etl_benchmark.py

This module implements the ETL (Extract, Transform, Load) pipeline for benchmark data used in the portfolio analytics dashboard.

It defines the BenchmarkETL class, which is responsible for:
- Extracting raw benchmark data from source(s)
- Transforming and cleaning the data
- Loading the processed data into the appropriate storage or dataframes

etl_benchmark.py is called by main_etl.py during the ETL process. It should not be executed directly.

To run the full ETL pipeline, use:
    python main_etl.py

See main_streamlit.py for launching the Streamlit dashboard using the processed data.
"""

import os
import pandas as pd
import yfinance as yf

from model.model_config import Config

from helpers import helpers_logger
from helpers import helpers_export

class BenchmarkETL():
    def __init__(self, config: Config):
        """
        Initialize the BenchmarkETL object.

        Args:
            config (EtlConfig): Configuration object for the ETL process.
        """
        self.logger = helpers_logger.initLogger(config.benchmark.logger.logname, config.log_path, config.benchmark.logger.filename)
        self.config = config
        self.df_raw = None
        self.df_transformed = None

    def extract(self) -> None:
        """
        Extract benchmark data from metadata and the yfinance API.

        This method loads the list of tickers from the metadata file, then downloads their historical price data using yfinance.
        The raw data is stored in self.df_raw.

        Raises:
            Exception: If reading the metadata file or fetching data from yfinance fails.
            ValueError: If the ticker column is missing in the metadata.
        """
        # 1. on récupere le path du csv des metadata pour récuperer les tickers du benchmark
        absolute_metadata_path = os.path.join(self.config.root_path, self.config.benchmark.tickers_info.dir, self.config.benchmark.tickers_info.file)
        self.logger.info(f"Extracting benchmark tickers from: {os.path.relpath(absolute_metadata_path, start=self.config.root_path)}")

        try:
            df_metadata = pd.read_csv(absolute_metadata_path)
        except Exception as e:
            self.logger.exception(f"Error loading metadata file: {e}")
            raise

        # 2. récupérer la colonne des tickers
        ticker_col = self.config.benchmark.tickers_info.column
        if ticker_col not in df_metadata.columns:
            self.logger.error(f"Ticker column '{ticker_col}' not found in metadata")
            raise ValueError("Ticker column missing")
        
        tickers = df_metadata[ticker_col].dropna().unique().tolist()
        self.logger.info(f"{len(tickers)} tickers found for benchmark")

        # 3. on fait appel à l'api sur yfinance avec les tickers
        self.logger.info(f"Extracting data from yfinance ({self.config.benchmark.name} benchmark)")
        try:
            df_yf = yf.download(
                tickers=" ".join(tickers),
                period="max",
                group_by='ticker',
                auto_adjust=True,
                threads=True
            )
        except Exception as e:
            self.logger.exception(f"Error fetching data from yfinance: {e}")
            raise

        self.df_raw = df_yf
        self.logger.info(f"yfinance data shape: {df_yf.shape}")


    def transform(self) -> None:
        """
        Transform the extracted benchmark data into a clean format.

        This method flattens the raw data, cleans and converts columns as needed, and stores the result in self.df_transformed.

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
            df = self.df_raw.copy()

            # 1. remove multi-index

            # 1.1 Stack sur le niveau 0 (Open, High, ...) → lignes = [Date, Ticker, Variable]
            df_long = df.stack(level=0, future_stack=True).reset_index()
            df_long.columns.name = None

            # 1.2 Rename columns
            df_long.rename(columns={
                "level_0": "Date",
                "level_1": "Ticker"
            }, inplace=True)

            #1.3 Drop useless rows.
            df = df_long[["Date", "Ticker", "Open", "High", "Low", "Close", "Volume"]]
            df.dropna(how="all", subset=["Open", "High", "Low", "Close", "Volume"], inplace=True)

            # transform les columns

            # 1.4 Drop useless columns.
            for col in self.config.benchmark.columns.columns_to_drop:
                if col in df.columns:
                     df.drop(col, axis=1, inplace=True)

            # 2. Change string format to datetime.
            for col in self.config.benchmark.columns.columns_date:
                if col in df.columns:
                    df[col] = pd.to_datetime(df[col])

            # 3. Change string format to numeric
            for col in self.config.benchmark.columns.columns_numeric:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col])

            # 4. Force string type
            for col in self.config.benchmark.columns.columns_string:
                new_col = self.config.benchmark.columns.columns_new_names.get(col, col)
                if new_col in df.columns:
                    df[new_col] = df[new_col].astype(str)

            # 5. Rename columns
            df.rename(columns=self.config.benchmark.columns.columns_new_names, inplace=True)

            self.df_transformed = df
            self.logger.info(f"Transformed data shape: {df.shape}")

        except Exception as e:
            self.logger.exception(f"Error while transforming: {e}")
            raise  

    def load(self) -> None:
        """
        Load the transformed benchmark data into Excel and/or SQLite, as specified in the configuration.

        This method exports the cleaned DataFrame to Excel and/or SQLite database, depending on the configuration.

        Raises:
            ValueError: If transform() was not called before load().
            Exception: If an error occurs during export to Excel or SQLite.
        """
        if self.df_transformed is None:
            self.logger.error("Data not transformed. transform() must be called before load().")
            raise ValueError("No data to load.")
        
        self.logger.info("Loading data")
        export = {self.config.etl_output.excel.benchmark_sheet: self.df_transformed}

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
