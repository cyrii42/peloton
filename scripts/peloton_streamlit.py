import pandas as pd
import sqlalchemy as db
import streamlit as st
import subprocess
from datetime import datetime
import numpy as np
import time
import streamlit as st
from pydantic import BaseModel
import streamlit_pydantic as sp

from peloton import PelotonPivots, PelotonProcessor

SQLITE_FILENAME = "sqlite:///data/peloton.db"

st.set_page_config(
    page_title="Ex-stream-ly Cool App",
    page_icon=":bicyclist:",
    layout="wide",
    initial_sidebar_state="auto",
    menu_items={
        'About': "# This is a header. This is an *extremely* cool app!"
    }
)
with st.sidebar:
    st.write("This code will be printed to the sidebar.")



sqlite_engine = db.create_engine(SQLITE_FILENAME)
peloton_processor = PelotonProcessor(sqlite_engine)
peloton_pivots = PelotonPivots(peloton_processor)



df_year_table = peloton_pivots.year_table
df_month_table = peloton_pivots.month_table.sort_index(ascending=False)
df_processed_data = peloton_pivots.processed_table.sort_index(ascending=False)

table_options = {
    'Year Table': df_year_table, 
    'Month Table': df_month_table, 
    'Processed Data': df_processed_data
}

option = st.selectbox('Which table?', table_options.keys())

'You selected: ', option

df = table_options[option]

if st.button('Reload peloton data...'):
    with st.spinner("Loading..."):
        # Run the script file
        # result = subprocess.Popen(['bash', 'peloton.sh'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        # stdout, stderr = result.communicate()

        # # Display the terminal output
        # st.text('\n'.join(stdout.decode().split('\n')[1:][:-1]))
        
        peloton_processor.check_for_new_workouts()
        # time.sleep(3)
        peloton_pivots = PelotonPivots(peloton_processor)
        df = peloton_pivots.processed_table.sort_index(ascending=False)
    st.success("Done!")
    
# x = st.slider('x', value=500, max_value=1000)  # 👈 this is a widget

st.title(":bicyclist: zach's peloton ride data :bicyclist:")
st.dataframe(df, use_container_width=True, hide_index=True)
# st.area_chart(df, x="time", y="weight", height=500, width=880, use_container_width=False) 

class ExampleModel(BaseModel):
    some_text: str
    some_number: int
    some_boolean: bool

data = sp.pydantic_form(key="my_form", model=ExampleModel)
if data:
    st.json(data.model_dump_json())
df2 = pd.DataFrame(data)
df2

