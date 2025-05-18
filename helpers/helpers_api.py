from typing import Sequence

import pandas as pd


def get_fund_data_from_api(fund_names: Sequence[str]) -> pd.DataFrame:
    """
    Fake API call.
    :param fund_names: list of fund names
    :return: Always the same dataframe
    """
    fake_results = {
        "Fund Name": [
            "RiskBalanced_Fund",
            "Portfolio_Defensive",
            "LongTermAlpha_portfolio",
        ],
        "Last Valuation Date": ["2024-11-10", "2024-11-05", "2024-11-01"],
        "Net Asset Value (NAV)": ["150000000", "120000000", "180000000"],
        "Portfolio Manager": ["Sophie", "Youssef", "Sarah"],
    }

    return pd.DataFrame(fake_results)
 