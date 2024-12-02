def calculate_price_groups(max_price, min_price, num_groups):
    ratio = (min_price / max_price) ** (1 / (num_groups - 1))
    prices = [round(max_price * (ratio ** i), 2) for i in range(num_groups)]
    return prices