import streamlit as st
import pandas as pd
import os
from datetime import datetime
import base64

# --- إعدادات النظام الاحترافية ---
st.set_page_config(page_title="الحل للتقنية", layout="wide")

# CSS متطور لحل مشاكل التداخل والطباعة
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    * { font-family: 'Cairo', sans-serif; direction: rtl; }
    
    /* تصميم البطاقات للموبايل لمنع تداخل النصوص */
    .stMetric { background: white; padding: 10px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    [data-testid="stMetricValue"] { font-size: 1.5rem !important; }
    
    /* تنسيق منطقة الطباعة */
    @media print {
        header, footer, .stTabs, .no-print, [data-testid="stHeader"], .stButton { display: none !important; }
        .print-only { display: block !important; width: 100% !important; border: none !important; }
    }
    .print-only { display: none; border: 1px dashed #ccc; padding: 20px; background: #fff; margin-top: 20px; }
    
    /* زر طباعة كبير وواضح */
    .print-btn-style {
        display: block; width: 100%; padding: 15px; background: #28a745; 
        color: white !important; text-align: center; border-radius: 10px;
        text-decoration: none; font-weight: bold; margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

DB_FILE = "solution_tech_v2.csv"

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

# وظيفة عرض الوصل الجاهز للطباعة
def show_receipt(row):
    qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=100x100&data=ID_{row['ID']}"
    st.markdown(f"""
    <div class="print-only">
        <div style="text-align:center; border:2px solid #000; padding:20px;">
            <h1 style="margin:0;">الحل للتقنية للصيانة</h1>
            <p>هاتف: 0916206100 | التاريخ: {row['التاريخ']}</p>
            <hr>
            <table style="width:100%; text-align:right; font-size:18px;">
                <tr><td><b>رقم الإيصال:</b> {row['ID']}</td><td><b>الزبون:</b> {row['الزبون']}</td></tr>
                <tr><td><b>الجهاز:</b> {row['الماركة']} {row['الموديل']}</td><td><b>الهاتف:</b> {row['الهاتف']}</td></tr>
                <tr><td colspan="2"><b>وصف العطل:</b> {row['العطل']}</td></tr>
            </table>
            <h2 style="background:#000; color:#fff; padding:10px;">المبلغ المطلوب: {row['التكلفة']} $</h2>
        </div>
        <div style="page-break-before: always; text-align:center; padding:20px; border:1px solid #000; width:250px; margin:20px auto;">
            <b>{row['الزبون']}</b><br>{row['الماركة']} {row['الموديل']}<br>
            <img src="{qr_url}" width="100"><br>
            <b>ID: {row['ID']}</b>
        </div>
    </div>
    """, unsafe_allow_html=True)
    if st.button(f"🖨️ تفعيل أمر الطباعة للجهاز رقم {row['ID']}", key=f"btn_{row['ID']}"):
        st.markdown('<script>window.print();</script>', unsafe_allow_html=True)

# --- الواجهة ---
st.title("🛠️ نظام الحل للتقنية")

# إحصائيات سريعة
db = st.session_state.db
c1, c2, c3 = st.columns(3)
c1.metric("إجمالي الأجهزة", len(db))
c2.metric("تحت الصيانة", len(db[db['الحالة']=="تحت الصيانة"]))
c3.metric("صافي الربح", f"{pd.to_numeric(db[db['الحالة']=='تم التسليم']['التكلفة']).sum() - pd.to_numeric(db[db['الحالة']=='تم التسليم']['سعر_القطع']).sum()} $")

tabs = st.tabs(["➕ إضافة جهاز", "🔍 بحث وتعديل شامل", "📑 التقارير"])

# 1. إضافة جهاز
with tabs[0]:
    with st.form("add_form"):
        name = st.text_input("اسم الزبون")
        phone = st.text_input("رقم الهاتف")
        col1, col2 = st.columns(2)
        brand = col1.selectbox("الماركة", ["iPhone", "Samsung", "Xiaomi", "Infinix", "أخرى"])
        model = col1.text_input("الموديل")
        cost = col2.number_input("التكلفة $", min_value=0)
        issue = col2.text_area("وصف العطل")
        img_f = st.file_uploader("تصوير الجهاز")
        if st.form_submit_button("✅ حفظ البيانات"):
            if name:
                new_id = len(st.session_state.db) + 1001
                new_row = {"ID": new_id, "الزبون": name, "الهاتف": phone, "الماركة": brand, "الموديل": model, "العطل": issue, "التكلفة": cost, "سعر_القطع": 0, "الحالة": "تحت الصيانة", "التاريخ": datetime.now().strftime("%Y-%m-%d"), "الصورة": img_to_base64(img_f)}
                st.session_state.db = pd.concat([st.session_state.db, pd.DataFrame([new_row])], ignore_index=True)
                save_data(st.session_state.db)
                st.success(f"تم الحفظ! رقم الوصل: {new_id}")
                show_receipt(new_row)

# 2. بحث وتعديل شامل
with tabs[1]:
    search_q = st.text_input("🔎 ابحث بالاسم أو الهاتف...")
    if search_q:
        results = st.session_state.db[st.session_state.db['الزبون'].astype(str).str.contains(search_q) | st.session_state.db['الهاتف'].astype(str).str.contains(search_q)]
        for idx, row in results.iterrows():
            with st.expander(f"⚙️ {row['الزبون']} - {row['الموديل']}"):
                with st.form(f"edit_{idx}"):
                    u_name = st.text_input("الاسم", value=row['الزبون'])
                    u_phone = st.text_input("الهاتف", value=row['الهاتف'])
                    u_cost = st.number_input("التكلفة $", value=int(row['التكلفة']))
                    u_parts = st.number_input("سعر القطع $", value=int(row['سعر_القطع']))
                    u_issue = st.text_area("العطل", value=row['العطل'])
                    u_status = st.selectbox("الحالة", ["تحت الصيانة", "تم التسليم"], index=0 if row['الحالة']=="تحت الصيانة" else 1)
                    
                    c_s, c_d = st.columns(2)
                    if c_s.form_submit_button("💾 حفظ التعديلات"):
                        st.session_state.db.loc[idx, ['الزبون', 'الهاتف', 'التكلفة', 'سعر_القطع', 'العطل', 'الحالة']] = [u_name, u_phone, u_cost, u_parts, u_issue, u_status]
                        save_data(st.session_state.db)
                        st.rerun()
                    if c_d.form_submit_button("🗑️ حذف"):
                        st.session_state.db = st.session_state.db.drop(idx)
                        save_data(st.session_state.db)
                        st.rerun()
                
                # عرض الصورة
                if row['الصورة'] and len(str(row['الصورة'])) > 50:
                    st.image(base64.b64decode(row['الصورة']), width=200)
                
                # منطقة الطباعة داخل البحث
                show_receipt(row)

# 3. التقارير
with tabs[2]:
    st.dataframe(st.session_state.db.drop(columns=['الصورة']), use_container_width=True)
