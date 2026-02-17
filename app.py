import streamlit as st
import pandas as pd
import os
from datetime import datetime

# --- إعدادات الصفحة ---
st.set_page_config(page_title="الحل للتقنية", layout="wide")

# CSS البسيط اللي اشتغل معاك أول مرة
st.markdown("""
    <style>
    @media print {
        header, footer, .stTabs, button, .no-print, [data-testid="stHeader"] {
            display: none !important;
        }
        .print-area { display: block !important; direction: rtl !important; }
    }
    .print-area { display: none; }
    .receipt-box { border: 2px solid black; padding: 15px; margin-bottom: 10px; direction: rtl; text-align: right; }
    .sticker-box { border: 1px solid black; padding: 5px; width: 200px; text-align: center; margin: 10px auto; direction: rtl; }
    </style>
    """, unsafe_allow_html=True)

DB_FILE = "maintenance_simple_v7.csv"

def load_data():
    if os.path.exists(DB_FILE):
        df = pd.read_csv(DB_FILE)
        for col in ["ID", "الزبون", "الهاتف", "الماركة", "الموديل", "العطل", "التكلفة", "سعر_القطع", "الحالة", "التاريخ"]:
            if col not in df.columns: df[col] = 0 if "سعر" in col or "التكلفة" in col else ""
        return df
    return pd.DataFrame(columns=["ID", "الزبون", "الهاتف", "الماركة", "الموديل", "العطل", "التكلفة", "سعر_القطع", "الحالة", "التاريخ"])

def save_data(df):
    df.to_csv(DB_FILE, index=False)

if 'db' not in st.session_state:
    st.session_state.db = load_data()

st.title("🛠️ الحل للتقنية - الإدارة السريعة")

tabs = st.tabs(["➕ إضافة جهاز", "🔍 بحث وتعديل", "📊 المالية"])

# دالة عرض الطباعة (الوصل والستيكر تحت بعض في نفس الورقة)
def render_simple_print(row):
    qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=80x80&data=ID_{row['ID']}"
    st.markdown(f"""
    <div class="print-area">
        <div class="receipt-box">
            <h2 style="text-align:center; margin:0;">الحل للتقنية للصيانة</h2>
            <p style="text-align:center; margin:0;">0916206100</p><hr>
            <p><b>رقم الوصل:</b> {row['ID']} | <b>الزبون:</b> {row['الزبون']}</p>
            <p><b>الجهاز:</b> {row['الماركة']} {row['الموديل']}</p>
            <p><b>العطل:</b> {row['العطل']}</p>
            <p><b>المبلغ:</b> {row['التكلفة']} $</p>
        </div>
        <div class="sticker-box">
            <b style="font-size:14px;">{row['الزبون']}</b><br>
            <span style="font-size:12px;">{row['الموديل']}</span><br>
            <img src="{qr_url}" width="70"><br>
            <b style="font-size:12px;">ID: {row['ID']}</b>
        </div>
    </div>
    """, unsafe_allow_html=True)

# 1. إضافة جهاز
with tabs[0]:
    with st.form("add_form", clear_on_submit=False):
        name = st.text_input("اسم الزبون")
        phone = st.text_input("رقم الهاتف")
        c1, c2 = st.columns(2)
        brand = c1.selectbox("الماركة", ["iPhone", "Samsung", "Xiaomi", "Infinix", "Techno", "أخرى"])
        model = c1.text_input("الموديل")
        cost = c2.number_input("التكلفة $", min_value=0)
        issue = c2.text_area("العطل")
        submitted = st.form_submit_button("✅ حفظ")

    if submitted and name:
        new_id = len(st.session_state.db) + 1001
        new_row = {"ID": new_id, "الزبون": name, "الهاتف": phone, "الماركة": brand, "الموديل": model, "العطل": issue, "التكلفة": cost, "سعر_القطع": 0, "الحالة": "تحت الصيانة", "التاريخ": datetime.now().strftime("%Y-%m-%d")}
        st.session_state.db = pd.concat([st.session_state.db, pd.DataFrame([new_row])], ignore_index=True)
        save_data(st.session_state.db)
        st.success(f"تم الحفظ! رقم الوصل: {new_id}")
        render_simple_print(new_row)
        if st.button("🖨️ طباعة الآن"):
            st.markdown('<script>window.print();</script>', unsafe_allow_html=True)

# 2. بحث وتعديل كامل
with tabs[1]:
    search = st.text_input("🔎 ابحث بالاسم")
    if search:
        results = st.session_state.db[st.session_state.db['الزبون'].astype(str).str.contains(search)]
        for idx, row in results.iterrows():
            with st.expander(f"⚙️ {row['الزبون']} - {row['ID']}"):
                with st.form(f"edit_{idx}"):
                    u_name = st.text_input("الاسم", value=row['الزبون'])
                    u_phone = st.text_input("الهاتف", value=row['الهاتف'])
                    u_cost = st.number_input("التكلفة $", value=int(row['التكلفة']))
                    u_parts = st.number_input("سعر القطع $", value=int(row['سعر_القطع']))
                    u_issue = st.text_area("العطل", value=row['العطل'])
                    u_status = st.selectbox("الحالة", ["تحت الصيانة", "تم التسليم"], index=0 if row['الحالة']=="تحت الصيانة" else 1)
                    if st.form_submit_button("💾 حفظ التعديلات"):
                        st.session_state.db.loc[idx, ['الزبون', 'الهاتف', 'التكلفة', 'سعر_القطع', 'العطل', 'الحالة']] = [u_name, u_phone, u_cost, u_parts, u_issue, u_status]
                        save_data(st.session_state.db)
                        st.rerun()
                
                render_simple_print(row)
                if st.button(f"🖨️ طباعة #{row['ID']}", key=f"p_{idx}"):
                    st.markdown('<script>window.print();</script>', unsafe_allow_html=True)

# 3. المالية
with tabs[2]:
    st.dataframe(st.session_state.db, use_container_width=True)
