import requests
import google
from google import genai
import gspread
import pandas as pd
import time

with open("C:\\Users\\eligp\\OneDrive\\Documents\\Coding Projects\\Star_Wars_Canon\\ref\\gspread_API_key.txt","r") as f:
    gspread_key = f.read()
gc = gspread.api_key(gspread_key)

# Open a sheet from a spreadsheet in one go
sh = gc.open_by_url("https://docs.google.com/spreadsheets/d/1PyWmeM1nwzQV6anIfTp9nre5Wg6-eTfFyYBk8R9z4cY/edit?gid=0#gid=0")
Timeline = sh.worksheet("Timeline")
data = Timeline.get_all_records()
df = pd.DataFrame.from_records(data)


with open("C:\\Users\\eligp\\OneDrive\\Documents\\Coding Projects\\Star_Wars_Canon\\ref\\gemini_API_key.txt","r") as f:
    gem_key = f.read()
client = genai.Client(api_key=gem_key)


media_name = 'blank'
prompt = 'Analyze the following Star Wars media: ' + str(media_name) + '.' \
'         Provide a detailed summary of the plot, highlighting key events and character arcs.' \
'         List the major characters present in this media.' \
'         Identify and describe the top 3 major themes explored.' \
'         Describe the overall tone and atmosphere of the media using 3-5 key words .'

response_list = []
for i in range(len(df)):
    media_name = df["Name"][i]
    response = client.models.generate_content(model="gemini-2.0-flash", contents=prompt)
    response_list.append(response.text)
    print(media_name)
    
    if i % 10 == 0:
        print("Sleeping for 61 seconds")
        time.sleep(61)
        


df['Full Summary'] = response_list
df.to_csv("C:\\Users\\eligp\\OneDrive\\Documents\\Coding Projects\\Star_Wars_Canon\\data\\Timeline.csv", index=False)
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