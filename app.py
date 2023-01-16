from requests import session
import streamlit as st
import pandas as pd
from google.oauth2 import service_account
import gspread
from gsheetsdb import connect
import plotly.graph_objects as go
from gspread_pandas import Spread, Client


# Create a Google Authentication connection object
scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/spreadsheets',
         "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]

# Create a connection object.
credentials = service_account.Credentials.from_service_account_info(
                    st.secrets["gcp_service_account"],
                    # scope of the application
                    scopes=scope,
)

spreadsheet_name = st.secrets["spreadsheet"]
worksheet_name = st.secrets["worksheet"]

client = Client(scope=scope,creds=credentials)
spread = Spread(spreadsheet_name,client = client)

spreadsheet = client.open(spreadsheet_name)

# Get the sheet as dataframe
def load_the_spreadsheet(worksheet_name):
    worksheet = spreadsheet.worksheet(worksheet_name)
    df = pd.DataFrame(worksheet.get_all_records())
    return df

# Update to Sheet
def update_the_spreadsheet(worksheet_name,dataframe):
    col = ['a','b', 'c']
    spread.df_to_sheet(dataframe[col],sheet = worksheet_name,index = False)

new_entry = {'a': ['apple_from_code'],
            'b' :  ['banada_from_code'], 
            'c': ["cat_from_code"]} 
new_entry_df = pd.DataFrame(new_entry)

# Load data from worksheet
df = load_the_spreadsheet(worksheet_name)

new_df = pd.concat([df, new_entry_df])
update_the_spreadsheet(worksheet_name,new_df)

df = load_the_spreadsheet(worksheet_name)
st.dataframe(df)



