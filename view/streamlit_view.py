import os
import pandas as pd
from sqlalchemy import create_engine

import streamlit as st

from model.model_config import EtlConfig

from helpers import helpers_logger
from helpers.helpers_streamlit import compute_indicators

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
        self.config = config
        self.logger = helpers_logger.initLogger(self.config.streamlit.logger.logname, self.config.log_path,
                                                self.config.streamlit.logger.filename)
        self.df = df
        self.min_date = self.df['date'].min()
        self.max_date = self.df['date'].max()

    def get_tickers_in_period(self, start_date, end_date):
        df_period = self.df[
            (self.df['date'] >= pd.Timestamp(start_date)) &
            (self.df['date'] <= pd.Timestamp(end_date))
            ]
        return df_period['ticker'].unique().tolist()

    def display(self):
        st.title("Dashboard portefeuille")

        date_input = st.date_input(
            "Choisissez la période d'analyse",
            value=(self.min_date, self.max_date),
            min_value=self.min_date,
            max_value=self.max_date
        )

        # Cas 1 : Aucune date sélectionnée (cas ultra rare)
        if date_input is None or (isinstance(date_input, tuple) and any(d is None for d in date_input)):
            st.warning("Veuillez sélectionner une période (deux dates).")
            return

        # Cas 2 : Une seule date (et pas une plage)
        if not isinstance(date_input, tuple) or len(date_input) != 2:
            st.warning("Veuillez sélectionner une période complète (date de début ET date de fin).")
            return

        start_date, end_date = date_input
        # Cas 3 : Dates invalides (ordre incorrect)
        if start_date >= end_date:
            st.warning("La date de fin doit être postérieure à la date de début.")
            return

        # 2. Récupère les tickers valides pour cette période
        tickers_in_period = self.get_tickers_in_period(start_date, end_date)
        default_tickers = [t for t in self.config.streamlit.portfolio.default_tickers if t in tickers_in_period]

        # 3. Adapter dynamiquement les tickers par défaut selon la période
        if len(tickers_in_period) == 0:
            st.warning(
                "Aucune action cotée sur cette période. Attention : il n'y a pas de cotation le week-end ni les jours fériés.")
            return

        # 4. Multiselect tickers (limité à ceux valides)
        tickers = st.multiselect(
            "Choisissez vos actions",
            options=tickers_in_period,
            default=default_tickers,
            max_selections=3,
            key="tickers_multiselect"
        )
        st.session_state["selected_tickers"] = tickers

        # 5. Contrôle UX final
        if not tickers:
            st.info("Sélectionnez au moins une action pour activer l’analyse.")
            return  # Pas de bouton tant que rien n'est sélectionné

        if st.button("Lancer l'analyse"):
            df_result = self.df[
                (self.df['date'] >= pd.Timestamp(start_date)) &
                (self.df['date'] <= pd.Timestamp(end_date)) &
                (self.df['ticker'].isin(tickers))
                ]
            if df_result.empty:
                st.warning("Aucune donnée sur cette période et ces actions. Veuillez changer la sélection.")
                return
            st.success("Analyse en cours !")

            # 1. Pivot portefeuille (tickers sélectionnés)
            df_pivot = df_result.pivot(index='date', columns='ticker', values='close').sort_index()

            # 2. garde uniquement les dates où tous les tickers ont un prix (évite biais jours fériés)**
            df_pivot = df_pivot.dropna(how='any', axis=0)
            if df_pivot.empty:
                st.warning("Aucune date commune de cotation pour toutes les actions sélectionnées sur la période.")
                return

            # 3. Benchmark : moyenne équipondérée de TOUS les tickers (benchmark officiel)
            benchmark_tickers = self.df['ticker'].unique()
            df_benchmark = self.df[
                (self.df['date'] >= pd.Timestamp(start_date)) &
                (self.df['date'] <= pd.Timestamp(end_date)) &
                (self.df['ticker'].isin(benchmark_tickers))
                ]
            df_bench_pivot = df_benchmark.pivot(index='date', columns='ticker', values='close').sort_index()

            # 4. Supprimer les lignes où toutes les valeurs sont NaN (dates où aucun prix disponible)
            df_pivot = df_pivot.dropna(how='any', axis=0)
            df_bench_pivot = df_bench_pivot.dropna(how='any', axis=0)

            # 5. Garder seulement les dates communes aux deux DataFrames
            common_dates = df_pivot.index.intersection(df_bench_pivot.index)
            df_pivot = df_pivot.loc[common_dates]
            df_bench_pivot = df_bench_pivot.loc[common_dates]

            # 6. Calculer les moyennes équipondérées (en ignorant les NaN éventuels par date)
            portfolio_prices = df_pivot.mean(axis=1)
            benchmark_prices = df_bench_pivot.mean(axis=1)
            portfolio_prices = portfolio_prices.dropna()
            benchmark_prices = benchmark_prices.dropna()

            st.info(f"{len(portfolio_prices)} jours de cotation utilisés pour les calculs.")

            # 7. Appeler ta fonction helpers pour les indicateurs
            ind_pf = compute_indicators(portfolio_prices, self.config)
            ind_bm = compute_indicators(benchmark_prices, self.config)

            indicateurs = [
                "Performance cumulée",
                "Volatilité annualisée",
                "Sharpe",
                "Max Drawdown"
            ]

            resultats = {
                "Portefeuille": [ind_pf[k] for k in indicateurs],
                "Benchmark": [ind_bm[k] for k in indicateurs]
            }
            df_comp = pd.DataFrame(resultats, index=indicateurs)
            df_comp["Écart"] = df_comp["Portefeuille"] - df_comp["Benchmark"]

            # DEBUG - Afficher les têtes pour voir ce qu'il se passe
            st.write("HEAD df_pivot (portfolio):")
            st.write(df_pivot.head())
            st.write("HEAD df_bench_pivot (benchmark):")
            st.write(df_bench_pivot.head())
            st.write("Portfolio prices:", portfolio_prices.head())
            st.write("Benchmark prices:", benchmark_prices.head())

            # Affichage du tableau final
            st.dataframe(df_comp)



        # weights = {}  # On va remplir ce dictionnaire avec les pondérations choisies par l'utilisateur, par ticker
        # total_weight = 0  # Pour additionner les pondérations et vérifier qu'on arrive bien à 1
        # for ticker in tickers:  # Pour chaque action sélectionnée (max 3 ici)
        #     # Pondération par défaut : soit celle du fichier de config, soit équipondéré si pas trouvé dans la config
        #     default_weight = self.config.streamlit.portfolio.default_weights.get(ticker, 1 / len(tickers))
        #     # Affiche un slider pour choisir la pondération de ce ticker
        #     weight = st.slider(
        #         f"Pondération de {ticker}",  # Label du slider
        #         min_value=0.0, max_value=1.0,  # Slider de 0 à 1 (0% à 100%)
        #         value=float(default_weight),  # Valeur affichée par défaut
        #         step=0.01,  # On bouge le slider par pas de 1%
        #         key=f"weight_{ticker}"  # Une clé unique pour chaque ticker (important dans Streamlit)
        #     )
        #     weights[ticker] = weight  # On sauvegarde la pondération dans le dict, ex : {'BNP.PA': 0.3, ...}
        #     total_weight += weight

        # # Contrôle que la somme des pondérations fait bien 1 (ou presque)
        # if abs(total_weight - 1) > 0.01:
        #     st.warning(f"La somme des pondérations doit être égale à 1 (actuellement : {total_weight:.2f})")
        #     return