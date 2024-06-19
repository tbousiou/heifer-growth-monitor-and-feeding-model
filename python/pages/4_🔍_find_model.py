import streamlit as st
import pandas as pd
from models import base_model_1, base_model_2, dmi0, dmi1
from database import init_connection

st.set_page_config(
    page_title="Find model",
    page_icon="⭕")

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

models = rows.data
models_names = [item['model_name'] for item in models]

st.title('Find a feeding model')
st.write('Find a feeding model suitable for your farm')


# Section 1 - Select breed type and show BW and DMI graphs

# Read excel file with growth charts
growth_data_file = pd.ExcelFile('data/growth_charts_1.xlsx')
# For each breed type there is a separate sheet
breed_types = growth_data_file.sheet_names  # see all sheet names

st.header("Step 1: Choose breed type")
selected_breed = st.selectbox('Select your breed type', breed_types)
model_bw_data = growth_data_file.parse(selected_breed, index_col=0)



st.header("Step 2: Upload your data")

st.markdown("""Upload a **spreadsheet** file with body weight data growth of all your animals.
The app will **calculate the average of all animals** and use this in the model estimation.
Each column must be a separate animal. Body weight sampling must be by **month** and you must have **exactly 24 rows** of data.""")

st.write("Example data:")
example_data = pd.DataFrame(data={'animal1': [60, 70, 80], 'animal2': [
                            62, 74, 84], 'animal3': [58, 71, 89]})
st.table(example_data)



uploaded_file = st.file_uploader("Choose a file")
if uploaded_file is not None:

    user_bw_data = pd.read_excel(uploaded_file, index_col=0)
    with st.expander("Click to see your uploladed data"):
        st.markdown('**Y axis**: Body Weight Growth (Kg), **X axis**: Month')
        st.line_chart(user_bw_data)

    # calculate average of every animal
    user_bw_data_mean = user_bw_data.mean(axis=1)
    
    estimator_bw = model_bw_data
    estimator_bw['user'] = user_bw_data_mean

    

    st.header("Step 3: Select a user model")
    selected_model_name = st.selectbox('Select a user feeding model', models_names)
    selected_model_index = models_names.index(selected_model_name)
    
    model = models[selected_model_index]
    # model
    model['location']
    


    # st.write("BW growth")
    # st.line_chart(estimator_bw)
    
    st.header("Step 4: Compare")

    st.markdown("""
        The following chart shows the DMI growth of the user data in comparison with the top and bottom acceptable percentiles. 
        """)

    # user_model = model
    

    if model['base_type'] == 0:
        parameter_a = model['pa']
        parameter_b = model['pb']

        dpa = base_model_1['params']['a']
        dpb = base_model_1['params']['b']

        estimator_dmi = estimator_bw.apply(dmi0,a=dpa,b=dpb)
        estimator_dmi['user'] = estimator_bw['user'].apply(dmi0,a=parameter_a,b=parameter_b)
        
    elif model['base_type'] == 1:
        parameter_a = model['pa']
        parameter_b = model['pb']
        parameter_c = model['pc']
        parameter_d = model['pd']

        dpa = base_model_2['params']['a']
        dpb = base_model_2['params']['b']
        dpc = base_model_2['params']['c']
        dpd = base_model_2['params']['d']

        estimator_dmi = estimator_bw.apply(dmi1,a=dpa,b=dpb,c=dpc,d=dpd)
        estimator_dmi['user'] = estimator_bw['user'].apply(dmi1,a=parameter_a,b=parameter_b,c=parameter_c,d=parameter_d)
    
    st.line_chart(estimator_dmi)

    st.write('TODO: Inform user when model is OK')
    
