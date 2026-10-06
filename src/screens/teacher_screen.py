import streamlit as st
import numpy as np
from PIL import Image

from src.ui.base_layout import style_background_dashboard, style_base_layout
from src.components.header import header_dashboard
from src.components.footer import footer_dashboard
from src.database.db import (
    check_teacher_exists,
    create_teacher,
    teacher_login,
    get_teacher_pk,
    get_student_pk,
    get_subject_pk,
    get_subject_name,
    get_session_pk,
    create_subject,
    get_teacher_subjects,
    archive_subject,
    get_all_students,
    get_enrolled_students,
    set_subject_roster,
    get_subject_attendance_summary,
    get_subject_sessions,
    get_session_records,
    create_attendance_session,
    get_session_pk
)
from src.pipelines.face_pipeline import predict_attendance
from src.pipelines.voice_pipeline import process_bulk_audio
from src.services.attendance_service import (
    prepare_session_review,
    finalize_and_save_session
)
from src.pipelines.qr_pipeline import create_qr_token, qr_token_to_png_bytes

# =========================================================
# TEACHER SCREEN ENTRY POINT
# =========================================================

def teacher_screen():
    style_background_dashboard()
    style_base_layout()

    if "teacher_data" in st.session_state and st.session_state.get("is_logged_in"):
        teacher_dashboard()
    elif (
        "teacher_login_type" not in st.session_state
        or st.session_state.get("teacher_login_type") == "login"
    ):
        teacher_screen_login()
    elif st.session_state.get("teacher_login_type") == "register":
        teacher_screen_register()

# =========================================================
# TEACHER DASHBOARD
# =========================================================

def teacher_dashboard():
    if "current_teacher_tab" not in st.session_state:
        st.session_state["current_teacher_tab"] = "manage_subjects"

    teacher_data = st.session_state["teacher_data"]
    teacher_id = get_teacher_pk(teacher_data)

    c1, c2 = st.columns(2, vertical_alignment="center", gap="xxlarge")
    with c1:
        header_dashboard()
    with c2:
        st.subheader(f"Welcome, Prof. {teacher_data.get('name', 'Teacher')}")
        if st.button("LogOut", type="secondary", key="teacher_logout_btn"):
            st.session_state.pop("teacher_data", None)
            st.session_state["is_logged_in"] = False
            st.session_state["current_teacher_tab"] = "manage_subjects"
            st.session_state["login_type"] = None
            st.rerun()

    st.markdown("<br/>", unsafe_allow_html=True)

    # Tabs selection
    tab1, tab2, tab3 = st.columns([1, 1, 1])

    with tab1:
        b_type = "primary" if st.session_state["current_teacher_tab"] == "take_attendance" else "tertiary"
        if st.button("Take Attendance", type=b_type, key="take_attendance_tab_btn"):
            st.session_state["current_teacher_tab"] = "take_attendance"
            st.rerun()

    with tab2:
        b_type = "primary" if st.session_state["current_teacher_tab"] == "manage_subjects" else "tertiary"
        if st.button("Manage Subjects", type=b_type, key="manage_subjects_tab_btn"):
            st.session_state["current_teacher_tab"] = "manage_subjects"
            st.rerun()

    with tab3:
        b_type = "primary" if st.session_state["current_teacher_tab"] == "attendance_records" else "tertiary"
        if st.button("Attendance Records", type=b_type, key="attendance_records_tab_btn"):
            st.session_state["current_teacher_tab"] = "attendance_records"
            st.rerun()

    st.divider()

    current_tab = st.session_state["current_teacher_tab"]

    if current_tab == "take_attendance":
        teacher_tab_take_attendance(teacher_id)
    elif current_tab == "manage_subjects":
        teacher_tab_manage_subjects(teacher_id)
    elif current_tab == "attendance_records":
        teacher_tab_attendance_records(teacher_id)
    else:
        teacher_tab_manage_subjects(teacher_id)

    footer_dashboard()

# =========================================================
# MANAGE SUBJECTS TAB
# =========================================================

def teacher_tab_manage_subjects(teacher_id):
    st.header("Manage Subjects & Student Rosters")

    col_create, col_list = st.columns([1, 1], gap="large")

    with col_create:
        with st.container(border=True):
            st.subheader("➕ Create New Subject")
            s_name = st.text_input("Subject Name", placeholder="e.g. Operating Systems", key="new_subj_name")
            s_code = st.text_input("Subject Code", placeholder="e.g. CS301", key="new_subj_code")

            if st.button("Save Subject", type="primary", key="save_subj_btn"):
                if s_name and s_code:
                    res = create_subject(teacher_id, s_name, s_code)
                    if res:
                        st.toast(f"Subject '{s_name}' created successfully!", icon="✅")
                        st.rerun()
                    else:
                        st.error("Failed to create subject.")
                else:
                    st.warning("Please fill in both Subject Name and Code.")

    with col_list:
        st.subheader("📚 Your Active Subjects")
        active_subjects = get_teacher_subjects(teacher_id, include_archived=False)

        if not active_subjects:
            st.info("No active subjects found. Create your first subject on the left!")
        else:
            for subj in active_subjects:
                s_id = get_subject_pk(subj)
                s_title = get_subject_name(subj)
                with st.expander(f"📖 {s_title} ({subj.get('subject_code', '')})", expanded=True):
                    # Show enrolled students count
                    enrolled = get_enrolled_students(s_id)
                    st.write(f"**Enrolled Students:** {len(enrolled)}")

                    c_arch, c_edit = st.columns(2)
                    with c_arch:
                        if st.button("Archive Subject", key=f"arch_btn_{s_id}", type="secondary"):
                            archive_subject(s_id)
                            st.toast(f"Archived {s_title}", icon="📦")
                            st.rerun()

                    # Roster Editor
                    st.markdown("---")
                    st.write("**Manage Roster:**")
                    all_students = get_all_students()
                    if not all_students:
                        st.warning("No students registered in the system yet.")
                    else:
                        student_options = {get_student_pk(s): f"{s.get('name')} (ID: {get_student_pk(s)})" for s in all_students}
                        enrolled_ids = [get_student_pk(s) for s in enrolled]

                        selected_ids = st.multiselect(
                            "Select Enrolled Students",
                            options=list(student_options.keys()),
                            default=enrolled_ids,
                            format_func=lambda sid: student_options[sid],
                            key=f"roster_select_{s_id}"
                        )

                        if st.button("Update Roster", key=f"update_roster_{s_id}", type="primary"):
                            if set_subject_roster(s_id, selected_ids):
                                st.toast("Subject roster updated!", icon="🎉")
                                st.rerun()

# =========================================================
# TAKE ATTENDANCE TAB
# =========================================================

def teacher_tab_take_attendance(teacher_id):
    st.header("Take AI Class Attendance")

    active_subjects = get_teacher_subjects(teacher_id, include_archived=False)
    if not active_subjects:
        st.warning("You have no active subjects. Please go to 'Manage Subjects' to create a subject first!")
        return

    subj_options = {get_subject_pk(s): f"{get_subject_name(s)} ({s.get('subject_code', '')})" for s in active_subjects}
    selected_subj_id = st.selectbox(
        "Select Subject",
        options=list(subj_options.keys()),
        format_func=lambda sid: subj_options[sid],
        key="take_att_subj_select"
    )

    enrolled = get_enrolled_students(selected_subj_id)
    if not enrolled:
        st.warning("No students enrolled in this subject yet! Please enroll students in 'Manage Subjects'.")
        return

    st.info(f"Enrolled Students in Subject: **{len(enrolled)}**")

    method = st.radio("Choose Identification Method", ["Face", "Voice", "Hybrid", "QR"], horizontal=True, key="att_method_radio")

    # Session state for scanning result review
    if "review_state" not in st.session_state or st.session_state.get("review_subj_id") != selected_subj_id:
        st.session_state["review_state"] = None
        st.session_state["review_subj_id"] = selected_subj_id

    detected_ids = []
    confidence_details = {}

    if method == "Face":
        photo_source = st.file_uploader("Upload Classroom Image", type=["jpg", "jpeg", "png"], key="class_photo_upload")
        cam_source = st.camera_input("Or Capture Classroom Photo", key="class_cam_input")
        image_input = cam_source or photo_source

        if image_input:
            img = np.array(Image.open(image_input))
            if st.button("Run Face Recognition", type="primary", key="run_face_btn"):
                with st.spinner("AI scanning faces in image..."):
                    det_dict, all_sids, num_faces, details = predict_attendance(img)
                    detected_ids = list(det_dict.keys())
                    confidence_details = details

                    rev = prepare_session_review(selected_subj_id, detected_ids, confidence_details)
                    rev["num_faces_detected"] = num_faces
                    st.session_state["review_state"] = rev
                    st.toast(f"Scanned {num_faces} faces in image.", icon="🔍")

    elif method == "Voice":
        audio_file = st.file_uploader("Upload Classroom Voice Recording", type=["wav", "mp3", "ogg"], key="class_voice_upload")
        if audio_file:
            if st.button("Run Voice Recognition", type="primary", key="run_voice_btn"):
                with st.spinner("AI analyzing voice audio..."):
                    candidates_dict = {get_student_pk(s): s.get("voice_embedding") for s in enrolled if s.get("voice_embedding")}
                    results = process_bulk_audio(audio_file.read(), candidates_dict)
                    detected_ids = list(results.keys())
                    confidence_details = {sid: {"score": round(score, 3), "confidence_label": "High Confidence" if score >= 0.75 else "Medium Confidence"} for sid, score in results.items()}

                    st.session_state["review_state"] = prepare_session_review(selected_subj_id, detected_ids, confidence_details)
                    st.toast("Voice processing complete!", icon="🎤")

    elif method == "Hybrid":
        st.write("Manual / Hybrid Selection Mode")
        if st.button("Start Manual Roster Verification", type="primary", key="start_manual_btn"):
            st.session_state["review_state"] = prepare_session_review(selected_subj_id, [], {})

    elif method == "QR":
        st.info("Generate a time-limited QR code. Students scan it from their portal to self check-in.")
        ttl_minutes = st.slider("QR validity (minutes)", min_value=1, max_value=15, value=5, step=1, key="qr_ttl_mins")

        if st.button("Generate New QR Session", type="primary", key="gen_qr_session_btn"):
            new_session = create_attendance_session(selected_subj_id, teacher_id, method="qr")
            if not new_session:
                st.error("Could not create attendance session for QR.")
            else:
                session_id = get_session_pk(new_session)
                token = create_qr_token(
                    subject_id=selected_subj_id,
                    teacher_id=teacher_id,
                    session_id=session_id,
                    ttl_seconds=ttl_minutes * 60
                )
                st.session_state["active_qr_session"] = {
                    "subject_id": selected_subj_id,
                    "session_id": session_id,
                    "token": token
                }
                st.toast("New QR session created.", icon="🧾")

        active_qr = st.session_state.get("active_qr_session")
        if active_qr and active_qr.get("subject_id") == selected_subj_id:
            png = qr_token_to_png_bytes(active_qr.get("token"))
            st.image(png, caption=f"Session #{active_qr.get('session_id')} QR", width=280)
            st.caption("Students should scan this QR from their Student Dashboard.")

    # Review & Finalize Section
    review_state = st.session_state.get("review_state")
    if review_state:
        st.divider()
        st.subheader("📋 Review Detected Students & Finalize Attendance")

        if "num_faces_detected" in review_state:
            st.write(f"**Total Faces Detected by AI:** {review_state['num_faces_detected']}")

        c_det, c_unrec = st.columns(2)
        with c_det:
            st.markdown("##### AI Identified Enrolled Students")
            if not review_state["detected_enrolled_ids"]:
                st.write("No enrolled students matched with high confidence.")
            else:
                for sid in review_state["detected_enrolled_ids"]:
                    s_obj = review_state["enrolled_map"].get(sid)
                    conf_info = review_state["confidence_details"].get(sid, {})
                    label = conf_info.get("confidence_label", "Detected")
                    score = conf_info.get("score")
                    score_str = f"(Match score: {score})" if score is not None else ""
                    st.success(f"✓ **{s_obj.get('name')}** — {label} {score_str}")

        with c_unrec:
            st.markdown("##### Manual Status Verification (All Enrolled Students)")
            st.write("Review and adjust final status for EVERY enrolled student:")

        # Form for final attendance adjustments
        with st.form("finalize_attendance_form"):
            final_status_map = {}
            for s in review_state["enrolled_students"]:
                s_id = get_student_pk(s)
                default_val = review_state["default_status_map"].get(s_id, "absent")
                is_present = default_val == "present"

                st_val = st.checkbox(
                    f"{s.get('name')} (ID: {s_id})",
                    value=is_present,
                    key=f"att_chk_{s_id}"
                )
                final_status_map[s_id] = "present" if st_val else "absent"

            submit_final = st.form_submit_button("✅ Finalize & Save Attendance Session", type="primary")
            if submit_final:
                success, msg = finalize_and_save_session(
                    subject_id=selected_subj_id,
                    teacher_id=teacher_id,
                    method=method.lower(),
                    final_status_map=final_status_map,
                    confidence_details=review_state["confidence_details"]
                )

                if success:
                    st.success("Attendance session recorded successfully for all enrolled students!")
                    st.session_state["review_state"] = None
                    st.toast("Saved session records!", icon="💾")
                else:
                    st.error(f"Error saving session: {msg}")

# =========================================================
# ATTENDANCE RECORDS TAB
# =========================================================

def teacher_tab_attendance_records(teacher_id):
    st.header("Attendance Records & Analytics")

    subjects = get_teacher_subjects(teacher_id, include_archived=True)
    if not subjects:
        st.info("No subjects created yet.")
        return

    subj_options = {get_subject_pk(s): f"{get_subject_name(s)} ({s.get('subject_code', '')}) {'[Archived]' if not s.get('is_active', True) else ''}" for s in subjects}
    selected_subj_id = st.selectbox(
        "Select Subject to View Records",
        options=list(subj_options.keys()),
        format_func=lambda sid: subj_options[sid],
        key="records_subj_select"
    )

    summary = get_subject_attendance_summary(selected_subj_id)
    sessions = get_subject_sessions(selected_subj_id)

    st.write(f"**Total Sessions Conducted:** {len(sessions)}")

    if not summary:
        st.info("No enrolled students or records found for this subject.")
        return

    # Render summary table
    st.subheader("📊 Student Attendance Summary")
    summary_data = []
    for item in summary:
        summary_data.append({
            "Student ID": item["student_id"],
            "Student Name": item["student_name"],
            "Present Count": item["present_count"],
            "Total Sessions": item["total_sessions"],
            "Attendance %": f"{item['percentage']}%"
        })

    st.dataframe(summary_data, use_container_width=True)

    # Detailed session logs
    if sessions:
        st.divider()
        st.subheader("📅 Past Attendance Sessions Log")
        session_dates = {get_session_pk(sess): f"Session #{get_session_pk(sess)} — {sess.get('session_date', '')} ({sess.get('method', 'face').upper()})" for sess in sessions}

        selected_sess_id = st.selectbox(
            "Select Session Details",
            options=list(session_dates.keys()),
            format_func=lambda sid: session_dates[sid],
            key="sess_log_select"
        )

        records = get_session_records(selected_sess_id)
        if records:
            rec_data = []
            for r in records:
                s_obj = next((s["student"] for s in summary if s["student_id"] == r.get("student_id")), None)
                s_name = s_obj.get("name") if s_obj else f"Student #{r.get('student_id')}"
                rec_data.append({
                    "Student ID": r.get("student_id"),
                    "Student Name": s_name,
                    "Status": r.get("status", "").upper(),
                    "Method": r.get("method", "").upper(),
                    "Score": r.get("confidence_score", "N/A"),
                    "Time": r.get("marked_at", "")
                })
            st.dataframe(rec_data, use_container_width=True)

# =========================================================
# TEACHER AUTH SCREENS (LOGIN / REGISTER)
# =========================================================

def teacher_screen_login():
    c1, c2 = st.columns(2, vertical_alignment="center", gap="xxlarge")
    with c1:
        header_dashboard()
    with c2:
        if st.button("Go back to home", type="secondary", key="teacher_login_back_btn"):
            st.session_state["login_type"] = None
            st.rerun()

    st.header("Teacher Login", text_alignment="center")

    username = st.text_input("Username", key="t_user_login_inp")
    password = st.text_input("Password", type="password", key="t_pass_login_inp")

    st.divider()
    btn1, btn2 = st.columns(2)
    with btn1:
        if st.button("Login", type="primary", width="stretch", key="t_login_btn"):
            teacher = teacher_login(username, password)
            if teacher:
                st.session_state["user_role"] = "teacher"
                st.session_state["teacher_data"] = teacher
                st.session_state["is_logged_in"] = True
                st.session_state["current_teacher_tab"] = "manage_subjects"
                st.toast("Welcome back!", icon="👋")
                st.rerun()
            else:
                st.error("Invalid username or password.")
    with btn2:
        if st.button("Register Instead", type="secondary", width="stretch", key="t_reg_instead_btn"):
            st.session_state["teacher_login_type"] = "register"
            st.rerun()

    footer_dashboard()

def teacher_screen_register():
    c1, c2 = st.columns(2, vertical_alignment="center", gap="xxlarge")
    with c1:
        header_dashboard()
    with c2:
        if st.button("Go back to home", type="secondary", key="teacher_reg_back_btn"):
            st.session_state["teacher_login_type"] = "login"
            st.rerun()

    st.header("Register Teacher Profile")

    username = st.text_input("Choose Username", key="t_reg_user_inp")
    name = st.text_input("Full Name", key="t_reg_name_inp")
    password = st.text_input("Password", type="password", key="t_reg_pass_inp")
    confirm_pass = st.text_input("Confirm Password", type="password", key="t_reg_conf_inp")

    st.divider()
    btn1, btn2 = st.columns(2)
    with btn1:
        if st.button("Create Account", type="primary", width="stretch", key="t_create_acc_btn"):
            if not username or not name or not password:
                st.warning("All fields are required.")
            elif check_teacher_exists(username):
                st.error("Username already taken.")
            elif password != confirm_pass:
                st.error("Passwords do not match.")
            else:
                create_teacher(username, password, name)
                st.success("Account created successfully! Please login.")
                st.session_state["teacher_login_type"] = "login"
                st.rerun()
    with btn2:
        if st.button("Login Instead", type="secondary", width="stretch", key="t_login_instead_btn"):
            st.session_state["teacher_login_type"] = "login"
            st.rerun()

    footer_dashboard()