import streamlit as st
import pandas as pd
import os
from datetime import datetime
import base64

# --- إعدادات الصفحة ---
st.set_page_config(page_title="الحل للتقنية", layout="wide")

# CSS بسيط وفعال يمنع التداخل ويحسن الطباعة
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo&display=swap');
    * { font-family: 'Cairo', sans-serif; direction: rtl; }
    .stApp { background-color: #f9f9f9; }
    
    /* تنسيق الوصل للطباعة */
    @media print {
        header, footer, .stTabs, .no-print, [data-testid="stHeader"], .stButton { display: none !important; }
        .print-area { display: block !important; width: 100% !important; border: none !important; }
    }
    .print-area { 
        display: none; border: 2px solid #000; padding: 20px; 
        background: white; margin-top: 20px; text-align: right; 
    }
    .main-card { background: white; padding: 15px; border-radius: 10px; border: 1px solid #ddd; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

DB_FILE = "solution_v3_stable.csv"

def load_data():
    if os.path.exists(DB_FILE):
        df = pd.read_csv(DB_FILE)
        cols = ["ID", "الزبون", "الهاتف", "الماركة", "الموديل", "العطل", "التكلفة", "سعر_القطع", "الحالة", "التاريخ", "الصورة"]
        for col in cols:
            if col not in df.columns: df[col] = 0 if "سعر" in col or "التكلفة" in col else ""
        return df
    return pd.DataFrame(columns=["ID", "الزبون", "الهاتف", "الماركة", "الموديل", "العطل", "التكلفة", "سعر_القطع", "الحالة", "التاريخ", "الصورة"])

def save_data(df):
    df.to_csv(DB_FILE, index=False)

if 'db' not in st.session_state:
    st.session_state.db = load_data()

# --- واجهة التطبيق ---
st.title("🛠️ الحل للتقنية (نسخة مستقرة)")

tabs = st.tabs(["➕ إضافة جهاز", "🔍 إدارة وبحث", "📊 المالية"])

# 1. إضافة جهاز
with tabs[0]:
    with st.form("add_form", clear_on_submit=True):
        st.subheader("بيانات الجهاز الجديد")
        name = st.text_input("اسم الزبون")
        phone = st.text_input("رقم الهاتف")
        c1, c2 = st.columns(2)
        brand = c1.selectbox("الماركة", ["iPhone", "Samsung", "Xiaomi", "أخرى"])
        model = c1.text_input("الموديل")
        cost = c2.number_input("التكلفة $", min_value=0)
        issue = c2.text_area("العطل")
        save_btn = st.form_submit_button("✅ حفظ البيانات")

    if save_btn and name:
        new_id = len(st.session_state.db) + 1001
        new_row = {"ID": new_id, "الزبون": name, "الهاتف": phone, "الماركة": brand, "الموديل": model, "العطل": issue, "التكلفة": cost, "سعر_القطع": 0, "الحالة": "تحت الصيانة", "التاريخ": datetime.now().strftime("%Y-%m-%d"), "الصورة": ""}
        st.session_state.db = pd.concat([st.session_state.db, pd.DataFrame([new_row])], ignore_index=True)
        save_data(st.session_state.db)
        st.success(f"تم الحفظ برقم: {new_id}. اذهب لتبويب البحث للطباعة.")

# 2. إدارة وبحث (التعديل الشامل والطباعة)
with tabs[1]:
    search_q = st.text_input("🔎 ابحث بالاسم أو الهاتف لطباعة الوصل وتعديله")
    if search_q:
        df = st.session_state.db
        results = df[df['الزبون'].astype(str).str.contains(search_q) | df['الهاتف'].astype(str).str.contains(search_q)]
        
        for idx, row in results.iterrows():
            with st.container():
                st.markdown(f"<div class='main-card'><b>{row['الزبون']}</b> | {row['الموديل']} (ID: {row['ID']})</div>", unsafe_allow_html=True)
                
                # منطقة التعديل الشامل
                with st.expander("🛠️ تعديل كل البيانات"):
                    with st.form(f"f_edit_{idx}"):
                        u_name = st.text_input("الاسم", value=row['الزبون'])
                        u_phone = st.text_input("الهاتف", value=row['الهاتف'])
                        u_cost = st.number_input("التكلفة $", value=int(row['التكلفة']))
                        u_parts = st.number_input("سعر القطع $", value=int(row['سعر_القطع']))
                        u_issue = st.text_area("العطل", value=row['العطل'])
                        u_status = st.selectbox("الحالة", ["تحت الصيانة", "تم التسليم"], index=0 if row['الحالة']=="تحت الصيانة" else 1)
                        
                        if st.form_submit_button("💾 حفظ التعديلات"):
                            st.session_state.db.loc[idx, ['الزبون', 'الهاتف', 'التكلفة', 'سعر_القطع', 'العطل', 'الحالة']] = [u_name, u_phone, u_cost, u_parts, u_issue, u_status]
                            save_data(st.session_state.db)
                            st.success("تم التحديث")
                            st.rerun()

                # منطقة عرض الوصل للطباعة
                st.markdown(f"""
                <div class="print-area">
                    <div style="text-align:center;">
                        <h2>الحل للتقنية للصيانة</h2>
                        <p>هاتف: 0916206100 | رقم الوصل: {row['ID']}</p>
                        <hr>
                        <p style="text-align:right;"><b>الزبون:</b> {row['الزبون']}</p>
                        <p style="text-align:right;"><b>الجهاز:</b> {row['الماركة']} {row['الموديل']}</p>
                        <p style="text-align:right;"><b>العطل:</b> {row['العطل']}</p>
                        <h3 style="text-align:center; border:1px solid #000; padding:10px;">التكلفة: {row['التكلفة']} $</h3>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # زر تفعيل الطباعة (خارج الفورم)
                if st.button(f"📄 عرض للطباعة #{row['ID']}", key=f"p_{idx}"):
                    st.info("للآيفون: اضغط (مشاركة -> طباعة). للكمبيوتر: اضغط (Ctrl + P).")

# 3. المالية
with tabs[2]:
    st.dataframe(st.session_state.db.drop(columns=['الصورة']), use_container_width=True)
