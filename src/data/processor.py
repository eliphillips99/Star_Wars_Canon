import pandas as pd

def save_results_to_csv(results, output_path):
    """
    Save the processed results to a CSV file.

    Args:
        results (list): A list of dictionaries containing processed media details.
        output_path (str): The file path to save the CSV.
    """
    df = pd.DataFrame(results)
    df.to_csv(output_path, index=False)
