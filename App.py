import streamlit as st
from streamlit_option_menu import option_menu
from PIL import Image

# Set page to wide layout.
st.set_page_config(page_title="tl;dw", layout="wide")

# Import subpages.
import demo

with st.sidebar:
    selected = option_menu("tl;dw", ["Home", "Demo"], 
        icons=['rocket', 'cast'], menu_icon="stopwatch", default_index=0)

# The following is the page router.

if selected == 'Home':
    st.image(Image.open('./images/home.png'))

if selected == 'Demo':
    demo.render()
