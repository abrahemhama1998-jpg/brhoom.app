import streamlit as st
import pandas as pd
import os
from datetime import datetime
import base64

# --- إعدادات النظام ---
st.set_page_config(page_title="الحل للتقنية", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo&display=swap');
    * { font-family: 'Cairo', sans-serif; direction: rtl; }
    @media print {
        header, footer, .stTabs, button, .no-print, [data-testid="stHeader"], .stMarkdown:not(.printable) { display: none !important; }
        .printable { display: block !important; width: 100% !important; }
    }
    .printable { display: none; }
    .metric-card { background: white; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); text-align: center; border-bottom: 4px solid #007bff; }
    </style>
    """, unsafe_allow_html=True)

DB_FILE = "fix_final_stable.csv"

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

st.title("🛠️ الحل للتقنية للصيانة")

tabs = st.tabs(["➕ استلام جهاز", "🔍 إدارة وبحث", "📊 المالية"])

# 1. استلام جهاز
with tabs[0]:
    with st.form("add_form"):
        name = st.text_input("اسم الزبون")
        phone = st.text_input("رقم الهاتف")
        c1, c2 = st.columns(2)
        brand = c1.selectbox("الماركة", ["iPhone", "Samsung", "Xiaomi", "أخرى"])
        model = c1.text_input("الموديل")
        cost = c2.number_input("التكلفة $", min_value=0)
        issue = c2.text_area("العطل")
        img_f = st.file_uploader("📸 صورة الجهاز")
        if st.form_submit_button("✅ حفظ البيانات"):
            if name:
                new_id = len(st.session_state.db) + 1001
                new_row = {"ID": new_id, "الزبون": name, "الهاتف": phone, "الماركة": brand, "الموديل": model, "العطل": issue, "التكلفة": cost, "سعر_القطع": 0, "الحالة": "تحت الصيانة", "التاريخ": datetime.now().strftime("%Y-%m-%d"), "الصورة": img_to_base64(img_f)}
                st.session_state.db = pd.concat([st.session_state.db, pd.DataFrame([new_row])], ignore_index=True)
                save_data(st.session_state.db)
                st.success(f"تم الحفظ! رقم الوصل: {new_id}")
                st.info("ابحث عن الزبون في قسم الإدارة للطباعة.")

# 2. إدارة وبحث (هنا الطباعة والتعديل المضمون)
with tabs[1]:
    search_q = st.text_input("🔎 ابحث بالاسم أو رقم الوصل")
    if search_q:
        results = st.session_state.db[st.session_state.db['الزبون'].astype(str).str.contains(search_q) | st.session_state.db['ID'].astype(str).str.contains(search_q)]
        for idx, row in results.iterrows():
            with st.expander(f"📋 {row['الزبون']} - {row['الموديل']} (ID: {row['ID']})"):
                # عرض الصورة
                if row['الصورة'] and len(str(row['الصورة'])) > 50:
                    st.image(base64.b64decode(row['الصورة']), width=200)
                
                # التعديل
                with st.form(f"edit_{idx}"):
                    u_cost = st.number_input("التكلفة $", value=int(row['التكلفة']))
                    u_parts = st.number_input("سعر القطع $", value=int(row['سعر_القطع']))
                    u_status = st.selectbox("الحالة", ["تحت الصيانة", "تم التسليم"], index=0 if row['الحالة']=="تحت الصيانة" else 1)
                    if st.form_submit_button("💾 حفظ التغييرات"):
                        st.session_state.db.loc[idx, ['التكلفة', 'سعر_القطع', 'الحالة']] = [u_cost, u_parts, u_status]
                        save_data(st.session_state.db)
                        st.rerun()

                # تصميم الطباعة (الوصل والستيكر)
                qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=100x100&data=ID_{row['ID']}"
                st.markdown(f"""
                <div class="printable">
                    <div style="border:2px solid #000; padding:20px; direction:rtl; text-align:right;">
                        <h2 style="text-align:center;">الحل للتقنية - وصل استلام</h2>
                        <hr>
                        <p>رقم الوصل: {row['ID']}</p>
                        <p>الزبون: {row['الزبون']}</p>
                        <p>الجهاز: {row['الموديل']}</p>
                        <p>التكلفة: {row['التكلفة']} $</p>
                        <div style="text-align:center;"><img src="{qr_url}"></div>
                    </div>
                    <br><br>
                    <div style="border:1px solid #000; padding:10px; width:200px; text-align:center; margin:0 auto;">
                        <b>{row['الزبون']}</b><br>{row['الموديل']}<br>
                        <img src="{qr_url}" width="80"><br>ID: {row['ID']}
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button(f"🖨️ طباعة الإيصال والستيكر #{row['ID']}", key=f"print_btn_{idx}"):
                    st.components.v1.html("<script>window.print();</script>", height=0)

# 3. المالية
with tabs[2]:
    df_f = st.session_state.db
    delivered = df_f[df_f['الحالة'] == "تم التسليم"]
    c1, c2, c3 = st.columns(3)
    c1.markdown(f"<div class='metric-card'>💰 الإيراد<br><h2>{pd.to_numeric(delivered['التكلفة']).sum()} $</h2></div>", unsafe_allow_html=True)
    c2.markdown(f"<div class='metric-card'>📉 قطع<br><h2>{pd.to_numeric(delivered['سعر_القطع']).sum()} $</h2></div>", unsafe_allow_html=True)
    c3.markdown(f"<div class='metric-card'>✅ ربح<br><h2>{pd.to_numeric(delivered['التكلفة']).sum() - pd.to_numeric(delivered['سعر_القطع']).sum()} $</h2></div>", unsafe_allow_html=True)
    st.table(df_f.drop(columns=['الصورة']))
