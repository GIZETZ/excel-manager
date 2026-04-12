import pandas as pd


def print_sheet_columns(file_path):
    try:
        xls = pd.ExcelFile(file_path)
        for idx, sheet in enumerate(xls.sheet_names):
            try:
                df = pd.read_excel(xls, sheet_name=sheet, nrows=0)
                print(f"Feuille {idx+1}: {sheet}")
                print(list(df.columns), flush=True)
            except Exception as e:
                print(f"Erreur lecture feuille {sheet}: {e}", flush=True)
    except Exception as e:
        print(f"Erreur ouverture fichier {file_path}: {e}", flush=True)

if __name__ == "__main__":
    print('UMTS CELL Info.xlsx:')
    print_sheet_columns('../docs/UMTS CELL Info.xlsx')
    print('\n2G3G4G_Cell Info.xlsx:')
    print_sheet_columns('../docs/2G3G4G_Cell Info.xlsx')
