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
    
    /* تصميم البطاقات في الواجهة */
    .preview-card {
        border: 1px solid #ddd;
        padding: 15px;
        border-radius: 10px;
        background: #f9f9f9;
        margin-bottom: 10px;
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

DB_FILE = "tech_solution_v25.csv"

def load_data():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE)
    return pd.DataFrame(columns=["ID", "الزبون", "الهاتف", "الماركة", "الموديل", "العطل", "التكلفة", "سعر_القطع", "الحالة", "التاريخ"])

def save_data(df):
    df.to_csv(DB_FILE, index=False)

if 'db' not in st.session_state:
    st.session_state.db = load_data()

# --- دالة الطباعة الذكية (تطبع محتوى محدد فقط) ---
def smart_print(html_content):
    js_code = f"""
    <script>
    var printWindow = window.open('', '', 'height=600,width=800');
    printWindow.document.write('<html><head><title>Print</title>');
    printWindow.document.write('<style>@import url("https://fonts.googleapis.com/css2?family=Cairo&display=swap"); body {{ font-family: "Cairo", sans-serif; direction: rtl; text-align: center; padding: 20px; color: black; }} .box {{ border: 2px solid #000; padding: 20px; }}</style>');
    printWindow.document.write('</head><body>');
    printWindow.document.write('{html_content}');
    printWindow.document.write('</body></html>');
    printWindow.document.close();
    setTimeout(function() {{ printWindow.print(); printWindow.close(); }}, 500);
    </script>
    """
    st.components.v1.html(js_code, height=0)

st.title("🛠️ الحل للتقنية - نظام الصيانة")

tabs = st.tabs(["➕ إضافة جهاز", "🔍 البحث والإدارة", "📊 المالية"])

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
            new_row = {"ID": new_id, "الزبون": name, "الهاتف": phone, "الماركة": brand, "الموديل": model, "العطل": issue, "التكلفة": cost, "سعر_القطع": 0, "الحالة": "تحت الصيانة", "التاريخ": datetime.now().strftime("%Y-%m-%d")}
            st.session_state.db = pd.concat([st.session_state.db, pd.DataFrame([new_row])], ignore_index=True)
            save_data(st.session_state.db)
            st.success(f"تم الحفظ برقم: {new_id}")

with tabs[1]:
    search = st.text_input("🔎 ابحث بالاسم أو ID")
    if search:
        results = st.session_state.db[st.session_state.db['الزبون'].astype(str).str.contains(search) | st.session_state.db['ID'].astype(str).str.contains(search)]
        for idx, row in results.iterrows():
            with st.expander(f"📋 {row['الزبون']} - ID: {row['ID']}"):
                
                # فورم التعديل الشامل
                with st.form(f"edit_{idx}"):
                    c_1, c_2 = st.columns(2)
                    u_cost = c_1.number_input("التكلفة $", value=int(row['التكلفة']))
                    u_parts = c_2.number_input("سعر القطع $", value=int(row['سعر_القطع']))
                    u_status = st.selectbox("الحالة", ["تحت الصيانة", "تم التسليم"], index=0 if row['الحالة']=="تحت الصيانة" else 1)
                    if st.form_submit_button("💾 حفظ التعديلات"):
                        st.session_state.db.loc[idx, ['التكلفة', 'سعر_القطع', 'الحالة']] = [u_cost, u_parts, u_status]
                        save_data(st.session_state.db)
                        st.rerun()

                qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=ID_{row['ID']}"
                
                col_a, col_b = st.columns(2)
                
                # 1. قسم الوصل
                with col_a:
                    st.markdown('<div class="preview-card">📄 معاينة الوصل</div>', unsafe_allow_html=True)
                    if st.button(f"🖨️ طباعة الوصل للزبون", key=f"p_rec_{idx}"):
                        content = f"""
                        <div class='box'>
                            <h1>الحل للتقنية للصيانة</h1>
                            <p>هاتف: 0916206100</p>
                            <hr>
                            <p><b>رقم الإيصال:</b> {row['ID']}</p>
                            <p><b>الزبون:</b> {row['الزبون']}</p>
                            <p><b>الجهاز:</b> {row['الموديل']}</p>
                            <h2>المبلغ المطلوب: {row['التكلفة']} $</h2>
                            <img src='{qr_url}' width='120'>
                        </div>
                        """
                        smart_print(content)

                # 2. قسم الستيكر
                with col_b:
                    st.markdown('<div class="preview-card">🏷️ معاينة الستيكر</div>', unsafe_allow_html=True)
                    if st.button(f"🏷️ طباعة ستيكر الجهاز", key=f"p_stk_{idx}"):
                        content = f"""
                        <div style='border:1px solid #000; padding:10px; width:220px; margin:0 auto;'>
                            <h2 style='margin:0;'>الحل للتقنية</h2>
                            <b>{row['الزبون']}</b><br>
                            <span>{row['الموديل']}</span><br>
                            <img src='{qr_url}' width='100'><br>
                            <b>ID: {row['ID']}</b>
                        </div>
                        """
                        smart_print(content)

with tabs[2]:
    st.write("### ملخص الحسابات")
    st.dataframe(st.session_state.db.drop(columns=['ID' if 'ID' not in st.session_state.db else 'ID']), use_container_width=True)
