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

    prompt = (f"Analyze the following Star Wars media: {media_name} from {show_trilogy}. "
              "Provide a summary of the plot, list the major characters, "
              "identify the top 3 major themes, and describe the overall tone. "
              "Output the results in the following format:\n\n"
              "*Plot Summary\n[summary]\n\n"
              "*Major characters\n[list of major characters]\n\n"
              "*Themes\n[list the top 3 themes of the media]\n\n"
              "*Tone\n[describe the overall tone using 3-5 key words]")
    print(prompt)
    response = client.models.generate_content(model="gemini-2.0-flash", contents=prompt)
    response_list.append(response.text)
    print(response.text)
    
    if i % 10 == 0 and i != 0:
        print("Sleeping for 61 seconds")
        time.sleep(61)

df['Full Summary'] = response_list
df.to_csv("C:\\Users\\eligp\\OneDrive\\Documents\\Coding Projects\\Star_Wars_Canon\\data\\Timeline.csv", index=False)