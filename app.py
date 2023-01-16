from requests import session
import streamlit as st
import pandas as pd
from google.oauth2 import service_account
import gspread
from gsheetsdb import connect
import plotly.graph_objects as go
from gspread_pandas import Spread, Client

import calendar  # Core Python Module
from datetime import datetime  # Core Python Module

# ------------------- SETTINGS ------------------- #
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

page_title = "Income and Expense Tracker"
page_icon = "💸"
st.set_page_config(page_title=page_title, page_icon=page_icon, layout="centered")
st.title(page_title + " " + page_icon)

# --------------- VARIABLES --------------------- #
categories = ["", "Expense", "Income"]
subcategories = ["", "Salary", "Utilities", "Dogs", "Car", "Other Expenses"]

# --------------- FUNCTIONS --------------------- #
# Get the sheet as dataframe
def load_the_spreadsheet(worksheet_name):
    worksheet = spreadsheet.worksheet(worksheet_name)
    df = pd.DataFrame(worksheet.get_all_records())
    return df

# Update to Sheet
def update_the_spreadsheet(worksheet_name,dataframe):
    col = ['Date','Category', 'Subcategory', 'Detail', 'Amount']
    spread.df_to_sheet(dataframe[col],sheet = worksheet_name,index = False)

def create_new_entry(date, category, subcategory, detail, amount):
    new_entry = {'Date': [date],
           'Category' :  [category], 
           'Subcategory' :  [subcategory], 
           'Detail' :  [detail], 
           'Amount' :  [amount]} 
    return pd.DataFrame(new_entry)

# ----------------------------------------------- #

st.header("Data Entry")
with st.form("entry_form", clear_on_submit=True):

    date = st.date_input("Date", datetime.today())
    category = st.selectbox("Category", categories)
    subcategory = st.selectbox("Subcategory", subcategories)
    detail = st.text_input("Detail", "")
    amount = st.number_input("Amount", min_value=0, step=100)
    
    "---"
    submitted = st.form_submit_button("Save Data")
    if submitted:
        try:
            new_record_df = create_new_entry(date, category, subcategory, detail, amount)
            df = load_the_spreadsheet(worksheet_name)
            new_df = pd.concat([df, new_record_df])
            update_the_spreadsheet(worksheet_name,new_df)
            st.success("Data saved! 😁")
        except:
            st.error("Something went wrong! 😔")

st.header("Data Visualization")
with st.form("saved_periods"):
        df = load_the_spreadsheet(worksheet_name)
        df['Date'] = pd.to_datetime(df['Date'])
        df['Month_Year'] = df['Date'].dt.strftime('%b-%Y')
        periods = df['Month_Year'].unique().tolist()

        period = st.multiselect("Select Period:",periods)
        submitted = st.form_submit_button("Plot Period")
        if submitted:
            df_filtered = df[df['Month_Year'].isin(period)]
            # Create metrics
            total_income = df_filtered.loc[df_filtered['Category'] == 'Income', 'Amount'].sum()
            total_expense = df_filtered.loc[df_filtered['Category'] == 'Expense', 'Amount'].sum()
            balance = total_income - total_expense
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Income", f"{total_income}")
            col2.metric("Total Expense", f"{total_expense} ")
            col3.metric("Balance", f"{balance}")