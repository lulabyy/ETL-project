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
    def __init__(self, df, config: EtlConfig):
        self.df = df
        self.config = config
        self.min_date = self.df['date'].min()
        self.max_date = self.df['date'].max()

    def get_tickers_in_period(self, start_date, end_date):
        df_period = self.df[
            (self.df['date'] >= pd.Timestamp(start_date)) &
            (self.df['date'] <= pd.Timestamp(end_date))
        ]
        return df_period['ticker'].unique()

    def display(self):
        st.title("Dashboard portefeuille")

        start_date, end_date = st.date_input(
            "Choisissez la période d'analyse",
            value=(self.min_date, self.max_date),
            min_value=self.min_date,
            max_value=self.max_date
        )

        # 2. Récupère les tickers valides pour cette période
        tickers_in_period = self.get_tickers_in_period(start_date, end_date)

        # 3. Empêche toute sélection impossible
        if len(tickers_in_period) == 0:
            st.warning("Aucune action n'a de données sur la période sélectionnée. Merci de choisir une autre période.")
            return

        # 5. Multiselect tickers (limité à ceux valides)
        tickers = st.multiselect(
            "Choisissez vos actions",
            options=tickers_in_period,
            default=self.config.streamlit.portfolio.default_tickers,
            max_selections=3,
            key="tickers_multiselect"
        )
        st.session_state["selected_tickers"] = tickers

        # 6. Contrôle UX final
        if not tickers:
            st.info("Sélectionnez au moins une action pour activer l’analyse.")
            return  # Pas de bouton tant que rien n'est sélectionné

        # 7. Bouton d'analyse
        if st.button("Lancer l'analyse"):
            df_result = self.df[
                (self.df['date'] >= pd.Timestamp(start_date)) &
                (self.df['date'] <= pd.Timestamp(end_date)) &
                (self.df['ticker'].isin(tickers))
            ]
            if df_result.empty:
                st.warning("Aucune donnée sur cette période et ces actions. Veuillez changer la sélection.")
            else:
                st.success("Analyse en cours !")
