import gspread
import pandas as pd
from gspread_dataframe import set_with_dataframe

def load_google_sheet_data(api_key):
    """
    Load data from the Google Sheet.

    Args:
        api_key (str): The gspread API key.

    Returns:
        pd.DataFrame: A DataFrame containing the sheet data.
    """
    gc = gspread.api_key(api_key)
    sh = gc.open_by_url("https://docs.google.com/spreadsheets/d/1PyWmeM1nwzQV6anIfTp9nre5Wg6-eTfFyYBk8R9z4cY/edit")
    worksheet = sh.worksheet("Timeline")
    data = worksheet.get_all_records()  # Import all data without specifying headers
    df = pd.DataFrame(data)

    # Normalize column names
    df.columns = df.columns.str.strip().str.lower()

    # Debugging: Print the normalized column names and the first few rows
    print("Normalized DataFrame Columns:", df.columns.tolist())
    print("First Few Rows of DataFrame:\n", df.head())

    return df

def write_dataframe_to_sheet(df, api_key, sheet_name="Processed Data"):
    """
    Write a DataFrame to a new sheet in the Google Sheet.

    Args:
        df (pd.DataFrame): The DataFrame to write.
        api_key (str): The Google Sheets API key.
        sheet_name (str): The name of the new sheet to create.
    """
    gc = gspread.api_key(api_key)
    sh = gc.open_by_url("https://docs.google.com/spreadsheets/d/1PyWmeM1nwzQV6anIfTp9nre5Wg6-eTfFyYBk8R9z4cY/edit")

    # Add a new sheet or overwrite if it already exists
    try:
        worksheet = sh.add_worksheet(title=sheet_name, rows="1000", cols="26")
    except gspread.exceptions.APIError:
        worksheet = sh.worksheet(sheet_name)
        worksheet.clear()

    # Write the DataFrame to the new sheet
    set_with_dataframe(worksheet, df)
