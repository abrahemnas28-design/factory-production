import streamlit as st
import pandas as pd
import os
from datetime import datetime

# הגדרות קבצים
DATA_FILE = "production_summary.csv"

# רשימת המכונות שלך - כאן אתה יכול להוסיף את כל המכונות מהמפעל
MACHINES = [
    "מכונה 1", "מכונה 2", "מכונה 3", "מכונה 4", 
    "מכונה א'", "מכונה ב'", "מדפסת 1", "מדפסת 2",
    "קו אריזה", "מכבש", "תנור 1"
]

# יצירת קובץ נתונים אם לא קיים
if not os.path.exists(DATA_FILE):
    df = pd.DataFrame(columns=["date", "machine", "count"])
    df.to_csv(DATA_FILE, index=False, encoding='utf-8-sig')

st.set_page_config(page_title="לוח בקרה ייצור", layout="wide")

# עיצוב כפתורי פלוס ומינוס גדולים
st.markdown("""
    <style>
    .stButton>button {
        width: 100%;
        height: 60px;
        font-size: 25px !important;
        font-weight: bold;
    }
    .plus-btn button {
        background-color: #28a745 !important;
        color: white !important;
    }
    .minus-btn button {
        background-color: #dc3545 !important;
        color: white !important;
    }
    .machine-label {
        font-size: 24px;
        font-weight: bold;
        padding-top: 15px;
    }
    .count-display {
        font-size: 30px;
        font-weight: bold;
        color: #007bff;
        text-align: center;
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 5px;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("📊 בקרת ייצור משטחים")
today = datetime.now().strftime("%Y-%m-%d")
st.subheader(f"תאריך: {today}")

# טעינת נתונים
df = pd.read_csv(DATA_FILE)

# פונקציה לעדכון כמות
def update_count(machine_name, delta):
    global df
    # בדיקה אם יש כבר שורה למכונה הזו היום
    mask = (df['date'] == today) & (df['machine'] == machine_name)
    if mask.any():
        df.loc[mask, 'count'] += delta
        if df.loc[mask, 'count'].values[0] < 0:
            df.loc[mask, 'count'] = 0
    else:
        new_row = pd.DataFrame([{"date": today, "machine": machine_name, "count": max(0, delta)}])
        df = pd.concat([df, new_row], ignore_index=True)
    
    df.to_csv(DATA_FILE, index=False, encoding='utf-8-sig')

# הצגת שורות המכונות
st.divider()
for m in MACHINES:
    col_name, col_count, col_plus, col_minus = st.columns([3, 2, 2, 2])
    
    with col_name:
        st.markdown(f"<div class='machine-label'>{m}</div>", unsafe_allow_html=True)
    
    with col_count:
        current_count = df[(df['date'] == today) & (df['machine'] == m)]['count'].sum()
        st.markdown(f"<div class='count-display'>{int(current_count)}</div>", unsafe_allow_html=True)
    
    with col_plus:
        st.markdown('<div class="plus-btn">', unsafe_allow_html=True)
        if st.button(f"➕", key=f"plus_{m}"):
            update_count(m, 1)
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
        
    with col_minus:
        st.markdown('<div class="minus-btn">', unsafe_allow_html=True)
        if st.button(f"➖", key=f"minus_{m}"):
            update_count(m, -1)
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    st.divider()

# כפתור הורדה למנהל בסרגל הצידי
csv = df.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')
st.sidebar.download_button("📥 הורד נתונים ל-Excel", data=csv, file_name=f"production_{today}.csv")
