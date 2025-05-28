import os
import pandas as pd
from sqlalchemy import create_engine

import streamlit as st
import matplotlib.pyplot as plt

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

        self.logger.info("Initializing Data class.")
        self.load_df_from_db()

    def load_df_from_db(self):
        db_path = os.path.join(
            self.config.root_path,
            self.config.database.dir,
            self.config.database.file.format(self.config.main_parameters.output_version)
        )
        self.logger.info(f"Database path resolved: {db_path}")

        try:
            engine = create_engine(f"sqlite:///{db_path}")
            self.logger.info("Successfully connected to the SQLite database.")

            self.df_price = pd.read_sql_table(self.config.database.benchmark_table, con=engine)
            self.logger.info(
                f"Loaded price table '{self.config.database.benchmark_table}' with shape {self.df_price.shape}."
            )

            self.df_meta = pd.read_sql_table(self.config.database.metadata_table, con=engine)
            self.logger.info(
                f"Loaded metadata table '{self.config.database.metadata_table}' with shape {self.df_meta.shape}."
            )

            engine.dispose()
            self.logger.info("Closed connection to the SQLite database.")

            self.df_merged = self.df_price.merge(self.df_meta, on="ticker", how="left")
            self.logger.info(
                f"Merged DataFrames on 'ticker' column. Final merged DataFrame shape: {self.df_merged.shape}."
            )
        except Exception as e:
            self.logger.error(f"Error while loading data from database: {e}")
            raise

class PortfolioDashboard: # faire les logs
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
        st.title("Portfolio Dashboard")

        start_date = st.date_input(
            "Select start date",
            value=self.min_date,
            min_value=self.min_date,
            max_value=self.max_date,
            key="start_date"
        )
        end_date = st.date_input(
            "Select end date",
            value=self.max_date,
            min_value=self.min_date,
            max_value=self.max_date,
            key="end_date"
        )

        if not start_date or not end_date:
            st.warning("Please select both a start and end date.")
            return

        if start_date >= end_date:
            st.warning("The end date must be later than the start date.")
            return

        # 2. Retrieve valid tickers for this period
        tickers_in_period = self.get_tickers_in_period(start_date, end_date)
        default_tickers = [t for t in self.config.streamlit.portfolio.default_tickers if t in tickers_in_period]

        # 3. Dynamically adjust default tickers based on the selected period
        if len(tickers_in_period) == 0:
            st.warning(
                "No stocks are traded during this period. Note: Markets are closed on weekends and public holidays.")
            return

        # 4. Multiselect tickers (limited to valid ones)
        tickers = st.multiselect(
            "Select your stocks",
            options=tickers_in_period,
            default=default_tickers,
            max_selections=3,
            key="tickers_multiselect"
        )
        st.session_state["selected_tickers"] = tickers

        # 5. Final UX check
        if not tickers:
            st.info("Select at least one stock to enable the analysis.")
            return  # Pas de bouton tant que rien n'est sélectionné

        if st.button("Run analysis"):
            df_result = self.df[
                (self.df['date'] >= pd.Timestamp(start_date)) &
                (self.df['date'] <= pd.Timestamp(end_date)) &
                (self.df['ticker'].isin(tickers))
                ]
            if df_result.empty:
                st.warning("No data available for this period and these stocks. Please change your selection.")
                return
            st.success("Analysis in progress !")

            # 1. Pivot portfolio (selected tickers)
            df_pivot = df_result.pivot(index='date', columns='ticker', values='close').sort_index()

            # 2. Keep only the dates where all tickers have a price (to avoid holiday bias)
            df_pivot = df_pivot.dropna(how='any', axis=0)
            if df_pivot.empty:
                st.warning("No common trading date for all selected stocks in the chosen period.")
                return

            # 3. Benchmark: equally weighted average of ALL tickers (official benchmark)
            benchmark_tickers = self.df['ticker'].unique()
            df_benchmark = self.df[
                (self.df['date'] >= pd.Timestamp(start_date)) &
                (self.df['date'] <= pd.Timestamp(end_date)) &
                (self.df['ticker'].isin(benchmark_tickers))
                ]
            df_bench_pivot = df_benchmark.pivot(index='date', columns='ticker', values='close').sort_index()

            # 4. Drop rows where all values are NaN (dates with no available prices)
            df_pivot = df_pivot.dropna(how='any', axis=0)
            df_bench_pivot = df_bench_pivot.dropna(how='any', axis=0)

            # 5. Keep only the dates common to both DataFrames
            common_dates = df_pivot.index.intersection(df_bench_pivot.index)
            df_pivot = df_pivot.loc[common_dates]
            df_bench_pivot = df_bench_pivot.loc[common_dates]

            # 6. Calculate the equally weighted averages
            portfolio_prices = df_pivot.mean(axis=1)
            benchmark_prices = df_bench_pivot.mean(axis=1)
            portfolio_prices = portfolio_prices.dropna()
            benchmark_prices = benchmark_prices.dropna()

            st.info(f"{len(portfolio_prices)} trading days used for calculations.")

            ind_pf = compute_indicators(portfolio_prices, self.config)
            ind_bm = compute_indicators(benchmark_prices, self.config)

            indicateurs = [
                "Cumulative Performance",
                "Annualized Volatility",
                "Sharpe Ratio",
                "Max Drawdown"
            ]

            resultats = {
                "Portfolio": [ind_pf[k] for k in indicateurs],
                "Benchmark": [ind_bm[k] for k in indicateurs]
            }
            df_comp = pd.DataFrame(resultats, index=indicateurs)
            df_comp["Gap"] = df_comp["Portfolio"] - df_comp["Benchmark"]

            # Display final dataset
            st.dataframe(df_comp)

            df_evol = pd.DataFrame({
                "Portfolio": portfolio_prices,
                "Benchmark": benchmark_prices
            }).dropna()

            with st.expander("Show time series table"):
                st.dataframe(df_evol)

            with st.expander("Portfolio vs Benchmark evolution chart"):
                st.line_chart(df_evol)

            df_selection_pf = self.df[self.df['ticker'].isin(tickers)]
            df_selection_bm = self.df[self.df['ticker'].isin(benchmark_tickers)]

            # Create a 2x2 grid of subplots for pie charts
            fig, axs = plt.subplots(2, 2, figsize=(10, 8))

            # PORTFOLIO – sector
            if not df_selection_pf.empty and "sector" in df_selection_pf.columns:
                secteur_pf = df_selection_pf['sector'].value_counts(normalize=True)
                if len(secteur_pf) > 1:
                    secteur_pf.plot.pie(
                        autopct='%1.0f%%', ylabel='', ax=axs[0, 0],
                        title="Portfolio – Sector Breakdown"
                    )
                else:
                    axs[0, 0].axis('off')
                    axs[0, 0].set_title("Portfolio – Sector Breakdown (Single Sector)")
            else:
                axs[0, 0].axis('off')
                axs[0, 0].set_title("Portfolio – Sector Breakdown (No data)")

            # PORTFOLIO – country
            if not df_selection_pf.empty and "country" in df_selection_pf.columns:
                country_pf = df_selection_pf['country'].value_counts(normalize=True)
                if len(country_pf) > 1:
                    country_pf.plot.pie(
                        autopct='%1.0f%%', ylabel='', ax=axs[0, 1],
                        title="Portfolio – Country Breakdown"
                    )
                else:
                    axs[0, 1].axis('off')
                    axs[0, 1].set_title("Portfolio – Country Breakdown (Single Country)")
            else:
                axs[0, 1].axis('off')
                axs[0, 1].set_title("Portfolio – Country Breakdown (No data)")

            # BENCHMARK – sector
            if not df_selection_bm.empty and "sector" in df_selection_bm.columns:
                secteur_bm = df_selection_bm['sector'].value_counts(normalize=True)
                if len(secteur_bm) > 1:
                    secteur_bm.plot.pie(
                        autopct='%1.0f%%', ylabel='', ax=axs[1, 0],
                        title="Benchmark – Sector Breakdown"
                    )
                else:
                    axs[1, 0].axis('off')
                    axs[1, 0].set_title("Benchmark – Sector Breakdown (Single Sector)")
            else:
                axs[1, 0].axis('off')
                axs[1, 0].set_title("Benchmark – Sector Breakdown (No data)")

            # BENCHMARK – country
            if not df_selection_bm.empty and "country" in df_selection_bm.columns:
                country_bm = df_selection_bm['country'].value_counts(normalize=True)
                if len(country_bm) > 1:
                    country_bm.plot.pie(
                        autopct='%1.0f%%', ylabel='', ax=axs[1, 1],
                        title="Benchmark – Country Breakdown"
                    )
                else:
                    axs[1, 1].axis('off')
                    axs[1, 1].set_title("Benchmark – Country Breakdown (Single Country)")
            else:
                axs[1, 1].axis('off')
                axs[1, 1].set_title("Benchmark – Country Breakdown (No data)")

            plt.tight_layout(pad=5)
            with st.expander("Portfolio & Benchmark Pie Charts"):
                st.pyplot(fig)