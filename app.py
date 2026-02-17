import streamlit as st
import pandas as pd
import os
from datetime import datetime
import base64

# --- إعدادات الصفحة ---
st.set_page_config(page_title="الحل للتقنية", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo&display=swap');
    * { font-family: 'Cairo', sans-serif; direction: rtl; }
    
    /* هذا الجزء هو السر: يضمن ظهور المحتوى عند الطباعة وإخفاء أزرار الموقع */
    @media print {
        header, footer, .stTabs, button, .no-print, [data-testid="stHeader"], [data-testid="stSidebar"] {
            display: none !important;
        }
        .printable-content {
            display: block !important;
            width: 100% !important;
            border: none !important;
        }
    }
    /* تنسيق المعاينة في الشاشة */
    .preview-style {
        border: 2px solid #333;
        padding: 20px;
        background: white;
        color: black;
        border-radius: 10px;
        margin-bottom: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

DB_FILE = "solution_tech_final.csv"

def load_data():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE)
    return pd.DataFrame(columns=["ID", "الزبون", "الهاتف", "الماركة", "الموديل", "العطل", "التكلفة", "سعر_القطع", "الحالة", "التاريخ", "الصورة"])

def save_data(df):
    df.to_csv(DB_FILE, index=False)

if 'db' not in st.session_state:
    st.session_state.db = load_data()

def img_to_base64(file):
    if file: return base64.b64encode(file.getvalue()).decode()
    return ""

st.title("🛠️ نظام الحل للتقنية - الصيانة")

tabs = st.tabs(["➕ إضافة جهاز", "🔍 إدارة وبحث", "📊 المالية"])

# 1. إضافة جهاز
with tabs[0]:
    with st.form("add_form"):
        name = st.text_input("اسم الزبون")
        phone = st.text_input("رقم الهاتف")
        c1, c2 = st.columns(2)
        brand = c1.selectbox("الماركة", ["iPhone", "Samsung", "Xiaomi", "أخرى"])
        model = c1.text_input("الموديل")
        cost = c2.number_input("التكلفة $", min_value=0)
        issue = c2.text_area("وصف العطل")
        img_f = st.file_uploader("📸 صورة الجهاز")
        if st.form_submit_button("✅ حفظ البيانات"):
            if name:
                new_id = len(st.session_state.db) + 1001
                new_row = {"ID": new_id, "الزبون": name, "الهاتف": phone, "الماركة": brand, "الموديل": model, "العطل": issue, "التكلفة": cost, "سعر_القطع": 0, "الحالة": "تحت الصيانة", "التاريخ": datetime.now().strftime("%Y-%m-%d"), "الصورة": img_to_base64(img_f)}
                st.session_state.db = pd.concat([st.session_state.db, pd.DataFrame([new_row])], ignore_index=True)
                save_data(st.session_state.db)
                st.success(f"تم الحفظ برقم {new_id}")

# 2. إدارة وبحث
with tabs[1]:
    sq = st.text_input("🔎 ابحث بالاسم أو رقم الوصل")
    if sq:
        results = st.session_state.db[st.session_state.db['الزبون'].astype(str).str.contains(sq) | st.session_state.db['ID'].astype(str).str.contains(sq)]
        for idx, row in results.iterrows():
            with st.expander(f"⚙️ {row['الزبون']} - {row['الموديل']}"):
                
                qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=100x100&data=ID_{row['ID']}"
                
                # --- القسم الأول: الوصل الكامل ---
                st.write("### 📄 إيصال الزبون")
                # هنا المعاينة تظهر في الموقع "printable-content"
                st.markdown(f"""
                <div class="printable-content preview-style">
                    <h1 style="text-align:center; margin:0; color:black;">الحل للتقنية للصيانة</h1>
                    <p style="text-align:center; margin:0; color:black;">هاتف: 0916206100</p>
                    <hr style="border:1px solid black;">
                    <p style="color:black;"><b>رقم الإيصال:</b> {row['ID']}</p>
                    <p style="color:black;"><b>الزبون:</b> {row['الزبون']} | <b>الهاتف:</b> {row['الهاتف']}</p>
                    <p style="color:black;"><b>الجهاز:</b> {row['الماركة']} {row['الموديل']}</p>
                    <p style="color:black;"><b>العطل:</b> {row['العطل']}</p>
                    <h2 style="text-align:center; background:#eee; padding:10px; color:black;">المطلوب: {row['التكلفة']} $</h2>
                    <div style="text-align:center;"><img src="{qr_url}"></div>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button(f"🖨️ طباعة الوصل", key=f"rec_{idx}"):
                    st.components.v1.html("<script>window.print();</script>", height=0)

                # --- القسم الثاني: الستيكر الصغير ---
                st.write("### 🏷️ ستيكر الجهاز")
                st.markdown(f"""
                <div class="printable-content preview-style" style="width:250px; margin: 0 auto; text-align:center;">
                    <h3 style="margin:0; color:black;">الحل للتقنية</h3>
                    <b style="color:black;">{row['الزبون']}</b><br>
                    <span style="color:black;">{row['الموديل']}</span><br>
                    <img src="{qr_url}" width="80"><br>
                    <b style="color:black;">ID: {row['ID']}</b>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button(f"🏷️ طباعة الستيكر", key=f"stk_{idx}"):
                    st.components.v1.html("<script>window.print();</script>", height=0)

# 3. المالية
with tabs[2]:
    st.dataframe(st.session_state.db.drop(columns=['الصورة']))
