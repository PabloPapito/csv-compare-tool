import pandas as pd
import numpy as np

def find_match_column(columns, default_keywords=None):
    """
    Próbuje znaleźć kolumnę, którą można użyć jako klucz dopasowania,
    przeszukując nazwy kolumn pod kątem słów kluczowych.
    Jeśli default_keywords nie zostanie podane, używa domyślnej listy.
    """
    if default_keywords is None:
        default_keywords = ['id', 'identifier', 'customer_id', 'order_id']
    for col in columns:
        if any(keyword in col.lower() for keyword in default_keywords):
            return col
    return None

def create_pivot_table(df_detail, common_columns):
    """
    Dla każdej wspólnej kolumny (poza kluczem) oblicza:
      - Liczbę rekordów,
      - Liczbę zgodnych wartości,
      - Liczbę różnic,
      - Procent zgodnych i różnic,
      - Jeśli kolumna jest numeryczna (delta została obliczona), średnią wartość delta.
    Zwraca DataFrame zawierający te podsumowania.
    """
    pivot_summary = []
    total = len(df_detail)
    for col in common_columns:
        match_col = f"{col}_match"
        if match_col not in df_detail.columns:
            continue
        count_match = df_detail[match_col].sum()  # True=1
        count_diff = total - count_match
        percent_match = round(count_match / total * 100, 2) if total > 0 else 0
        percent_diff = round(count_diff / total * 100, 2) if total > 0 else 0

        delta_col = f"{col}_delta"
        if delta_col in df_detail.columns:
            avg_delta = df_detail[delta_col].dropna().mean()
            avg_delta = round(avg_delta, 2) if not np.isnan(avg_delta) else "N/A"
        else:
            avg_delta = "N/A"

        pivot_summary.append({
            "Column": col,
            "Total Records": total,
            "Matches": count_match,
            "Mismatches": count_diff,
            "Match Percentage (%)": percent_match,
            "Mismatch Percentage (%)": percent_diff,
            "Average Delta": avg_delta
        })
    return pd.DataFrame(pivot_summary)

def compare_csv_files(file1, file2, output_file, match_key=None, encoding='utf-8', sep=',', key_keywords=None):
    """
    Porównuje dwa pliki CSV i zapisuje wynikowy raport do pliku Excel.
    
    Parametry:
      - file1, file2: Ścieżki do plików CSV.
      - output_file: Ścieżka do pliku wyjściowego Excel.
      - match_key: Nazwa kolumny do dopasowania rekordów. Jeśli nie podasz, spróbuje automatycznie wykryć klucz
                   przy użyciu key_keywords (domyślnie: ['id', 'identifier', 'customer_id', 'order_id']).
      - encoding, sep: Parametry przekazywane do pd.read_csv.
      - key_keywords: Lista słów kluczowych do automatycznego wykrywania kolumny, jeśli match_key nie został podany.
    """
    # Wczytanie plików CSV
    df1 = pd.read_csv(file1, dtype=str, encoding=encoding, sep=sep)
    df2 = pd.read_csv(file2, dtype=str, encoding=encoding, sep=sep)
    df1.fillna('', inplace=True)
    df2.fillna('', inplace=True)

    # Ustalenie klucza dopasowania
    if match_key is None:
        if key_keywords is None:
            key_keywords = ['id', 'identifier', 'customer_id', 'order_id']
        match_key_candidate = find_match_column(df1.columns, default_keywords=key_keywords)
        if match_key_candidate is None:
            raise ValueError("Nie znaleziono kolumny do dopasowania w pliku 1!")
        match_key = match_key_candidate

    # Standaryzacja – zmieniamy nazwę kolumny match_key na "match_key" i normalizujemy jej wartości
    df1.rename(columns={match_key: "match_key"}, inplace=True)
    df2.rename(columns={match_key: "match_key"}, inplace=True)
    df1["match_key"] = df1["match_key"].astype(str).str.strip().str.lower()
    df2["match_key"] = df2["match_key"].astype(str).str.strip().str.lower()

    # Ustal wspólne kolumny (poza kluczem)
    common_columns = list(set(df1.columns).intersection(set(df2.columns)))
    common_columns = [col for col in common_columns if col != "match_key"]

    # Łączenie wierszy na podstawie match_key (inner merge)
    df_merged = pd.merge(df1, df2, on="match_key", how="inner", suffixes=("_file1", "_file2"))

    # Budujemy tabelę szczegółowego porównania – dla każdego rekordu (klucza)
    detailed_rows = []
    for _, row in df_merged.iterrows():
        key_val = row["match_key"]
        row_data = {"match_key": key_val}
        for col in common_columns:
            col_file1 = f"{col}_file1"
            col_file2 = f"{col}_file2"
            if col_file1 in row and col_file2 in row:
                value1 = row[col_file1]
                value2 = row[col_file2]
                is_match = value1 == value2
                row_data[f"{col}_file1"] = value1
                row_data[f"{col}_file2"] = value2
                row_data[f"{col}_match"] = is_match
                try:
                    num1 = float(value1)
                    num2 = float(value2)
                    row_data[f"{col}_delta"] = num2 - num1
                except ValueError:
                    row_data[f"{col}_delta"] = np.nan
        detailed_rows.append(row_data)
    df_detail = pd.DataFrame(detailed_rows)

    # Unikalne klucze w obu plikach
    keys1 = set(df1["match_key"])
    keys2 = set(df2["match_key"])
    unique1 = sorted(list(keys1 - keys2))
    unique2 = sorted(list(keys2 - keys1))

    # Podsumowanie – statystyki
    summary_lines = []
    summary_lines.append("############# SUMMARY #############")
    summary_lines.append(f"Total keys in file1: {len(keys1)}")
    summary_lines.append(f"Total keys in file2: {len(keys2)}")
    summary_lines.append(f"Common keys: {len(df_merged)}")
    summary_lines.append("")
    summary_lines.append("Keys only in file1:")
    summary_lines.append(", ".join(unique1) if unique1 else "None")
    summary_lines.append("")
    summary_lines.append("Keys only in file2:")
    summary_lines.append(", ".join(unique2) if unique2 else "None")
    summary_text = "\n".join(summary_lines)

    # Tabela przestawna z danych szczegółowych – podsumowanie różnic dla każdej wspólnej kolumny
    pivot_table = create_pivot_table(df_detail, common_columns)

    # Zapis do pliku Excel – arkusze:
    # 1. Summary
    # 2. File1 – oryginalny plik 1
    # 3. File2 – oryginalny plik 2
    # 4. Detailed Comparison – rekord po rekordie
    # 5. Unique in File1 – klucze unikalne dla pliku 1
    # 6. Unique in File2 – klucze unikalne dla pliku 2
    # 7. Pivot Table – podsumowanie różnic
    with pd.ExcelWriter(output_file, engine="openpyxl") as writer:
        pd.DataFrame({"Summary": summary_text.split("\n")}).to_excel(writer, sheet_name="Summary", index=False)
        df1.to_excel(writer, sheet_name="File1", index=False)
        df2.to_excel(writer, sheet_name="File2", index=False)
        df_detail.to_excel(writer, sheet_name="Detailed Comparison", index=False)
        pd.DataFrame({"Unique in File1": unique1}).to_excel(writer, sheet_name="Unique File1", index=False)
        pd.DataFrame({"Unique in File2": unique2}).to_excel(writer, sheet_name="Unique File2", index=False)
        pivot_table.to_excel(writer, sheet_name="Pivot Table", index=False)

    print("Comparison complete. Output saved to:", output_file)

if __name__ == "__main__":
    file1 = r"C:\Users\PabloPapito\Downloads\lazyDev\lazyDev_test_file1.csv"
    file2 = r"C:\Users\PabloPapito\Downloads\lazyDev\lazyDev_test_file2.csv"
    output_file = r"C:\Users\PabloPapito\Downloads\lazyDev\Comparison.xlsx" # w CWD lub tam gdzie mamy pliki
    compare_csv_files(file1, file2, output_file, match_key="customer_id", encoding="utf-8", sep=",")
