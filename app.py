import streamlit as st
import pandas as pd
import os
from datetime import datetime
import urllib.parse
import base64

# --- إعدادات الصفحة ---
st.set_page_config(page_title="الحل للتقنية", layout="wide")

# كود CSS للطباعة
st.markdown("""
    <style>
    @media print {
        header, footer, .stTabs, .stButton, .no-print, [data-testid="stHeader"], [data-testid="stSidebar"] {
            display: none !important;
        }
        .printable { display: block !important; direction: rtl !important; }
    }
    .printable { display: none; }
    .receipt-box { border: 2px solid #000; padding: 20px; direction: rtl; text-align: right; background: white; color: black; }
    .sticker-box { border: 1px solid #000; padding: 5px; width: 220px; text-align: center; direction: rtl; background: white; color: black; }
    .print-link {
        display: inline-block; padding: 10px 20px; background-color: #4CAF50; color: white !important;
        text-decoration: none; border-radius: 5px; font-weight: bold; margin: 5px;
    }
    </style>
    """, unsafe_allow_html=True)

DB_FILE = "maintenance_data.csv"
APP_URL = "https://brhoom-tech.streamlit.app"

def load_data():
    if os.path.exists(DB_FILE):
        try:
            df = pd.read_csv(DB_FILE)
            if "الصورة" not in df.columns: df["الصورة"] = ""
            return df
        except: return pd.DataFrame(columns=["ID", "الزبون", "الهاتف", "الماركة", "الموديل", "العطل", "التكلفة", "سعر_القطع", "الحالة", "التاريخ", "الصورة"])
    return pd.DataFrame(columns=["ID", "الزبون", "الهاتف", "الماركة", "الموديل", "العطل", "التكلفة", "سعر_القطع", "الحالة", "التاريخ", "الصورة"])

def save_data(df):
    df.to_csv(DB_FILE, index=False)

if 'db' not in st.session_state:
    st.session_state.db = load_data()

def img_to_base64(image_file):
    if image_file: return base64.b64encode(image_file.getvalue()).decode()
    return ""

st.title("🛠️ الحل للتقنية للصيانة")

tabs = st.tabs(["➕ إضافة جهاز", "🔍 بحث وتعديل شامل", "📊 المالية"])

# --- 1. إضافة جهاز جديد ---
with tabs[0]:
    with st.form("add_form"):
        c1, c2 = st.columns(2)
        name = c1.text_input("اسم الزبون")
        phone = c1.text_input("رقم الهاتف")
        brand = c1.selectbox("الماركة", ["iPhone", "Samsung", "Xiaomi", "Infinix", "Techno", "أخرى"])
        model = c2.text_input("الموديل")
        cost = c2.number_input("التكلفة $", min_value=0)
        issue = c2.text_area("وصف العطل")
        img_upload = st.file_uploader("📸 تصوير/إضافة صورة للجهاز", type=["jpg", "png", "jpeg"])
        
        if st.form_submit_button("✅ حفظ الجهاز"):
            if name and phone:
                new_id = len(st.session_state.db) + 1001
                img_data = img_to_base64(img_upload)
                new_entry = {"ID": new_id, "الزبون": name, "الهاتف": phone, "الماركة": brand, "الموديل": model, "العطل": issue, "التكلفة": cost, "سعر_القطع": 0, "الحالة": "تحت الصيانة", "التاريخ": datetime.now().strftime("%Y-%m-%d"), "الصورة": img_data}
                st.session_state.db = pd.concat([st.session_state.db, pd.DataFrame([new_entry])], ignore_index=True)
                save_data(st.session_state.db)
                st.success("تم الحفظ!")

# --- 2. البحث والتعديل الشامل ---
with tabs[1]:
    search_query = st.text_input("ابحث بالاسم أو الهاتف", value=st.query_params.get("search", ""))
    if search_query:
        df = st.session_state.db
        results = df[df['الزبون'].astype(str).str.contains(search_query) | df['الهاتف'].astype(str).str.contains(search_query)]
        
        for idx, row in results.iterrows():
            with st.expander(f"📋 {row['الزبون']} - {row['الموديل']} (ID: {row['ID']})", expanded=True):
                # عرض الصورة
                if str(row.get('الصورة')) != "nan" and row.get('الصورة') != "":
                    st.image(base64.b64decode(row['الصورة']), width=250)

                with st.form(f"edit_{idx}"):
                    c1, c2 = st.columns(2)
                    u_name = c1.text_input("الاسم", value=row['الزبون'])
                    u_phone = c1.text_input("الهاتف", value=row['الهاتف'])
                    u_brand = c1.selectbox("الماركة", ["iPhone", "Samsung", "Xiaomi", "Infinix", "Techno", "أخرى"], index=0)
                    u_model = c2.text_input("الموديل", value=row['الموديل'])
                    u_cost = c2.number_input("التكلفة $", value=int(row['التكلفة']))
                    u_parts = c2.number_input("سعر القطع $", value=int(row.get('سعر_القطع', 0)))
                    u_issue = st.text_area("العطل", value=row['العطل'])
                    u_status = st.selectbox("الحالة", ["تحت الصيانة", "تم التسليم"], index=0 if row['الحالة']=="تحت الصيانة" else 1)
                    u_img = st.file_uploader("تحديث الصورة", type=["jpg", "png", "jpeg"], key=f"up_{idx}")
                    
                    if st.form_submit_button("💾 حفظ التعديلات"):
                        img_data = img_to_base64(u_img) if u_img else row['الصورة']
                        st.session_state.db.loc[idx] = [row['ID'], u_name, u_phone, u_brand, u_model, u_issue, u_cost, u_parts, u_status, row['التاريخ'], img_data]
                        save_data(st.session_state.db)
                        st.success("تم التحديث!")
                        st.rerun()

                # --- منطقة الطباعة ---
                st.write("---")
                qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data={APP_URL}/?search={u_phone}"
                
                # إعداد المحتوى للطباعة
                st.markdown(f"""
                <div class="printable receipt-box">
                    <h2 style="text-align:center;">الحل للتقنية للصيانة</h2>
                    <p><b>رقم الوصل:</b> {row['ID']} | <b>الزبون:</b> {u_name}</p>
                    <p><b>الجهاز:</b> {u_brand} {u_model}</p>
                    <p><b>العطل:</b> {u_issue}</p>
                    <p><b>التكلفة:</b> {u_cost} $</p>
                    <p><b>التاريخ:</b> {row['التاريخ']}</p>
                </div>
                <div class="printable sticker-box">
                    <b>{u_name}</b><br>{u_brand} {u_model}<br>
                    <img src="{qr_url}" width="90"><br>ID: {row['ID']}
                </div>
                <a href="javascript:window.print()" class="print-link">🖨️ اضغط هنا لفتح نافذة الطباعة</a>
                """, unsafe_allow_html=True)

# --- 3. المالية ---
with tabs[2]:
    delivered = st.session_state.db[st.session_state.db['الحالة'] == "تم التسليم"]
    st.metric("صافي الربح", f"{delivered['التكلفة'].sum() - delivered['سعر_القطع'].sum()} $")
    st.dataframe(st.session_state.db.drop(columns=['الصورة']))
