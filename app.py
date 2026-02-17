import streamlit as st
import pandas as pd
import os
from datetime import datetime
import base64

# --- إعدادات الصفحة ---
st.set_page_config(page_title="الحل للتقنية", layout="wide")

# CSS لإصلاح شكل الواجهة فقط (الطباعة سنعتمد فيها على التوليد المباشر)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo&display=swap');
    * { font-family: 'Cairo', sans-serif; direction: rtl; }
    .stMetric { background: #f8f9fa; padding: 10px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    .main-box { border: 1px solid #ddd; padding: 20px; border-radius: 10px; background: white; }
    </style>
    """, unsafe_allow_html=True)

DB_FILE = "tech_solution_final_v12.csv"

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

def img_to_base64(file):
    if file: return base64.b64encode(file.getvalue()).decode()
    return ""

# دالة توليد صفحة الطباعة لمنع ظهور الصفحة البيضاء
def get_print_script(html_content):
    return f"""
    <script>
    var win = window.open('', '', 'height=700,width=900');
    win.document.write('<html><head><title>طباعة</title>');
    win.document.write('<style>body {{ font-family: Cairo, sans-serif; direction: rtl; text-align: right; color: black; background: white; }}</style>');
    win.document.write('</head><body>');
    win.document.write('{html_content}');
    win.document.write('</body></html>');
    win.document.close();
    win.print();
    </script>
    """

st.title("🛠️ منظومة الحل للتقنية - الإصدار المستقر")

tabs = st.tabs(["➕ إضافة جهاز", "🔍 الإدارة والتعديل", "📊 المالية"])

# 1. إضافة جهاز
with tabs[0]:
    with st.form("add_form"):
        c1, c2 = st.columns(2)
        name = c1.text_input("اسم الزبون")
        phone = c1.text_input("رقم الهاتف")
        brand = c2.selectbox("الماركة", ["iPhone", "Samsung", "Xiaomi", "أخرى"])
        model = c2.text_input("الموديل")
        cost = c1.number_input("التكلفة $", min_value=0)
        issue = c2.text_area("وصف العطل")
        img_f = st.file_uploader("📸 صورة الجهاز")
        if st.form_submit_button("✅ حفظ البيانات"):
            if name:
                new_id = len(st.session_state.db) + 1001
                new_row = {"ID": new_id, "الزبون": name, "الهاتف": phone, "الماركة": brand, "الموديل": model, "العطل": issue, "التكلفة": cost, "سعر_القطع": 0, "الحالة": "تحت الصيانة", "التاريخ": datetime.now().strftime("%Y-%m-%d"), "الصورة": img_to_base64(img_f)}
                st.session_state.db = pd.concat([st.session_state.db, pd.DataFrame([new_row])], ignore_index=True)
                save_data(st.session_state.db)
                st.success(f"تم الحفظ! رقم الوصل: {new_id}")

# 2. الإدارة والتعديل الشامل
with tabs[1]:
    sq = st.text_input("🔎 ابحث بالاسم أو رقم الوصل")
    if sq:
        df = st.session_state.db
        results = df[df['الزبون'].astype(str).str.contains(sq) | df['ID'].astype(str).str.contains(sq)]
        for idx, row in results.iterrows():
            with st.expander(f"⚙️ تعديل: {row['الزبون']} (ID: {row['ID']})"):
                if row['الصورة'] and len(str(row['الصورة'])) > 50:
                    st.image(base64.b64decode(row['الصورة']), width=200)
                
                # التعديل الشامل
                with st.form(f"edit_f_{idx}"):
                    col1, col2 = st.columns(2)
                    u_name = col1.text_input("الاسم", value=row['الزبون'])
                    u_phone = col1.text_input("الهاتف", value=row['الهاتف'])
                    u_cost = col2.number_input("التكلفة $", value=int(row['التكلفة']))
                    u_parts = col2.number_input("سعر القطع $", value=int(row['سعر_القطع']))
                    u_status = col1.selectbox("الحالة", ["تحت الصيانة", "تم التسليم"], index=0 if row['الحالة']=="تحت الصيانة" else 1)
                    u_issue = col2.text_area("وصف العطل", value=row['العطل'])
                    u_img = st.file_uploader("تحديث الصورة", key=f"img_{idx}")
                    if st.form_submit_button("💾 حفظ التعديلات"):
                        img_final = img_to_base64(u_img) if u_img else row['الصورة']
                        st.session_state.db.loc[idx] = [row['ID'], u_name, u_phone, row['الماركة'], row['الموديل'], u_issue, u_cost, u_parts, u_status, row['التاريخ'], img_final]
                        save_data(st.session_state.db)
                        st.rerun()

                # --- الطباعة ---
                qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=100x100&data=ID_{row['ID']}"
                
                c_p1, c_p2 = st.columns(2)
                
                # محتوى الوصل
                receipt_html = f"<h2>الحل للتقنية للصيانة</h2><hr><p>رقم الوصل: {row['ID']}</p><p>الزبون: {row['الزبون']}</p><p>الهاتف: {row['الهاتف']}</p><p>الجهاز: {row['الموديل']}</p><p>العطل: {row['العطل']}</p><h3>المطلوب: {row['التكلفة']} $</h3><center><img src='{qr_url}'></center>"
                if c_p1.button(f"🖨️ طباعة الوصل", key=f"btn_r_{idx}"):
                    st.components.v1.html(get_print_script(receipt_html), height=0)

                # محتوى الستيكر
                sticker_html = f"<div style='border:1px solid black; padding:10px; width:200px; text-align:center;'><h3>الحل للتقنية</h3><b>{row['الزبون']}</b><br>{row['الموديل']}<br><img src='{qr_url}' width='80'><br>ID: {row['ID']}</div>"
                if c_p2.button(f"🏷️ طباعة الستيكر", key=f"btn_s_{idx}"):
                    st.components.v1.html(get_print_script(sticker_html), height=0)

# 3. المالية
with tabs[2]:
    delivered = st.session_state.db[st.session_state.db['الحالة'] == "تم التسليم"]
    c1, c2, c3 = st.columns(3)
    c1.metric("💰 المقبوضات", f"{pd.to_numeric(delivered['التكلفة']).sum()} $")
    c2.metric("📉 القطع", f"{pd.to_numeric(delivered['سعر_القطع']).sum()} $")
    profit = pd.to_numeric(delivered['التكلفة']).sum() - pd.to_numeric(delivered['سعر_القطع']).sum()
    c3.metric("✅ الصافي", f"{profit} $")
    st.write("### سجل العمليات")
    st.table(st.session_state.db.drop(columns=['الصورة']))
