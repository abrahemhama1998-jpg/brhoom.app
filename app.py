import streamlit as st
import pandas as pd
import os
from datetime import datetime
import base64

# --- إعدادات الصفحة ---
st.set_page_config(page_title="الحل للتقنية | المطور", layout="wide")

# CSS احترافي للطباعة والواجهة
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    * { font-family: 'Cairo', sans-serif; direction: rtl; }
    
    /* تصميم البطاقات */
    .stExpander { background-color: white !important; border-radius: 10px !important; box-shadow: 0 2px 5px rgba(0,0,0,0.1) !important; }
    
    /* تنسيق المعاينة قبل الطباعة */
    .preview-box { border: 1px solid #ddd; padding: 15px; border-radius: 8px; background: #fdfdfd; margin-bottom: 10px; }
    
    /* إعدادات الطباعة */
    @media print {
        header, footer, .stTabs, .stButton, .no-print, [data-testid="stHeader"], .stMarkdown:not(.printable) {
            display: none !important;
        }
        .printable { display: block !important; width: 100% !important; }
    }
    .printable { display: none; }
    </style>
    """, unsafe_allow_html=True)

DB_FILE = "advanced_fix_v8.csv"

def load_data():
    if os.path.exists(DB_FILE):
        df = pd.read_csv(DB_FILE)
        for col in ["ID", "الزبون", "الهاتف", "الماركة", "الموديل", "العطل", "التكلفة", "سعر_القطع", "الحالة", "التاريخ", "الصورة"]:
            if col not in df.columns: df[col] = ""
        return df
    return pd.DataFrame(columns=["ID", "الزبون", "الهاتف", "الماركة", "الموديل", "العطل", "التكلفة", "سعر_القطع", "الحالة", "التاريخ", "الصورة"])

def save_data(df):
    df.to_csv(DB_FILE, index=False)

if 'db' not in st.session_state:
    st.session_state.db = load_data()

def img_to_base64(image_file):
    if image_file: return base64.b64encode(image_file.getvalue()).decode()
    return ""

# دالة المعاينة والطباعة
def render_ui_with_print(row, unique_id):
    qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=100x100&data=ID_{row['ID']}"
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📄 معاينة الوصل")
        st.markdown(f"""
        <div class="preview-box">
            <h4 style="text-align:center;">الحل للتقنية</h4>
            <p><b>رقم:</b> {row['ID']} | <b>الزبون:</b> {row['الزبون']}</p>
            <p><b>الجهاز:</b> {row['الموديل']}</p>
            <p><b>التكلفة:</b> {row['التكلفة']} $</p>
            <img src="{qr_url}" width="60">
        </div>
        <div class="printable">
            <div style="border:2px solid #000; padding:20px; text-align:right; direction:rtl;">
                <h1 style="text-align:center;">إيصال صيانة - الحل للتقنية</h1>
                <hr>
                <p style="font-size:20px;"><b>رقم الوصل:</b> {row['ID']}</p>
                <p style="font-size:20px;"><b>الزبون:</b> {row['الزبون']} | <b>هاتف:</b> {row['الهاتف']}</p>
                <p style="font-size:20px;"><b>الجهاز:</b> {row['الماركة']} {row['الموديل']}</p>
                <p style="font-size:20px;"><b>العطل:</b> {row['العطل']}</p>
                <p style="font-size:20px;"><b>المبلغ:</b> {row['التكلفة']} $</p>
                <div style="text-align:center;"><img src="{qr_url}" width="120"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button(f"🖨️ طباعة الوصل", key=f"p_rec_{unique_id}"):
            st.markdown('<script>window.print();</script>', unsafe_allow_html=True)

    with col2:
        st.markdown("### 🏷️ معاينة الستيكر")
        st.markdown(f"""
        <div class="preview-box" style="text-align:center;">
            <b>{row['الزبون']}</b><br>{row['الموديل']}<br>
            <img src="{qr_url}" width="60"><br>ID: {row['ID']}
        </div>
        <div class="printable">
            <div style="border:1px solid #000; padding:10px; width:250px; text-align:center; margin: 0 auto; direction:rtl;">
                <h2 style="margin:5px;">الحل للتقنية</h2>
                <b style="font-size:18px;">{row['الزبون']}</b><br>
                <span style="font-size:16px;">{row['الموديل']}</span><br>
                <img src="{qr_url}" width="100"><br>
                <b>ID: {row['ID']}</b>
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button(f"🖨️ طباعة الستيكر", key=f"p_stk_{unique_id}"):
            st.markdown('<script>window.print();</script>', unsafe_allow_html=True)

# --- الواجهة ---
st.title("🛠️ منظومة الحل للتقنية الاحترافية")

tabs = st.tabs(["➕ إضافة جهاز", "🔍 بحث وتعديل شامل"])

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
        img_f = st.file_uploader("📸 إضافة صورة للجهاز", type=["jpg", "png", "jpeg"])
        submitted = st.form_submit_button("✅ حفظ البيانات")

    if submitted and name:
        new_id = len(st.session_state.db) + 1001
        img_str = img_to_base64(img_f)
        new_row = {"ID": new_id, "الزبون": name, "الهاتف": phone, "الماركة": brand, "الموديل": model, "العطل": issue, "التكلفة": cost, "سعر_القطع": 0, "الحالة": "تحت الصيانة", "التاريخ": datetime.now().strftime("%Y-%m-%d"), "الصورة": img_str}
        st.session_state.db = pd.concat([st.session_state.db, pd.DataFrame([new_row])], ignore_index=True)
        save_data(st.session_state.db)
        st.success(f"تم الحفظ! رقم الوصل: {new_id}")
        render_ui_with_print(new_row, "new")

# 2. بحث وتعديل شامل
with tabs[1]:
    sq = st.text_input("🔎 ابحث بالاسم أو الهاتف")
    if sq:
        results = st.session_state.db[st.session_state.db['الزبون'].astype(str).str.contains(sq) | st.session_state.db['الهاتف'].astype(str).str.contains(sq)]
        for idx, row in results.iterrows():
            with st.expander(f"⚙️ {row['الزبون']} - {row['الموديل']} (ID: {row['ID']})"):
                # عرض الصورة الحالية
                if row['الصورة'] and len(str(row['الصورة'])) > 50:
                    st.image(base64.b64decode(row['الصورة']), width=200, caption="صورة الجهاز الحالية")
                
                with st.form(f"edit_{idx}"):
                    c1, c2 = st.columns(2)
                    u_name = c1.text_input("الاسم", value=row['الزبون'])
                    u_phone = c1.text_input("الهاتف", value=row['الهاتف'])
                    u_cost = c2.number_input("التكلفة $", value=int(row['التكلفة']))
                    u_parts = c2.number_input("سعر القطع $", value=int(row['سعر_القطع']))
                    u_status = st.selectbox("الحالة", ["تحت الصيانة", "تم التسليم"], index=0 if row['الحالة']=="تحت الصيانة" else 1)
                    u_issue = st.text_area("العطل", value=row['العطل'])
                    u_img = st.file_uploader("📸 تحديث الصورة", type=["jpg", "png", "jpeg"], key=f"img_edit_{idx}")
                    
                    if st.form_submit_button("💾 حفظ كل التعديلات"):
                        img_final = img_to_base64(u_img) if u_img else row['الصورة']
                        st.session_state.db.loc[idx] = [row['ID'], u_name, u_phone, row['الماركة'], row['الموديل'], u_issue, u_cost, u_parts, u_status, row['التاريخ'], img_final]
                        save_data(st.session_state.db)
                        st.rerun()

                # المعاينة والطباعة داخل التعديل
                render_ui_with_print(row, f"edit_ui_{idx}")
