import camelot
import pandas as pd
from typing import List
import json

def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Applies post-cleaning logic to extracted tables:
    - Normalizes column names
    - Strips ₹, %, and newline characters
    """
    if df.empty:
        return df

    # Normalize column names: string format, replace newlines
    df.columns = [str(col).replace('\n', ' ').strip() for col in df.columns]
    
    # Strip whitespace, ₹, and % signs from all string cells
    # Convert dates or other specifics if desired.
    df = df.apply(lambda col: col.map(
        lambda x: str(x).replace('\n', ' ').replace('₹', '').replace('%', '').strip() if isinstance(x, str) else x
    ))
    
    return df

def extract_tables(pdf_path: str, mode: str = "lattice") -> List[pd.DataFrame]:
    """
    Extracts tables from a PDF using Camelot.
    Use "lattice" mode for scanned tables and "stream" mode for text-based tables.
    Returns a list of cleaned pandas DataFrames.
    """
    try:
        # Note: flavor allows 'lattice' or 'stream'
        tables = camelot.read_pdf(pdf_path, pages='all', flavor=mode)
    except Exception as e:
        print(f"Error extracting tables from {pdf_path}: {e}")
        return []
        
    cleaned_tables = []
    for table in tables:
        df = table.df
        if not df.empty:
            # Assume first row is header for generic cleaning
            new_header = df.iloc[0]
            df = df[1:]
            df.columns = new_header
            
            cleaned_df = clean_dataframe(df)
            cleaned_tables.append(cleaned_df)
            
    return cleaned_tables

def export_tables_to_json(tables: List[pd.DataFrame]) -> str:
    """
    Converts list of DataFrames to a JSON string for UI preview or API output.
    """
    tables_dict = []
    for i, df in enumerate(tables):
        tables_dict.append({
            "table_index": i,
            "data": df.to_dict(orient="records")
        })
    return json.dumps(tables_dict, indent=2)
