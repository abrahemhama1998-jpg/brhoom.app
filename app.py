import streamlit as st
import pandas as pd
import os
from datetime import datetime
import base64

# --- إعدادات الصفحة ---
st.set_page_config(page_title="الحل للتقنية", layout="wide")

# CSS لإجبار الطباعة وتنسيق المحتوى
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo&display=swap');
    * { font-family: 'Cairo', sans-serif; direction: rtl; }
    
    @media print {
        .no-print { display: none !important; }
        .printable { display: block !important; width: 100% !important; color: black !important; background: white !important; }
    }
    .printable { display: none; }
    .preview-card { border: 2px solid #333; padding: 15px; border-radius: 10px; background: white; color: black; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

DB_FILE = "tech_solution_final_v20.csv"

def load_data():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE)
    return pd.DataFrame(columns=["ID", "الزبون", "الهاتف", "الماركة", "الموديل", "العطل", "التكلفة", "سعر_القطع", "الحالة", "التاريخ", "الصورة"])

def save_data(df):
    df.to_csv(DB_FILE, index=False)

if 'db' not in st.session_state:
    st.session_state.db = load_data()

# --- دالة الطباعة المحسنة ---
def print_button():
    st.markdown('<script>window.print();</script>', unsafe_allow_html=True)

st.title("🛠️ الحل للتقنية - نظام الصيانة الذكي")

# الحصول على الرابط الحالي للمنظومة لربطه بالباركود
try:
    current_url = st.query_params.get("id", "")
except:
    current_url = ""

tabs = st.tabs(["➕ إضافة جهاز", "🔍 البحث والإدارة", "📊 المالية"])

# --- 1. إضافة جهاز ---
with tabs[0]:
    with st.form("add_form"):
        c1, c2 = st.columns(2)
        name = c1.text_input("اسم الزبون")
        phone = c1.text_input("رقم الهاتف")
        brand = c2.selectbox("الماركة", ["iPhone", "Samsung", "Xiaomi", "أخرى"])
        model = c2.text_input("الموديل")
        cost = c1.number_input("التكلفة $", min_value=0)
        issue = c2.text_area("وصف العطل")
        if st.form_submit_button("✅ حفظ"):
            new_id = len(st.session_state.db) + 1001
            new_row = {"ID": new_id, "الزبون": name, "الهاتف": phone, "الماركة": brand, "الموديل": model, "العطل": issue, "التكلفة": cost, "سعر_القطع": 0, "الحالة": "تحت الصيانة", "التاريخ": datetime.now().strftime("%Y-%m-%d"), "الصورة": ""}
            st.session_state.db = pd.concat([st.session_state.db, pd.DataFrame([new_row])], ignore_index=True)
            save_data(st.session_state.db)
            st.success(f"تم الحفظ! رقم ID: {new_id}")

# --- 2. البحث والإدارة ---
with tabs[1]:
    # ميزة قراءة الباركود: إذا كان الرابط يحتوي على ID سيقوم بالبحث عنه تلقائياً
    query_id = st.query_params.get("id", "")
    search_input = st.text_input("🔎 ابحث بالاسم أو ID", value=query_id)
    
    if search_input:
        df = st.session_state.db
        results = df[df['الزبون'].astype(str).str.contains(search_input) | df['ID'].astype(str).str.contains(search_input)]
        
        for idx, row in results.iterrows():
            with st.expander(f"📋 {row['الزبون']} - {row['الموديل']} (ID: {row['ID']})", expanded=True if query_id else False):
                
                # التعديل الشامل
                with st.form(f"edit_{idx}"):
                    c_1, c_2 = st.columns(2)
                    u_cost = c_1.number_input("التكلفة $", value=int(row['التكلفة']))
                    u_parts = c_2.number_input("سعر القطع $", value=int(row['سعر_القطع']))
                    u_status = st.selectbox("الحالة", ["تحت الصيانة", "تم التسليم"], index=0 if row['الحالة']=="تحت الصيانة" else 1)
                    if st.form_submit_button("💾 حفظ التعديلات"):
                        st.session_state.db.loc[idx, ['التكلفة', 'سعر_القطع', 'الحالة']] = [u_cost, u_parts, u_status]
                        save_data(st.session_state.db)
                        st.rerun()

                # --- الباركود الذكي (رابط يفتح صفحة الجهاز) ---
                # استبدل 'your-app-url' برابط المنظومة الفعلي الخاص بك
                base_url = "https://your-app-url.streamlit.app/" 
                qr_link = f"{base_url}?id={row['ID']}"
                qr_img_url = f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data={qr_link}"
                
                st.write("### 🖨️ الطباعة")
                col_a, col_b = st.columns(2)
                
                with col_a:
                    st.markdown(f"""
                    <div class="preview-card">
                        <h2 style="text-align:center;">الحل للتقنية</h2>
                        <p>رقم الإيصال: {row['ID']}</p>
                        <p>الزبون: {row['الزبون']}</p>
                        <p>الجهاز: {row['الموديل']}</p>
                        <h3 style="text-align:center;">المبلغ: {row['التكلفة']} $</h3>
                    </div>
                    """, unsafe_allow_html=True)
                    if st.button(f"طباعة الوصل #{row['ID']}", key=f"p_rec_{idx}"):
                        st.components.v1.html(f"<script>window.print();</script>", height=0)

                with col_b:
                    st.markdown(f"""
                    <div class="preview-card" style="text-align:center;">
                        <b>{row['الزبون']}</b><br>
                        <img src="{qr_img_url}" width="100"><br>
                        <b>ID: {row['ID']}</b>
                    </div>
                    """, unsafe_allow_html=True)
                    if st.button(f"طباعة الستيكر #{row['ID']}", key=f"p_stk_{idx}"):
                        st.components.v1.html(f"<script>window.print();</script>", height=0)

# --- 3. المالية ---
with tabs[2]:
    st.write("إجمالي الأرباح")
    st.table(st.session_state.db.drop(columns=['الصورة']))
