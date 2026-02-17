import streamlit as st
import pandas as pd
import os
from datetime import datetime
import urllib.parse

# --- إعدادات الصفحة ---
st.set_page_config(page_title="الحل للتقنية", layout="wide")

# كود CSS للتحكم في الطباعة وفصل الوصل عن الستيكر
st.markdown("""
    <style>
    /* تنسيق للطباعة فقط */
    @media print {
        header, footer, .stTabs, .stButton, .no-print, [data-testid="stHeader"], [data-testid="stSidebar"], .main-ui {
            display: none !important;
        }
        .printable {
            display: block !important;
            direction: rtl !important;
            width: 100% !important;
        }
    }
    .printable { display: none; }
    .receipt-box { border: 2px solid #000; padding: 20px; direction: rtl; text-align: right; font-family: Arial; }
    .sticker-box { border: 1px solid #000; padding: 5px; width: 250px; text-align: center; direction: rtl; font-family: Arial; }
    </style>
    """, unsafe_allow_html=True)

APP_URL = "https://brhoom-tech.streamlit.app" 
DB_FILE = "maintenance_data.csv"

def load_data():
    if os.path.exists(DB_FILE):
        try: return pd.read_csv(DB_FILE)
        except: return pd.DataFrame(columns=["ID", "الزبون", "الهاتف", "الماركة", "الموديل", "العطل", "التكلفة", "سعر_القطع", "الحالة", "التاريخ"])
    return pd.DataFrame(columns=["ID", "الزبون", "الهاتف", "الماركة", "الموديل", "العطل", "التكلفة", "سعر_القطع", "الحالة", "التاريخ"])

def save_data(df):
    df.to_csv(DB_FILE, index=False)

if 'db' not in st.session_state:
    st.session_state.db = load_data()

# دالة توليد الأكواد البرمجية للطباعة
def render_printable_area(id, name, phone, brand, model, cost, issue, mode="receipt"):
    encoded_search = urllib.parse.quote(str(phone))
    qr_link = f"{APP_URL}/?search={encoded_search}"
    qr_img_url = f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data={qr_link}"
    
    if mode == "receipt":
        # تصميم الوصل
        content = f"""
        <div class="printable receipt-box">
            <h1 style="text-align:center;">الحل للتقنية للصيانة</h1>
            <p style="text-align:center;">هاتف: 0916206100</p>
            <hr>
            <p><b>رقم الإيصال:</b> {id}</p>
            <p><b>الزبون:</b> {name} | <b>الهاتف:</b> {phone}</p>
            <p><b>الجهاز:</b> {brand} {model}</p>
            <p><b>العطل:</b> {issue}</p>
            <p><b>التكلفة:</b> {cost} $</p>
            <p><b>التاريخ:</b> {datetime.now().strftime("%Y-%m-%d")}</p>
            <div style="text-align:center; margin-top:20px;">
                <img src="{qr_img_url}" width="120"><br>
                <small>امسح للمتابعة</small>
            </div>
        </div>
        """
    else:
        # تصميم الستيكر الصغير
        content = f"""
        <div class="printable sticker-box">
            <b style="font-size:20px;">{name}</b><br>
            <span style="font-size:14px;">{brand} {model}</span><br>
            <img src="{qr_img_url}" width="90"><br>
            <b style="font-size:12px;">ID: {id}</b>
        </div>
        """
    st.markdown(content, unsafe_allow_html=True)

st.title("🛠️ الحل للتقنية")

query_params = st.query_params
auto_search = query_params.get("search", "")

tabs = st.tabs(["➕ إضافة جهاز", "🔍 بحث وتعديل", "📊 المالية"])

# --- القسم الأول: إضافة جهاز ---
with tabs[0]:
    with st.form("add_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        name = col1.text_input("اسم الزبون")
        phone = col1.text_input("رقم الهاتف")
        brand = col1.selectbox("الماركة", ["iPhone", "Samsung", "Xiaomi", "Infinix", "Techno", "أخرى"])
        model = col2.text_input("الموديل")
        cost = col2.number_input("التكلفة $", min_value=0)
        issue = col2.text_area("وصف العطل")
        submitted = st.form_submit_button("💾 حفظ الجهاز")
        
        if submitted and name and phone:
            new_id = len(st.session_state.db) + 1001
            new_entry = {"ID": new_id, "الزبون": name, "الهاتف": phone, "الماركة": brand, "الموديل": model, "العطل": issue, "التكلفة": cost, "سعر_القطع": 0, "الحالة": "تحت الصيانة", "التاريخ": datetime.now().strftime("%Y-%m-%d")}
            st.session_state.db = pd.concat([st.session_state.db, pd.DataFrame([new_entry])], ignore_index=True)
            save_data(st.session_state.db)
            st.success("تم الحفظ بنجاح!")
            
            # عرض الأزرار بعد الحفظ مباشرة
            col_b1, col_b2 = st.columns(2)
            with col_b1:
                if st.button("🖨️ طباعة وصل الزبون"):
                    render_printable_area(new_id, name, phone, brand, model, cost, issue, "receipt")
                    st.markdown('<script>window.print();</script>', unsafe_allow_html=True)
            with col_b2:
                if st.button("🏷️ طباعة ستيكر الجهاز"):
                    render_printable_area(new_id, name, phone, brand, model, cost, issue, "sticker")
                    st.markdown('<script>window.print();</script>', unsafe_allow_html=True)

# --- القسم الثاني: البحث والتعديل ---
with tabs[1]:
    search_query = st.text_input("ابحث بالاسم أو الهاتف", value=auto_search)
    if search_query:
        df = st.session_state.db
        results = df[df['الزبون'].astype(str).str.contains(search_query) | df['الهاتف'].astype(str).str.contains(search_query)]
        for idx, row in results.iterrows():
            with st.expander(f"📋 {row['الزبون']} - {row['الموديل']}"):
                # خيارات التعديل هنا (كما في الكود السابق)
                # ...
                # أزرار الطباعة المنفصلة
                c1, c2 = st.columns(2)
                if c1.button(f"🖨️ طباعة الوصل للزبون", key=f"rec_{idx}"):
                    render_printable_area(row['ID'], row['الزبون'], row['الهاتف'], row['الماركة'], row['الموديل'], row['التكلفة'], row['العطل'], "receipt")
                    st.markdown('<script>window.print();</script>', unsafe_allow_html=True)
                if c2.button(f"🏷️ طباعة ستيكر الجهاز", key=f"stk_{idx}"):
                    render_printable_area(row['ID'], row['الزبون'], row['الهاتف'], row['الماركة'], row['الموديل'], row['التكلفة'], row['العطل'], "sticker")
                    st.markdown('<script>window.print();</script>', unsafe_allow_html=True)
