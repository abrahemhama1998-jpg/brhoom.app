import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import qrcode
from io import BytesIO
import base64

st.set_page_config(page_title="الحل للتقنية V21", layout="wide")

# ================= DATABASE =================
conn = sqlite3.connect("tech_solution_v21.db", check_same_thread=False)
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS repairs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    phone TEXT,
    brand TEXT,
    model TEXT,
    issue TEXT,
    cost REAL,
    parts REAL,
    status TEXT,
    date TEXT
)
""")
conn.commit()

# ================= LOGIN SYSTEM =================
if "role" not in st.session_state:
    st.session_state.role = None

def login():
    st.title("🔐 تسجيل الدخول")
    user = st.text_input("اسم المستخدم")
    pwd = st.text_input("كلمة المرور", type="password")

    if st.button("دخول"):
        if user == "admin" and pwd == "1234":
            st.session_state.role = "admin"
        elif user == "staff" and pwd == "1111":
            st.session_state.role = "staff"
        else:
            st.error("بيانات خاطئة")

if st.session_state.role is None:
    login()
    st.stop()

# ================= MAIN UI =================
st.title("🛠️ الحل للتقنية - نظام الصيانة V21")

tabs = st.tabs(["➕ إضافة جهاز", "🔍 البحث والإدارة", "📊 المالية", "📈 الإحصائيات"])

# ================= ADD =================
with tabs[0]:
    with st.form("add"):
        col1, col2 = st.columns(2)
        name = col1.text_input("اسم الزبون")
        phone = col1.text_input("الهاتف")
        brand = col2.text_input("الماركة")
        model = col2.text_input("الموديل")
        issue = st.text_area("العطل")
        cost = st.number_input("السعر $", 0.0)
        parts = st.number_input("تكلفة القطع $", 0.0)

        if st.form_submit_button("حفظ"):
            c.execute("""
            INSERT INTO repairs 
            (name, phone, brand, model, issue, cost, parts, status, date)
            VALUES (?,?,?,?,?,?,?,?,?)
            """,(name, phone, brand, model, issue, cost, parts, "تحت الصيانة", datetime.now().strftime("%Y-%m-%d")))
            conn.commit()
            st.success("تم الحفظ بنجاح")

# ================= SEARCH =================
with tabs[1]:
    search = st.text_input("بحث (اسم / هاتف / ID)")
    df = pd.read_sql_query("SELECT * FROM repairs", conn)

    if search:
        df = df[
            df['name'].astype(str).str.contains(search, case=False) |
            df['phone'].astype(str).str.contains(search) |
            df['id'].astype(str).str.contains(search)
        ]

    for _, row in df.iterrows():
        with st.expander(f"{row['name']} - {row['model']} (#{row['id']})"):
            
            if st.session_state.role == "admin":
                new_status = st.selectbox("الحالة", ["تحت الصيانة","تم التسليم"], 
                    index=0 if row["status"]=="تحت الصيانة" else 1,
                    key=f"s{row['id']}")
                if st.button("تحديث", key=f"u{row['id']}"):
                    c.execute("UPDATE repairs SET status=? WHERE id=?",(new_status,row['id']))
                    conn.commit()
                    st.rerun()

            # QR Code
            qr = qrcode.make(f"Repair ID: {row['id']}")
            buffer = BytesIO()
            qr.save(buffer)
            img_str = base64.b64encode(buffer.getvalue()).decode()

            st.markdown(f"""
            <div style='border:1px solid black;padding:10px;text-align:center;'>
            <h3>الحل للتقنية</h3>
            <p>ID: {row['id']}</p>
            <p>{row['name']}</p>
            <p>{row['model']}</p>
            <p>السعر: {row['cost']} $</p>
            <img src="data:image/png;base64,{img_str}" width="120">
            </div>
            """, unsafe_allow_html=True)

# ================= FINANCE =================
with tabs[2]:
    df = pd.read_sql_query("SELECT * FROM repairs WHERE status='تم التسليم'", conn)

    total_income = df["cost"].sum()
    total_parts = df["parts"].sum()
    net = total_income - total_parts

    c1, c2, c3 = st.columns(3)
    c1.metric("الإيرادات", f"{total_income} $")
    c2.metric("تكلفة القطع", f"{total_parts} $")
    c3.metric("صافي الربح", f"{net} $")

# ================= STATS =================
with tabs[3]:
    df = pd.read_sql_query("SELECT * FROM repairs", conn)
    df['month'] = pd.to_datetime(df['date']).dt.to_period('M')
    monthly = df.groupby('month')['cost'].sum()

    st.bar_chart(monthly)
