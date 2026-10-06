from src.database.config import supabase
import bcrypt
import streamlit as st

def hash_pass(pwd):
    return bcrypt.hashpw(pwd.encode(), bcrypt.gensalt()).decode()

def check_pass(pwd, hashed):
    try:
        return bcrypt.checkpw(pwd.encode(), hashed.encode())
    except Exception:
        return False

# ==========================================
# PK RESOLUTION HELPERS
# ==========================================

def get_teacher_pk(teacher_dict):
    if not teacher_dict:
        return None
    return teacher_dict.get('teacher_id') if 'teacher_id' in teacher_dict else teacher_dict.get('id')

def get_student_pk(student_dict):
    if not student_dict:
        return None
    return student_dict.get('student_id') if 'student_id' in student_dict else student_dict.get('id')

def get_subject_pk(subject_dict):
    if not subject_dict:
        return None
    return subject_dict.get('subject_id') if 'subject_id' in subject_dict else subject_dict.get('id')

def get_subject_name(subject_dict):
    if not subject_dict:
        return ""
    return subject_dict.get('name') or subject_dict.get('subject_name') or ""

def get_session_pk(session_dict):
    if not session_dict:
        return None
    return session_dict.get('session_id') if 'session_id' in session_dict else session_dict.get('id')

# ==========================================
# TEACHER OPERATIONS
# ==========================================

def check_teacher_exists(username):
    try:
        response = supabase.table("teachers").select("username").eq("username", username).execute()
        return len(response.data) > 0
    except Exception as e:
        st.error(f"Database error checking teacher existence: {e}")
        return False

def create_teacher(username, password, name):
    data = {"username": username, "password": hash_pass(password), "name": name}
    response = supabase.table("teachers").insert(data).execute()
    return response.data

def teacher_login(username, password):
    try:
        response = supabase.table("teachers").select("*").eq("username", username).execute()
        if response.data:
            teacher = response.data[0]
            if check_pass(password, teacher['password']):
                return teacher
    except Exception as e:
        st.error(f"Database error during teacher login: {e}")
    return None

# ==========================================
# STUDENT OPERATIONS
# ==========================================

def get_all_students():
    try:
        response = supabase.table('students').select("*").execute()
        return response.data or []
    except Exception as e:
        st.error(f"Database error fetching students: {e}")
        return []

def get_student_by_id(student_id):
    try:
        response = supabase.table('students').select("*").eq("student_id", student_id).execute()
        if response.data:
            return response.data[0]
        response = supabase.table('students').select("*").eq("id", student_id).execute()
        if response.data:
            return response.data[0]
    except Exception:
        pass
    return None

def create_student(new_name, face_embedding=None, voice_embedding=None):
    try:
        data = {'name': new_name, 'face_embedding': face_embedding, "voice_embedding": voice_embedding}
        response = supabase.table('students').insert(data).execute()
        return response.data
    except Exception as e:
        st.error(f"Database error creating student profile: {e}")
        return None

# ==========================================
# SUBJECT OPERATIONS
# ==========================================

def create_subject(teacher_id, subject_name, subject_code):
    try:
        # DB schema has 'name' column in DB
        data = {
            "teacher_id": teacher_id,
            "name": subject_name,
            "subject_code": subject_code
        }
        response = supabase.table("subjects").insert(data).execute()
        return response.data
    except Exception as e:
        try:
            data = {
                "teacher_id": teacher_id,
                "subject_name": subject_name,
                "subject_code": subject_code
            }
            response = supabase.table("subjects").insert(data).execute()
            return response.data
        except Exception as e2:
            st.error(f"Database error creating subject: {e2}")
            return None

def get_teacher_subjects(teacher_id, include_archived=False):
    try:
        query = supabase.table("subjects").select("*").eq("teacher_id", teacher_id)
        if not include_archived:
            try:
                query = query.eq("is_active", True)
            except Exception:
                pass
        response = query.execute()
        return response.data or []
    except Exception as e:
        st.error(f"Database error fetching teacher subjects: {e}")
        return []

def archive_subject(subject_id):
    try:
        try:
            response = supabase.table("subjects").update({"is_active": False}).eq("subject_id", subject_id).execute()
        except Exception:
            response = supabase.table("subjects").update({"is_active": False}).eq("id", subject_id).execute()
        return response.data
    except Exception as e:
        st.error(f"Database error archiving subject: {e}")
        return None

def update_subject(subject_id, subject_name, subject_code):
    try:
        try:
            response = supabase.table("subjects").update({
                "name": subject_name,
                "subject_code": subject_code
            }).eq("subject_id", subject_id).execute()
        except Exception:
            response = supabase.table("subjects").update({
                "subject_name": subject_name,
                "subject_code": subject_code
            }).eq("id", subject_id).execute()
        return response.data
    except Exception as e:
        st.error(f"Database error updating subject: {e}")
        return None

# ==========================================
# SUBJECT ROSTER / ENROLLMENT OPERATIONS
# ==========================================

def get_enrolled_students(subject_id):
    """Fetch student objects enrolled in a subject."""
    try:
        res = supabase.table("subject_students").select("student_id").eq("subject_id", subject_id).execute()
        if not res.data:
            return []
        
        enrolled_ids = [row["student_id"] for row in res.data]
        if not enrolled_ids:
            return []
            
        all_students = get_all_students()
        enrolled_students = [
            s for s in all_students
            if get_student_pk(s) in enrolled_ids
        ]
        return enrolled_students
    except Exception as e:
        st.error(f"Database error fetching subject roster: {e}")
        return []

def enroll_student_in_subject(subject_id, student_id):
    try:
        data = {"subject_id": subject_id, "student_id": student_id}
        response = supabase.table("subject_students").insert(data).execute()
        return response.data
    except Exception:
        # Ignore duplicate enrollment silently
        return None

def unenroll_student_from_subject(subject_id, student_id):
    try:
        response = supabase.table("subject_students").delete().eq("subject_id", subject_id).eq("student_id", student_id).execute()
        return response.data
    except Exception as e:
        st.error(f"Database error unenrolling student: {e}")
        return None

def set_subject_roster(subject_id, selected_student_ids):
    """Update full roster for a subject by inserting new and removing unselected."""
    try:
        existing_res = supabase.table("subject_students").select("student_id").eq("subject_id", subject_id).execute()
        existing_ids = set(row["student_id"] for row in (existing_res.data or []))
        new_ids = set(selected_student_ids)

        to_add = new_ids - existing_ids
        to_remove = existing_ids - new_ids

        for s_id in to_add:
            enroll_student_in_subject(subject_id, s_id)

        for s_id in to_remove:
            unenroll_student_from_subject(subject_id, s_id)

        return True
    except Exception as e:
        st.error(f"Database error setting subject roster: {e}")
        return False

# ==========================================
# ATTENDANCE SESSION & RECORDS OPERATIONS
# ==========================================

def create_attendance_session(subject_id, teacher_id, method="face"):
    try:
        data = {
            "subject_id": subject_id,
            "teacher_id": teacher_id,
            "method": method
        }
        response = supabase.table("attendance_sessions").insert(data).execute()
        if response.data:
            return response.data[0]
    except Exception as e:
        st.error(f"Database error creating attendance session: {e}")
    return None

def save_session_attendance(session_id, records_dict, method="face", confidence_map=None):
    """
    Save complete attendance records for a session.
    records_dict: dict of student_id -> status ('present' or 'absent')
    confidence_map: dict of student_id -> numeric score (optional)
    """
    if confidence_map is None:
        confidence_map = {}
        
    try:
        insert_rows = []
        for student_id, status in records_dict.items():
            conf = confidence_map.get(student_id)
            insert_rows.append({
                "session_id": session_id,
                "student_id": student_id,
                "status": status,
                "method": method,
                "confidence_score": conf
            })
            
        if insert_rows:
            response = supabase.table("attendance_records").insert(insert_rows).execute()
            return response.data
    except Exception as e:
        st.error(f"Database error saving attendance records: {e}")
        return None

def get_subject_sessions(subject_id):
    try:
        response = supabase.table("attendance_sessions").select("*").eq("subject_id", subject_id).execute()
        return response.data or []
    except Exception as e:
        st.error(f"Database error fetching subject sessions: {e}")
        return []

def get_session_records(session_id):
    try:
        response = supabase.table("attendance_records").select("*").eq("session_id", session_id).execute()
        return response.data or []
    except Exception as e:
        st.error(f"Database error fetching session records: {e}")
        return []

def get_attendance_session_by_id(session_id):
    try:
        res = supabase.table("attendance_sessions").select("*").eq("session_id", session_id).execute()
        if res.data:
            return res.data[0]

        res_alt = supabase.table("attendance_sessions").select("*").eq("id", session_id).execute()
        if res_alt.data:
            return res_alt.data[0]
    except Exception as e:
        st.error(f"Database error loading attendance session: {e}")
    return None

def is_student_enrolled_in_subject(subject_id, student_id):
    try:
        res = (
            supabase
            .table("subject_students")
            .select("id")
            .eq("subject_id", subject_id)
            .eq("student_id", student_id)
            .execute()
        )
        return bool(res.data)
    except Exception as e:
        st.error(f"Database error checking enrollment: {e}")
        return False

def mark_qr_attendance(session_id, student_id):
    """
    Mark a student present for a QR session.
    Returns tuple: (success: bool, message: str)
    """
    try:
        existing = (
            supabase
            .table("attendance_records")
            .select("record_id,status")
            .eq("session_id", session_id)
            .eq("student_id", student_id)
            .execute()
        )

        if existing.data:
            row = existing.data[0]
            if row.get("status") == "present":
                return True, "Attendance already marked as present."

            rec_id = row.get("record_id")
            if rec_id is not None:
                supabase.table("attendance_records").update({
                    "status": "present",
                    "method": "qr"
                }).eq("record_id", rec_id).execute()
            else:
                supabase.table("attendance_records").update({
                    "status": "present",
                    "method": "qr"
                }).eq("session_id", session_id).eq("student_id", student_id).execute()

            return True, "Attendance updated to present."

        supabase.table("attendance_records").insert({
            "session_id": session_id,
            "student_id": student_id,
            "status": "present",
            "method": "qr",
            "confidence_score": None
        }).execute()
        return True, "Attendance marked present."
    except Exception as e:
        return False, f"Failed to mark attendance: {e}"

def get_subject_attendance_summary(subject_id):
    """
    Calculate summary stats for each student enrolled in a subject.
    """
    enrolled_students = get_enrolled_students(subject_id)
    if not enrolled_students:
        return []

    sessions = get_subject_sessions(subject_id)
    total_sessions = len(sessions)

    if total_sessions == 0:
        return [
            {
                "student": s,
                "student_id": get_student_pk(s),
                "student_name": s.get("name", "Unknown"),
                "total_sessions": 0,
                "present_count": 0,
                "percentage": 0.0
            }
            for s in enrolled_students
        ]

    session_ids = [get_session_pk(sess) for sess in sessions]
    try:
        records_res = supabase.table("attendance_records").select("*").in_("session_id", session_ids).execute()
        all_records = records_res.data or []
    except Exception:
        all_records = []

    summary = []
    for student in enrolled_students:
        s_id = get_student_pk(student)
        student_records = [r for r in all_records if r.get("student_id") == s_id]
        present_count = sum(1 for r in student_records if r.get("status") == "present")
        pct = (present_count / total_sessions * 100.0) if total_sessions > 0 else 0.0

        summary.append({
            "student": student,
            "student_id": s_id,
            "student_name": student.get("name", "Unknown"),
            "total_sessions": total_sessions,
            "present_count": present_count,
            "percentage": round(pct, 1)
        })

    return summary

def get_student_attendance_summary(student_id):
    """
    Fetch subject-wise attendance breakdown for a student.
    """
    try:
        roster_res = supabase.table("subject_students").select("subject_id").eq("student_id", student_id).execute()
        if not roster_res.data:
            return [], 0.0

        subject_ids = [r["subject_id"] for r in roster_res.data]
        if not subject_ids:
            return [], 0.0

        all_subjects = []
        for sid in subject_ids:
            try:
                res = supabase.table("subjects").select("*").eq("subject_id", sid).execute()
                if res.data:
                    all_subjects.extend(res.data)
                else:
                    res2 = supabase.table("subjects").select("*").eq("id", sid).execute()
                    if res2.data:
                        all_subjects.extend(res2.data)
            except Exception:
                pass

        result = []
        tot_sessions_all = 0
        tot_present_all = 0

        for subj in all_subjects:
            s_id = get_subject_pk(subj)
            sessions = get_subject_sessions(s_id)
            total_sessions = len(sessions)
            
            if total_sessions > 0:
                s_ids = [get_session_pk(sess) for sess in sessions]
                recs = supabase.table("attendance_records").select("*").in_("session_id", s_ids).eq("student_id", student_id).execute()
                student_recs = recs.data or []
                present_count = sum(1 for r in student_recs if r.get("status") == "present")
            else:
                present_count = 0

            pct = (present_count / total_sessions * 100.0) if total_sessions > 0 else 0.0

            tot_sessions_all += total_sessions
            tot_present_all += present_count

            result.append({
                "subject_id": s_id,
                "subject_name": get_subject_name(subj),
                "subject_code": subj.get("subject_code"),
                "total_sessions": total_sessions,
                "present_count": present_count,
                "percentage": round(pct, 1)
            })

        overall_pct = (tot_present_all / tot_sessions_all * 100.0) if tot_sessions_all > 0 else 0.0
        return result, round(overall_pct, 1)
    except Exception as e:
        st.error(f"Database error calculating student summary: {e}")
        return [], 0.0