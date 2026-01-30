import streamlit as st
import pandas as pd
import os
from datetime import datetime
import plotly.express as px

# הגדרות קבצים - שמות פנימיים באנגלית למניעת שגיאות
DATA_FILE = "production_logs.csv"

# הגדרת המחלקות והמכונות
DEPARTMENTS = {
    "מחלקת הזרקה": ["מכונה 1", "מכונה 2", "מכונה 3", "מכונה 4"],
    "מחלקת ניפוח": ["מכונה א'", "מכונה ב'"],
    "מחלקת דפוס": ["מדפסת 1", "מדפסת 2", "מדפסת 3"],
    "מחלקת הרכבה": ["קו ידני 1", "קו אוטומטי"],
    "מחלקת אריזה": ["מכונת עטיפה", "משטח ידני"],
    "מחלקת צבע": ["תנור 1", "תנור 2"],
    "מחלקת אחזקה": ["עמדת תיקונים"]
}

# יצירת הקובץ אם לא קיים
if not os.path.exists(DATA_FILE):
    cols = ["time", "date", "dept", "machine", "product", "worker", "count"]
    df = pd.DataFrame(columns=cols)
    df.to_csv(DATA_FILE, index=False, encoding='utf-8-sig')

st.set_page_config(page_title="ניהול ייצור", layout="wide")

# עיצוב כפתור ענק לטאבלט
st.markdown("""
    <style>
    div.stButton > button:first-child {
        height: 150px;
        font-size: 40px !important;
        background-color: #28a745;
        color: white;
        border-radius: 20px;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

menu = st.sidebar.radio("תפריט:", ["📱 עמדת דיווח", "📊 דוחות (מנהל)"])

if menu == "📱 עמדת דיווח":
    st.header("דיווח משטח מוכן")
    
    col1, col2 = st.columns(2)
    with col1:
        d_select = st.selectbox("1. בחר מחלקה", list(DEPARTMENTS.keys()))
        w_name = st.text_input("2. שם העובד")
    with col2:
        m_select = st.selectbox("3. בחר מכונה", DEPARTMENTS[d_select])
        p_name = st.text_input("4. שם המוצר", value="כללי")

    st.divider()
    
    if st.button(f"✅ לחץ כאן: משטח מוכן ב{m_select}", use_container_width=True):
        if w_name and p_name:
            df = pd.read_csv(DATA_FILE)
            now = datetime.now()
            new_row = pd.DataFrame([{
                "time": now.strftime("%H:%M:%S"),
                "date": now.strftime("%Y-%m-%d"),
                "dept": d_select,
                "machine": m_select,
                "product": p_name,
                "worker": w_name,
                "count": 1
            }])
            df = pd.concat([df, new_row], ignore_index=True)
            df.to_csv(DATA_FILE, index=False, encoding='utf-8-sig')
            st.balloons()
            st.success(f"נרשם בהצלחה! מוצר: {p_name}")
        else:
            st.error("נא למלא שם עובד ומוצר")

else:
    st.header("📈 סיכום ייצור")
    df = pd.read_csv(DATA_FILE)
    
    if not df.empty:
        today_str = datetime.now().strftime("%Y-%m-%d")
        f_df = df[df["date"] == today_str]
        
        st.subheader(f"סה" + "כ משטחים היום: " + str(f_df["count"].sum()))
        
        # תצוגת נתונים בטבלה עם שמות בעברית
        view_df = f_df.rename(columns={
            "time": "שעה", "date": "תאריך", "dept": "מחלקה",
            "machine": "מכונה", "product": "מוצר", "worker": "עובד", "count": "כמות"
        })
        
        st.dataframe(view_df.sort_values("שעה", ascending=False), use_container_width=True)
        
        # כפתור הורדה
        csv = df.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')
        st.download_button("📥 הורד קובץ ל-Excel", data=csv, file_name="production.csv", mime="text/csv")
    else:
        st.info("אין נתונים להצגה")
