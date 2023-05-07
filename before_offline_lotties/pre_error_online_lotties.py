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
import plotly.graph_objects as go
import time # Import time for Loading Bar

#Image In Sidebar 
with st.sidebar.container():
    image = Image.open(r"images\pictures\ahead_transparent_edit2.png")
    st.image(image, use_column_width=True)
    
    

# Page Info Will Cause an Error on this Page
# # Page Info 
# st.set_page_config(
#     page_title="Ecommerce Analytics",
#     page_icon="📈",
# )


# https://discuss.streamlit.io/t/ann-streamlit-folium-a-component-for-rendering-folium-maps/4367


# READ CSV 
#df = pd.read_csv("olist\dataset\oilist_cleaned_ahead_demo_dataset.csv")



# Map CSV
#df_map = pd.read_csv("olist\dataset\other_datasets\MAP_olist.csv")

#df = df_map

df = pd.read_csv("final_olist_dataset.csv")

df_map = df.copy()

df["volume_cm3"] = df["product_length_cm"] * df["product_height_cm"] * df["product_width_cm"]

# st.dataframe(df.head())




# Auto convert datetime columns by iterating through them 
for col in df.columns:
    if df[col].dtype == 'object':
        try:
            df[col] = pd.to_datetime(df[col])
        except ValueError:
            pass

# Gets Hour of the Day
df["order_purchase_hour"] = df["order_purchase_timestamp"].dt.hour



# Can define the functions that we will use throughout the project 

# IMAGES / Motion Graphics 
# Image Lottie - May replace with a function that enables downloads 


def load_lottieurl(url):
    """If the lottie file does not display the image return nothing. This will prevent errors when trying to display the Lottie Files.
    Requires importing packages streamlit_lottie and requests"""
    r = requests.get(url)
    if r.status_code != 200:
        return None 
    return r.json()

def lottie_credit(credit):
    return st.markdown(f"<p style='text-align: center; color: gray;'>{credit}</p>", unsafe_allow_html=True)

# CONVERTING COLUMNS INTO DATES 
def datetime_maker(column_name):
    """
    Converts a string that represents datetime into an actual date. Then it saves the recognizeable date into a column in the df.
    Finally, the modified data column is returned to the project wide dataframe. 
    
    This will overwrite the original column name.
    """
    
    df[column_name] = pd.to_datetime(df[column_name])

    return df


def date_subtract(late_date, early_date, name_of_diff_col, interval="days"):
    """
    Can subtract two columns of your choosing. The latest column of dates goes first. Then the earliest. Then you can define what you want to call the column when you add it to the dataframe.

    Note that both columns have to be a date or this function will not work.
    """
    mask = (df[late_date].notnull()) & (df[early_date].notnull())
    df[name_of_diff_col] = ""
    if interval == "days":
        df.loc[mask, name_of_diff_col] = (df[late_date] - df[early_date]).dt.days
    if interval == "minutes":
        df.loc[mask, name_of_diff_col] = (df[late_date] - df[early_date]).dt.total_seconds() / 60

    return df




# Making Columns With Date Subtraction 
date_subtract("order_delivered_customer_date", "order_purchase_timestamp", "delivery_days_taken")

date_subtract("order_delivered_customer_date", "order_estimated_delivery_date", "actual_delivery_date_minus_estimated")
    
date_subtract("order_approved_at", "order_purchase_timestamp", "process_order_time_minutes", interval = "minutes")


# VISUALIZATION FUNCTIONS

# Pie charts
def make_pie(column):
    # Best way to make pie is with value counts
    
    pie = px.pie(df[column], values = df[column].value_counts().values , names = df[column].value_counts().index)
    st.plotly_chart(pie)

# Bar charts 
def bar_chart(x, y, count = True):
    """Group by the the X value and computes the sum by it by the aggregate. 
    Reset the index. Then sort it by the index."""
    
    if count == True:
        x = df[x].value_counts().index
        y = df[y].value_count().value
    
    df_fixed = df.groupby(f"{x}").agg("sum").reset_index().sort_values( f"{y}",ascending= False)
    fig = px.bar(df_fixed, x = x , y = y, color = x, width = 1200, height  = 700,  text_auto = True, title = f"{y} by {x} Bar Charts")
    yaxis = {f"{y}" : "total descending" }
    #st.plotly_chart(fig)
    
    st.plotly_chart(fig)
    
    
def bar_chart_count(x):
    """
    This one only does a bar chart of one variable instead of taking two.
    Group by the the X value and computes the sum by it by the aggregate. 
    Reset the index. Then sort it by the index.
    
    This code creates a countplot.
    """
    
    # x = df[x].value_counts().index
    # y = df[y].value_count().value
    
    count_df = df.groupby(by = x).size().reset_index(name = "counts")
    
    get_column_names = list(count_df.columns)
    
    fig = px.bar(count_df, x = count_df.iloc[:, 0], y = count_df.iloc[:, 1], color = count_df.iloc[:, 1], barmode = "group", text_auto= True, width = 1200, height= 700)
    
    fig.update_layout(xaxis_title =  get_column_names[0] ,  yaxis_title = f"Count",  xaxis={'categoryorder':'total descending'})
    
    
    
    # df_fixed = df.groupby(f"{x}").agg("sum").reset_index().sort_values( f"{y}",ascending= False)
    # fig = px.bar(df_fixed, x = x , y = y, color = x, width = 1000, height  = 500,  text_auto = True, title = f"{y} by {x} Bar Charts")
    # yaxis = {f"{y}" : "total descending" }
    #st.plotly_chart(fig)
    
    st.plotly_chart(fig, use_container_width=True)


# LINE CHART ------------------------------------------------------------------------- NOTE Can add a way to have custom widths and lengths 
def line_chart_count(counted, chart = "daily"):
    
    """
    Counted describes which column is being counted. This is a variable that has no numerical number (of significance) assigned to it. An example would be 'payment_type. 
    
    Counted also serves as the color distinguisher. 
    """
    
    # The function could be improved by adding in a way to change the datetime column to another date in the dataset but that is superfluous. 
    
    # Real Grouping - dataframe group 
    
     #Daily counts verified
    if chart == "daily":
        dfg = df.groupby(df["order_purchase_timestamp"].dt.date)[counted].value_counts().reset_index(name = "count")
    
    # Monthly counts
    if chart == "monthly":
        dfg = df.groupby(df["order_purchase_timestamp"].dt.month)[counted].value_counts().reset_index(name = "count")
    
    # Yearly count verified
    if chart == "yearly":
        dfg = df.groupby(df["order_purchase_timestamp"].dt.year)[counted].value_counts().reset_index(name = "count")
    
    # Yearly and Monthly
    if chart == "year_month":
        dfg = df.groupby(df["order_purchase_timestamp"].apply(lambda x: x.strftime('%B-%Y')) )[counted].value_counts().reset_index(name = "count")
    
    
    fig = px.line(dfg, x = "order_purchase_timestamp", y = "count", color = counted, markers = True,  width = 1200, height = 700)
    
    # Display the chart 
    #st.plotly_chart(fig)
    
    st.plotly_chart(fig)
    


def histogram(column, color_pick = "None"):
    
    """
    Creates a histogram. A color can even be picked for the histogram if desired. Below some of the parameters for picking a color will be defined. 
    
      The 'color' property is a color and may be specified as:
      - A hex string (e.g. '#ff0000')
      - An rgb/rgba string (e.g. 'rgb(255,0,0)')
      - An hsl/hsla string (e.g. 'hsl(0,100%,50%)')
      - An hsv/hsva string (e.g. 'hsv(0,100%,100%)')
      - A named CSS color:
            aliceblue, antiquewhite, aqua, aquamarine, azure,
            beige, bisque, black, blanchedalmond, blue,
            blueviolet, brown, burlywood, cadetblue,
    
    """
    
    if color_pick == "None":
        fig = px.histogram(df, x = column, text_auto = True, opacity = 0.8)
    else:
        fig = px.histogram(df, x = column, text_auto = True, opacity = 0.8, color_discrete_sequence = [color_pick])
        
    
    
    st.plotly_chart(fig)
    
    
# Boxplot 
def simple_boxplot(column):
    fig = px.box(df, y = column, points = False)
    
    st.plotly_chart(fig)


    

def line_chart_sum(column_to_sum, date_column, chart_interval, seperation = ""):
    """"""
    dfg = df
    # Daily Chart 
    if chart_interval == "daily" and seperation == "":
       dfg = df.groupby(df[date_column].dt.date).sum(column_to_sum).reset_index()
    elif chart_interval == "daily" and seperation != "":
        dfg = df.groupby([df[date_column].dt.date, seperation]).sum(column_to_sum).reset_index()
       
    
    # Monthly Chart 
    if chart_interval == "monthly" and seperation == "":
        dfg = df.groupby(df[date_column].dt.month).sum(column_to_sum).reset_index()
    elif chart_interval == "monthly" and seperation != "":
        dfg = df.groupby([df[date_column].dt.month, seperation]).sum(column_to_sum).reset_index()
        
    # Yearly Chart 
    if chart_interval == "yearly" and seperation == "":
        dfg = df.groupby(df[date_column].dt.year).sum(column_to_sum).reset_index()
    elif chart_interval == "yearly" and seperation != "":
        # Make Column Year 
        dfg = df
        year = dfg[date_column].dt.year.astype(int)
        dfg["year"] = year
        dfg = df.groupby([year, seperation]).sum(column_to_sum).reset_index()
        
        fig = px.line(dfg, y = column_to_sum, x = date_column, color = seperation, markers = True, width = 1000, height = 600)
        
        #return fig.show()
        return st.plotly_chart(fig, use_container_width=True)
        
        
        
        # Year and Monthly Chart 
    if chart_interval == "year_month" and seperation == "":
        dfg = df.groupby(df[date_column].dt.to_period('M')).sum(column_to_sum).reset_index()
        # Convert PeriodIndex to string representation
        dfg[date_column] = dfg[date_column].dt.strftime('%Y-%m')
    elif chart_interval == "year_month" and seperation != "":
        dfg = df.groupby([df[date_column].dt.to_period('M'), seperation]).sum(column_to_sum).reset_index()
        # Convert PeriodIndex to string representation
        dfg[date_column] = dfg[date_column].dt.strftime('%Y-%m')

    
    
    # No color Seperation for a categorical variable, I,e city Region, State etc. 
    if seperation == "" and seperation == "":
        fig = px.line(dfg, x = date_column, y = column_to_sum, markers = True,  width = 1000, height = 600)
 
    # In order to have a color be a factor it must be included in the groupby. Now we can keep things  such Region, Payment Type, etc. 
    else:
        fig = px.line(dfg, x = date_column, y = column_to_sum, markers = True, color = seperation  ,width = 1000, height = 600)
        
    # Plot the chart 
    st.plotly_chart(fig)
    
    # fig.show()

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Quick Data Sectioning 

def quick_data_section(column_to_split):
    st.divider()
    
    column_name = str(column_to_split)
    column_title = column_name.title()
    
    greeting = f"{column_to_split} Analysis"
    st.subheader(greeting.title())
    
    
    tab1, tab2 = st.tabs([f"Pie Chart of {column_title}", f"Countplot of Orders By {column_title}"])
    with tab1:
        make_pie(column_to_split)
    with tab2:
        bar_chart_count(column_to_split)
    
    
    barchart_maker_sum(column_to_split, "payment_value")
    
    st.warning("May need to use directional buttons to navigate between the tabs.", icon = "⚠")
    st.write("Total Payments will be sometimes abbreviated as TPay.")
    tab3, tab4, tab5, tab6 = st.tabs([f"Yr TPAY By {column_title}", f"Monthly TPay By {column_title}", f"Year/Month TPay By {column_title}", f"Daily TPay By {column_title}"])
    
    with tab3:
        line_chart_sum("payment_value", "order_purchase_timestamp", "yearly", column_to_split)
    with tab4:
        line_chart_sum("payment_value", "order_purchase_timestamp", "monthly", column_to_split)
    with tab5:
        line_chart_sum("payment_value", "order_purchase_timestamp", "year_month", column_to_split)
    with tab6:
        line_chart_sum("payment_value", "order_purchase_timestamp", "daily", column_to_split)
   
   
    st.divider()
    
# ------------------------------------------------------------------------------


# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Quick Data Sectioning 

def quick_data_section_count(column_to_split):
    st.divider()
    
    column_name = str(column_to_split)
    column_title = column_name.title()
    
    greeting = f"{column_to_split} Count Analysis"
    st.subheader(greeting.title())
    
    
    tab1, tab2 = st.tabs([f"Pie Chart of {column_title}", f"Countplot of Orders By {column_title}"])
    with tab1:
        make_pie(column_to_split)
    with tab2:
        bar_chart_count(column_to_split)
    
    
    barchart_maker_sum(column_to_split, "payment_value")
    
   
    tab3, tab4, tab5, tab6 = st.tabs([f"Yr Count of {column_title}", f"Monthly Count of {column_title}", f"Year/Month Count By {column_title}", f"Daily Count By {column_title}"])
    
    with tab3:
        line_chart_count(column_to_split, "yearly")
        #line_chart_sum("payment_value", "order_purchase_timestamp", "yearly", column_to_split)
    with tab4:
        #line_chart_sum("payment_value", "order_purchase_timestamp", "monthly", column_to_split)
        line_chart_count(column_to_split, "monthly")
    with tab5:
        #line_chart_sum("payment_value", "order_purchase_timestamp", "year_month", column_to_split)
        line_chart_count(column_to_split, "year_month")
    with tab6:
        #line_chart_sum("payment_value", "order_purchase_timestamp", "daily", column_to_split)
        line_chart_count(column_to_split, "daily")
   
   
    st.divider()
    
# ------------------------------------------------------------------------------



# Map Section --------------------------------------------------------
# For this section we will have to use df_map

    
    
    
    
    
    
    
    
    
    
# line_chart_sum("payment_value", "order_purchase_timestamp", "daily")  # Great Code to Reuse No longer needed

# Barchart 
def barchart_maker_sum(x_pick, y_pick):
    """We must sum up the column of payment after the group by. If we don't Plotly will pick up on the individual slices stacked on top of eachother.
    
    Without the groupby you cannot even label the text. As it is not feasible or even possible to display the text of hundreds of little slices. 
    
    The x value is a categorial variable. You can then sum up a number of your choice and then plot it. For example Sales by region etc. 
    """
    
    df = df_map.groupby(x_pick).sum(y_pick).reset_index()
    # Recently added the width as 1200 and height as 700
    fig = px.bar(df, x = x_pick , y = y_pick, color = x_pick, width = 1200, height = 700, text_auto = True)
    fig.update_layout(xaxis = {"categoryorder":"total descending"})
    
    st.plotly_chart(fig)
    
# NOTE Beggining of the Filter section

def slide_creator(column, step_pick):
    """Can create sliders in a single coding function. It returns something that can be used as a filter. """
    df[column] = df[column].astype("float")  # Converts into a float
    ranges = df[column].unique().tolist()
    ranger = st.slider(f"Select a range of values for {column}.",
    min_value = min(ranges),
    max_value = max(ranges),
    value = (min(ranges), max(ranges)),
    step = step_pick
    )
    st.caption(f"Selected Minimum Value:  {ranger[0]: ,}")
    st.caption(f"Selected Maximum Value: {ranger[1]: ,}")
    # return ranger
    return df[column].between(*ranger)

def multi_choose(column_name):
        # df[column_name].fillna("! Not Specified")
        # df[column_name] = df[column_name].astype("string")
        # Previous two lines makes sure that everything is readable
        listing = df[column_name].unique().tolist()
        listing.sort()
        checkbox_all = st.checkbox(f"Select all for {column_name}.", key = column_name, value = True)


        

        if checkbox_all:
            select = st.multiselect(f"Select values from {column_name} that you wish to select.", listing, default = listing)
        else:
            select = st.multiselect(f"Select values from {column_name} that you wish to select.", listing)

        return (df[column_name].isin(select))

# multi_choose("customer_city") & multi_choose("seller_city") 

# Enable multiselect
def enable_multiselect(df, column_to_fix):
    """This code will fix columns that are not recognized as string values. By converting these columns into strings we can use them in multiselect. 
    
    However this code should only be used as a contigency if the code fails when being tested on its own. This will overwrite the column in the selected dataframe. 
    """
    
    df[column_to_fix] = df[column_to_fix].astype(str)
    return df[column_to_fix]

#df["product_category_name_english"] = df["product_category_name_english"].astype(str)

enable_multiselect(df, "product_category_name_english")
enable_multiselect(df, "payment_type")

# with st.expander("Click to See the Filters"):
#     mask = slide_creator("payment_value", 20.0) & slide_creator("review_score", 1.0) & multi_choose("Region_Customer") & multi_choose("State_Customer") &  multi_choose("Region_Seller") & multi_choose("State_Seller") & multi_choose("product_category_name_english") & df["order_status"] & multi_choose("customer_city")
    
# df = df[mask]

# Filter By Date 
#df["order_purchase_date"] = df["order_purchase_timestamp"]



# date_slider_creator(df, "order_purchase_date")


st.title('AHEAD DataIku Demonstration')
st.subheader("Uilizing Innovative Tech to Drive Data Driven Decisions")

col1, col2 = st.columns(2)

with col1:
    man_shop = load_lottieurl("https://assets2.lottiefiles.com/packages/lf20_rVEgYArLER.json")
    st_lottie(man_shop, height = 300, key = "man_shop")

with col2:
    collab = load_lottieurl("https://assets10.lottiefiles.com/packages/lf20_jneva4pr.json")
    st_lottie(collab, height = 300, key = "collab")

st.header("About The Dataset 📈")
st.write("""The dataset that was chosen for this demonstration was published by a Brazillian E-Commerce company called Olist. Olist gave the public access to real anonymized data. The data tracks about 100,000 orders from 2016-2018. The dataset collects a plethora 
         of informattion from customers including customer location, price, payment, shipping information, and much more. Due to the fact that the data comes from real life customer purchases (instead of artificially generated data) all of the insights shown in this 
         demo is pertinent to the real world and could be use to augment sales strategy and customer satisfaction.
         """)




#st.write("The dataset comes from a website Kaggle a subsidiary of Google. Kaggle is one of the most popular repositories of data. It hosts datasets and other resources for data analysts and data scientists professionals and enthusiasts alike.")


st.subheader("Why Utilize Dataiku?")
st.write("""Dataiku has been instrumental in making this project possible. AHEAD is a proud partner partner of Dataiku. Dataiku is typically thought as a artificial intelligence and machine learning platform. In reality Dataiku is much more than that.
         Dataiku also enables its users to do advanced data engineering and wrangling tasks without having to write a single line of code. By using Dataiku we were able to clean and combine data from across 9 different files into one comprehensible CSV that is ready
         for analysis. In addition to create impressive visualizations without having to leave the platform. The data engineering/wrangling and the in house visualizations will be expounded upon in seperate sections. 
         """)
st.success("See how Dataiku made this project possible on the Dataiku page of this project.", icon = "✅")

st.write("Without further ado let the analytics commence!")


st.header("Filtering The Data")

filter1 = load_lottieurl("https://assets8.lottiefiles.com/packages/lf20_8NgueIxoD0.json")
st_lottie(filter1, height = 300, key = "dark_filter")

st.write("In order to help answer adhoc questions and to mitigate idiosyncracies of the dataset, users will be able to filter through the data. It is important to keep in mind that any analysis provided below is only pertinent to the unfiltered dataset.")
with st.expander("Click to See the Filters"):
    st.warning("Data scrubbing is beyond the scope of this demonstration. Some filters may not work as expected. For example the customer city 'Sao Vicente' was assigned 8 different states in the olist dataset instead of just one. In addition to this one distinct state can be listed as pertaining to several regions which is not congruent with reality. Filters are likely to be pretty accurate in most cases but far from perfect.", icon = "🚨")
    mask = slide_creator("payment_value", 20.0) & slide_creator("review_score", 1.0) & multi_choose("Region_Customer") & multi_choose("State_Customer") &  multi_choose("Region_Seller") & multi_choose("State_Seller") & multi_choose("product_category_name_english") & multi_choose("order_status") & multi_choose("payment_type") #& multi_choose("customer_city")
    
df = df[mask]
df_map = df[mask]





# Undivided Data Section 
st.header("Undivided Sales Data - Time Series")

st.write("Here we can analyze time series information regarding sales over various intervals.")



pcol1, pcol2, pcol3, pcol4 = st.tabs(["Yearly Sales Chart", "Monthly Sales Chart",  "Year-Month Sales Chart", "Daily Sales Chart"])
with pcol1:
    line_chart_sum("payment_value", "order_purchase_timestamp", "yearly")
with pcol2:
    line_chart_sum("payment_value", "order_purchase_timestamp", "monthly")
with pcol3:
    line_chart_sum("payment_value", "order_purchase_timestamp", "year_month")
with pcol4:
    line_chart_sum("payment_value", "order_purchase_timestamp", "daily")



# Map City Preperation FOR CITIES-----------------------------
# Makes sure each city is only listed once 
# Make sure each city has a lat, lng if they don't drop it 

# No longer needed }}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}
# df_map_cleaned = df.drop_duplicates(subset = "city")
# unique_cities = df_map_cleaned.drop_duplicates(subset = "city")
# unique_cities = unique_cities.dropna(subset=["lat", "lng"])
#}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}

# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Quick Data Sectioning 

# def quick_data_section(column_to_split):
#     st.divider()
    
#     column_name = str(column_to_split)
#     column_title = column_name.title()
    
#     greeting = f"{column_to_split} Analysis"
#     st.subheader(greeting.title())
    
    
#     tab1, tab2 = st.tabs([f"Pie Chart of {column_title}", f"Countplot of Orders By {column_title}"])
#     with tab1:
#         make_pie(column_to_split)
#     with tab2:
#         bar_chart_count(column_to_split)
    
    
#     barchart_maker_sum(column_to_split, "payment_value")
    
#     st.write("Total Payments will be sometimes abbreviated as TPay.")
#     tab3, tab4, tab5, tab6 = st.tabs([f"TPAY By {column_title}", f"Monthly TPay By {column_title}", f"Year and Month TPay By {column_title}", f"Daily TPay By {column_title}"])
    
#     with tab3:
#         line_chart_sum("payment_value", "order_purchase_timestamp", "yearly", column_to_split)
#     with tab4:
#         line_chart_sum("payment_value", "order_purchase_timestamp", "monthly", column_to_split)
#     with tab5:
#         line_chart_sum("payment_value", "order_purchase_timestamp", "year_month", column_to_split)
#     with tab6:
#         line_chart_sum("payment_value", "order_purchase_timestamp", "daily", column_to_split)
   
   
#     st.divider()
    




# Map Section --------------------------------------------------------
# For this section we will have to use df_map


# Will Plot a Map of All of the Seller's cities 
st.header("Geographic Analytics")

def create_bubble_map(df, lat_col, lon_col, popup_col, radius_col):
    # drop rows with null latitude or longitude values
    df = df.dropna(subset=[lat_col, lon_col])

    # group data by popup column
    grouped = df.groupby(popup_col, as_index=False)

    # calculate sum of radius for each group
    aggregated = grouped.agg({lat_col: 'mean', lon_col: 'mean', radius_col: 'sum'})

    # center the map on Brazil
    m = folium.Map(location=[-14.2350, -51.9253], zoom_start=4)

    # add circle markers to the map for each group
    for i, row in aggregated.iterrows():
        folium.CircleMarker([row[lat_col], row[lon_col]], radius=row[radius_col]/100000, color='red', fill=True, fill_color='red', fill_opacity=0.5, popup=row[popup_col]).add_to(m)

    # show the map
    #return m
    return folium_static(m)

# Parallel Categories Diagram 
def parallel_categories_diagram_three(df, col1, col2, col3, color = "Blues", specified_height = 600):
    # Count the number of occurrences for each combination of values in the three columns
    counts = df.groupby([col1, col2, col3]).size().reset_index(name='count')
    
    # Create the parallel categories diagram using plotly.graph_objects
    fig = go.Figure(data=[go.Parcats(
        dimensions=[{'label': col1, 'values': counts[col1]},
                    {'label': col2, 'values': counts[col2]},
                    {'label': col3, 'values': counts[col3]}],
        counts=counts['count'],
        line={'color': counts['count'], 'colorscale': color},
        arrangement='freeform')])
    
    # Update the layout of the diagram
    
    fig.update_layout(
        margin=dict(l=70, r=70, t=20, b=20),
        paper_bgcolor="Black",
        )
    
    
    fig.update_layout({
        'xaxis': {'title': col1},
        'yaxis': {'title': col2},
        'height': specified_height,
        "width": 1200
    })
    
    #'title': {'text': 'Parallel Categories Diagram'},
   
    # Show the diagram
    #fig.show()
    return st.plotly_chart(fig)

def parallel_categories_diagram_two(df, col1, col2, color = "Blues", specified_height = 600):
    # Count the number of occurrences for each combination of values in the three columns
    counts = df.groupby([col1, col2]).size().reset_index(name='count')
    
    # Create the parallel categories diagram using plotly.graph_objects
    fig = go.Figure(data=[go.Parcats(
        dimensions=[{'label': col1, 'values': counts[col1]},
                    {'label': col2, 'values': counts[col2]},
                    ],
        counts=counts['count'],
        line={'color': counts['count'], 'colorscale': color},
        arrangement='freeform')])
    
    # Update the layout of the diagram
    
    fig.update_layout(
        margin=dict(l=70, r=70, t=20, b=20),
        paper_bgcolor="Black",
        )
    
    
    fig.update_layout({
        'xaxis': {'title': col1},
        'yaxis': {'title': col2},
        'height': specified_height,
        "width": 1200
    })
    
    #'title': {'text': 'Parallel Categories Diagram'},
   
    # Show the diagram
    #fig.show()
    return st.plotly_chart(fig)


def parallel_categories_diagram_four(df, col1, col2, col3, col4, color = "Blues", specified_height = 600):
    # Count the number of occurrences for each combination of values in the four columns
    counts = df.groupby([col1, col2, col3, col4]).size().reset_index(name='count')
    
    # Create the parallel categories diagram using plotly.graph_objects
    fig = go.Figure(data=[go.Parcats(
        dimensions=[{'label': col1, 'values': counts[col1]},
                    {'label': col2, 'values': counts[col2]},
                    {'label': col3, 'values': counts[col3]},
                    {'label': col4, 'values': counts[col4]}],
        counts=counts['count'],
        line={'color': counts['count'], 'colorscale': color},
        arrangement='freeform')])
    
    # Update the layout of the diagram
    fig.update_layout({
        'xaxis': {'title': col1},
        'yaxis': {'title': col2},
        'height': specified_height,
        "width": 1200
    })
    
    # Update the layout of the diagram
    fig.update_layout(
        margin=dict(l=70, r=70, t=20, b=20),
        paper_bgcolor="Black",
        )
    
    # Show the diagram
    #fig.show()
    return st.plotly_chart(fig)




create_bubble_map(df, 'city_lat_customer', 'city_lng_customer', 'customer_city','payment_value')
st.caption("The first map shows customer zip codes coordinates grouped together by city for buyers.")

create_bubble_map(df, 'city_lat_seller', 'city_lng_seller', 'seller_city','payment_value')
st.caption("The second map shows customer zip codes coordinates grouped together by city for buyers. The right map shows zip code coordinates grouped together by city for sellers. Evidently there are fewer sellers than buyers.")

with st.expander("See Regional Map of Brazil"):
    region_image = Image.open(r"images\pictures\brazil-regions-states_basic.jpg")
    st.image(region_image, caption = "Map created by iheartbrazil.com")
    


st.header("Logistical Geographic Analytics")

col1, col2 = st.columns(2)

with col1:
    unload_truck = load_lottieurl("https://assets10.lottiefiles.com/packages/lf20_toa6tsan.json")
    st_lottie(unload_truck, height = 300, key = "unloading")

with col2:
    handoff = load_lottieurl("https://assets5.lottiefiles.com/packages/lf20_3tryizhw.json")
    st_lottie(handoff, height = 300, key = "delivery_handoff")

biker = load_lottieurl("https://assets2.lottiefiles.com/packages/lf20_vvx1ff1l.json")
st_lottie(biker, height = 500, key = "bike_deliver")

st.write("In this sub section we will explore how goods are transported between buyers and sellers amongst other things. This will be done using Parallel Category Diagrams. Parallel Category Diagrams are similar to Sankey Charts/Alluvial diagrams.")
st.write("")

#parallel_categories_diagram_three(df, 'Region_Customer', 'payment_type', 'Region_Seller', color = "Mint")
parallel_categories_diagram_two(df, 'Region_Customer', 'Region_Seller', color = "Mint")

#parallel_categories_diagram_three(df, 'State_Customer', 'payment_type', 'State_Seller', color = 'YlOrBr')
parallel_categories_diagram_two(df, 'State_Customer', 'State_Seller', color = 'YlOrBr')
parallel_categories_diagram_four(df, 'Region_Customer', 'State_Customer', 'Region_Seller', "State_Seller", color = "Purples")


st.subheader("Other Parallel Categories Visualizations")

pcol1, pcol2, pcol3, pcol4 = st.tabs(["Regions With Payment Type", "States With Payment_Type", "State Customer Order Status" ,"Review Score State"])

with pcol1:
    parallel_categories_diagram_three(df, 'Region_Customer', 'payment_type', 'Region_Seller', color = "deep")
with pcol2:
    parallel_categories_diagram_three(df, 'State_Customer', 'payment_type', 'State_Seller', color = 'YlOrBr')
with pcol3:
    parallel_categories_diagram_three(df, 'State_Customer', 'order_status', 'State_Seller', color = 'OrRd')
with pcol4:
    parallel_categories_diagram_three(df, 'State_Customer', 'review_score', 'State_Seller', color = 'Magma')

# biker = load_lottieurl("https://assets2.lottiefiles.com/packages/lf20_vvx1ff1l.json")
# st_lottie(biker, height = 500, key = "bike_deliver")
    
    


# brazil_map = folium.Map(location = [-14.3779, -51.7977], zoom_start= 4, tiles="Stamen Terrain")

# marker_cluster = MarkerCluster().add_to(brazil_map)

# for index, row in unique_cities.iterrows():
#   # No need to skip lat and lng with nulls because the unique_countries does this for us 

    
#     # Add a marker for the current row to the marker cluster
#     folium.Marker(location=[row['lat'], row['lng']], 
#                   tooltip=row['city'],  # add tooltip with value of 'city' column
#                   fill_color='region', 
#                   radius=8).add_to(marker_cluster)



#folium_static(brazil_map)


# Customer
# Customer Region
quick_data_section("Region_Customer")

barchart_maker_sum("Region_Customer", "payment_value")
make_pie("Region_Customer")

quick_data_section("State_Customer")

#City Analysis Takes too much power
#quick_data_section("customer_city")

barchart_maker_sum("State_Customer", "payment_value")
make_pie("Region_Customer")
make_pie("State_Customer")
bar_chart_count("State_Customer")

barchart_maker_sum("customer_city", "payment_value")


## Sales Data ---------------------------------------------------------







# PAYMENT Types Section ------------------------------

# Pie Charts 
st.header("Payment Type")
# make_pie("payment_type")
# bar_chart_count("payment_type")

quick_data_section("payment_type")



# Line Chart plots
# Line chart for count 
# tab1, tab2, tab3, tab4 = st.tabs(["Daily Chart", "Monthly Chart", "Yearly Chart", "Yearly and Monthly Chart"])

# with tab1:
#     line_chart_count("payment_type", "daily")
# with tab2:
#     line_chart_count("payment_type", "monthly")
# with tab3:
#     line_chart_count("payment_type", "yearly")
# with tab4:
#     line_chart_count("payment_type", "year_month")


# line_chart_sum("payment_value", "order_purchase_timestamp", "yearly", seperation= "payment_type")

# Line chart for money spent 
# tab1, tab2, tab3, tab4 = st.tabs(["Daily Chart", "Monthly Chart", "Yearly Chart", "Yearly and Monthly Chart"])

# with tab1:
#     line_chart_sum("payment_value", "order_purchase_timestamp", "daily", seperation= "payment_type")
# with tab2:
#     line_chart_sum("payment_value", "order_purchase_timestamp", "monthly", seperation= "payment_type")
# with tab3:
#     line_chart_sum("payment_value", "order_purchase_timestamp", "yearly", seperation= "payment_type")
#     #line_chart_sum("payment_value", "order_purchase_timestamp", "monthly", seperation= "payment_type")
# with tab4:
#     #line_chart_sum("payment_value", "order_purchase_timestamp", "yearly", seperation= "payment_type")
#     line_chart_sum("payment_value", "order_purchase_timestamp", "monthly", seperation= "payment_type")



# line_chart_sum("payment_value", "order_purchase_timestamp", "daily", seperation= "payment_type")
    




# Add divider to seperate sections. 
st.divider()


# Payment Installments 
# NOTE Need scatterplot for payment installments and price. (Another one with payment value.)
# NOTE Need statistical testing for each aforementioned groups. 
st.header("Payment Installments")

st.write("In this section we will analyze the importance of payment installments to Olist.")
histogram("payment_installments", "#880D1E")
make_pie("payment_installments")

st.subheader("Do Customers Who Use Payment Installments Tend to Spend More?")
st.write("It is tempting to believe that customers who spend more money are more suceptible to using payment plans where shoppers can pay for their goods in installments. Although this prediction is logical we need to check to see if the data vindicates this assumption.")

corr_inst_pay =df["payment_installments"].corr(df["payment_value"])

st.write("The correlation between payments_installments and payment value according to pandas is about: 0.27. The R^2 value is shown to be 0.07 no correlation at all. You can see the line of best fit in the scatterplot below.")

def scatterplot_with_line_of_best_fit(df, x_col, y_col, given_title):
    fig = px.scatter(df, x = x_col, y = y_col, trendline = "ols", title= given_title, trendline_color_override= "yellow")

    #fig.show()
    st.plotly_chart(fig)

scatterplot_with_line_of_best_fit(df, "payment_installments", "payment_value", "Payment Value Vs Payment Installments Scatterplot")

#scatterplot_with_line_of_best_fit(df, "payment_installments", "price", "Price Vs Payment Installments Scatterplot")

st.write("There does not seem to be any correlation between paymet_installments and the total ammount paid (payment_value). At best the correlation is positive and very weak.")

st.divider()

st.header("Order Status")
histogram("order_purchase_hour")


quick_data_section_count("order_status")
# make_pie("order_status")

st.divider()

# Shipping Analysis Need to Revisit--------------------------------------------------------------------------------------------- 
# Need to investigate histogram for delivery days taken 

# NOTE Need to add functionality to make the histogram a custom size but have the default size be normal. 
st.header("Shiping Analysis")

st.subheader("Days Taken to Deliver Histogram")
histogram("delivery_days_taken")
simple_boxplot("delivery_days_taken")


# Difference In Delivery Date vs Estimate  
histogram("actual_delivery_date_minus_estimated")
simple_boxplot("actual_delivery_date_minus_estimated")


# Order Processing Difference 
# We can see how long it takes for the processing of the order to be completed once the order is placed 

#Not really needed 
#histogram("process_order_time_minutes")
#------------------------------------------------------------------------------------------------------------------

# Analyzing Products 
st.header("Product Categories Analysis")

# Needs to be fixed 
#bar_chart_count("product_category_name_english")   # Want a NEW function with descending order and products as a a different color entity 


quick_data_section("product_category_name_english")





# NOTE add analysis later with an analysis function 

# Review Section
st.header("Reviews")
st.write("Reviews are very important for a plethora of reasons. It can let sellers gauge the quality of their product and delivery.")


histogram("review_score")
simple_boxplot("review_score")


# See What Percent of People Leave a Review 

#st.subheader("Review Left Pie Chart")
#df["review_left"] = [False if pd.isna(x) else True for x in df["review_score"]]

# Get rid of review left as the nulls are somehow gone even when we tried to convert it to a string
# make_pie("review_left")

quick_data_section_count("review_score")


# How Long Does It Take for People to make a review 
date_subtract("review_creation_date", "order_delivered_customer_date", "days_from_review_to_reciept")
#st.write("The above code shows the difference between the day the review was created and the day that the order came in. Some of the results is somewhat perplexing. Some people seemed to have reviewed the items before they bought it. This is possible on some websites but we would not expect this to be too common.")

histogram("days_from_review_to_reciept")
with st.expander("Click To See Unfiltered Analysis of Reviews to Reciept"):
    st.write("The above code shows the difference between the day the review was created and the day that the order came in. Some of the results is somewhat perplexing. Some people seemed to have reviewed the items before they bought it. This is possible on some websites but we would not expect this to be too common. People reviewing a hundred days after their order is more explainable.")



# 3D Analysis 
st.header("Spatial Analysis")

#df["volume"] = df["product_length_cm"] * df["product_height_cm"] * df["product_width_cm"]

def three_dimensions(color_var = "volume_cm3"):
    fig = px.scatter_3d(df, x="product_length_cm", y= "product_width_cm", z="product_height_cm", color= color_var, opacity = 0.7, size_max = 18, hover_data =["volume_cm3", "product_category_name_english", "price"])
    fig.update_layout(margin=dict(l=0, r=0, b=0, t=0))
    
    st.plotly_chart(fig, theme= None)
    



# with st.expander("Dimensional analysis"):
st.write("This is a 3D visualization that allows users to visualize the width and lenghth and height of the purchased items. ")
three_dimensions()

# Need Average Review By Product Over Time 


# make_pie("payment_type")
# bar_chart_count("payment_type")

# NOTE fix the bar function. Make a simple bar chart function using this link: https://plotly.com/python/bar-charts/










