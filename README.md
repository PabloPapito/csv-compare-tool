# csv-compare-tool

**csv-compare-tool** is a Python tool for comparing CSV files based on a specified key (e.g., `customer_id`). It generates a comprehensive Excel report containing summary statistics, detailed record-by-record comparisons, and a pivot table that highlights discrepancies for each common column. This tool is ideal for fast data analysis and identifying differences between datasets.

## Features

- **Custom Key Matching:** Compare CSV files using a user-defined key. If no key is provided, the tool attempts to auto-detect one using a default set of keywords.
- **Detailed Comparison:** The Excel report includes:
  - **Summary:** Overall statistics such as total keys in each file, common keys, and unique keys.
  - **File1 & File2:** Original CSV file contents.
  - **Detailed Comparison:** Record-by-record comparisons with values from both files, match indicators, and numerical delta for numeric fields.
  - **Unique Keys:** Lists of keys that are unique to each file.
  - **Pivot Table:** A pivot table summarizing discrepancies for each common column (matches, mismatches, percentages, and average delta for numeric data).
