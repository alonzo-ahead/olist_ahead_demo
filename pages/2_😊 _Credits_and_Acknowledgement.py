import streamlit as st
import pandas as pd
import numpy as np
#import dataiku
import plotly
import plotly_express  as px
import streamlit.components.v1 as components
from PIL import Image
import requests
from streamlit_lottie import st_lottie
from streamlit_folium import folium_static
import folium.plugins as plugins
from folium.plugins import HeatMap
import folium
from folium.plugins import MarkerCluster
import json 

# Page Info 
st.set_page_config(
    page_title="Credits",
    page_icon= "🎓",
)

#Image In Sidebar 
with st.sidebar.container():
    image = Image.open(r"images\pictures\ahead_transparent_edit2.png")
    st.image(image, use_column_width=True)

# ahead_transparent.png

def load_lottieurl(url):
    """If the lottie file does not display the image return nothing. This will prevent errors when trying to display the Lottie Files.
    Requires importing packages streamlit_lottie and requests"""
    r = requests.get(url)
    if r.status_code != 200:
        return None 
    return r.json()

# Import Downloaded JSON
# Must set encoding and ignore errors to make it work 
def import_json(path):
    with open(path, "r", encoding="utf8", errors="ignore") as file:
        url = json.load(file)
        return url



st.title("Credits and Acknowledgements")

#awards = load_lottieurl("https://assets6.lottiefiles.com/private_files/lf30_mn5tqu4c.json")
awards = import_json(r"images\lotties\award.json")
st_lottie(awards, height = 300, key = "awards")

st.header("Other Datasets")
st.write("There were other datasets utilized for this project besides the 9 Olist datasets showcased earlier.")

st.write("One of the other datasets was scraped from a website called 'brazil-help.com'. This dataset gave the full name of the state. The olist dataset only gave the two letter abbreviation. For example São Paulo was shown as SP in the Olist dataset. Joining this dataset to the list dataset also gave the region the state is located in.")

st.write("The other dataset came from Simplemaps. This allowed us to be able to get the coordinates of Brazillian cities as well as many other cities from around the world. The Olist dataset only gives the coordinates of the zip codes of the customers. With the Simple Maps dataset we could obtain the coordinates of the Brazillian cities after the join.")

st.write("These datasets were joined in Pandas for logistical reasons. These joinings could also have been performed in Dataiku using code recipes.")

with st.expander("Click to See URLs of the two other datasets."):
    st.write("""
             https://brazil-help.com/brazilian_states.htm
             https://simplemaps.com/data/world-cities
             
             """)

st.header("Lottiefiles Credit")
st.write("The motion graphics were provided by various talented artists on Lottiefiles.")

with st.expander("Click to See Lottiefiles URLs etc."):
    st.write("""Man Shops With Cart Online - Jagrav Computer \n
    https://lottiefiles.com/130373-ecommerce-online-banner \n

    Team Ecommerce - Muhammad Usman \n
    https://lottiefiles.com/84631-team-ecommerce \n

    Purple Filtering  \n
    https://lottiefiles.com/141959-data-extraction \n

    Delivery Truck  \n
    https://lottiefiles.com/90409-delivery-truck \n

    Order Handoff  \n
    https://lottiefiles.com/89626-order-delivery  \n

    Mortorcycle Delivery  \n
    https://lottiefiles.com/50434-motorcycle-delivery \n

    Coffee Data \n
    https://lottiefiles.com/88178-no-data \n

    Data Visualization  \n
    https://lottiefiles.com/48244-dashboard-data-visualization \n


    Data Dashboard Visualization \n
    https://lottiefiles.com/48244-dashboard-data-visualization  \n

    Strong Man \n 
    https://lottiefiles.com/143475-weightlifting-competition \n 

    Party  \n
    https://lottiefiles.com/29774-dance-party  \n
    
    Award \n
    https://lottiefiles.com/45911-award \n
    



    Sill Images ----------------------

    Brazil Region Map \n
    https://www.iheartbrazil.com/brazil-map/ \n

            
            
            
            """)
st.write("\n \n")

st.header("Project Credits")

st.subheader("About AHEAD")

ahead_logo = Image.open(r"images\pictures\AHEAD-Logo.jpg")
st.image(ahead_logo)

st.write("AHEAD builds platforms for digital business. By stitching together advances in Cloud, Automation, Operations, Security and DevOps, we help clients deliver on the promise of digital transformation.")
st.write("Dataiku Transformations and Visualizations Created By Monmoy")
st.write("Python/Streamlit Project + Additional Data Wrangling Created by Alonzo ")


