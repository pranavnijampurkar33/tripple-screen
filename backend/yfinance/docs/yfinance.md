# yfinance data limits (Yahoo Finance API)

Historical depth depends on **interval**. These are Yahoo’s typical limits (enforced by the API, not by this project).

## Interval history limits

| Interval | Typical Yahoo limit |
|----------|---------------------|
| `1m` | ~7 days |
| `2m`, `5m`, `15m`, `30m`, `90m` | ~60 days |
| `1h` | **730 days** (~2 years) |
| `1d`, `5d`, `1wk`, `1mo` | Many years |


## Send Email
python .\sheet_and_alerts\send-mail.py