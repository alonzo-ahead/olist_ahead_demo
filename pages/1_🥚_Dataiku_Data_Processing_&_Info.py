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
    page_title="Dataiku Workflow",
    page_icon= "🐣",
)

#Image In Sidebar 
with st.sidebar.container():
    image = Image.open(r"images\pictures\ahead_transparent_edit2.png")
    st.image(image, use_column_width=True)

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





st.title("Dataiku Data Processing")

dataiku_logo = Image.open(r"images\pictures\DataikuStraight.jpg")
st.image(dataiku_logo, caption = "Dataiku was instrumental in creating this projectas you'll se on this page.")

st.write("\n")

st.write("As mentioned before this dataset came from Kaggle and was provided by Olist. Olist is the biggest E-commerce website in Brazil. On this page we will explore how Dataiku made processing complicated datasets possible.")

st.write("The dataset is special because it provides real world anonymized data that was colllected over the course of several years. The dataset was broken up into 9 different CSV files. In order for the data to be ready for analytics the data had to be processed and joined.")

#coffee_data = load_lottieurl("https://assets8.lottiefiles.com/packages/lf20_chws1oam.json")
coffee_data = import_json(r"images\lotties\coffee_data.json")
st_lottie(coffee_data, height = 399, key = "drink_data")

st.divider()
st.subheader("Breakdown of Olist Datasets")
st.info("Use arrow keys to navigate between diifferent Olist datasets.", icon = "ℹ")
customer, geolocation, order_items, order_payments, order_reviews, orders_dataset, product_dataset, seller_dataset, category_name = st.tabs(["olist_customers_dataset.csv", "olist_geolocation_dataset.csv", "olist_order_items_dataset.csv", "olist_order_payments_dataset.csv", "olist_order_reviews_dataset.csv", "olist_orders_dataset.csv", "olist_products_dataset.csv", "olist_sellers_dataset.csv", "product_category_name_translation.csv"])

with customer:
    st.subheader("Customer Dataset (1/9)")
    st.write("""customer_id - key to the orders dataset. Each order has a unique customer_id. \n
             customer_unique_id - unique identifier of a customer. \n 
             customer_zip_code_prefix - first five digits of customer zip code
             customer_city - customer city name
             customer_state - customer state
             """)
with geolocation: 
    st.subheader("Geolocation Dataset (2/9)")    
    st.write("""geolocation_zip_code_prefix - first 5 digits of zip code \n
             geolocation_lat - latitude \n
             geolocation_lng - longitude \n
             geolocation_city - city name \n
             geolocation_state - state \n
             """)

with order_items:
    st.subheader("Order_Items Dataset (3/9)")
    st.write("""order_id - order unique identifier \n 
             order_item_id - sequential number identifying number of items included in the same order. \n
             product_id - product unique identifier \n
             seller_id - seller unique identifier \n
             shipping_limit_date - Shows the seller shipping limit date for handling the order over to the logistic partner. \n
             price - item price \n
             freight_value - item freight value item (if an order has more than one item the freight value is splitted between items)
             """)

with order_payments:
    st.subheader("Order_Payment Dataset (4/9)")
    st.write("""order_id - unique identifier of an order. \n
             payment_sequential - a customer may pay an order with more than one payment method. If he does so, a sequence will be created to (sic) \n
             payment_type - method of payment chosen by the customer. \n
             payment_installments - number of installments chosen by the customer. \n
             payment_value - transaction value.
             """)

with order_reviews:
    st.subheader("Order_Reviews Datataset (5/9)")
    st.write("""review_id - unique review identifier  \n
             order_id - unique order identifier  \n
             review_score - Note ranging from 1 to 5 given by the customer on a satisfaction survey. \n
             review_comment_title - Comment title from the review left by the customer, in Portuguese. \n
             review_comment_message - Comment message from the review left by the customer, in Portuguese. \n
             review_creation_date - Shows the date in which the satisfaction survey was sent to the customer. \n
             review_answer_timestamp - Shows satisfaction survey answer timestamp.
             """)

with orders_dataset:
    st.subheader("Orders Dataset (6/9)")
    st.write("""order_id - unique identifier of the order. \n
             customer_id - key to the customer dataset. Each order has a unique customer_id. \n
             order_status - Reference to the order status (delivered, shipped, etc). \n
             order_purchase_timestamp - Shows the purchase timestamp. \n 
             order_approved_at - Shows the payment approval timestamp. \n
             order_delivered_carrier_date - Shows the order posting timestamp. When it was handled to the logistic partner. \n
             order_delivered_customer_date - Shows the actual order delivery date to the customer. \n 
             order_estimated_delivery_date - Shows the estimated delivery date that was informed to customer at the purchase moment.
             """)
    
with product_dataset:
    st.subheader("Product Dataset (7/9)")
    st.write("""product_id - unique product identifier  \n
             product_category_name - root category of product, in Portuguese. \n
             product_name_lenght - number of characters extracted from the product name. \n
             product_description_lenght - number of characters extracted from the product description. \n
             product_photos_qty - number of product published photos \n
             product_weight_g - product weight measured in grams.
             product_length_cm - product length measured in centimeters. \n
             product_height_cm - product height measured in centimeters. \n
             product_width_cm - product width measured in centimeters. \n
             """)

with seller_dataset:
    st.subheader("Seller Dataset (8/9)")
    st.write("""seller_id - seller unique identifier  \n
             seller_zip_code_prefix - first 5 digits of seller zip code  \n
             seller_city - seller city name  \n
             seller_state - seller state  \n
             """)

with category_name:
    st.subheader("Category_Name Dataset (9/9)")
    st.write("""
             product_category_name - category name in Portuguese  \n
             product_category_name_english - category name in English  \n
             """)
st.divider()
# Post Image of the provided data model 
brazil_data_model = Image.open(r"images\pictures\brazil_data_model.png")
st.image(brazil_data_model, caption = "Data model of the dataset provided by Olist.")
    

st.write("""Joining these 9 datasets together would be a Herculean task in most cases. Typically one would have to used a flavor of SQL or Python Pandas in order to join the data together. With Dataiku the joins were able to be made without having to write a single line of code!
         However joining the datasets was only half of the battle. In addition to this, Dataiku made it easy to process data using data preperation recipes. For, this project code recipes were used to format dates and coordinates (i.e longitude and lattitude).
         
         """)

#strong_guy = load_lottieurl("https://assets1.lottiefiles.com/packages/lf20_JkRdsa6Exx.json")
strong_guy = import_json(r"images\lotties\strong_man.json")
st_lottie(strong_guy, height = 399, key = "lifter")
st.caption("Dataiku makes data projects easier by doing a lot of the heavy lifting for you. Many complicated transformation can be done with zero lines of code required.")

st.write("\n \n")

st.subheader("Dataiku Flow")
st.write("With Dataiku we could join the data tables with ease. Zero code required!")
dataiku_flow = Image.open(r"images\pictures\dataiku_flow.png")
st.image(dataiku_flow, caption = "Dataiku flow for joining the data tables and processing the data.")

st.write("\n \n")


# Show Image of the flow in Dataiku 

st.header("Visualization in Dataiku")
dashboard = load_lottieurl("https://assets2.lottiefiles.com/packages/lf20_acryqbdv.json")
st_lottie(dashboard, height = 399, key = "dashboard")

st.write("Dataiku is not only a good place to for data wrangling. It is also a great place to visualize the data. Below there will be screenshots of vizualizations that were created in Dataiku. These interactive visualizations help give critical analytics information in an aestethically pleasing manner.")
#st.info("Note that there may be virtually negligible differences between the Dataiku visualizations and the ones displayed in this Streamlit app as certain rows had to be dropped to prevent errors. This will be explained in the Credits and Acknowledgement section of this web application.", icon = "ℹ")



# Post images of Visualizations made with Dataiku or slide show 

st.warning("Utilize the directional buttons to navigate between the images.", icon = "⚠")

tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs(["Map", "Delivery Date Vs. Actual", "Histogram of Customer City", "Pie Chart of Order Status", "Map of Customer Orders", "Price Payment Instsllments", "Price Vs Weight", "Spearman Correlation"])

with tab1:
    st.subheader("Dataiku Image (1/8): Averages ")
    average = Image.open(r"images\pictures\average_cards.png")
    st.image(average, caption = "KPI cards that show various averages.")
with tab2:
    st.subheader("Dataiku Image (2/8): Estimation vs Actual Delivery Date")
    estimate = Image.open(r"images\pictures\estimation_vs_actual.png")
    st.image(estimate, caption = "A graph that shows the estimated delivery date vs the actual one.")
with tab3:
    st.subheader("Dataiku Image (3/8): Histogram of Customer City")
    customer_city = Image.open(r"images\pictures\histogram_customer_city.png")
    st.image(customer_city, "Histogram of top ")
with tab4:
    st.subheader("Dataiku Image (4/8):Pie Chart of Order Status")
    pie = Image.open(r"images\pictures\pie_chart.png")
    st.image(pie, "Pie chart of delivery status.")
with tab5:
    st.subheader("Dataiku Image (5/8): Map of Customer Orders")
    map = Image.open(r"images\pictures\map_sa.png")
    st.image(map, "Map of customer orders in Brazil.")
with tab6:
    st.subheader("Dataiku Image (6/8): Price Payment Installments")
    price = Image.open(r"images\pictures\price_payment_installments.png")
    st.image(price, "Payment Installments and Prices")
with tab7:
    st.subheader("Dataiku Image (7/8): Price vs. Weight")
    price_weight = Image.open(r"images\pictures\price_vs_weight.png")
    st.image(price_weight, "Price vs weight chart.")
with tab8:
    st.subheader("Dataiku Image (8/8): Spearman Correlation")
    correlation = Image.open(r"images\pictures\spearman_correlation.png")
    st.image(correlation, "Spearman Correlation Table")
    
    
st.write("Keep in mind that the visuals created in Dataiku are powered by Plotly. This makes the visualizations interactive similar to the ones that were displayed in this project.")

st.header("This Project Was Made Possible By Dataiku!")

#party = load_lottieurl("https://assets1.lottiefiles.com/packages/lf20_6aYlBl.json")
party = import_json(r"images\lotties\party.json")

st_lottie(party, height = 399, key = "celebration")
st.write("To see how Dataiku can help your data workflow visit their website.")

if st.button("Click to Celebrate"):
    st.balloons()
else:
    pass 

    