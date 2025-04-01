import pandas as pd

def save_results_to_csv(df, output_path):
    """
    Save the processed results to a CSV file.

    Args:
        df (pd.DataFrame): The DataFrame containing processed media details.
        output_path (str): The file path to save the CSV.
    """
    df.to_csv(output_path, index=False)