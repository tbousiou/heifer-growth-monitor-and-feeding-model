import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Growth Monitor",
    page_icon="⭕")

st.title('Dairy Heifer Growth monitor')
st.write('Monitor Heifer growth with breed standards. Growth charts and references:')
"""
- https://extension.psu.edu/growth-charts-for-dairy-heifers
- https://lactanet.ca/en/growth-chart-by-breed/
"""

# Read excel file with growth charts
growth_data_file = pd.ExcelFile('data/growth_charts_1.xlsx')
# For each breed type there is a separate sheet
breed_types = growth_data_file.sheet_names  # see all sheet names

#xl.parse(sheet_name)  # read a specific sheet to DataFrame
st.header("Step 1: Choose breed type")
selected_breed = st.selectbox('Select breed type', breed_types)
model_bw_data = growth_data_file.parse(selected_breed,index_col=0)


st.header("Step 2: Upload your data")
st.markdown("""Upload a **spreadsheet** file with body weight data growth of all your animals.
Each column must be a separate animal. Body weight sampling must be by **month** and you must have **up to 24 rows** of data.""")


st.write("Example data:")
example_data = pd.DataFrame(data={'col1': [60, 70, 80], 'col2': [62, 74, 84], 'col3': [58, 71, 89]})
st.table(example_data)

uploaded_file = st.file_uploader("Choose a file")


if uploaded_file is not None:
    user_bw_data = pd.read_excel(uploaded_file,index_col=0)

    with st.expander("Click to see your uploladed data"):
        st.markdown('**Y axis**: Body Weight Growth (Kg), **X axis**: Month')
        st.line_chart(user_bw_data)

    st.header("Step 3: View summary of results")

    text = """
        The following table summarizes the results for all animals and displays a warning sign when an animal is out of the recommended growth charts.
        The decision is made by comparing a **treshold value** with the mean absolute errors of the top and bottom percentiles of the recommended growth.
        When **both errors** are below the treshold value then the growh rate is considered OK.
        You can change the treshold value using the slider below.
    """
    st.markdown(text)
    
    # calculate the mean absolute error against the top and bottom percentile
    errors = pd.DataFrame()
    # errors['bottom mae'] = abs(user_bw_data.sub(model_bw_data['75th'], axis=0)).mean()
    # errors['top mae'] = abs(user_bw_data.sub(model_bw_data['95th'], axis=0)).mean()
    
    errors['bottom mae'] = abs(user_bw_data.sub(model_bw_data.iloc[:,0], axis=0)).mean()
    errors['top mae'] = abs(user_bw_data.sub(model_bw_data.iloc[:,1], axis=0)).mean()
    
    # compare mae against a treshold value
    error_treshold = st.slider('Error Treshold in Kg, default=30', 0, 60, 30)
    errors['test'] = (errors['bottom mae'] <= error_treshold) & (errors['top mae'] <= error_treshold)
    errors['icon'] = errors['test'].apply(lambda x: '🆗' if x else '⚠️')
    
    st.table(errors)
       
    total_animals = user_bw_data.shape[1]
    st.header("Step 4: View each animal")
    st.markdown("""Graphicaly compare each animal growth curve against the recommended top and bottom percentiles.
     Use the slider below to select the animal to compare""")

    selected_animal = st.slider('Select animal to compare', min_value=1, max_value=total_animals, value=1, step=1)
   
    animal_data = user_bw_data.iloc[:,selected_animal-1]

    model_bw_data['current_animal'] = animal_data
    
    st.markdown('**Y axis**: Body Weight Growth (Kg), **X axis**: Month')
    st.line_chart(model_bw_data)
    