import os
import pandas as pd
import yfinance as yf

from model.model_config import EtlConfig

from helpers import helpers_logger
from helpers import helpers_export

class BenchmarkETL():
    def __init__(self, config: EtlConfig):
        self.logger = helpers_logger.initLogger(config.benchmark.logger.logname, config.log_path, config.benchmark.logger.filename)
        self.config = config
        self.df_raw = None
        self.df_transformed = None

    def extract(self):
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


    def transform(self):
        if self.df_raw is None:
            self.logger.error("Data not extracted. extract() must be called before transform().")
            raise ValueError("No data to transform.")
        
        self.logger.info("Transforming data")
        df = self.df_raw.copy(deep=True)

        try:
            df = self.df_raw.copy()

            # 1. Stack sur le niveau 0 (Open, High, ...) → lignes = [Date, Ticker, Variable]
            df_long = df.stack(level=0, future_stack=True).reset_index()
            df_long.columns.name = None  

            # 2. Renommer proprement les colonnes
            df_long.rename(columns={
                "level_0": "Date",
                "level_1": "Ticker"
            }, inplace=True)

            df_ordered = df_long[["Date", "Ticker", "Open", "High", "Low", "Close", "Volume"]]
            df_ordered.dropna(how="all", subset=["Open", "High", "Low", "Close", "Volume"], inplace=True)

            # 4. Stockage
            self.df_transformed = df_ordered
            self.logger.info(f"Transformed data shape: {df_ordered.shape}")

        except Exception as e:
            self.logger.exception(f"Error while transforming: {e}")
            raise  

    def load(self):
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
