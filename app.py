import streamlit as st
import pandas as pd
import os
from datetime import datetime

# --- إعدادات الصفحة ---
st.set_page_config(page_title="منظومة إبراهيم المتكاملة", layout="wide")

DB_FILE = "maintenance_data.csv"

# --- قاعدة بيانات الهواتف الضخمة ---
DEVICES_DATA = {
    "iPhone": ["15 Pro Max", "15 Pro", "15 Plus", "15", "14 Pro Max", "14", "13 Pro", "13", "12 Pro", "12", "11 Pro", "11", "XS Max", "X", "8 Plus", "7"],
    "Samsung": ["S24 Ultra", "S23 Ultra", "S22 Ultra", "S21 FE", "Note 20 Ultra", "A54", "A34", "A14", "A05", "M54", "Z Fold 5", "Z Flip 5"],
    "Xiaomi": ["13 Ultra", "12T Pro", "Redmi Note 13 Pro", "Redmi Note 12", "Poco F5", "Poco X5 Pro", "Redmi 12C"],
    "Infinix": ["Zero 30", "Note 30 VIP", "Hot 40 Pro", "Hot 30", "Smart 8", "Zero Ultra"],
    "Techno": ["Phantom V Fold", "Camon 20 Pro", "Spark 10 Pro", "Pova 5", "Pop 7"],
    "Google Pixel": ["Pixel 8 Pro", "Pixel 7 Pro", "Pixel 6a", "Pixel 5", "Pixel 4 XL"],
    "OnePlus": ["OnePlus 12", "OnePlus 11", "Nord 3", "OnePlus 10 Pro", "Nord CE 3"],
    "Huawei": ["Mate 60 Pro", "P60 Pro", "Nova 11i", "Mate 50 Pro", "P50 Pocket", "Y9a"],
    "أخرى": ["اكتب موديل آخر"]
}

def load_data():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE)
    return pd.DataFrame(columns=["ID", "الزبون", "الهاتف", "الماركة", "الموديل", "العطل", "الفني", "التكلفة", "سعر_القطع", "الحالة", "التاريخ"])

def save_data(df):
    df.to_csv(DB_FILE, index=False)

if 'db' not in st.session_state:
    st.session_state.db = load_data()

st.title("🛠️ منظومة صيانة إبراهيم الشاملة")

tab1, tab2, tab3 = st.tabs(["➕ إضافة جهاز", "🔍 بحث وتعديل", "📊 الأرباح والتقارير"])

with tab1:
    with st.form("add_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            customer = st.text_input("👤 اسم الزبون")
            phone = st.text_input("📞 رقم الهاتف")
            
            # اختيار الماركة أولاً
            brand = st.selectbox("📦 اختر الماركة", options=list(DEVICES_DATA.keys()))
            # تظهر الموديلات بناءً على الماركة المختارة
            model = st.selectbox("📱 اختر الموديل", options=DEVICES_DATA[brand])
            
            custom_model = ""
            if brand == "أخرى" or model == "اكتب موديل آخر":
                custom_model = st.text_input("اكتب اسم الماركة والموديل هنا:")
            
        with col2:
            technician = st.selectbox("👨‍🔧 الفني", ["إبراهيم"])
            cost = st.number_input("💰 التكلفة على الزبون", min_value=0)
            parts = st.number_input("🔧 تكلفة قطع الغيار", min_value=0)
            issue = st.text_area("📝 وصف العطل")
            
        submitted = st.form_submit_button("✅ حفظ البيانات")

        if submitted:
            final_model = custom_model if custom_model else model
            new_id = len(st.session_state.db) + 1001
            new_entry = {
                "ID": new_id, "الزبون": customer, "الهاتف": phone, "الماركة": brand,
                "الموديل": final_model, "العطل": issue, "الفني": technician,
                "التكلفة": cost, "سعر_القطع": parts, "الحالة": "تحت الصيانة",
                "التاريخ": datetime.now().strftime("%Y-%m-%d")
            }
            st.session_state.db = pd.concat([st.session_state.db, pd.DataFrame([new_entry])], ignore_index=True)
            save_data(st.session_state.db)
            st.success(f"تم الحفظ! رقم الجهاز: {new_id}")
