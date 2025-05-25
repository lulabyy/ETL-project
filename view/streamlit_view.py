import os
import pandas as pd
from sqlalchemy import create_engine

import streamlit as st

from model.model_config import EtlConfig

from helpers import helpers_logger

class Data:
    def __init__(self, config: EtlConfig):
        self.config = config
        self.logger = helpers_logger.initLogger(self.config.streamlit.logger.logname, self.config.log_path,
                                                self.config.streamlit.logger.filename)
        self.df_price = None
        self.df_meta = None
        self.df_merged = None

        self.load_df_from_db()

    def load_df_from_db(self):
        db_path = os.path.join(
            self.config.root_path,
            self.config.database.dir,
            self.config.database.file.format(self.config.main_parameters.output_version)
        )

        engine = create_engine(f"sqlite:///{db_path}")
        self.df_price = pd.read_sql_table(self.config.database.benchmark_table, con=engine)
        self.df_meta = pd.read_sql_table(self.config.database.metadata_table, con=engine)
        engine.dispose()

        self.df_merged = self.df_price.merge(self.df_meta, on="ticker", how="left")

class PortfolioDashboard:
    def __init__(self, config: EtlConfig, data: Data):
        self.config = config
        self.data = data
        self.df = data.df_merged
        self.all_tickers = self.df['ticker'].unique()

    def display(self):
        st.title("Dashboard portefeuille")

        min_date = self.df['date'].min()
        max_date = self.df['date'].max()

        start_date, end_date = st.date_input(
            "Choisissez la période d'analyse",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date
        )

        # Filtrer le df selon la période
        df_period = self.df[
            (self.df['date'] >= pd.Timestamp(start_date)) &
            (self.df['date'] <= pd.Timestamp(end_date))
            ]

        # Proposer les tickers dispo sur cette période
        @st.cache_data
        def get_all_tickers(df):
            return df['ticker'].unique()

        all_tickers = get_all_tickers(self.df)
        tickers = st.multiselect(
            "Choisissez jusqu'à 3 actions",
            options=all_tickers,
            default=self.config.streamlit.portfolio.default_tickers,
            max_selections=self.config.streamlit.portfolio.max_nb_tickers
        )

        st.write(f"Tickers sélectionnés : {tickers}")
