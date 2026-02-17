import streamlit as st
import pandas as pd
import os
from datetime import datetime
import base64

# --- إعدادات النظام ---
st.set_page_config(page_title="الحل للتقنية", layout="wide")

# --- محرك التصميم المطور للهواتف ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    * { font-family: 'Cairo', sans-serif; direction: rtl; }
    .stApp { background-color: #f8f9fa; }
    
    /* مربعات الإحصائيات العلوية */
    .stat-box {
        background: white; padding: 15px; border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05); text-align: center;
        border-bottom: 4px solid #007bff; margin-bottom: 10px;
    }
    
    /* تصميم بطاقة الجهاز */
    .device-card {
        background: #ffffff; padding: 15px; border-radius: 15px;
        border: 1px solid #e0e0e0; margin-bottom: 15px;
    }

    /* زر الطباعة المخصص للهاتف */
    .mobile-print-btn {
        display: block; width: 100%; text-align: center;
        background: #28a745; color: white !important;
        padding: 12px; border-radius: 10px; font-weight: bold;
        text-decoration: none; margin: 10px 0;
    }

    @media print {
        header, footer, .stTabs, .no-print, [data-testid="stHeader"] { display: none !important; }
        .print-area { display: block !important; }
    }
    .print-area { display: none; }
    </style>
    """, unsafe_allow_html=True)

DB_FILE = "final_pro_db.csv"

def load_data():
    if os.path.exists(DB_FILE):
        try:
            df = pd.read_csv(DB_FILE)
            for col in ["ID", "الزبون", "الهاتف", "الماركة", "الموديل", "العطل", "التكلفة", "سعر_القطع", "الحالة", "التاريخ", "الصورة"]:
                if col not in df.columns: df[col] = 0 if "سعر" in col or "التكلفة" in col else ""
            return df
        except: pass
    return pd.DataFrame(columns=["ID", "الزبون", "الهاتف", "الماركة", "الموديل", "العطل", "التكلفة", "سعر_القطع", "الحالة", "التاريخ", "الصورة"])

def save_data(df):
    df.to_csv(DB_FILE, index=False)

if 'db' not in st.session_state:
    st.session_state.db = load_data()

def img_to_base64(image_file):
    if image_file: return base64.b64encode(image_file.getvalue()).decode()
    return ""

def render_receipt(row):
    qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=100x100&data=ID_{row['ID']}"
    # تصميم الوصل والستيكر
    st.markdown(f"""
    <div class="print-area" style="direction:rtl; text-align:right; font-family:Arial;">
        <div style="border:2px solid #000; padding:15px;">
            <h2 style="text-align:center;">الحل للتقنية للصيانة</h2>
            <p style="text-align:center;">هاتف: 0916206100</p><hr>
            <p><b>رقم الوصل:</b> {row['ID']}</p>
            <p><b>الزبون:</b> {row['الزبون']}</p>
            <p><b>الجهاز:</b> {row['الماركة']} {row['الموديل']}</p>
            <p><b>العطل:</b> {row['العطل']}</p>
            <h3 style="text-align:center; border:1px solid #000;">التكلفة: {row['التكلفة']} $</h3>
        </div>
        <div style="page-break-before: always; text-align:center; padding:20px;">
            <b>{row['الزبون']}</b><br>{row['الموديل']}<br>
            <img src="{qr_url}" width="100"><br>ID: {row['ID']}
        </div>
    </div>
    <a href="javascript:window.print()" class="mobile-print-btn no-print">🖨️ اضغط هنا للطباعة</a>
    """, unsafe_allow_html=True)

# --- الواجهة الرئيسية (الإحصائيات بالأعلى) ---
st.markdown("<h2 style='text-align:center;'>🛠️ منظومة الحل للتقنية</h2>", unsafe_allow_html=True)

db = st.session_state.db
m1, m2, m3 = st.columns(3)
with m1:
    st.markdown(f"<div class='stat-box'><h6>صافي الربح</h6><h4>{pd.to_numeric(db[db['الحالة']=='تم التسليم']['التكلفة']).sum() - pd.to_numeric(db[db['الحالة']=='تم التسليم']['سعر_القطع']).sum()} $</h4></div>", unsafe_allow_html=True)
with m2:
    st.markdown(f"<div class='stat-box'><h6>تحت الصيانة</h6><h4>{len(db[db['الحالة']=='تحت الصيانة'])}</h4></div>", unsafe_allow_html=True)
with m3:
    st.markdown(f"<div class='stat-box'><h6>إجمالي الأجهزة</h6><h4>{len(db)}</h4></div>", unsafe_allow_html=True)

tabs = st.tabs(["➕ إضافة", "🔍 إدارة وبحث", "📊 المالية"])

# --- التبويب 1: إضافة جهاز ---
with tabs[0]:
    with st.form("add_form", clear_on_submit=True):
        name = st.text_input("👤 اسم الزبون")
        phone = st.text_input("📞 رقم الهاتف")
        c1, c2 = st.columns(2)
        brand = c1.selectbox("الماركة", ["iPhone", "Samsung", "Xiaomi", "Infinix", "أخرى"])
        model = c2.text_input("الموديل")
        cost = st.number_input("💵 التكلفة المقدرة $", min_value=0)
        issue = st.text_area("📝 وصف العطل")
        img_f = st.file_uploader("📸 صورة الجهاز")
        if st.form_submit_button("✅ حفظ وإصدار وصل"):
            if name:
                new_id = len(st.session_state.db) + 1001
                new_row = {"ID": new_id, "الزبون": name, "الهاتف": phone, "الماركة": brand, "الموديل": model, "العطل": issue, "التكلفة": cost, "سعر_القطع": 0, "الحالة": "تحت الصيانة", "التاريخ": datetime.now().strftime("%Y-%m-%d"), "الصورة": img_to_base64(img_f)}
                st.session_state.db = pd.concat([st.session_state.db, pd.DataFrame([new_row])], ignore_index=True)
                save_data(st.session_state.db)
                st.success("تم الحفظ!")
                render_receipt(new_row)

# --- التبويب 2: البحث والتعديل الكامل ---
with tabs[1]:
    sq = st.text_input("🔎 ابحث بالاسم أو الهاتف...")
    if sq:
        results = st.session_state.db[st.session_state.db['الزبون'].astype(str).str.contains(sq) | st.session_state.db['الهاتف'].astype(str).str.contains(sq)]
        for idx, row in results.iterrows():
            with st.container():
                st.markdown(f"<div class='device-card'><b>{row['الزبون']}</b> - {row['الموديل']} (ID: {row['ID']})</div>", unsafe_allow_html=True)
                with st.expander("📝 تعديل البيانات"):
                    with st.form(f"edit_{idx}"):
                        u_name = st.text_input("الاسم", value=row['الزبون'])
                        u_phone = st.text_input("الهاتف", value=row['الهاتف'])
                        u_cost = st.number_input("التكلفة $", value=int(row['التكلفة']))
                        u_parts = st.number_input("سعر القطع $", value=int(row['سعر_القطع']))
                        u_issue = st.text_area("العطل", value=row['العطل'])
                        u_status = st.selectbox("الحالة", ["تحت الصيانة", "تم التسليم"], index=0 if row['الحالة']=="تحت الصيانة" else 1)
                        
                        col1, col2 = st.columns(2)
                        if col1.form_submit_button("💾 حفظ"):
                            st.session_state.db.loc[idx, ['الزبون', 'الهاتف', 'التكلفة', 'سعر_القطع', 'العطل', 'الحالة']] = [u_name, u_phone, u_cost, u_parts, u_issue, u_status]
                            save_data(st.session_state.db)
                            st.rerun()
                        if col2.form_submit_button("🗑️ حذف"):
                            st.session_state.db = st.session_state.db.drop(idx)
                            save_data(st.session_state.db)
                            st.rerun()
                
                # فحص الصورة بأمان
                if row['الصورة'] and len(str(row['الصورة'])) > 100:
                    st.image(base64.b64decode(row['الصورة']), width=150)
                render_receipt(row)

# --- التبويب 3: المالية ---
with tabs[2]:
    st.dataframe(st.session_state.db.drop(columns=['الصورة']), use_container_width=True)
