"""
    Title: Sample Momentum Trading Strategy Template
    Description: A simple trend-following momentum trading algorithm is
    applied to an asset. A long position is taken when there is a golden
    cross and a short position is taken when there is a death cross.
    Dataset: NSE Minute

    ############################# DISCLAIMER #############################
    This is a strategy template only and should not be used for live
    trading without appropriate backtesting and tweaking of the strategy
    parameters.
    ######################################################################
"""

# Import numpy
import numpy as np

# Import Zipline libraries
from zipline.api import (
                            symbol,
                            order_target_percent,
                            schedule_function,
                            date_rules,
                            time_rules,
                        )


def initialize(context):
    # Define symbol
    context.security = symbol('TATASTEEL')

    # Define short term window size
    context.short_term_window = 50

    # Define long term window size
    context.long_term_window = 200

    # Define lookback
    context.lookback = context.long_term_window + context.short_term_window

    # Schedule the rebalance function
    schedule_function(
                        rebalance,
                        date_rule=date_rules.every_day(),
                        time_rule=time_rules.market_close(minutes=5)
                     )


def rebalance(context, data):
    """
        A function to rebalance the portfolio. This function is called by the
        schedule_function above.
    """

    # Fetch lookback no. days data for the given security
    prices = data.history(
        context.security,
        ['close'],
        context.lookback,
        '1d')

    # Store the short term moving average in a new column 'window_ST'
    prices.loc[:, 'window_ST'] = prices['close'].rolling(
                                            context.short_term_window).mean()

    # Store the long term moving average in a new column 'window_LT'
    prices.loc[:, 'window_LT'] = prices['close'].rolling(
                                            context.long_term_window).mean()

    # Get the latest signal, 1 for golden cross, -1 for death cross
    prices.loc[:, 'signal'] = np.where(
                            prices['window_ST'] > prices['window_LT'], 1, -1)

    latest_signal = prices.loc[:, 'signal'][-1]

    # Place the order
    if latest_signal == 1:
        # Long position
        order_target_percent(context.security, 1)

    # Comment the elif block if you want a long-only strategy
    elif latest_signal == -1:
        # Short position
        order_target_percent(context.security, -1)

    else:
        # Square-off position
        order_target_percent(context.security, 0)
