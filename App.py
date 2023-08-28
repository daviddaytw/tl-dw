import streamlit as st
from streamlit_option_menu import option_menu
from PIL import Image

st.set_page_config(layout="wide")

# Import subpages.
import demo

with st.sidebar:
    selected = option_menu("tl;dw", ["Home", "Our mission", 'Demo'], 
        icons=['house', 'rocket', 'cast'], menu_icon="stopwatch", default_index=0)

if selected == 'Home':
    st.image(Image.open('./images/home.png'))

if selected == 'Our mission':
    st.image(Image.open('./images/mission.png'))

if selected == 'Demo':
    demo.render()
