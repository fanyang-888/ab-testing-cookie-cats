# Experiment Data

This folder contains the dataset used for the Cookie Cats A/B test lab.

## Data file

- **File name:** `cookie_cats.csv`
- **Format:** CSV (comma-separated values)

## Column definitions (schema)

| Column           | Description |
|------------------|-------------|
| `userid`         | User identifier (int) |
| `version`         | Experiment group: `gate_30` (control) or `gate_40` (treatment) |
| `sum_gamerounds` | Total game rounds played in the first week (continuous) |
| `retention_1`    | Whether the user returned on day 1 (0 or 1) |
| `retention_7`    | Whether the user returned on day 7 (0 or 1) |

## Analysis window

- The data covers **D0–D7** after first exposure (first week post sign-up or first exposure to the experiment).

## How to use

1. Place `cookie_cats.csv` in this `data/` folder.
2. Run the analysis notebook `code/A_B_Testing_Python.ipynb`; it expects the dataset at `data/cookie_cats.csv`.

## Notes

- If the full dataset cannot be shared publicly, use a small sample and document how to reproduce the full dataset.
