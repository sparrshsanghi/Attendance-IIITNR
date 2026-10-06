import streamlit as st


def footer_home():
    logo_url = "Fighters.png"
    
    st.markdown(f""" 
        <div class="app-footer home-footer">
            <p>Crafted by Fighters</p>
            <img src='{logo_url}' style='max-height:23px;' />
        </div>
                """, unsafe_allow_html=True)

def footer_dashboard():
    logo_url = "Fighters.png"
    
    st.markdown(f""" 
        <div class="app-footer dash-footer">
            <p>Crafted by Fighters</p>
            <img src='{logo_url}' style='max-height:23px' />
        </div>
                """, unsafe_allow_html=True)