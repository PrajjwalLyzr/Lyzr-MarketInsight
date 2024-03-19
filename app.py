import os
from PIL import Image
import yfinance as yf
import pandas as pd
from pathlib import Path
import streamlit as st
from utils import utils
from dotenv import load_dotenv; load_dotenv()
from lyzr import DataConnector, DataAnalyzr

apikey = os.getenv('OPENAI_API_KEY') #replace this with your openai api key or create an environment variable for storing the key.

# create directory if it doesn't exist
data = "data"
plot = 'plot'
os.makedirs(data, exist_ok=True)
os.makedirs(plot, exist_ok=True)


# Setup your config
st.set_page_config(
    page_title="LyzrVoice DocuFill",
    layout="centered",  # or "wide" 
    initial_sidebar_state="auto",
    page_icon="./logo/lyzr-logo-cut.png"
)

# Load and display the logo
image = Image.open("./logo/lyzr-logo.png")
st.image(image, width=150)

# App title and introduction
st.title("NSE Market-Insight by Lyzr")
st.markdown("### Welcome to the Market-Insight!")
st.markdown("Gain valuable insights into trends, patterns, and volatility, empowering you to make informed investment decisions.")

# Custom function to style the app
def style_app():
    # You can put your CSS styles here
    st.markdown("""
    <style>
    .app-header { visibility: hidden; }
    .css-18e3th9 { padding-top: 0; padding-bottom: 0; }
    .css-1d391kg { padding-top: 1rem; padding-right: 1rem; padding-bottom: 1rem; padding-left: 1rem; }
    </style>
    """, unsafe_allow_html=True)

# Market Insight Application
    

def save_option(selected_option):
    #Downlaod company data
    dataframe = yf.download(selected_option)
    utils.remove_existing_files(data)
    dataframe.to_csv(f"data/{selected_option}.csv")


def select_compnay():
    options_list = utils.company_list()
    selected_option = st.selectbox("Select an option", options_list)

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Save Option"):
            save_option(selected_option)
            st.write("You selected:", selected_option)

    with col2:
        if st.button('Clear'):
            utils.remove_existing_files(data)
            utils.remove_existing_files(plot)
    

    
        
    
def market_analyzr():
    path = utils.get_files_in_directory(data)
    path = path[0]

    dataframe = DataConnector().fetch_dataframe_from_csv(file_path=Path(path))
    analyzr = DataAnalyzr(df=dataframe, api_key=apikey)

    return analyzr

def generating_insights(analyzr):
    description = analyzr.dataset_description()
    analysis = analyzr.analysis_recommendation()
    prompts = ["Create a candlestick chart to visualize the open, high, low, and close prices of the stock for each trading day over a specific period",
               "Plot Bollinger Bands around the closing price chart to visualize volatility and potential reversal points",
               "Plot the RSI indicator to assess the stock's momentum and overbought/oversold conditions. RSI values above 70 indicate overbought conditions, while values below 30 indicate oversold conditions",
               "Plot the MACD indicator to identify trend changes and potential buy/sell signals. MACD consists of a fast line (MACD line), slow line (signal line), and a histogram representing the difference between the two lines",
               "Plot a histogram of daily returns (percentage change in closing price) to visualize the distribution of returns and assess risk",
               "Plot a chart showing the high, low, and closing prices for each trading day over a specific period. This provides a comprehensive view of daily price fluctuations.",
               "Overlay moving average lines (e.g.,44-day moving averages) on the closing price chart to smooth out price fluctuations and identify long-term trends."
                ]
    
    utils.remove_existing_files(plot)
    for prompt in prompts:
        vis = analyzr.visualizations(user_input=prompt, dir_path=Path('./plot'))

    return description, analysis


def file_checker():
    file = []
    for filename in os.listdir(data):
        file_path = os.path.join(data, filename)
        file.append(file_path)

    return file

       

if __name__ == "__main__":
    style_app()
    select_compnay()
    file = file_checker()
    if len(file)>0:
        analyzr = market_analyzr()
        description, analysis = generating_insights(analyzr)
        if description is not None:
            st.subheader("Description the Company data")
            st.write(description)
            plot_files = os.listdir("./plot")
            st.subheader("Technical Indicators about the company stock")
            for plot_file in plot_files:
                st.image(f"./plot/{plot_file}")
            st.subheader("Recommended Analysis")
            st.write(analysis)
        else:
            st.error('Error: occurs while generating description')

    with st.expander("ℹ️ - About this App"):
        st.markdown("""
        This app uses Lyzr DataAnalyzr agent to generate analysis on data. With DataAnalyzr, you can streamline the complexity of data analytics into a powerful, intuitive, and conversational interface that lets you command data with ease. For any inquiries or issues, please contact Lyzr.
        
        """)
        st.link_button("Lyzr", url='https://www.lyzr.ai/', use_container_width = True)
        st.link_button("Book a Demo", url='https://www.lyzr.ai/book-demo/', use_container_width = True)
        st.link_button("Discord", url='https://discord.gg/nm7zSyEFA2', use_container_width = True)
        st.link_button("Slack", url='https://join.slack.com/t/genaiforenterprise/shared_invite/zt-2a7fr38f7-_QDOY1W1WSlSiYNAEncLGw', use_container_width = True)
