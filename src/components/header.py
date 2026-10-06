import streamlit as st


def header_home():

    logo_url = "https://i.ibb.co/YTYGn5qV/logo.png"
    
    st.markdown(f""" 
        <div class="brand-home-wrap">
            <img src='{logo_url}' class='brand-home-logo' />
            <h1 class='brand-home-title'>IIIT<br/>ATTENDANCE</h1>
            <p class='brand-home-subtitle'>Smart attendance with face and voice intelligence</p>
        </div>
                """, unsafe_allow_html=True)


def header_dashboard():

    logo_url = "https://i.ibb.co/YTYGn5qV/logo.png"
    
    st.markdown(f""" 
        <div class="brand-dash-wrap">
           <img src='{logo_url}' class='brand-dash-logo' />
           <div>
             <h2 class='brand-dash-title'>IIIT<br/>ATTENDANCE</h2>
             <p class='brand-dash-subtitle'>Realtime AI Attendance Suite</p>
           </div>
        </div>
                """, unsafe_allow_html=True)