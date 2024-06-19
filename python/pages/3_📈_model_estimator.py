import streamlit as st
import pandas as pd
from geopy.geocoders import Nominatim
from models import base_model_1, base_model_2, dmi0, dmi1
from database import init_connection

st.set_page_config(
    page_title="Model Estimator",
    page_icon="⭕")

st.title('Dairy Heifer Model Prameter Estimator')
st.write('Estimate parameters from various feeding models to specific farmer requirements')

base_models = [base_model_1, base_model_2]



# Section 1 - Choose base feeding models
model_names = [ item['name'] for item in base_models]

st.header("Step 1: Choose base feeding model")
selected_model_name = st.selectbox(
    'Select the base feeding model', model_names)
selected_model_index = model_names.index(selected_model_name)

model = base_models[selected_model_index]
st.latex(model['latex'])

model_params = model['params']

if model['model_id'] == 0:
    param_a = model_params['a']
    param_b = model_params['b']
    st.write(f"Default model parameters a = {param_a}, b={param_b}")
elif model['model_id'] == 1:
    param_a = model_params['a']
    param_b = model_params['b']
    param_c = model_params['c']
    param_d = model_params['d']
    st.write(f"Default model parameters a = {param_a}, b={param_b},  c = {param_c}, d={param_d}")


# Section 2 - Select breed type and show BW and DMI graphs

# Read excel file with growth charts
growth_data_file = pd.ExcelFile('data/growth_charts_1.xlsx')
# For each breed type there is a separate sheet
breed_types = growth_data_file.sheet_names  # see all sheet names

st.header("Step 2: Choose breed type")
selected_breed = st.selectbox('Select your breed type', breed_types)
model_bw_data = growth_data_file.parse(selected_breed, index_col=0)


st.header("Step 3: Upload your data")

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

    # st.write("BW growth")
    # st.line_chart(estimator_bw)
    
    st.header("Step 4: Estimate model parameters")

    st.markdown("""
        The following chart shows the DMI growth of the user data in comparison with the top and bottom acceptable percentiles. 
        
        **Click on +/- to change the model parameteres** to match the user curve somewhere between the top and bottomm percentiles""")

    # user_model = model

    if model['model_id'] == 0:
        parameter_a = st.number_input(
            'Parameter a', min_value=1.0, max_value=20.0, value=param_a, step=0.5)
        parameter_b = st.number_input(
            'Parameter b', min_value=0.001, max_value=0.003, value=param_b, step=0.0001, format='%.4f')

        estimator_dmi = estimator_bw.apply(dmi0,a=model_params['a'],b=model_params['b'])
        estimator_dmi['user'] = estimator_bw['user'].apply(dmi0,a=parameter_a,b=parameter_b)
        
    elif model['model_id'] == 1:
        parameter_a = st.number_input(
            'Parameter a', min_value=0.5, max_value=1.0, value=param_a, step=0.01, format='%.4f')
        parameter_b = st.number_input(
            'Parameter b', min_value=0.2, max_value=0.3, value=param_b, step=0.001, format='%.4f')
        parameter_c = st.number_input(
            'Parameter c', min_value=0.03, max_value=0.06, value=param_c, step=0.005, format='%.4f')
        parameter_d = st.number_input(
            'Parameter d', min_value=0.05, max_value=0.2, value=param_d, step=0.01, format='%.4f')

        

        estimator_dmi = estimator_bw.applymap(dmi1,a=model_params['a'],b=model_params['b'],c=model_params['c'],d=model_params['d'])
        estimator_dmi['user'] = estimator_bw['user'].apply(dmi1,a=parameter_a,b=parameter_b,c=parameter_c,d=parameter_d)
        
    
    # user_model = model
    # estimator_dmi = estimator_bw.apply(dmi0,a=model_params['a'],b=model_params['b'])
    # estimator_dmi['user'] = estimator_bw['user'].apply(dmi0,a=parameter_a,b=parameter_b)
    # estimator_dmi
    st.line_chart(estimator_dmi)
    

    st.header("Step 5: Submit your model")
    st.write(
        "You can submit your model with the custom parameters to the database so other can use it.")
    st.warning('Please do not submit the same model twice!', icon="⚠️")

    st.subheader("Location")
    st.write(
        "Type your location and click the Find button. Repeat until the location is correct")
    
    with st.form("location_form"):
        city = st.text_input("County, city, town, village",
                             placeholder="ex. Katerini, Pieria")
        country = st.text_input("Country", placeholder="Greece")
        submitted1 = st.form_submit_button("Find location")
        if submitted1:
            geolocator = Nominatim(user_agent="feeding-model-app")
            
            location = geolocator.geocode(f"{city}, {country}")

            if not location:
                st.error("Could not find location, please try again", icon='⚠️')
                st.stop()

            
            st.write("Acording to your data your location is:")
            st.write(location.address)
            st.write(
                f"Latitude: {location.latitude}, Longiture: {location.longitude}")
            st.info("Enter address again if the location is not correct, otherwise continue below to submit your model to the database")
            st.map(pd.DataFrame(
                {'lat': [location.latitude], 'lon': [location.longitude]}))

            # Save location info to session, required to pass this info to the next form
            st.session_state.location = location.address
            st.session_state.lat = location.latitude
            st.session_state.lon = location.longitude
    
    
    st.subheader("Submit your model")
    st.warning('Please do not submit the same model twice!', icon="⚠️")

    st.write("Enter your name and/or company name and click Submit")
    with st.form("model_form"):
        model_name = st.text_input("Your name, or company name")

        # Every form must have a submit button.
        submitted2 = st.form_submit_button("Submit")
        if submitted2:
            st.write(model_name)
            if 'location' not in locals() and model_name=='':
                st.error("No location or name specified")
                st.stop()

            custom_model = dict()
            custom_model['model_name'] = model_name
            custom_model['location'] = st.session_state.location
            custom_model['lat'] = st.session_state.lat
            custom_model['lon'] = st.session_state.lon
            custom_model['base_type'] = model['model_id']
            custom_model['pa'] = parameter_a
            custom_model['pb'] = parameter_b
            if model['model_id'] == 1:
                custom_model['pc'] = parameter_c
                custom_model['pd'] = parameter_d

            custom_model['breed_type'] = selected_breed

            custom_model

            # Delete all the items in Session state
            for key in st.session_state.keys():
                del st.session_state[key]
            
            # custom_model
            try:
                supabase = init_connection()
                supabase.table("custom_models").insert(custom_model).execute()
                st.success("Model submited to the database", icon='👍')
            except:
                st.error("Something went wrong, could not connect to the database", icon='😨')
