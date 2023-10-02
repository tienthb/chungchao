CREATE TABLE IF NOT EXISTS transaction_snapshot (
    ticker VARCHAR(20),
    total_buy_3_months INT8,
    total_sell_3_months INT8,
    total_vol_n_months INT8,
    price INT
)
