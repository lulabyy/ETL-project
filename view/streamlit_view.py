import pandas as pd
from sqlalchemy import create_engine
import os
import streamlit as st
from helpers import helpers_config

from model.model_config import EtlConfig
from helpers import helpers_logger

config = helpers_config.get_config()

class Data:
    def __init__(self, config: EtlConfig):
        self.config = config
        self.logger = helpers_logger.initLogger(self.config.streamlit.logger.logname, self.config.log_path,
                                                self.config.streamlit.logger.filename)
        self.df_price = None
        self.df_meta = None
        self.db_path = os.path.join(
            self.config.root_path,
            self.config.database.dir,
            self.config.database.file.format(self.config.main_parameters.output_version)
        )
        engine = create_engine(f"sqlite:///{self.db_path}")

        self.df_price = pd.read_sql_table(self.config.database.benchmark_table, con=engine)
        self.df_meta = pd.read_sql_table(self.config.database.metadata_table, con=engine)
        engine.dispose()
        print("📊 Colonnes de df_price :", self.df_price.columns.tolist())
        print("📊 Colonnes de df_meta  :", self.df_meta.columns.tolist())
        self.df_merged = self.df_price.merge(self.df_meta, on="ticker", how="left")

        def getDataFrame(self):
            return self.df_price, self.df_meta

class PortfolioDashboard:
    def __init__(self, config: EtlConfig, data: Data):
        self.data = data
        self.config = config
        self.df = data.df_merged

    def display(self):
        st.title("Dashboard portefeuille")

        tickers = st.multiselect(
            "Choisissez jusqu'à 3 actions :",
            options=self.df["ticker"].unique(),
            default=self.config.streamlit.portfolio.default_tickers,
            max_selections=self.config.streamlit.portfolio.max_nb_tickers
                )

        st.write(f"Tickers sélectionnés : {tickers}")
