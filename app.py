import streamlit as st
import pandas as pd
import os
from datetime import datetime

# הגדרות קבצים
DATA_FILE = "production_summary.csv"

# הגדרת המחלקות והמכונות
DEPARTMENTS = {
    "מחלקת הזרקה": ["מכונה 1", "מכונה 2", "מכונה 3", "מכונה 4", "מכונה 5", "מכונה 6", "מכונה 7"],
    "מחלקת ניפוח": ["ניפוח 1", "ניפוח 2", "ניפוח 3", "ניפוח 4", "ניפוח 5", "ניפוח 6", "ניפוח 7"],
    "מחלקת דפוס": ["מדפסת 1", "מדפסת 2", "מדפסת 3", "מדפסת 4", "מדפסת 5", "מדפסת 6", "מדפסת 7"],
    "מחלקת הרכבה": ["הרכבה 1", "הרכבה 2", "הרכבה 3", "הרכבה 4", "הרכבה 5", "הרכבה 6", "הרכבה 7"],
    "מחלקת אריזה": ["אריזה 1", "אריזה 2", "אריזה 3", "אריזה 4", "אריזה 5", "אריזה 6", "אריזה 7"],
    "מחלקת צבע": ["צבע 1", "צבע 2", "צבע 3", "צבע 4", "צבע 5", "צבע 6", "צבע 7"],
    "מחלקת מחסן": ["מחסן 1", "מחסן 2", "מחסן 3", "מחסן 4", "מחסן 5", "מחסן 6", "מחסן 7"]
}

if not os.path.exists(DATA_FILE):
    df = pd.DataFrame(columns=["date", "dept", "machine", "count"])
    df.to_csv(DATA_FILE, index=False, encoding='utf-8-sig')

st.set_page_config(page_title="ניהול ייצור משטחים", layout="wide")

# עיצוב כפתורים גדולים
st.markdown("""
    <style>
    .stButton>button { width: 100%; height: 70px; font-size: 30px !important; font-weight: bold; }
    .plus-btn button { background-color: #28a745 !important; color: white !important; }
    .minus-btn button { background-color: #dc3545 !important; color: white !important; }
    .machine-label { font-size: 24px; font-weight: bold; padding-top: 20px; }
    .count-box { font-size: 32px; font-weight: bold; color: #007bff; text-align: center; background-color: #f0f2f6; border-radius: 10px; padding: 10px; }
    </style>
    """, unsafe_allow_html=True)

st.title("📊 בקרת ייצור משטחים")
selected_dept = st.selectbox("📌 בחר מחלקה:", list(DEPARTMENTS.keys()))

today = datetime.now().strftime("%Y-%m-%d")
st.write(f"### מחלקה: {selected_dept} | תאריך: {today}")

# טעינת נתונים
try:
    df = pd.read_csv(DATA_FILE)
except:
    df = pd.DataFrame(columns=["date", "dept", "machine", "count"])

def update_val(d_name, m_name, delta):
    global df
    mask = (df['date'] == today) & (df['dept'] == d_name) & (df['machine'] == m_name)
    if mask.any():
        df.loc[mask, 'count'] += delta
        if df.loc[mask, 'count'].values[0] < 0: df.loc[mask, 'count'] = 0
    else:
        new_row = pd.DataFrame([{"date": today, "dept": d_name, "machine": m_name, "count": max(0, delta)}])
        df = pd.concat([df, new_row], ignore_index=True)
    df.to_csv(DATA_FILE, index=False, encoding='utf-8-sig')

# הצגת המכונות
st.divider()
for m in DEPARTMENTS[selected_dept]:
    c1, c2, c3, c4 = st.columns([3, 2, 2, 2])
    with c1: st.markdown(f"<div class='machine-label'>{m}</div>", unsafe_allow_html=True)
    with c2:
        val = df[(df['date'] == today) & (df['dept'] == selected_dept) & (df['machine'] == m)]['count'].sum()
        st.markdown(f"<div class='count-box'>{int(val)}</div>", unsafe_allow_html=True)
    with c3:
        st.markdown('<div class="plus-btn">', unsafe_allow_html=True)
        if st.button("➕", key=f"p_{m}"):
            update_val(selected_dept, m, 1)
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    with c4:
        st.markdown('<div class="minus-btn">', unsafe_allow_html=True)
        if st.button("➖", key=f"m_{m}"):
            update_val(selected_dept, m, -1)
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    st.divider()

# כפתור הורדה
csv_data = df.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')
st.sidebar.download_button("📥 הורד קובץ אקסל", data=csv_data, file_name=f"report_{today}.csv")
