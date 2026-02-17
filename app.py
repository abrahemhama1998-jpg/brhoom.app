import streamlit as st
import pandas as pd
import os
from datetime import datetime
import base64

# --- إعدادات الصفحة ---
st.set_page_config(page_title="الحل للتقنية", layout="wide")

# CSS احترافي لإجبار المتصفح على طباعة المحتوى وتجنب الصفحات البيضاء
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo&display=swap');
    * { font-family: 'Cairo', sans-serif; direction: rtl; }
    
    /* تنسيق واجهة المنظومة */
    .stMetric { background: #fdfdfd; padding: 15px; border-radius: 10px; border: 1px solid #eee; }
    
    /* السر في حل الصفحة البيضاء: إخفاء كل شيء وقت الطباعة إلا المحتوى المطلوب */
    @media print {
        header, footer, .stTabs, .stButton, [data-testid="stHeader"], [data-testid="stSidebar"], .no-print {
            display: none !important;
        }
        .printable-area {
            display: block !important;
            width: 100% !important;
            color: black !important;
            background: white !important;
            position: relative;
        }
        /* إخفاء المعاينات التي لا نريد طباعتها حالياً */
        .no-print-this { display: none !important; }
    }
    
    /* شكل المعاينة في المتصفح */
    .receipt-box { border: 2px solid black; padding: 20px; background: white; color: black; border-radius: 8px; margin-bottom: 20px; }
    .sticker-box { border: 1px solid black; padding: 10px; width: 250px; text-align: center; background: white; color: black; margin: 0 auto; }
    </style>
    """, unsafe_allow_html=True)

DB_FILE = "tech_solution_v16.csv"

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

st.title("🛠️ الحل للتقنية - الإدارة الشاملة")

tabs = st.tabs(["➕ استلام جهاز جديد", "🔍 إدارة وبحث وتعديل", "📊 الحسابات المالية"])

# --- 1. استلام جهاز جديد ---
with tabs[0]:
    with st.form("add_form"):
        c1, c2 = st.columns(2)
        name = c1.text_input("اسم الزبون")
        phone = c1.text_input("رقم الهاتف")
        brand = c2.selectbox("الماركة", ["iPhone", "Samsung", "Xiaomi", "Infinix", "Techno", "أخرى"])
        model = c2.text_input("الموديل")
        cost = c1.number_input("التكلفة الكلية $", min_value=0)
        issue = c2.text_area("وصف العطل")
        img_f = st.file_uploader("📸 صورة الجهاز عند الاستلام")
        if st.form_submit_button("✅ حفظ البيانات وإصدار ID"):
            if name:
                new_id = len(st.session_state.db) + 1001
                new_row = {"ID": new_id, "الزبون": name, "الهاتف": phone, "الماركة": brand, "الموديل": model, "العطل": issue, "التكلفة": cost, "سعر_القطع": 0, "الحالة": "تحت الصيانة", "التاريخ": datetime.now().strftime("%Y-%m-%d"), "الصورة": img_to_base64(img_f)}
                st.session_state.db = pd.concat([st.session_state.db, pd.DataFrame([new_row])], ignore_index=True)
                save_data(st.session_state.db)
                st.success(f"تم الحفظ! رقم الوصل: {new_id}")

# --- 2. الإدارة والبحث والتعديل الشامل ---
with tabs[1]:
    search_query = st.text_input("🔎 ابحث بالاسم أو رقم الهاتف أو ID الوصل")
    if search_query:
        df = st.session_state.db
        results = df[df['الزبون'].astype(str).str.contains(search_query) | df['ID'].astype(str).str.contains(search_query)]
        
        for idx, row in results.iterrows():
            with st.expander(f"📋 {row['الزبون']} - {row['الموديل']} (ID: {row['ID']})"):
                
                # عرض الصورة الحالية إن وجدت
                if row['الصورة'] and len(str(row['الصورة'])) > 50:
                    st.image(base64.b64decode(row['الصورة']), width=200, caption="صورة الجهاز")

                # فورم التعديل الشامل (الذي طلبته)
                with st.form(f"edit_form_{idx}"):
                    col1, col2 = st.columns(2)
                    u_name = col1.text_input("الاسم", value=row['الزبون'])
                    u_phone = col1.text_input("الهاتف", value=row['الهاتف'])
                    u_cost = col2.number_input("التكلفة $", value=int(row['التكلفة']))
                    u_parts = col2.number_input("سعر القطع $", value=int(row['سعر_القطع']))
                    u_status = col1.selectbox("الحالة", ["تحت الصيانة", "تم التسليم"], index=0 if row['الحالة']=="تحت الصيانة" else 1)
                    u_issue = col2.text_area("تعديل العطل", value=row['العطل'])
                    u_img = st.file_uploader("تحديث الصورة", key=f"img_update_{idx}")
                    
                    if st.form_submit_button("💾 حفظ التغييرات"):
                        img_final = img_to_base64(u_img) if u_img else row['الصورة']
                        st.session_state.db.loc[idx] = [row['ID'], u_name, u_phone, row['الماركة'], row['الموديل'], u_issue, u_cost, u_parts, u_status, row['التاريخ'], img_final]
                        save_data(st.session_state.db)
                        st.rerun()

                # --- منطقة الطباعة المحسنة ---
                qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=100x100&data=ID_{row['ID']}"
                
                st.write("### 🖨️ طباعة المستندات")
                col_print1, col_print2 = st.columns(2)
                
                with col_print1:
                    # معاينة الوصل
                    st.markdown(f"""
                    <div class="printable-area receipt-box">
                        <h2 style="text-align:center; margin:0;">الحل للتقنية للصيانة</h2>
                        <p style="text-align:center;">رقم التواصل: 0916206100</p>
                        <hr style="border:1px solid black;">
                        <p><b>رقم الوصل:</b> {row['ID']}</p>
                        <p><b>الزبون:</b> {row['الزبون']} | <b>الهاتف:</b> {row['الهاتف']}</p>
                        <p><b>الجهاز:</b> {row['الماركة']} {row['الموديل']}</p>
                        <p><b>العطل:</b> {row['العطل']}</p>
                        <h3 style="text-align:center; background:#f0f0f0; padding:10px;">المبلغ الكلي: {row['التكلفة']} $</h3>
                        <div style="text-align:center;"><img src="{qr_url}"></div>
                    </div>
                    """, unsafe_allow_html=True)
                    if st.button(f"طباعة الوصل {row['ID']}", key=f"p_btn_rec_{idx}"):
                        st.markdown('<script>window.print();</script>', unsafe_allow_html=True)

                with col_print2:
                    # معاينة الستيكر
                    st.markdown(f"""
                    <div class="printable-area sticker-box">
                        <h4 style="margin:5px;">الحل للتقنية</h4>
                        <b>{row['الزبون']}</b><br>
                        <span>{row['الموديل']}</span><br>
                        <img src="{qr_url}" width="80"><br>
                        <b>ID: {row['ID']}</b>
                    </div>
                    """, unsafe_allow_html=True)
                    if st.button(f"طباعة الستيكر {row['ID']}", key=f"p_btn_stk_{idx}"):
                        st.markdown('<script>window.print();</script>', unsafe_allow_html=True)

# --- 3. الحسابات المالية ---
with tabs[2]:
    delivered = st.session_state.db[st.session_state.db['الحالة'] == "تم التسليم"]
    c1, c2, c3 = st.columns(3)
    income = pd.to_numeric(delivered['التكلفة']).sum()
    parts_cost = pd.to_numeric(delivered['سعر_القطع']).sum()
    
    c1.metric("💰 إجمالي الدخل", f"{income} $")
    c2.metric("📉 تكلفة القطع", f"{parts_cost} $")
    c3.metric("✅ صافي الأرباح", f"{income - parts_cost} $")
    
    st.write("---")
    st.write("### سجل الأجهزة")
    st.dataframe(st.session_state.db.drop(columns=['الصورة']), use_container_width=True)
