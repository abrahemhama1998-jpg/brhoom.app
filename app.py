import streamlit as st
import pandas as pd
import os
from datetime import datetime
import base64

# --- إعدادات الصفحة ---
st.set_page_config(page_title="الحل للتقنية", layout="wide")

# CSS قوي لإجبار الألوان على الظهور في الطباعة
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo&display=swap');
    * { font-family: 'Cairo', sans-serif; direction: rtl; }
    
    /* تنسيق الطباعة الصارم */
    @media print {
        header, footer, .stTabs, button, .no-print, [data-testid="stHeader"], [data-testid="stSidebar"], .stButton {
            display: none !important;
        }
        /* إجبار المحتوى المطبوع على الظهور بلون أسود وخلفية بيضاء */
        .printable-area {
            display: block !important;
            width: 100% !important;
            color: black !important;
            background-color: white !important;
        }
        h1, h2, h3, p, b, span { color: black !important; }
    }

    /* تنسيق المعاينة داخل التطبيق */
    .preview-box {
        border: 2px solid #000;
        padding: 20px;
        background-color: #fff;
        color: #000;
        border-radius: 10px;
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

DB_FILE = "solution_stable_v11.csv"

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

st.title("🛠️ نظام الحل للتقنية")

tabs = st.tabs(["➕ إضافة جهاز", "🔍 البحث والإدارة"])

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
        img_f = st.file_uploader("📸 صورة")
        if st.form_submit_button("✅ حفظ"):
            if name:
                new_id = len(st.session_state.db) + 1001
                new_row = {"ID": new_id, "الزبون": name, "الهاتف": phone, "الماركة": brand, "الموديل": model, "العطل": issue, "التكلفة": cost, "سعر_القطع": 0, "الحالة": "تحت الصيانة", "التاريخ": datetime.now().strftime("%Y-%m-%d"), "الصورة": img_to_base64(img_f)}
                st.session_state.db = pd.concat([st.session_state.db, pd.DataFrame([new_row])], ignore_index=True)
                save_data(st.session_state.db)
                st.success(f"تم الحفظ! رقم الوصل {new_id}")

# 2. إدارة وطباعة
with tabs[1]:
    search = st.text_input("🔎 ابحث بالاسم")
    if search:
        results = st.session_state.db[st.session_state.db['الزبون'].astype(str).str.contains(search)]
        for idx, row in results.iterrows():
            with st.expander(f"📋 {row['الزبون']} - {row['ID']}"):
                
                qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=100x100&data=ID_{row['ID']}"
                
                # إظهار المحتوى "مرئياً" دائماً للمتصفح ليتمكن من طباعته
                st.markdown("### 📄 إيصال الزبون")
                st.markdown(f"""
                <div class="printable-area preview-box">
                    <h1 style="text-align:center;">الحل للتقنية للصيانة</h1>
                    <p style="text-align:center;">رقم التواصل: 0916206100</p>
                    <hr>
                    <p><b>رقم الإيصال:</b> {row['ID']}</p>
                    <p><b>الزبون:</b> {row['الزبون']} | <b>الهاتف:</b> {row['الهاتف']}</p>
                    <p><b>الجهاز:</b> {row['الموديل']}</p>
                    <p><b>التكلفة المتفق عليها:</b> {row['التكلفة']} $</p>
                    <div style="text-align:center;"><img src="{qr_url}"></div>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button(f"🖨️ طباعة الوصل", key=f"btn_p_{idx}"):
                    st.components.v1.html("<script>window.print();</script>", height=0)

                st.write("---")
                st.markdown("### 🏷️ ستيكر الجهاز")
                st.markdown(f"""
                <div class="printable-area preview-box" style="width:250px; margin:auto; text-align:center;">
                    <h3 style="margin:5px;">الحل للتقنية</h3>
                    <b>{row['الزبون']}</b><br>
                    <span>{row['الموديل']}</span><br>
                    <img src="{qr_url}" width="90"><br>
                    <b>ID: {row['ID']}</b>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button(f"🏷️ طباعة ستيكر", key=f"btn_s_{idx}"):
                    st.components.v1.html("<script>window.print();</script>", height=0)
