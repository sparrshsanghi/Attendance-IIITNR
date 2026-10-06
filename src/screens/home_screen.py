import streamlit as st
from src.components.header import header_home
from src.components.footer import footer_home
from src.ui.base_layout import style_base_layout,style_background_home
def home_screen():
    
    
     

    header_home()
    style_background_home()
    style_base_layout()


    col1,col2 = st.columns(2, gap='large')

    with col1:
        st.markdown("""
        <div class="portal-card">
           <h3>Student Portal</h3>
           <p class="portal-note">Quick FaceID access, live attendance status, and your subject-level analytics.</p>
        </div>
        """, unsafe_allow_html=True)
        st.image("https://i.ibb.co/844D9Lrt/mascot-student.png",width=120)
        if  st.button('Student Portal',type='primary',icon=':material/arrow_outward:',icon_position='right'):
            st.session_state['login_type']='student'
            st.rerun()
     
    with col2:
        st.markdown("""
        <div class="portal-card">
           <h3>Teacher Portal</h3>
           <p class="portal-note">Create subjects, run AI attendance sessions, and review complete records confidently.</p>
        </div>
        """, unsafe_allow_html=True)
        st.image("https://i.ibb.co/CsmQQV6X/mascot-prof.png",width=145)
        if  st.button('Teacher Portal',type='primary',icon=':material/arrow_outward:',icon_position='right'):
            st.session_state['login_type'] = 'teacher'
            st.rerun()

    footer_home()