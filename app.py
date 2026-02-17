import streamlit as st
import pandas as pd
import os
from datetime import datetime

# --- إعدادات الصفحة ---
st.set_page_config(page_title="الحل للتقنية", layout="wide")

# CSS المطور لفصل الصفحات
st.markdown("""
    <style>
    @media print {
        header, footer, .stTabs, button, .no-print, [data-testid="stHeader"] {
            display: none !important;
        }
        .print-area { display: block !important; direction: rtl !important; }
        
        /* أمر فصل الصفحات */
        .page-break { page-break-before: always; }
    }
    .print-area { display: none; }
    .receipt-box { border: 2px solid black; padding: 30px; margin-bottom: 20px; direction: rtl; }
    .sticker-box { border: 1px solid black; padding: 10px; width: 250px; text-align: center; margin: 0 auto; direction: rtl; }
    </style>
    """, unsafe_allow_html=True)

DB_FILE = "maintenance_v6.csv"

def load_data():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE)
    return pd.DataFrame(columns=["ID", "الزبون", "الهاتف", "الماركة", "الموديل", "العطل", "التكلفة", "سعر_القطع", "الحالة", "التاريخ"])

def save_data(df):
    df.to_csv(DB_FILE, index=False)

if 'db' not in st.session_state:
    st.session_state.db = load_data()

st.title("🛠️ الحل للتقنية - نظام الإيصالات")

tabs = st.tabs(["➕ إضافة جهاز", "🔍 بحث وتعديل"])

# دالة عرض الطباعة المنفصلة
def render_printable_content(row):
    qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=100x100&data=ID_{row['ID']}"
    st.markdown(f"""
    <div class="print-area">
        <div class="receipt-box">
            <h1 style="text-align:center;">الحل للتقنية للصيانة</h1>
            <p style="text-align:center;">هاتف: 0916206100</p>
            <hr>
            <h3>إيصال استلام جهاز #{row['ID']}</h3>
            <p><b>الزبون:</b> {row['الزبون']}</p>
            <p><b>الجهاز:</b> {row['الماركة']} {row['الموديل']}</p>
            <p><b>العطل:</b> {row['العطل']}</p>
            <p><b>التكلفة:</b> {row['التكلفة']} $</p>
            <p><b>التاريخ:</b> {row['التاريخ']}</p>
        </div>
        
        <div class="page-break"></div>
        <div class="sticker-box">
            <h4 style="margin:5px;">الحل للتقنية</h4>
            <b>{row['الزبون']}</b><br>
            <span>{row['الموديل']}</span><br>
            <img src="{qr_url}" width="100" style="margin:10px 0;"><br>
            <b>ID: {row['ID']}</b>
        </div>
    </div>
    """, unsafe_allow_html=True)

# 1. إضافة جهاز
with tabs[0]:
    with st.form("add_form"):
        name = st.text_input("اسم الزبون")
        phone = st.text_input("رقم الهاتف")
        c1, c2 = st.columns(2)
        brand = c1.selectbox("الماركة", ["iPhone", "Samsung", "Xiaomi", "أخرى"])
        model = c1.text_input("الموديل")
        cost = c2.number_input("التكلفة $", min_value=0)
        issue = c2.text_area("العطل")
        submitted = st.form_submit_button("✅ حفظ")

    if submitted and name:
        new_id = len(st.session_state.db) + 1001
        new_row = {"ID": new_id, "الزبون": name, "الهاتف": phone, "الماركة": brand, "الموديل": model, "العطل": issue, "التكلفة": cost, "سعر_القطع": 0, "الحالة": "تحت الصيانة", "التاريخ": datetime.now().strftime("%Y-%m-%d")}
        st.session_state.db = pd.concat([st.session_state.db, pd.DataFrame([new_row])], ignore_index=True)
        save_data(st.session_state.db)
        st.success(f"تم الحفظ! رقم الوصل: {new_id}")
        render_printable_content(new_row)
        st.button(f"🖨️ طباعة الآن", on_click=lambda: st.write('<script>window.print();</script>', unsafe_allow_html=True))

# 2. بحث وتعديل
with tabs[1]:
    search = st.text_input("🔎 ابحث بالاسم")
    if search:
        results = st.session_state.db[st.session_state.db['الزبون'].astype(str).str.contains(search)]
        for idx, row in results.iterrows():
            with st.expander(f"⚙️ {row['الزبون']} - {row['ID']}"):
                render_printable_content(row)
                st.button(f"🖨️ طباعة الإيصال والستيكر #{row['ID']}", key=f"p_{idx}", on_click=lambda: st.write('<script>window.print();</script>', unsafe_allow_html=True))
