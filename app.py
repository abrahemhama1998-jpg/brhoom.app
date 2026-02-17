import streamlit as st
import pandas as pd
import os
from datetime import datetime
import base64

# --- إعدادات الصفحة ---
st.set_page_config(page_title="الحل للتقنية", layout="wide")

# تنسيق CSS للطباعة والواجهة
st.markdown("""
    <style>
    @media print {
        header, footer, .stTabs, .stButton, .no-print, [data-testid="stHeader"], [data-testid="stSidebar"], .stFileUploader {
            display: none !important;
        }
        .print-area { display: block !important; width: 100% !important; direction: rtl !important; }
    }
    .print-area { display: none; }
    .receipt-box { border: 2px solid #000; padding: 20px; direction: rtl; text-align: right; background: white; color: black; font-family: Arial; }
    .sticker-box { border: 1px solid #000; padding: 10px; width: 250px; text-align: center; direction: rtl; background: white; color: black; font-family: Arial; margin: 10px auto; }
    .btn-print {
        display: inline-block; padding: 15px 25px; background-color: #28a745; color: white !important;
        text-decoration: none; border-radius: 10px; font-weight: bold; text-align: center; margin: 10px 0; width: 100%;
    }
    </style>
    """, unsafe_allow_html=True)

DB_FILE = "maintenance_data.csv"

def load_data():
    if os.path.exists(DB_FILE):
        try:
            df = pd.read_csv(DB_FILE)
            for col in ["ID", "الزبون", "الهاتف", "الماركة", "الموديل", "العطل", "التكلفة", "سعر_القطع", "الحالة", "التاريخ", "الصورة"]:
                if col not in df.columns: df[col] = ""
            return df
        except: pass
    return pd.DataFrame(columns=["ID", "الزبون", "الهاتف", "الماركة", "الموديل", "العطل", "التكلفة", "سعر_القطع", "الحالة", "التاريخ", "الصورة"])

def save_data(df):
    df.to_csv(DB_FILE, index=False)

if 'db' not in st.session_state:
    st.session_state.db = load_data()

def img_to_base64(image_file):
    if image_file is not None:
        return base64.b64encode(image_file.getvalue()).decode()
    return ""

def render_print_ui(row, suffix):
    u_name = row['الزبون']
    u_phone = row['الهاتف']
    qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=100x100&data=https://brhoom-tech.streamlit.app/?search={u_phone}"
    
    # محتوى الطباعة المخفي
    st.markdown(f"""
    <div class="print-area">
        <div class="receipt-box">
            <h2 style="text-align:center;">الحل للتقنية للصيانة</h2>
            <p style="text-align:center;">تواصل: 0916206100</p><hr>
            <p><b>رقم الوصل:</b> {row['ID']}</p>
            <p><b>الزبون:</b> {u_name} | <b>الهاتف:</b> {u_phone}</p>
            <p><b>الجهاز:</b> {row['الماركة']} {row['الموديل']}</p>
            <p><b>العطل:</b> {row['العطل']}</p>
            <p><b>التكلفة:</b> {row['التكلفة']} $</p>
            <p><b>التاريخ:</b> {row['التاريخ']}</p>
        </div>
        <div style="page-break-before: always;" class="sticker-box">
            <b>{u_name}</b><br>{row['الماركة']} {row['الموديل']}<br>
            <img src="{qr_url}" width="100"><br>ID: {row['ID']}
        </div>
    </div>
    <a href="javascript:window.print()" class="btn-print no-print">🖨️ اضغط هنا لفتح نافذة الطباعة فوراً</a>
    """, unsafe_allow_html=True)

st.title("🛠️ الحل للتقنية للصيانة")
tabs = st.tabs(["➕ إضافة جهاز", "🔍 بحث وتعديل", "📊 المالية"])

# --- 1. إضافة جهاز ---
with tabs[0]:
    with st.form("add_form", clear_on_submit=False):
        c1, c2 = st.columns(2)
        name = c1.text_input("اسم الزبون")
        phone = c1.text_input("رقم الهاتف")
        brand = c1.selectbox("الماركة", ["iPhone", "Samsung", "Xiaomi", "Infinix", "Techno", "أخرى"])
        model = c2.text_input("الموديل")
        cost = c2.number_input("التكلفة $", min_value=0)
        issue = c2.text_area("العطل")
        img_file = st.file_uploader("📸 تصوير الجهاز", type=["jpg", "png", "jpeg"])
        submitted = st.form_submit_button("✅ حفظ وطباعة")

    if submitted and name:
        new_id = len(st.session_state.db) + 1001
        img_str = img_to_base64(img_file)
        new_row = {"ID": new_id, "الزبون": name, "الهاتف": phone, "الماركة": brand, "الموديل": model, "العطل": issue, "التكلفة": cost, "سعر_القطع": 0, "الحالة": "تحت الصيانة", "التاريخ": datetime.now().strftime("%Y-%m-%d"), "الصورة": img_str}
        st.session_state.db = pd.concat([st.session_state.db, pd.DataFrame([new_row])], ignore_index=True)
        save_data(st.session_state.db)
        st.success(f"تم الحفظ! رقم الوصل: {new_id}")
        render_print_ui(new_row, "new")

# --- 2. البحث والتعديل ---
with tabs[1]:
    search_q = st.text_input("🔎 ابحث بالاسم أو الهاتف")
    if search_q:
        results = st.session_state.db[st.session_state.db['الزبون'].astype(str).str.contains(search_q) | st.session_state.db['الهاتف'].astype(str).str.contains(search_q)]
        for idx, row in results.iterrows():
            with st.expander(f"⚙️ {row['الزبون']} - {row['الموديل']}", expanded=False):
                # فحص الصورة بأمان
                if isinstance(row['الصورة'], str) and len(row['الصورة']) > 10:
                    try:
                        st.image(base64.b64decode(row['الصورة']), width=150)
                    except: st.warning("الصورة بها خلل")
                
                with st.form(f"edit_{idx}"):
                    u_name = st.text_input("الاسم", value=row['الزبون'])
                    u_phone = st.text_input("الهاتف", value=row['الهاتف'])
                    u_cost = st.number_input("التكلفة $", value=int(row['التكلفة']) if row['التكلفة'] else 0)
                    u_status = st.selectbox("الحالة", ["تحت الصيانة", "تم التسليم"], index=0 if row['الحالة']=="تحت الصيانة" else 1)
                    u_img = st.file_uploader("تحديث الصورة", type=["jpg", "png", "jpeg"])
                    
                    if st.form_submit_button("💾 حفظ التعديلات"):
                        img_up = img_to_base64(u_img) if u_img else row['الصورة']
                        st.session_state.db.at[idx, 'الزبون'] = u_name
                        st.session_state.db.at[idx, 'الهاتف'] = u_phone
                        st.session_state.db.at[idx, 'التكلفة'] = u_cost
                        st.session_state.db.at[idx, 'الحالة'] = u_status
                        st.session_state.db.at[idx, 'الصورة'] = img_up
                        save_data(st.session_state.db)
                        st.rerun()
                render_print_ui(row, f"search_{idx}")

# --- 3. المالية ---
with tabs[2]:
    delivered = st.session_state.db[st.session_state.db['الحالة'] == "تم التسليم"]
    st.metric("إجمالي الربح", f"{delivered['التكلفة'].astype(float).sum()} $")
    st.dataframe(st.session_state.db.drop(columns=['الصورة']))
