import streamlit as st
from snowflake.connector import connect
import pandas as pd
import chart_funcs as cf

#Set page configuration
st.set_page_config(
    page_title="Dashboard Analysis",
    page_icon="📊",
)

#set page title
st.title("📊 Dashboard Analysis")
st.markdown("Analyse your data by customising the dashboard's chart types and fields. \
            Currently data is loaded directly from a Snowflake table for demo purposes. You can upload your own data in csv \
            format using the dropdown on the sidebar.")
st.divider()

#Create Streamlit containers
ln_cht = st.container()
bar_cht = st.container()
sc_pl = st.container()

df = None

#Functions for retrieving snowflake data
# Function to connect to Snowflake
def connect_to_sf(acct,usr,pwd,rl,wh,db):
    ctx = connect(user=usr,account=acct,password=pwd,role=rl,warehouse=wh,database=db)
    cs = ctx.cursor()
    st.session_state['snow_conn'] = cs
    st.session_state['ready'] = True
    return cs

# Function to get Snowflake data
def get_sf_data():
    query = f'SELECT * FROM STREAMLIT_COMP_DB.STREAMLIT_COMP_SCHMA.PART_ORDERS LIMIT 500' 
    results = st.session_state['snow_conn'].execute(query)
    results = st.session_state['snow_conn'].fetch_pandas_all()
    return results

# Load data from Snowflake
@st.cache_data
def load_sf_data_source():
    connect_to_sf(st.secrets['sf_creds']["account"],st.secrets['sf_creds']["username"],st.secrets['sf_creds']["password"], \
                st.secrets['sf_creds']["role"],st.secrets['sf_creds']["warehouse"],st.secrets['sf_creds']["database"])
    if 'ready' not in st.session_state:
        st.session_state['ready'] = False

    if st.session_state['ready'] == True:
        df = get_sf_data()
        return df

# Load data from uploaded file
@st.cache_data
def load_file_data_source(uploaded_file):
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        st.session_state['ready'] = True
        return df

# Set default values
if 'ds_type_sf' not in st.session_state:
    st.session_state.ds_type_sf = True

if 'ready' not in st.session_state:
    st.session_state.ready = False

# Show sidebar UI
with st.sidebar:
    data_source_type = st.selectbox('Data Source Type', ['❄️ Snowflake', '📁 File'])

    if data_source_type == '❄️ Snowflake':
        st.session_state.ds_type_sf = True
        
        df = load_sf_data_source()

    else:
        st.session_state.ds_type_sf = False
        st.session_state.ready = False


    # Show file upload UI
    if not st.session_state.ds_type_sf:
        uploaded_file = st.file_uploader('Upload a CSV File', type='csv')
        df = load_file_data_source(uploaded_file)



    ##########


if df is not None:

    st.session_state['df'] = df

    #Prepare the data and additional dataframes
    for col in df.columns:
            if df[col].dtype == 'object':
                try:
                    df[col] = pd.to_datetime(df[col])
                except ValueError:
                    pass

    dt_cols = df.select_dtypes(include='datetime').columns
    st.session_state['dates_df'] = df[dt_cols]
    cats = df.select_dtypes(include='object').columns
    cat_cols = [col for col in cats if col not in dt_cols]
    st.session_state['cats_df'] = df[cat_cols]
    st.session_state['nums_df'] = df.select_dtypes(include='number')


    with ln_cht:
        st.subheader("Line Chart Analysis")
        with st.expander("Chart Options"):
            ln_cat_val,x_val,y_val,y_agg,y_nm,dt_lvl = cf.line_chart_fields(st.session_state.cats_df,st.session_state.nums_df,st.session_state.dates_df)
        cf.line_chart_build(st.session_state.df,ln_cat_val,x_val,y_val,y_agg,y_nm,dt_lvl)  
        st.divider()

    with bar_cht:
        st.subheader("Bar Chart Analysis")
        with st.expander("Chart Options"):
            display_bars,cat_val,metric_val,metric_agg  = cf.bar_chart_fields(st.session_state.cats_df,st.session_state.nums_df)
        cf.bar_chart_build(df,display_bars,cat_val,metric_val,metric_agg) 
        st.divider()

    with sc_pl:
        st.subheader("Scatter Plot Analysis")
        with st.expander("Chart Options"):
            y_metric_val,x_metric_val,data_point_cat_val,y_metric_agg,x_metric_agg  = cf.scatter_plot_fields(st.session_state.nums_df,st.session_state.cats_df)
        cf.scatter_plot_build(df,y_metric_val,x_metric_val,data_point_cat_val,y_metric_agg,x_metric_agg)