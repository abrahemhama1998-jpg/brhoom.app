import streamlit as st
import pandas as pd
import os
from datetime import datetime
import urllib.parse

# --- إعدادات الصفحة ---
st.set_page_config(page_title="الحل للتقنية", layout="wide")

# كود CSS محسن للطباعة والعرض
st.markdown("""
    <style>
    @media print {
        header, footer, .stTabs, .stButton, .no-print, [data-testid="stHeader"], [data-testid="stSidebar"], .main-ui {
            display: none !important;
        }
        .printable-area {
            display: block !important;
            direction: rtl !important;
            width: 100% !important;
        }
    }
    .printable-area { 
        display: block; 
        border: 1px solid #ddd; 
        padding: 20px; 
        background-color: #fff; 
        color: #000; 
        border-radius: 10px;
        margin-top: 10px;
    }
    .receipt-box { border: 3px solid #000; padding: 20px; direction: rtl; text-align: right; }
    .sticker-box { border: 2px solid #000; padding: 10px; width: 250px; text-align: center; margin: auto; }
    </style>
    """, unsafe_allow_html=True)

APP_URL = "https://brhoom-tech.streamlit.app" 
DB_FILE = "maintenance_data.csv"

def load_data():
    if os.path.exists(DB_FILE):
        try:
            return pd.read_csv(DB_FILE)
        except:
            return pd.DataFrame(columns=["ID", "الزبون", "الهاتف", "الماركة", "الموديل", "العطل", "التكلفة", "سعر_القطع", "الحالة", "التاريخ"])
    return pd.DataFrame(columns=["ID", "الزبون", "الهاتف", "الماركة", "الموديل", "العطل", "التكلفة", "سعر_القطع", "الحالة", "التاريخ"])

def save_data(df):
    df.to_csv(DB_FILE, index=False)

if 'db' not in st.session_state:
    st.session_state.db = load_data()

# دالة توليد منطقة الطباعة مع زر "تفعيل الطباعة"
def render_printable_and_print(id, name, phone, brand, model, cost, issue, mode="receipt"):
    encoded_search = urllib.parse.quote(str(phone))
    qr_link = f"{APP_URL}/?search={encoded_search}"
    qr_img_url = f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data={qr_link}"
    
    if mode == "receipt":
        html_content = f"""
        <div class="printable-area receipt-box">
            <h1 style="text-align:center;">الحل للتقنية للصيانة</h1>
            <p style="text-align:center;">هاتف: 0916206100</p>
            <hr>
            <p><b>رقم الإيصال:</b> {id}</p>
            <p><b>الزبون:</b> {name} | <b>الهاتف:</b> {phone}</p>
            <p><b>الجهاز:</b> {brand} {model}</p>
            <p><b>العطل:</b> {issue}</p>
            <p><b>التكلفة:</b> {cost} $</p>
            <p><b>التاريخ:</b> {datetime.now().strftime("%Y-%m-%d")}</p>
            <div style="text-align:center; margin-top:20px;"><img src="{qr_img_url}" width="120"></div>
        </div>
        <script>
            setTimeout(function() {{ window.print(); }}, 500);
        </script>
        """
    else:
        html_content = f"""
        <div class="printable-area sticker-box">
            <b style="font-size:20px;">{name}</b><br>
            <span style="font-size:16px;">{brand} {model}</span><br>
            <img src="{qr_img_url}" width="100"><br>
            <b>ID: {id}</b>
        </div>
        <script>
            setTimeout(function() {{ window.print(); }}, 500);
        </script>
        """
    st.components.v1.html(html_content, height=500, scrolling=True)

st.title("🛠️ الحل للتقنية")

query_params = st.query_params
auto_search = query_params.get("search", "")

tabs = st.tabs(["➕ إضافة جهاز", "🔍 بحث وتعديل", "📊 المالية"])

# --- 1. إضافة جهاز ---
with tabs[0]:
    with st.form("add_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        name = c1.text_input("اسم الزبون")
        phone = c1.text_input("رقم الهاتف")
        brand = c1.selectbox("الماركة", ["iPhone", "Samsung", "Xiaomi", "Infinix", "Techno", "أخرى"])
        model = c2.text_input("الموديل")
        cost = c2.number_input("التكلفة $", min_value=0)
        issue = c2.text_area("العطل")
        if st.form_submit_button("✅ حفظ الجهاز"):
            if name and phone:
                new_id = len(st.session_state.db) + 1001
                new_entry = {"ID": new_id, "الزبون": name, "الهاتف": phone, "الماركة": brand, "الموديل": model, "العطل": issue, "التكلفة": cost, "سعر_القطع": 0, "الحالة": "تحت الصيانة", "التاريخ": datetime.now().strftime("%Y-%m-%d")}
                st.session_state.db = pd.concat([st.session_state.db, pd.DataFrame([new_entry])], ignore_index=True)
                save_data(st.session_state.db)
                st.success("تم الحفظ!")

# --- 2. البحث والتعديل ---
with tabs[1]:
    search_query = st.text_input("ابحث بالاسم أو الهاتف", value=auto_search)
    if search_query:
        df = st.session_state.db
        results = df[df['الزبون'].astype(str).str.contains(search_query) | df['الهاتف'].astype(str).str.contains(search_query)]
        for idx, row in results.iterrows():
            with st.expander(f"📋 {row['الزبون']} - {row['الموديل']}"):
                with st.form(f"edit_f_{idx}"):
                    u_status = st.selectbox("الحالة", ["تحت الصيانة", "تم التسليم"], index=0 if row['الحالة']=="تحت الصيانة" else 1)
                    if st.form_submit_button("تحديث الحالة"):
                        st.session_state.db.at[idx, 'الحالة'] = u_status
                        save_data(st.session_state.db)
                        st.rerun()
                
                # هنا قمت بتغيير طريقة عمل الأزرار لتكون أكثر استجابة
                c1, c2 = st.columns(2)
                if c1.button(f"🖨️ تجهيز الوصل للطباعة", key=f"rec_{idx}"):
                    render_printable_and_print(row['ID'], row['الزبون'], row['الهاتف'], row['الماركة'], row['الموديل'], row['التكلفة'], row['العطل'], "receipt")
                
                if c2.button(f"🏷️ تجهيز الستيكر للطباعة", key=f"stk_{idx}"):
                    render_printable_and_print(row['ID'], row['الزبون'], row['الهاتف'], row['الماركة'], row['الموديل'], row['التكلفة'], row['العطل'], "sticker")

# --- 3. المالية ---
with tabs[2]:
    delivered = st.session_state.db[st.session_state.db['الحالة'] == "تم التسليم"]
    st.metric("صافي الربح", f"{delivered['التكلفة'].sum()} $")
    st.dataframe(st.session_state.db)
