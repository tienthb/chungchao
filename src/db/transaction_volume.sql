CREATE TABLE IF NOT EXISTS transaction_volume (
	ticker VARCHAR(20),
	transaction_date date,
	buy_vol INT8,
	buy_amt INT8,
	sell_vol INT8,
	sell_amt INT8,
	volume INT8,
	oi INT8,
	daily_vol INT8
) 