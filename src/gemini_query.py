import requests
import google
from google import genai
import gspread
import pandas as pd

gc = gspread.api_key("AIzaSyD9gJandrwDO-FpjGIZxtt9I0srgRqsJ74")

# Open a sheet from a spreadsheet in one go
sh = gc.open_by_url("https://docs.google.com/spreadsheets/d/1PyWmeM1nwzQV6anIfTp9nre5Wg6-eTfFyYBk8R9z4cY/edit?gid=0#gid=0")
Timeline = sh.worksheet("Timeline")
data = Timeline.get_all_records()
df = pd.DataFrame.from_records(data)
print(df)


client = genai.Client(api_key="AIzaSyCu9ptrc2qRwNEeKl1hzEkD-5FtSBMTPSQ")



response = client.models.generate_content(model="gemini-2.0-flash", contents="give me a synopsis of revenge of the sith")

print(response.text) 

'''
# Currently using Gemini 2.0 Flash
def query_gemini_api(endpoint, params=None, api_key=None):
    base_url = "https://api.gemini.com/v1"
    url = f"{base_url}/{endpoint}"
    headers = {}
    if api_key:
        headers['Authorization'] = f'Bearer {api_key}'
    response = requests.get(url, params=params, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        response.raise_for_status()

# Example usage
if __name__ == "__main__":
    endpoint = "pubticker/btcusd"
    api_key = "AIzaSyCu9ptrc2qRwNEeKl1hzEkD-5FtSBMTPSQ"  # Replace with your actual API key
    data = query_gemini_api(endpoint, api_key=api_key)
    print(data)
'''