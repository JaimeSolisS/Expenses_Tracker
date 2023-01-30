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
            # filter data by period
            df_filtered = df[df['Month_Year'].isin(period)]

            # get data 
            incomes = df_filtered.loc[df_filtered['Category'] == 'Income']
            expenses = df_filtered.loc[df_filtered['Category'] == 'Expense']

            # Create metrics
            total_income = incomes["Amount"].sum()
            total_expense = expenses["Amount"].sum()
            balance = total_income - total_expense
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Income", f"{total_income}")
            col2.metric("Total Expense", f"{total_expense}")
            col3.metric("Balance", f"{balance}")

            # Sum total by cateogry and Create Dictionaries for sankey
            incomes_dict = incomes.groupby("Subcategory").sum().reset_index()
            expenses_dict = expenses.groupby("Subcategory").sum().reset_index()
            incomes_dict=incomes_dict.set_index('Subcategory').T.to_dict('list')
            expenses_dict=expenses_dict.set_index('Subcategory').T.to_dict('list')
            
             # Create sankey chart
            label = list(incomes_dict.keys()) + ["Total Income"] + list(expenses_dict.keys())
            source = list(range(len(incomes_dict))) + [len(incomes_dict)] * len(expenses_dict)
            target = [len(incomes_dict)] * len(incomes_dict) + [label.index(expense) for expense in expenses_dict.keys()]
            value = list(incomes_dict.values()) + list(expenses_dict.values())

            # Data to dict, dict to sankey
            link = dict(source=source, target=target, value=value)
            node = dict(label=label, pad=20, thickness=30)
            data = go.Sankey(link=link, node=node)

            # Plot
            fig = go.Figure(data)
            fig.update_layout(margin=dict(l=0, r=0, t=5, b=5))
            st.plotly_chart(fig, use_container_width=True)

            st.subheader("Incomes:")
            st.dataframe(incomes[['Date', 'Subcategory', 'Detail', 'Amount']].reset_index(drop=True))
            st.subheader("Expenses:")
            st.dataframe(expenses[['Date', 'Subcategory', 'Detail', 'Amount']].reset_index(drop=True))