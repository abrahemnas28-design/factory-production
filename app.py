import streamlit as st
import pandas as pd
import os
from datetime import datetime
import plotly.express as px

# הגדרות קבצים
DATA_FILE = "factory_production_master.csv"

# הגדרת 7 המחלקות והמכונות שלך - שנה כאן את השמות לשמות האמיתיים
DEPARTMENTS = {
    "מחלקת הזרקה": ["מכונה 1", "מכונה 2", "מכונה 3", "מכונה 4"],
    "מחלקת ניפוח": ["מכונה א'", "מכונה ב'"],
    "מחלקת דפוס": ["מדפסת 1", "מדפסת 2", "מדפסת 3"],
    "מחלקת הרכבה": ["קו ידני 1", "קו אוטומטי"],
    "מחלקת אריזה": ["מכונת עטיפה", "משטח ידני"],
    "מחלקת צבע": ["תנור 1", "תנור 2"],
    "מחלקת אחזקה": ["עמדת תיקונים"]
}

if not os.path.exists(DATA_FILE):
    df = pd.DataFrame(columns=["זמן", "תאריך", "מחלקה", "מכונה", "מוצר", "עובד", "משטחים"])
    df.to_csv(DATA_FILE, index=False, encoding='utf-8-sig')

st.set_page_config(page_title="ניהול ייצור - טאבלט", layout="wide")

# עיצוב כפתורים גדולים לטאבלט
st.markdown("""
    <style>
    div.stButton > button:first-child {
        height: 100px;
        font-size: 30px;
        background-color: #28a745;
        color: white;
        border-radius: 15px;
    }
    </style>
    """, unsafe_allow_html=True)

menu = st.sidebar.radio("תפריט:", ["📱 עמדת דיווח (טאבלט)", "📈 דוחות וסיכומים"])

if menu == "📱 עמדת דיווח (טאבלט)":
    st.header("דיווח יציאת משטח")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        dept = st.selectbox("1. בחר מחלקה", list(DEPARTMENTS.keys()))
        worker = st.text_input("2. שם העובד")
        
    with col2:
        machine = st.selectbox("3. בחר מכונה", DEPARTMENTS[dept])
        
    with col3:
        product = st.text_input("4. מוצר נוכחי", value="כללי", help="שנה את שם המוצר כאן כשהמכונה עוברת מוצר")

    st.divider()
    
    # הצגת המצב הנוכחי בגדול
    st.subheader(f"מכונה: {machine} | מוצר: {product}")
    
    if st.button(f"📤 משטח מוכן - לחץ כאן", use_container_width=True):
        if worker and product:
            df = pd.read_csv(DATA_FILE)
            now = datetime.now()
            new_row = pd.DataFrame([{
                "זמן": now.strftime("%H:%M:%S"),
                "תאריך": now.strftime("%Y-%m-%d"),
                "מחלקה": dept,
                "מכונה": machine,
                "מוצר": product,
                "עובד": worker,
                "משטחים": 1
            }])
            df = pd.concat([df, new_row], ignore_index=True)
            df.to_csv(DATA_FILE, index=False, encoding='utf-8-sig')
            st.success(f"משטח מס' {len(df[df['תאריך']==now.strftime('%Y-%m-%d')])} נרשם בהצלחה!")
            st.balloons()
        else:
            st.error("חובה להזין שם עובד ומוצר")

else:
    st.header("📈 סיכום ייצור יומי")
    df = pd.read_csv(DATA_FILE)
    
    if not df.empty:
        today = st.date_input("בחר תאריך לבדיקה", value=datetime.now())
        today_str = today.strftime("%Y-%m-%d")
        
        f_df = df[df["תאריך"] == today_str]
        
        if not f_df.empty:
            # סיכום לפי מוצר ומכונה
            prod_summary = f_df.groupby(["מחלקה", "מכונה", "מוצר"])["משטחים"].sum().reset_index()
            
            st.write(f"### סה"כ משטחים היום: {f_df['משטחים'].sum()}")
            
            # גרף הספק לפי מכונה ומוצר
            fig = px.bar(prod_summary, x="מכונה", y="משטחים", color="מוצר", 
                         title="התפלגות ייצור לפי מכונה ומוצר", barmode="stack")
            st.plotly_chart(fig, use_container_width=True)
            
            # כפתור הורדה ל-CSV (שאפשר לפתוח ב-Sheets)
            csv = df.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')
            st.download_button(
                label="📥 הורד קובץ ל-Excel / Google Sheets",
                data=csv,
                file_name=f"production_{today_str}.csv",
                mime="text/csv",
            )
            
            st.dataframe(f_df.sort_values("זמן", ascending=False), use_container_width=True)
        else:
            st.warning("אין נתונים ליום זה")
    else:
        st.info("ממתין לדיווחים...")
