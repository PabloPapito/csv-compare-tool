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

## Installation

1. **Clone the Repository:**

    ```bash
    git clone https://github.com/yourusername/csv-compare-tool.git
    cd csv-compare-tool

2. **(Optional) Create and Activate a Virtual Environment:**

3. **Install Dependencies:**

    ```bash
    pip install -r requirements.txt

## Usage

1. **Prepare Your CSV Files:**  
   Ensure that your CSV files include the key column you want to use for matching (e.g., `customer_id`).

2. **Configure the Script:**  
   Open the main script (`lazyDev.py`) and edit the file paths and specify the key column in the main section. For example:

   ```python
   if __name__ == "__main__":
       file1 = r"path\to\file1.csv"
       file2 = r"path\to\file2.csv"
       output_file = r"path\to\output\Comparison.xlsx"
       compare_csv_files(file1, file2, output_file, match_key="customer_id", encoding="utf-8", sep=",")

## Contributing

Contributions are welcome! If you have ideas for improvements, bug fixes, or new features, please follow these steps:

1. **Fork the Repository:**  
   Click the "Fork" button on the top-right of the GitHub page to create your own copy.

2. **Create a New Branch:**  
   Use a descriptive name for your branch, for example:
   ```bash
   git checkout -b feature/your-feature-name

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
