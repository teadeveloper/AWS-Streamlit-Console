import pandas as pd
import streamlit as st
from PIL import Image
from AWS_services.s3 import AwsS3

from pandas.api.types import (
    is_categorical_dtype,
    is_datetime64_any_dtype,
    is_numeric_dtype,
    is_object_dtype,
)
aws_end_end_point = None

image = Image.open('pages/icons/amazon-s3.png')
st.image(image,width=60)
st.title("AWS S3")


def filter_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Adds a UI on top of a dataframe to let viewers filter columns

    Args:
        df (pd.DataFrame): Original dataframe

    Returns:
        pd.DataFrame: Filtered dataframe
    """
    modify = st.checkbox("Add filters",key="3")

    if not modify:
        return df

    df = df.copy()

    # Try to convert datetimes into a standard format (datetime, no timezone)
    for col in df.columns:
        if is_object_dtype(df[col]):
            try:
                df[col] = pd.to_datetime(df[col])
            except Exception:
                pass

        if is_datetime64_any_dtype(df[col]):
            df[col] = df[col].dt.tz_localize(None)

    modification_container = st.container()

    with modification_container:
        to_filter_columns = st.multiselect("Filter dataframe on", df.columns)
        for column in to_filter_columns:
            left, right = st.columns((1, 20))
            left.write("↳")
            # Treat columns with < 10 unique values as categorical
            if is_categorical_dtype(df[column]) or df[column].nunique() < 10:
                user_cat_input = right.multiselect(
                    f"Values for {column}",
                    df[column].unique(),
                    default=list(df[column].unique()),
                )
                df = df[df[column].isin(user_cat_input)]
            elif is_numeric_dtype(df[column]):
                _min = float(df[column].min())
                _max = float(df[column].max())
                step = (_max - _min) / 100
                user_num_input = right.slider(
                    f"Values for {column}",
                    _min,
                    _max,
                    (_min, _max),
                    step=step,
                )
                df = df[df[column].between(*user_num_input)]
            elif is_datetime64_any_dtype(df[column]):
                user_date_input = right.date_input(
                    f"Values for {column}",
                    value=(
                        df[column].min(),
                        df[column].max(),
                    ),
                )
                if len(user_date_input) == 2:
                    user_date_input = tuple(map(pd.to_datetime, user_date_input))
                    start_date, end_date = user_date_input
                    df = df.loc[df[column].between(start_date, end_date)]
            else:
                user_text_input = right.text_input(
                    f"Substring or regex in {column}",
                )
                if user_text_input:
                    df = df[df[column].str.contains(user_text_input)]

    return df


tab1, tab2, tab3 = st.tabs(["List buckets", "List objects & size", "Export instances"])

with tab1:
    
    buckets = AwsS3(aws_end_end_point)
    data = buckets.get_buckets()
    df = pd.DataFrame(data)

    #replace Header With First Row 
    df.columns = df.iloc[0] 
    df = df[1:]
    df.head()

    st.dataframe(filter_dataframe(df),width=1000, height=500)

with tab2:
  
    st.markdown ("""
    
    ### Interactivity
   
    Table displayed as interactive tables have the following interactive features:

    - Column sorting: sort columns by clicking on their headers.
    - Column resizing: resize columns by dragging and dropping column header borders.
    - Table (height, width) resizing: resize tables by dragging and dropping the bottom right corner of tables.
    - Search: search through data by clicking a table, using hotkeys (⌘ Cmd + F or Ctrl + F) to bring up the search bar, and using the search bar to filter data.
    
    """)

    buckets = AwsS3(aws_end_end_point)
    data = buckets.get_buckets()
    data.pop(0)

    buckets_size = []

    for a in data:
       bksize = buckets.get_number_of_objets_size(a[0])
       buckets_size.append(bksize)

    st.dataframe(buckets_size, width=1000, height=350)
    

with tab3:

    buckets = AwsS3(aws_end_end_point)
    data = buckets.get_buckets()
    data.pop(0)

    st.dataframe(data,width=1000, height=350)

    st.write ("Total to export: ", df.shape[0])

    option = st.selectbox(
    'Download format',
    ('HTML', 'CSV', 'JSON','MARKDOWN','PARQUET'))

    if option == "CSV":
        data= df.to_csv()
    elif option == "JSON":
        data= df.to_json()
    elif option == "MARKDOWN":
        data= df.to_markdown()
    elif option == "HTML":
        data= df.to_html()
    elif option == "PARQUET":
        data= df.to_parquet()     

    st.download_button("Download", data, key="2")
