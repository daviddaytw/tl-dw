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
    st.video(open('./video.mp4', 'rb').read())
    st.write("""
        ## References
        - [Long Emergency Room Waits May Raise Risk of Death. UPI, UPI, 19 Jan. 2022](https://www.upi.com/Health_News/2022/01/19/emergency-room-delays-death-risk/9731642622635/)
        - [Infographic: Average Wait Times to See a Doctor.” RelyMD, 6 Aug. 2019](https://relymd.com/blog-infographic-average-wait-times-to-see-a-doctor/)
        - [Fernandez, Elizabeth. “Why Wait Times in the Emergency Room Are so Long in California | UC San Francisco.” www.ucsf.edu, 22 June 2023](https://www.ucsf.edu/news/2023/06/425661/why-wait-times-emergency-room-are-so-long-california)
        - [Blakemore, Erin. “Why Are Wait Times so Long in Emergency Rooms?” Washington Post, 30 May 2020](https://www.washingtonpost.com/health/why-are-wait-times-so-long-in-emergency-rooms/2020/05/29/405204b8-a056-11ea-81bb-c2f70f01034b_story.html)
        - [Mann, Denise. “U.S. Hospitals under Strain as ER Wait Times Lengthen.” US News, U.S. News & World Report L.P., 11 Oct. 2022](https://www.usnews.com/news/health-news/articles/2022-10-11/u-s-hospitals-under-strain-as-er-wait-times-lengthen.)
        - [News, A. B. C. “ER Wait Times Getting Longer.” ABC News](https://abcnews.go.com/Health/Healthday/story?id=4510063)
    """)

if selected == 'Demo':
    demo.render()
