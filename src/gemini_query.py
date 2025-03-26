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


response_list = []
for i in range(len(df)):
    media_name = df["Name"].iloc[i]
    show_trilogy = df["Show/Trilogy"].iloc[i]
    season = df["Season"].iloc[i]
    episode_num = df["Episode Num"].iloc[i]

    prompt = ('Analyze the following Star Wars media: ' + str(media_name) + ', season ' + str(season) + ' episode ' + str(episode_num) + ' from ' + str(show_trilogy) + 
              '. Provide a summary of the plot, list the major characters, '
              'identify the top 3 major themes, and describe the overall tone. '
              'Output the results in the following format:\n\n'
              '*Plot Summary\n[summary]\n\n'
              '*Major characters\n[list of major characters]\n\n'
              '*Themes\n[list the top 3 themes of the media]\n\n'
              '*Tone\n[describe the overall tone using 3-5 key words]')
    print(prompt)
    response = client.models.generate_content(model="gemini-2.0-flash", contents=prompt)
    response_list.append(response.text)
    print(response.text)
    
    if i % 10 == 0 and i != 0:
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