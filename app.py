import streamlit as st
import pandas as pd
import os
from datetime import datetime
import base64
import streamlit.components.v1 as components

# --- إعدادات الصفحة ---
st.set_page_config(page_title="الحل للتقنية", layout="wide")

# كود CSS لتنسيق الطباعة
st.markdown("""
    <style>
    @media print {
        header, footer, .stTabs, .stButton, .no-print, [data-testid="stHeader"], [data-testid="stSidebar"] {
            display: none !important;
        }
    }
    .receipt-style { border: 2px solid #000; padding: 15px; direction: rtl; text-align: right; font-family: Arial; }
    .sticker-style { border: 1px solid #000; padding: 5px; width: 200px; text-align: center; direction: rtl; font-family: Arial; }
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

st.title("🛠️ الحل للتقنية للصيانة")

tabs = st.tabs(["➕ إضافة جهاز", "🔍 بحث وتعديل شامل", "📊 المالية"])

# --- 1. إضافة جهاز ---
with tabs[0]:
    with st.form("add_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        name = c1.text_input("اسم الزبون")
        phone = c1.text_input("رقم الهاتف")
        brand = c1.selectbox("الماركة", ["iPhone", "Samsung", "Xiaomi", "Infinix", "Techno", "أخرى"])
        model = c2.text_input("الموديل")
        cost = c2.number_input("التكلفة $", min_value=0)
        issue = c2.text_area("وصف العطل")
        if st.form_submit_button("✅ حفظ الجهاز"):
            if name and phone:
                new_id = len(st.session_state.db) + 1001
                new_entry = {"ID": new_id, "الزبون": name, "الهاتف": phone, "الماركة": brand, "الموديل": model, "العطل": issue, "التكلفة": cost, "سعر_القطع": 0, "الحالة": "تحت الصيانة", "التاريخ": datetime.now().strftime("%Y-%m-%d"), "الصورة": ""}
                st.session_state.db = pd.concat([st.session_state.db, pd.DataFrame([new_entry])], ignore_index=True)
                save_data(st.session_state.db)
                st.success("تم الحفظ!")

# --- 2. البحث والتعديل والطباعة ---
with tabs[1]:
    search_query = st.text_input("ابحث بالاسم أو الهاتف", value=st.query_params.get("search", ""))
    if search_query:
        df = st.session_state.db
        results = df[df['الزبون'].astype(str).str.contains(search_query) | df['الهاتف'].astype(str).str.contains(search_query)]
        for idx, row in results.iterrows():
            with st.expander(f"📋 {row['الزبون']} - {row['الموديل']} (ID: {row['ID']})", expanded=True):
                
                with st.form(f"edit_f_{idx}"):
                    c1, c2 = st.columns(2)
                    u_name = c1.text_input("الاسم", value=row['الزبون'])
                    u_phone = c1.text_input("الهاتف", value=row['الهاتف'])
                    u_cost = c2.number_input("التكلفة $", value=int(row['التكلفة']))
                    u_parts = c2.number_input("سعر القطع $", value=int(row.get('سعر_القطع', 0)))
                    u_issue = st.text_area("العطل", value=row['العطل'])
                    u_status = st.selectbox("الحالة", ["تحت الصيانة", "تم التسليم"], index=0 if row['الحالة']=="تحت الصيانة" else 1)
                    
                    cb1, cb2 = st.columns(2)
                    if cb1.form_submit_button("💾 حفظ التعديلات"):
                        st.session_state.db.loc[idx, ['الزبون', 'الهاتف', 'التكلفة', 'سعر_القطع', 'العطل', 'الحالة']] = [u_name, u_phone, u_cost, u_parts, u_issue, u_status]
                        save_data(st.session_state.db)
                        st.success("تم التحديث")
                        st.rerun()
                    if cb2.form_submit_button("🗑️ حذف"):
                        st.session_state.db = st.session_state.db.drop(idx)
                        save_data(st.session_state.db)
                        st.rerun()

                # --- أزرار الطباعة الفورية المنفصلة ---
                st.write("---")
                qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=100x100&data=https://brhoom-tech.streamlit.app/?search={u_phone}"
                
                # HTML للوصل
                receipt_html = f"""
                <button onclick="window.print()" style="width:100%; padding:12px; background-color:#28a745; color:white; border:none; border-radius:8px; cursor:pointer; font-weight:bold; margin-bottom:10px;">🖨️ طباعة وصل الزبون</button>
                <div class="no-print" style="display:none;"></div>
                <div class="receipt-style" style="display:none; display:block-only-on-print;">
                    <h2 style="text-align:center;">الحل للتقنية للصيانة</h2>
                    <p style="text-align:center;">تواصل: 0916206100</p><hr>
                    <p><b>رقم الوصل:</b> {row['ID']}</p>
                    <p><b>الزبون:</b> {u_name} | <b>الهاتف:</b> {u_phone}</p>
                    <p><b>الجهاز:</b> {row['الماركة']} {row['الموديل']}</p>
                    <p><b>العطل:</b> {u_issue}</p>
                    <p><b>التكلفة:</b> {u_cost} $</p>
                    <p><b>التاريخ:</b> {row['التاريخ']}</p>
                </div>
                <style>
                    @media print {{ .receipt-style {{ display: block !important; }} .sticker-style {{ display: none !important; }} }}
                </style>
                """
                
                # HTML للستيكر
                sticker_html = f"""
                <button onclick="window.print()" style="width:100%; padding:12px; background-color:#007bff; color:white; border:none; border-radius:8px; cursor:pointer; font-weight:bold;">🏷️ طباعة ستيكر الجهاز</button>
                <div class="sticker-style" style="display:none; display:block-only-on-print;">
                    <b>{u_name}</b><br>{row['الماركة']} {row['الموديل']}<br>
                    <img src="{qr_url}" width="80"><br>ID: {row['ID']}
                </div>
                <style>
                    @media print {{ .sticker-style {{ display: block !important; }} .receipt-style {{ display: none !important; }} }}
                </style>
                """
                
                c_p1, c_p2 = st.columns(2)
                with c_p1: components.html(receipt_html, height=70)
                with c_p2: components.html(sticker_html, height=70)

# --- 3. المالية ---
with tabs[2]:
    delivered = st.session_state.db[st.session_state.db['الحالة'] == "تم التسليم"]
    st.metric("صافي الربح", f"{delivered['التكلفة'].sum() - delivered['سعر_القطع'].sum()} $")
    st.dataframe(st.session_state.db.drop(columns=['الصورة']))
