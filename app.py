import streamlit as st
import pandas as pd
import os
from datetime import datetime
import base64

# --- إعدادات الصفحة ---
st.set_page_config(page_title="الحل للتقنية", layout="wide")

# CSS قوي جداً للطباعة: يحدد ما يظهر وما يختفي بدقة
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo&display=swap');
    * { font-family: 'Cairo', sans-serif; direction: rtl; }
    
    /* عند الطباعة: اخفِ كل شيء إلا منطقة المعاينة */
    @media print {
        header, footer, .stTabs, .stButton, [data-testid="stHeader"], .no-print {
            display: none !important;
        }
        .print-container {
            display: block !important;
            width: 100% !important;
            color: black !important;
            background: white !important;
        }
    }
    
    /* شكل المعاينة في المنظومة */
    .receipt-preview {
        border: 2px solid #000;
        padding: 20px;
        background: #fff;
        color: #000;
        margin-bottom: 20px;
        border-radius: 10px;
    }
    .sticker-preview {
        border: 1px solid #000;
        padding: 10px;
        width: 250px;
        margin: 0 auto;
        text-align: center;
        background: #fff;
        color: #000;
    }
    </style>
    """, unsafe_allow_html=True)

DB_FILE = "solution_v15_stable.csv"

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

st.title("🛠️ الحل للتقنية - الإدارة الاحترافية")

tabs = st.tabs(["➕ استلام جهاز", "🔍 إدارة وبحث وتعديل", "📊 التقارير المالية"])

# --- 1. استلام جهاز ---
with tabs[0]:
    with st.form("add_form"):
        c1, c2 = st.columns(2)
        name = c1.text_input("اسم الزبون")
        phone = c1.text_input("رقم الهاتف")
        brand = c2.selectbox("الماركة", ["iPhone", "Samsung", "Xiaomi", "Infinix", "أخرى"])
        model = c2.text_input("الموديل")
        cost = c1.number_input("التكلفة الكلية $", min_value=0)
        issue = c2.text_area("وصف العطل")
        img_f = st.file_uploader("📸 صورة الجهاز")
        if st.form_submit_button("✅ حفظ البيانات"):
            if name:
                new_id = len(st.session_state.db) + 1001
                new_row = {"ID": new_id, "الزبون": name, "الهاتف": phone, "الماركة": brand, "الموديل": model, "العطل": issue, "التكلفة": cost, "سعر_القطع": 0, "الحالة": "تحت الصيانة", "التاريخ": datetime.now().strftime("%Y-%m-%d"), "الصورة": img_to_base64(img_f)}
                st.session_state.db = pd.concat([st.session_state.db, pd.DataFrame([new_row])], ignore_index=True)
                save_data(st.session_state.db)
                st.success(f"تم الحفظ! رقم الوصل: {new_id}")

# --- 2. إدارة وبحث وتعديل شامل ---
with tabs[1]:
    search = st.text_input("🔎 ابحث بالاسم أو رقم الوصل")
    if search:
        results = st.session_state.db[st.session_state.db['الزبون'].astype(str).str.contains(search) | st.session_state.db['ID'].astype(str).str.contains(search)]
        for idx, row in results.iterrows():
            with st.expander(f"📋 {row['الزبون']} - {row['الموديل']} (ID: {row['ID']})"):
                
                # عرض الصورة
                if row['الصورة'] and len(str(row['الصورة'])) > 50:
                    st.image(base64.b64decode(row['الصورة']), width=200)

                # التعديل الشامل
                with st.form(f"edit_{idx}"):
                    c1, c2 = st.columns(2)
                    u_name = c1.text_input("الاسم", value=row['الزبون'])
                    u_phone = c1.text_input("الهاتف", value=row['الهاتف'])
                    u_cost = c2.number_input("التكلفة $", value=int(row['التكلفة']))
                    u_parts = c2.number_input("سعر القطع $", value=int(row['سعر_القطع']))
                    u_status = c1.selectbox("الحالة", ["تحت الصيانة", "تم التسليم"], index=0 if row['الحالة']=="تحت الصيانة" else 1)
                    u_issue = c2.text_area("العطل", value=row['العطل'])
                    u_img = st.file_uploader("تحديث الصورة", key=f"img_u_{idx}")
                    if st.form_submit_button("💾 حفظ التعديلات"):
                        img_final = img_to_base64(u_img) if u_img else row['الصورة']
                        st.session_state.db.loc[idx] = [row['ID'], u_name, u_phone, row['الماركة'], row['الموديل'], u_issue, u_cost, u_parts, u_status, row['التاريخ'], img_final]
                        save_data(st.session_state.db)
                        st.rerun()

                # --- منطقة الطباعة (معاينة حية) ---
                qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=100x100&data=ID_{row['ID']}"
                
                st.write("### 🖨️ خيارات الطباعة")
                
                # معاينة الوصل
                st.markdown(f"""
                <div class="print-container receipt-preview">
                    <h1 style="text-align:center; margin:0;">الحل للتقنية للصيانة</h1>
                    <p style="text-align:center;">هاتف: 0916206100</p>
                    <hr style="border:1px solid black;">
                    <p><b>رقم الإيصال:</b> {row['ID']}</p>
                    <p><b>الزبون:</b> {row['الزبون']} | <b>الهاتف:</b> {row['الهاتف']}</p>
                    <p><b>الجهاز:</b> {row['الماركة']} {row['الموديل']}</p>
                    <p><b>العطل:</b> {row['العطل']}</p>
                    <h2 style="text-align:center; background:#eee; padding:10px;">المبلغ: {row['التكلفة']} $</h2>
                    <div style="text-align:center;"><img src="{qr_url}"></div>
                </div>
                """, unsafe_allow_html=True)
                if st.button(f"طباعة الوصل #{row['ID']}", key=f"p_rec_{idx}"):
                    st.markdown('<script>window.print();</script>', unsafe_allow_html=True)

                st.write("---")
                
                # معاينة الستيكر
                st.markdown(f"""
                <div class="print-container sticker-preview">
                    <h3 style="margin:5px;">الحل للتقنية</h3>
                    <b>{row['الزبون']}</b><br>
                    <span>{row['الموديل']}</span><br>
                    <img src="{qr_url}" width="90"><br>
                    <b>ID: {row['ID']}</b>
                </div>
                """, unsafe_allow_html=True)
                if st.button(f"طباعة الستيكر #{row['ID']}", key=f"p_stk_{idx}"):
                    st.markdown('<script>window.print();</script>', unsafe_allow_html=True)

# --- 3. المالية ---
with tabs[2]:
    delivered = st.session_state.db[st.session_state.db['الحالة'] == "تم التسليم"]
    c1, c2, c3 = st.columns(3)
    c1.metric("💰 المقبوضات", f"{pd.to_numeric(delivered['التكلفة']).sum()} $")
    c2.metric("📉 تكلفة القطع", f"{pd.to_numeric(delivered['سعر_القطع']).sum()} $")
    profit = pd.to_numeric(delivered['التكلفة']).sum() - pd.to_numeric(delivered['سعر_القطع']).sum()
    c3.metric("✅ صافي الربح", f"{profit} $")
    st.dataframe(st.session_state.db.drop(columns=['الصورة']))
