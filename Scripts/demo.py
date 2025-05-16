import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# st.write("First Page")

# df = pd.read_csv("C:/Users/VENKAT/Downloads/smart.csv")

# st.dataframe(df)

# l = [1,2,3,4,5,6,7,8]

# n= np.array(l)

# st.dataframe(n)

data = pd.DataFrame(
    np.random.randn(100,3),
    columns=['a','b','c']
)

st.line_chart(data)