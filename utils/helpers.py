def cal_take_profit(cupr, reward_percentage):
    """
    Calculate the take profit price.
    :param cupr: Current price of the asset
    :param reward_percentage: Percentage gain to take profit (e.g., 0.05 for 5%)
    :return: Take profit price
    """
    return cupr + (cupr * reward_percentage)


def cal_stop_loss(cupr, risk_percentage):
    """
    Calculate the stop loss price.
    :param cupr: Current price of the asset
    :param risk_percentage: Percentage drop to set stop loss (e.g., 0.02 for 2%)
    :return: Stop loss price
    """
    return cupr - (cupr * risk_percentage)