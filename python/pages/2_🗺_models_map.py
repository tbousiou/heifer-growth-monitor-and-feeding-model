import pandas as pd
import streamlit as st
import pydeck as pdk

from database import init_connection


st.set_page_config(
    page_title="Models Map",
    page_icon="⭕")

st.title("Model Locations")
st.write("Here you can view the custom feeding models where users have submitted. If you find a model in your region and with same type of breed you can select it in the feeding monitor page")
st.info("If you have just sumbitted a model and does not appear here press the **C** key to clear the page cache", icon='ℹ️')
# Fetch data from the database

# Uses st.experimental_memo to only rerun when the query changes or after 10 min.
@st.experimental_memo(ttl=60)
def run_query():
    return supabase.table("custom_models").select("*").execute()

try:
    supabase = init_connection()
    rows = run_query()
except:
    st.error("Something went wrong, could not connect to the database", icon='😨')
    st.stop()


df = pd.DataFrame(rows.data)
map_df = df[['lat', 'lon', 'model_name', 'location']]
st.header("Models map")

# SCATTERPLOT_LAYER_DATA = "https://raw.githubusercontent.com/visgl/deck.gl-data/master/website/bart-stations.json"
# df = pd.read_json(SCATTERPLOT_LAYER_DATA)


# Use pandas to calculate additional data
# df["coor"] = df["exits"].apply(lambda exits_count: math.sqrt(exits_count))

# Define a layer to display on a map
layer = pdk.Layer(
    "ScatterplotLayer",
    map_df,
    pickable=True,
    opacity=0.8,
    stroked=True,
    filled=True,
    radius_scale=6,
    radius_min_pixels=5,
    radius_max_pixels=100,
    line_width_min_pixels=1,
    get_position=['lon','lat'],
    # get_radius=50,
    get_fill_color=[255, 140, 0],
    get_line_color=[0, 0, 0],
    
)

# Set the viewport location
view_state = pdk.ViewState(latitude=49.7749295, longitude=13.0, zoom=3, bearing=0, pitch=0)

# Render
r = pdk.Deck(layers=[layer], initial_view_state=view_state, tooltip={"text": "{model_name}\n{location}"})

st.pydeck_chart(r)

st.header("Models Table")
df[['model_name', 'breed_type', 'base_type','location']]