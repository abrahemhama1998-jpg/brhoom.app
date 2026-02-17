import streamlit as st
import pandas as pd
import os
from datetime import datetime
import base64

# --- إعدادات الصفحة ---
st.set_page_config(page_title="الحل للتقنية", layout="wide")

# كود CSS للتحكم الكامل في الطباعة
st.markdown("""
    <style>
    /* إخفاء كل شيء عند الطباعة إلا القسم المطلوب */
    @media print {
        header, footer, .stTabs, .stButton, .no-print, [data-testid="stHeader"], [data-testid="stSidebar"] {
            display: none !important;
        }
        .print-area { display: block !important; width: 100% !important; direction: rtl !important; }
    }
    .print-area { display: none; }
    .receipt-design { border: 2px solid #000; padding: 20px; direction: rtl; text-align: right; background: white; color: black; font-family: Arial; }
    .sticker-design { border: 1px solid #000; padding: 10px; width: 250px; text-align: center; direction: rtl; background: white; color: black; font-family: Arial; }
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
        name = c1.text_input("👤 اسم الزبون")
        phone = c1.text_input("📞 رقم الهاتف")
        brand = c1.selectbox("📦 الماركة", ["iPhone", "Samsung", "Xiaomi", "Infinix", "Techno", "أخرى"])
        model = c2.text_input("📱 الموديل")
        cost = c2.number_input("💰 التكلفة المتفق عليها $", min_value=0)
        issue = c2.text_area("📝 وصف العطل")
        if st.form_submit_button("✅ حفظ البيانات"):
            if name and phone:
                new_id = len(st.session_state.db) + 1001
                new_entry = {"ID": new_id, "الزبون": name, "الهاتف": phone, "الماركة": brand, "الموديل": model, "العطل": issue, "التكلفة": cost, "سعر_القطع": 0, "الحالة": "تحت الصيانة", "التاريخ": datetime.now().strftime("%Y-%m-%d"), "الصورة": ""}
                st.session_state.db = pd.concat([st.session_state.db, pd.DataFrame([new_entry])], ignore_index=True)
                save_data(st.session_state.db)
                st.success(f"تم تسجيل الجهاز برقم: {new_id}")

# --- 2. البحث والتعديل والطباعة ---
with tabs[1]:
    search_q = st.text_input("🔎 ابحث بالاسم أو رقم الهاتف")
    if search_q:
        df = st.session_state.db
        results = df[df['الزبون'].astype(str).str.contains(search_q) | df['الهاتف'].astype(str).str.contains(search_q)]
        
        for idx, row in results.iterrows():
            with st.expander(f"⚙️ تعديل: {row['الزبون']} - {row['الموديل']}", expanded=True):
                # نموذج التعديل
                with st.form(f"edit_{idx}"):
                    c1, c2 = st.columns(2)
                    u_name = c1.text_input("الاسم", value=row['الزبون'])
                    u_phone = c1.text_input("الهاتف", value=row['الهاتف'])
                    u_cost = c2.number_input("التكلفة $", value=int(row['التكلفة']))
                    u_parts = c2.number_input("سعر القطع $", value=int(row.get('سعر_القطع', 0)))
                    u_issue = st.text_area("العطل", value=row['العطل'])
                    u_status = st.selectbox("الحالة", ["تحت الصيانة", "تم التسليم"], index=0 if row['الحالة']=="تحت الصيانة" else 1)
                    
                    col_b1, col_b2 = st.columns(2)
                    if col_b1.form_submit_button("💾 حفظ التعديلات"):
                        st.session_state.db.loc[idx, ['الزبون', 'الهاتف', 'التكلفة', 'سعر_القطع', 'العطل', 'الحالة']] = [u_name, u_phone, u_cost, u_parts, u_issue, u_status]
                        save_data(st.session_state.db)
                        st.rerun()
                    if col_b2.form_submit_button("🗑️ حذف الجهاز"):
                        st.session_state.db = st.session_state.db.drop(idx)
                        save_data(st.session_state.db)
                        st.rerun()

                # --- منطقة الطباعة ---
                st.write("---")
                st.subheader("🖨️ قسم الطباعة")
                
                qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=100x100&data=https://brhoom-tech.streamlit.app/?search={u_phone}"
                
                # معاينة الوصل
                st.markdown(f"""
                <div class="receipt-design no-print">
                    <h3 style="text-align:center;">إيصال زبون - الحل للتقنية</h3>
                    <p><b>رقم التواصل:</b> 0916206100</p>
                    <p><b>الزبون:</b> {u_name} | <b>الهاتف:</b> {u_phone}</p>
                    <p><b>الجهاز:</b> {row['الماركة']} {row['الموديل']}</p>
                    <p><b>العطل:</b> {u_issue}</p>
                    <p><b>التكلفة:</b> {u_cost} $</p>
                </div>
                <div class="print-area receipt-design">
                    <h2 style="text-align:center;">الحل للتقنية للصيانة</h2>
                    <p style="text-align:center;">تواصل: 0916206100</p><hr>
                    <p><b>رقم الوصل:</b> {row['ID']}</p>
                    <p><b>الزبون:</b> {u_name} | <b>الهاتف:</b> {u_phone}</p>
                    <p><b>الجهاز:</b> {row['الماركة']} {row['الموديل']}</p>
                    <p><b>العطل:</b> {u_issue}</p>
                    <p><b>التكلفة:</b> {u_cost} $</p>
                    <p><b>التاريخ:</b> {row['التاريخ']}</p>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button(f"📄 اطبع وصل الزبون الآن", key=f"btn_r_{idx}"):
                    st.markdown('<script>window.print();</script>', unsafe_allow_html=True)
                
                st.write("---")
                
                # معاينة الستيكر
                st.markdown(f"""
                <div class="sticker-design no-print" style="margin: auto;">
                    <b>{u_name}</b><br>{row['الماركة']} {row['الموديل']}<br>
                    <img src="{qr_url}" width="80"><br>ID: {row['ID']}
                </div>
                <div class="print-area sticker-design">
                    <b>{u_name}</b><br>{row['الماركة']} {row['الموديل']}<br>
                    <img src="{qr_url}" width="100"><br>ID: {row['ID']}
                </div>
                """, unsafe_allow_html=True)

                if st.button(f"🏷️ اطبع ستيكر الجهاز الآن", key=f"btn_s_{idx}"):
                    st.markdown('<script>window.print();</script>', unsafe_allow_html=True)

# --- 3. المالية ---
with tabs[2]:
    delivered = st.session_state.db[st.session_state.db['الحالة'] == "تم التسليم"]
    st.metric("إجمالي الأرباح", f"{delivered['التكلفة'].sum() - delivered['سعر_القطع'].sum()} $")
    st.dataframe(st.session_state.db.drop(columns=['الصورة']))
