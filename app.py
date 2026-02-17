import streamlit as st
import pandas as pd
import os
from datetime import datetime
import base64

# --- إعدادات الصفحة ---
st.set_page_config(page_title="الحل للتقنية", layout="wide")

# كود CSS للطباعة والجماليات
st.markdown("""
    <style>
    @media print {
        header, footer, .stTabs, .stButton, .no-print, [data-testid="stHeader"], [data-testid="stSidebar"] {
            display: none !important;
        }
        .print-area { display: block !important; width: 100% !important; direction: rtl !important; }
    }
    .print-area { display: none; }
    .receipt-design { border: 2px solid #000; padding: 15px; direction: rtl; text-align: right; background: white; color: black; font-family: Arial; }
    .sticker-design { border: 1px solid #000; padding: 5px; width: 220px; text-align: center; direction: rtl; background: white; color: black; font-family: Arial; margin: 0 auto; }
    </style>
    """, unsafe_allow_html=True)

DB_FILE = "maintenance_data.csv"

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

def show_print_ui(row, key_suffix):
    u_name = row['الزبون']
    u_phone = row['الهاتف']
    qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=100x100&data=https://brhoom-tech.streamlit.app/?search={u_phone}"
    
    st.write("---")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"""<div class="receipt-design no-print"><h4>📄 معاينة الوصل</h4><p>الزبون: {u_name}<br>الجهاز: {row['الماركة']} {row['الموديل']}</p></div>""", unsafe_allow_html=True)
        if st.button("🖨️ طباعة الوصل", key=f"print_r_{key_suffix}"):
            st.markdown(f'<div class="print-area receipt-design"><h2 style="text-align:center;">الحل للتقنية</h2><p style="text-align:center;">تواصل: 0916206100</p><hr><p><b>رقم الوصل:</b> {row["ID"]}</p><p><b>الزبون:</b> {u_name}</p><p><b>الجهاز:</b> {row["الماركة"]} {row["الموديل"]}</p><p><b>العطل:</b> {row["العطل"]}</p><p><b>التكلفة:</b> {row["التكلفة"]} $</p></div><script>window.print();</script>', unsafe_allow_html=True)
    with c2:
        st.markdown(f"""<div class="sticker-design no-print"><b>{u_name}</b><br>{row['الموديل']}</div>""", unsafe_allow_html=True)
        if st.button("🏷️ طباعة الستيكر", key=f"print_s_{key_suffix}"):
            st.markdown(f'<div class="print-area sticker-design"><b>{u_name}</b><br>{row["الماركة"]} {row["الموديل"]}<br><img src="{qr_url}" width="100"><br>ID: {row["ID"]}</div><script>window.print();</script>', unsafe_allow_html=True)

st.title("🛠️ الحل للتقنية للصيانة")
tabs = st.tabs(["➕ إضافة جهاز", "🔍 بحث وتعديل", "📊 المالية"])

# --- 1. إضافة جهاز ---
with tabs[0]:
    with st.form("add_form"):
        c1, c2 = st.columns(2)
        name = c1.text_input("اسم الزبون")
        phone = c1.text_input("رقم الهاتف")
        brand = c1.selectbox("الماركة", ["iPhone", "Samsung", "Xiaomi", "Infinix", "Techno", "أخرى"])
        model = c2.text_input("الموديل")
        cost = c2.number_input("التكلفة $", min_value=0)
        issue = c2.text_area("العطل")
        img_file = st.file_uploader("📸 إضافة صورة للجهاز", type=["jpg", "png", "jpeg"])
        submitted = st.form_submit_button("✅ حفظ")

    if submitted and name:
        new_id = len(st.session_state.db) + 1001
        img_data = img_to_base64(img_file)
        new_row = {"ID": new_id, "الزبون": name, "الهاتف": phone, "الماركة": brand, "الموديل": model, "العطل": issue, "التكلفة": cost, "سعر_القطع": 0, "الحالة": "تحت الصيانة", "التاريخ": datetime.now().strftime("%Y-%m-%d"), "الصورة": img_data}
        st.session_state.db = pd.concat([st.session_state.db, pd.DataFrame([new_row])], ignore_index=True)
        save_data(st.session_state.db)
        st.success("تم الحفظ!")
        show_print_ui(new_row, "new")

# --- 2. البحث والتعديل ---
with tabs[1]:
    sq = st.text_input("ابحث بالاسم أو الهاتف")
    if sq:
        results = st.session_state.db[st.session_state.db['الزبون'].astype(str).str.contains(sq) | st.session_state.db['الهاتف'].astype(str).str.contains(sq)]
        for idx, row in results.iterrows():
            with st.expander(f"⚙️ {row['الزبون']} - {row['الموديل']}"):
                if row['الصورة']: st.image(base64.b64decode(row['الصورة']), width=150)
                with st.form(f"ed_{idx}"):
                    u_name = st.text_input("الاسم", value=row['الزبون'])
                    u_cost = st.number_input("التكلفة $", value=int(row['التكلفة']))
                    u_status = st.selectbox("الحالة", ["تحت الصيانة", "تم التسليم"], index=0 if row['الحالة']=="تحت الصيانة" else 1)
                    u_img = st.file_uploader("تحديث الصورة", type=["jpg", "png", "jpeg"])
                    if st.form_submit_button("💾 حفظ"):
                        img_d = img_to_base64(u_img) if u_img else row['الصورة']
                        st.session_state.db.loc[idx, ['الزبون', 'التكلفة', 'الحالة', 'الصورة']] = [u_name, u_cost, u_status, img_d]
                        save_data(st.session_state.db)
                        st.rerun()
                show_print_ui(row, f"search_{idx}")

# --- 3. المالية ---
with tabs[2]:
    delivered = st.session_state.db[st.session_state.db['الحالة'] == "تم التسليم"]
    st.metric("صافي الأرباح", f"{delivered['التكلفة'].sum()} $")
    st.dataframe(st.session_state.db.drop(columns=['الصورة']))
