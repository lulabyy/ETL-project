import os
import pandas as pd
from sqlalchemy import create_engine

import streamlit as st
import matplotlib.pyplot as plt

from model.model_config import Config

from helpers import helpers_logger
from helpers.helpers_streamlit import compute_indicators

class Data:
    def __init__(self, config: Config):
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

class PortfolioDashboard:
    def __init__(self, df, config: Config):
        self.config = config
        self.logger = helpers_logger.initLogger(self.config.streamlit.logger.logname, self.config.log_path,
                                                self.config.streamlit.logger.filename)
        self.df = df
        self.min_date = self.df['date'].min()
        self.max_date = self.df['date'].max()

        self.logger.info("PortfolioDashboard initialized with dataframe of shape %s", self.df.shape)
        self.logger.info("Min date: %s, Max date: %s", self.min_date, self.max_date)

    def get_tickers_in_period(self, start_date, end_date):
        df_period = self.df[
            (self.df['date'] >= pd.Timestamp(start_date)) &
            (self.df['date'] <= pd.Timestamp(end_date))
            ]
        tickers = df_period['ticker'].unique().tolist()
        self.logger.info("Tickers found for the period: %s", tickers)
        return tickers
    
    def select_dates(self):
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

        self.logger.info("Start date selected: %s, End date selected: %s", start_date, end_date)

        if not start_date or not end_date:
            self.logger.warning("Start date or end date not selected.")
            st.warning("Please select both a start and end date.")
            return None, None
        
        if start_date >= end_date:
            self.logger.warning("End date must be later than the start date.")
            st.warning("The end date must be later than the start date.")
            return None, None
        
        return start_date, end_date

    def select_tickers(self, start_date, end_date):
        # 1. Retrieve valid tickers for this period
        tickers_in_period = self.get_tickers_in_period(start_date, end_date)
        default_tickers = [t for t in self.config.streamlit.portfolio.default_tickers if t in tickers_in_period]
        self.logger.info("Default tickers for the period: %s", default_tickers)

        # 2. Dynamically adjust default tickers based on the selected period
        if len(tickers_in_period) == 0:
            self.logger.warning("No stocks are traded during this period.")
            st.warning("No stocks are traded during this period. Note: Markets are closed on weekends and public holidays.")
            return []
        
        # 3. Multiselect tickers (limited to valid ones)
        tickers = st.multiselect(
            "Select your stocks",
            options=tickers_in_period,
            default=default_tickers,
            max_selections=3,
            key="tickers_multiselect"
        )
        self.logger.info("Tickers selected by user: %s", tickers)
        st.session_state["selected_tickers"] = tickers

        # 4. Final UX check
        if not tickers:
            self.logger.info("No tickers selected, analysis not enabled.")
            st.info("Select at least one stock to enable the analysis.")

        return tickers

    def prepare_data(self, start_date, end_date, tickers):
        df_result = self.df[
            (self.df['date'] >= pd.Timestamp(start_date)) &
            (self.df['date'] <= pd.Timestamp(end_date)) &
            (self.df['ticker'].isin(tickers))
        ]
        self.logger.info("Resulting dataframe for analysis has shape: %s", df_result.shape)
        if df_result.empty:
            self.logger.warning("No data available for this period and these stocks.")
            st.warning("No data available for this period and these stocks. Please change your selection.")
            return None, None, None, None
        st.success("Analysis in progress !")

        # 1. Pivot portfolio (selected tickers)
        df_pivot = df_result.pivot(index='date', columns='ticker', values='close').sort_index()
        self.logger.info("Pivoted dataframe for selected tickers has shape: %s", df_pivot.shape)

        # 2. Keep only the dates where all tickers have a price (to avoid holiday bias)
        df_pivot = df_pivot.dropna(how='any', axis=0)
        if df_pivot.empty:
            self.logger.warning("No common trading date for all selected stocks in the chosen period.")
            st.warning("No common trading date for all selected stocks in the chosen period.")
            return None, None, None, None

        # 3. Prepare the benchmark DataFrame: closing prices for all tickers over the selected period
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
        self.logger.info("df_pivot after dropping NA: %s, df_bench_pivot after dropping NA: %s",
                         df_pivot.shape, df_bench_pivot.shape)

        # 5. Keep only the dates common to both DataFrames
        common_dates = df_pivot.index.intersection(df_bench_pivot.index)
        df_pivot = df_pivot.loc[common_dates]
        df_bench_pivot = df_bench_pivot.loc[common_dates]
        self.logger.info("Number of common trading dates: %d", len(common_dates))

        # 6. Calculate the equally weighted averages
        portfolio_prices = df_pivot.mean(axis=1)
        benchmark_prices = df_bench_pivot.mean(axis=1)
        portfolio_prices = portfolio_prices.dropna()
        benchmark_prices = benchmark_prices.dropna()
        self.logger.info("Portfolio prices length: %d, Benchmark prices length: %d",
                         len(portfolio_prices), len(benchmark_prices))
        st.info(f"{len(portfolio_prices)} trading days used for calculations.")

        return portfolio_prices, benchmark_prices, tickers, benchmark_tickers

    def show_comparisons(self, portfolio_prices, benchmark_prices) -> None:
        ind_pf = compute_indicators(portfolio_prices, self.config)
        ind_bm = compute_indicators(benchmark_prices, self.config)
        self.logger.info("Indicators computed for portfolio and benchmark.")

        indicateurs = [
            "Cumulative Performance (%)",
            "Annualized Volatility (%)",
            "Max Drawdown (%)",
            "Sharpe Ratio"
        ]

        resultats = {
            "Portfolio": [ind_pf[k] for k in indicateurs],
            "Benchmark": [ind_bm[k] for k in indicateurs]
        }
        df_comp = pd.DataFrame(resultats, index=indicateurs)
        df_comp["Gap (Portfolio - Benchmark)"] = df_comp["Portfolio"] - df_comp["Benchmark"]

        self.logger.info("Comparison dataframe ready for display.")

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

    def show_pie_charts(self, tickers, benchmark_tickers) -> None:
        df_selection_pf = self.df[self.df['ticker'].isin(tickers)]
        df_selection_bm = self.df[self.df['ticker'].isin(benchmark_tickers)]

        fig, axs = plt.subplots(2, 2, figsize=(10, 8))

        # Portfolio - sector
        self.plot_pie(df_selection_pf, "sector", axs[0, 0], "Portfolio - Sector Breakdown")
        # Portfolio - country
        self.plot_pie(df_selection_pf, "country", axs[0, 1], "Portfolio - Country Breakdown")
        # Benchmark - sector
        self.plot_pie(df_selection_bm, "sector", axs[1, 0], "Benchmark - Sector Breakdown")
        # Benchmark - country
        self.plot_pie(df_selection_bm, "country", axs[1, 1], "Benchmark - Country Breakdown")

        plt.tight_layout(pad=5)
        with st.expander("Portfolio & Benchmark Pie Charts"):
            st.pyplot(fig)

    @staticmethod
    def plot_pie(df, col, ax, title):
        if not df.empty and col in df.columns:
            counts = df[col].value_counts(normalize=True)
            if len(counts) > 1:
                counts.plot.pie(
                    autopct='%1.0f%%', ylabel='', ax=ax, title=title
                )
            else:
                ax.axis('off')
                ax.set_title(f"{title} (Single {col.title()})")
        else:
            ax.axis('off')
            ax.set_title(f"{title} (No data)")

    def display(self):
        st.title("Portfolio Dashboard")
        self.logger.info("Displaying Portfolio Dashboard")

        # les dates
        start_date, end_date = self.select_dates()
        if not start_date or not end_date:
            return
        
        # sélection de tickers
        tickers = self.select_tickers(start_date, end_date)
        if not tickers:
            return
        
        # bouton pour lancer l'analyse
        if st.button("Run analysis"):
            self.logger.info("Run analysis button pressed.")

            portfolio_prices, benchmark_prices, selected_tickers, benchmark_tickers = self.prepare_data(start_date, end_date, tickers)
            if portfolio_prices is None:
                return
            
            self.show_comparisons(portfolio_prices, benchmark_prices)
            self.show_pie_charts(selected_tickers, benchmark_tickers)
