# Data

This project analyzes the Cookie Cats A/B test dataset.

## File
- `cookie_cats.xlsx` (or `cookie_cats.csv` if converted)

## Columns (schema)
- `userid`: user identifier
- `version`: experiment group (`gate_30` or `gate_40`)
- `sum_gamerounds`: total rounds played in the first week
- `retention_1`: returned on day 1 (0/1)
- `retention_7`: returned on day 7 (0/1)

## Analysis window
- D0–D7 after first exposure (as represented in the dataset)

## Notes
- If the original dataset cannot be shared publicly, keep only a small sample and document how to reproduce the full dataset.
