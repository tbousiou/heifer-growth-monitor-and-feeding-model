import streamlit as st

st.set_page_config(
    page_title="Home",
    page_icon="⭕")

# Title of the main page
st.title("Heifer Feeding model application")

st.header("Intro")
'''
This application consists of the following tools:
* **Growth monitor**: Monitor the body weight growth of your animals and compare it with the recommended growth.
* **Feeding models map and catalogue**: Explore custom feeding models that other users have created.
* **Model estimator**: Create a custom model to meet your requirements.
* **Find model**: Find a model suitable for your requirements.

More instructions you will find at the page of each tool.
'''


st.header("How to use this app")
'''
Use the growth monitor tool to monitor the growth of your animals. You compare the growth against the standard ideal feeding
models or a custom model created by another user. To find more info about the custom models use the models map and catalogue tool.
Finally you can create your custom model and submit it to the database using the model estimator tool.
'''
st.subheader("Sample data")
'''
[Full 24 months](https://github.com/tbousiou/feedingmodelmonitor/raw/main/data/example_user_growth_data-1.xlsx) sample body growth data, for use in all tools.

[Partial 14 months](https://github.com/tbousiou/feedingmodelmonitor/raw/main/data/example_user_growth_data-2.xlsx) sample body growth data, for use in growth monitor.
'''
st.header("About")
'''
This work is part of the ATLAS project.
'''
st.image('assets/atlas-logo.png', width=300)
'''
### Team 
- **Supervisors**: 
    - Thomas Kotsopoulos, Professor, Aristotle University of Thessaloniki, Greece
    - Dimitrios Moschou, Professor, Aristotle University of Thessaloniki, Greece
- **Research**: Vasilis Firfiris
- **Developer**: Theodoros Bousiou

### Licence
This work is licensed under the MIT licence

[View code in github](https://github.com/tbousiou/feedingmodelmonitor) 

'''