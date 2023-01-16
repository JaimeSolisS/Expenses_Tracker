from requests import session
import streamlit as st
import pandas as pd
from google.oauth2 import service_account
import gspread
from gsheetsdb import connect
import plotly.graph_objects as go

# Create a connection object.
credentials = service_account.Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    # scope of the application
    scopes=["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/spreadsheets',
         "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"],
)

conn = connect(credentials=credentials)
client = gspread.authorize(credentials)

spreadsheetname = st.secrets["spreadsheet"]
worksheetname = st.secrets["worksheet"]

# Open the spreadhseet
data = client.open(spreadsheetname).worksheet("expenses").get_all_records()
df = pd.DataFrame.from_dict(data)

st.dataframe(df)