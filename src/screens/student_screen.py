import streamlit as st
import numpy as np
import time
from PIL import Image

from src.ui.base_layout import style_background_dashboard, style_base_layout
from src.components.header import header_dashboard
from src.components.footer import footer_dashboard
from src.pipelines.face_pipeline import predict_attendance, get_face_embeddings, train_classifier
from src.pipelines.voice_pipeline import get_voice_embedding
from src.database.db import (
    get_all_students,
    create_student,
    get_student_pk,
    get_student_attendance_summary,
    get_attendance_session_by_id,
    is_student_enrolled_in_subject,
    mark_qr_attendance
)
from src.pipelines.qr_pipeline import decode_qr_from_image_file, verify_qr_token

def student_screen():
    style_background_dashboard()
    style_base_layout()

    if "student_data" in st.session_state and st.session_state.get("is_logged_in"):
        student_dashboard()
        return

    c1, c2 = st.columns(2, vertical_alignment="center", gap="xxlarge")
    with c1:
        header_dashboard()
    with c2:
        if st.button("Go back to home", type="secondary", key="stud_login_back_btn"):
            st.session_state["login_type"] = None
            st.rerun()

    st.header("Student Portal — FaceID Login", text_alignment="center")

    show_registration = False
    photo_source = st.camera_input("Position your face in the center of the camera")

    if photo_source:
        img = np.array(Image.open(photo_source))

        with st.spinner("AI scanning FaceID..."):
            detected, all_sids, num_faces, details = predict_attendance(img)

            if num_faces == 0:
                st.warning("No face detected in camera image. Please position face clearly.")
            elif num_faces > 1:
                st.warning("Multiple faces detected! Please ensure only one person is in frame.")
            else:
                if detected:
                    student_id = list(detected.keys())[0]
                    all_students = get_all_students()
                    student = next((s for s in all_students if get_student_pk(s) == student_id), None)

                    if student:
                        st.session_state["is_logged_in"] = True
                        st.session_state["user_role"] = "student"
                        st.session_state["student_data"] = student
                        st.toast(f"Welcome Back, {student.get('name')}!", icon="👋")
                        time.sleep(1)
                        st.rerun()
                else:
                    st.info("Face not recognized! You might be a new student.")
                    show_registration = True

    if show_registration and photo_source:
        with st.container(border=True):
            st.header("Register New Student Profile")
            new_name = st.text_input("Enter your full name", placeholder="e.g. Sparsh Sanghi")

            st.subheader("Optional: Voice Enrollment")
            st.info("Record a short phrase (min 0.5s) to enable voice-based attendance.")

            audio_data = None
            try:
                audio_data = st.audio_input("Record phrase: 'I am present'")
            except Exception:
                st.error("Audio recording widget unavailable.")

            if st.button("Create Student Profile", type="primary"):
                if new_name:
                    with st.spinner("Creating your AI profile..."):
                        img = np.array(Image.open(photo_source))
                        encodings = get_face_embeddings(img)
                        if encodings:
                            face_emb = encodings[0].tolist()

                            voice_emb = None
                            if audio_data:
                                voice_emb = get_voice_embedding(audio_data.read())

                            response_data = create_student(new_name, face_embedding=face_emb, voice_embedding=voice_emb)

                            if response_data:
                                train_classifier()
                                new_student = response_data[0] if isinstance(response_data, list) else response_data
                                st.session_state["is_logged_in"] = True
                                st.session_state["user_role"] = "student"
                                st.session_state["student_data"] = new_student
                                st.toast(f"Profile Created! Welcome {new_name}!", icon="🎉")
                                time.sleep(1)
                                st.rerun()
                            else:
                                st.error("Failed to insert student profile into database.")
                        else:
                            st.error("Could not extract facial features from camera image.")
                else:
                    st.warning("Please enter your name to register.")

    footer_dashboard()

def student_dashboard():
    student_data = st.session_state["student_data"]
    student_id = get_student_pk(student_data)
    student_name = student_data.get("name", "Student")

    c1, c2 = st.columns(2, vertical_alignment="center", gap="xxlarge")
    with c1:
        header_dashboard()
    with c2:
        st.subheader(f"Welcome, {student_name}")
        if st.button("LogOut", type="secondary", key="stud_logout_btn"):
            st.session_state.pop("student_data", None)
            st.session_state["is_logged_in"] = False
            st.session_state["login_type"] = None
            st.rerun()

    st.markdown("<br/>", unsafe_allow_html=True)

    # Fetch attendance breakdown for student
    subjects_summary, overall_pct = get_student_attendance_summary(student_id)

    # Overview cards / badges
    b1, b2 = st.columns([1, 1])
    with b1:
        with st.container(border=True):
            st.write("**Student ID**")
            st.subheader(f"#{student_id}")

    with b2:
        with st.container(border=True):
            st.write("**Overall Attendance**")
            color = "green" if overall_pct >= 75.0 else "orange" if overall_pct >= 60.0 else "red"
            st.subheader(f"{overall_pct}%")

    st.divider()

    st.subheader("QR Quick Check-in")
    st.caption("Scan your teacher QR to mark attendance for a live class session.")
    qr_capture = st.camera_input("Scan Attendance QR", key="student_qr_scan")

    if qr_capture and st.button("Process QR Check-in", type="primary", key="student_qr_submit"):
        raw_token = decode_qr_from_image_file(qr_capture)
        if not raw_token:
            st.warning("Could not decode QR. Try better lighting and hold camera steady.")
        else:
            ok, msg, payload = verify_qr_token(raw_token)
            if not ok:
                st.error(msg)
            else:
                session_id = payload.get("session_id")
                subject_id = payload.get("subject_id")

                session = get_attendance_session_by_id(session_id)
                if not session:
                    st.error("QR session does not exist.")
                elif session.get("subject_id") != subject_id:
                    st.error("Session data mismatch. Please ask your teacher to regenerate QR.")
                else:
                    is_enrolled = is_student_enrolled_in_subject(subject_id, student_id)
                    if not is_enrolled:
                        st.error("You are not enrolled in this subject.")
                    else:
                        success, mark_msg = mark_qr_attendance(session_id, student_id)
                        if success:
                            st.success(mark_msg)
                            st.toast("QR attendance completed.", icon="✅")
                        else:
                            st.error(mark_msg)

    st.subheader("📚 Subject-wise Attendance Breakdown")

    if not subjects_summary:
        st.info("You are currently not enrolled in any subjects, or no attendance sessions have been conducted yet.")
    else:
        table_data = []
        for s in subjects_summary:
            table_data.append({
                "Subject Code": s["subject_code"],
                "Subject Name": s["subject_name"],
                "Sessions Attended": f"{s['present_count']} / {s['total_sessions']}",
                "Attendance %": f"{s['percentage']}%"
            })
        st.dataframe(table_data, use_container_width=True)

    footer_dashboard()