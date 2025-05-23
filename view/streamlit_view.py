import pandas as pd
from sqlalchemy import create_engine
import os

from model.model_config import EtlConfig
from helpers import helpers_logger
from helpers import helpers_export

class GetData:
    def __init__(self, config: EtlConfig):
        self.logger = helpers_logger.initLogger(config.streamlit.logger.logname, config.log_path,
                                                config.streamlit.logger.filename)
        self.config = config
        self.df_price = None
        self.df_meta = None
        self.db_path = os.path.join(
            self.config.root_path,
            self.config.database.file.format(self.config.main_parameters.output_version)
        )
        engine = create_engine(f"sqlite:///{self.db_path}")
        self.df_price = pd.read_sql_table(self.config.database.benchmark_table, con=engine)
        self.df_meta = pd.read_sql_table(self.config.database.metadata_table, con=engine)
        engine.dispose()

        self.df_merged = self.df_price.merge(self.df_meta, on="ticker", how="left")
# 
# class PortfolioDashboard:
#     def __init__(self, data: GetData):

