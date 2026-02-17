import streamlit as st
import pandas as pd
import os
from datetime import datetime
import base64

# --- إعدادات النظام ---
st.set_page_config(page_title="الحل للتقنية | النظام المتكامل", layout="wide")

# --- محرك التصميم CSS ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    * { font-family: 'Cairo', sans-serif; direction: rtl; }
    .stApp { background-color: #f4f7f6; }
    
    /* تصميم الكروت */
    .device-card {
        background: white; padding: 20px; border-radius: 15px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08); margin-bottom: 20px;
        border-right: 8px solid #007bff;
    }
    
    /* أزرار احترافية */
    .stButton>button { width: 100%; border-radius: 8px; font-weight: bold; height: 45px; }
    .print-btn {
        background: linear-gradient(90deg, #28a745, #218838);
        color: white !important; text-decoration: none; display: block;
        text-align: center; padding: 12px; border-radius: 10px; font-weight: bold;
        margin-top: 15px; box-shadow: 0 4px 10px rgba(40,167,69,0.2);
    }

    /* تنسيق الطباعة */
    @media print {
        header, footer, .stTabs, [data-testid="stHeader"], .no-print, .stSidebar { display: none !important; }
        .print-only { display: block !important; width: 100% !important; }
    }
    .print-only { display: none; }
    </style>
    """, unsafe_allow_html=True)

# --- إدارة البيانات ---
DB_FILE = "master_repair_db.csv"

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

# --- وظائف مساعدة ---
def img_to_base64(image_file):
    if image_file: return base64.b64encode(image_file.getvalue()).decode()
    return ""

def render_professional_print(row):
    qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=100x100&data=ID_{row['ID']}"
    st.markdown(f"""
    <div class="print-only" style="padding: 20px; border: 2px solid #000; font-family: Arial;">
        <div style="text-align:center;">
            <h1>الحل للتقنية للصيانة</h1>
            <p>العنوان: Tripoli | هاتف: 0916206100</p>
            <hr>
        </div>
        <table style="width:100%; text-align:right; font-size:18px;">
            <tr><td><b>رقم الوصل:</b> {row['ID']}</td><td><b>التاريخ:</b> {row['التاريخ']}</td></tr>
            <tr><td><b>الزبون:</b> {row['الزبون']}</td><td><b>الهاتف:</b> {row['الهاتف']}</td></tr>
            <tr><td><b>الجهاز:</b> {row['الماركة']} - {row['الموديل']}</td><td><b>التكلفة:</b> {row['التكلفة']} $</td></tr>
        </table>
        <p><b>وصف العطل:</b> {row['العطل']}</p>
        <div style="margin-top:30px; text-align:center; border-top:1px dashed #000; padding-top:20px;">
            <p>ملصق الجهاز (Sticker)</p>
            <b>{row['الزبون']}</b><br>
            <img src="{qr_url}" width="100"><br>
            <b>ID: {row['ID']}</b>
        </div>
    </div>
    <a href="javascript:window.print()" class="print-btn no-print">🖨️ طباعة الإيصال والملصق فوراً</a>
    """, unsafe_allow_html=True)

# --- القائمة الجانبية (Sidebar) ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2942/2942503.png", width=100)
    st.title("لوحة التحكم")
    db = st.session_state.db
    total_revenue = pd.to_numeric(db[db['الحالة']=='تم التسليم']['التكلفة']).sum()
    total_parts = pd.to_numeric(db[db['الحالة']=='تم التسليم']['سعر_القطع']).sum()
    st.metric("صافي الأرباح 💰", f"{total_revenue - total_parts} $")
    st.metric("أجهزة قيد العمل 🛠️", len(db[db['الحالة']=='تحت الصيانة']))
    st.write("---")
    st.info("رقم المحل: 0916206100")

# --- الواجهة الرئيسية ---
st.markdown("<h1 style='text-align:center;'>🛠️ نظام إدارة صيانة الحل للتقنية</h1>", unsafe_allow_html=True)

tabs = st.tabs(["➕ استقبال جهاز جديد", "🔍 البحث والإدارة الشاملة", "📊 التقارير المالية"])

# --- التبويب 1: إضافة جهاز ---
with tabs[0]:
    with st.form("main_add_form", clear_on_submit=True):
        c1, c2, c3 = st.columns([2,2,1])
        name = c1.text_input("👤 اسم الزبون")
        phone = c2.text_input("📞 رقم الهاتف")
        cost = c3.number_input("💵 التكلفة $", min_value=0)
        
        c4, c5, c6 = st.columns([1,1,2])
        brand = c4.selectbox("🏷️ الماركة", ["iPhone", "Samsung", "Xiaomi", "أخرى"])
        model = c5.text_input("📱 الموديل")
        issue = c6.text_input("📝 وصف العطل")
        
        img_f = st.file_uploader("📸 صورة توثيق")
        
        if st.form_submit_button("✅ حفظ وطباعة الوصل"):
            if name and phone:
                new_id = len(st.session_state.db) + 1001
                img_str = img_to_base64(img_f)
                new_row = {"ID": new_id, "الزبون": name, "الهاتف": phone, "الماركة": brand, "الموديل": model, "العطل": issue, "التكلفة": cost, "سعر_القطع": 0, "الحالة": "تحت الصيانة", "التاريخ": datetime.now().strftime("%Y-%m-%d"), "الصورة": img_str}
                st.session_state.db = pd.concat([st.session_state.db, pd.DataFrame([new_row])], ignore_index=True)
                save_data(st.session_state.db)
                st.success(f"تم الحفظ بنجاح! رقم الجهاز {new_id}")
                render_professional_print(new_row)

# --- التبويب 2: البحث والتعديل الكامل ---
with tabs[1]:
    search = st.text_input("🔎 ابحث بالاسم، الهاتف، أو رقم الوصل...")
    if search:
        results = st.session_state.db[st.session_state.db['الزبون'].str.contains(search) | st.session_state.db['ID'].astype(str).str.contains(search)]
        for idx, row in results.iterrows():
            with st.container():
                st.markdown(f"""<div class='device-card'>
                    <h3 style='margin:0;'>{row['الزبون']} - {row['الماركة']} {row['الموديل']}</h3>
                    <p style='color:#666;'>رقم الوصل: {row['ID']} | التاريخ: {row['التاريخ']}</p>
                </div>""", unsafe_allow_html=True)
                
                with st.expander("📝 تعديل كامل البيانات أو حذف الجهاز"):
                    with st.form(f"full_edit_{idx}"):
                        e1, e2 = st.columns(2)
                        en_name = e1.text_input("الاسم", value=row['الزبون'])
                        en_phone = e1.text_input("الهاتف", value=row['الهاتف'])
                        en_cost = e2.number_input("التكلفة $", value=int(row['التكلفة']))
                        en_parts = e2.number_input("سعر القطع $", value=int(row['سعر_القطع']))
                        en_issue = st.text_area("وصف العطل", value=row['العطل'])
                        en_status = st.selectbox("الحالة", ["تحت الصيانة", "تم التسليم"], index=0 if row['الحالة']=="تحت الصيانة" else 1)
                        
                        eb1, eb2 = st.columns(2)
                        if eb1.form_submit_button("💾 حفظ كافة التعديلات"):
                            st.session_state.db.loc[idx] = [row['ID'], en_name, en_phone, row['الماركة'], row['الموديل'], en_issue, en_cost, en_parts, en_status, row['التاريخ'], row['الصورة']]
                            save_data(st.session_state.db)
                            st.success("تم التحديث")
                            st.rerun()
                        if eb2.form_submit_button("🗑️ حذف الجهاز نهائياً"):
                            st.session_state.db = st.session_state.db.drop(idx)
                            save_data(st.session_state.db)
                            st.rerun()
                
                if row['الصورة']: st.image(base64.b64decode(row['الصورة']), width=150)
                render_professional_print(row)

# --- التبويب 3: المالية ---
with tabs[2]:
    st.markdown("### 📊 كشف الحساب التفصيلي")
    st.dataframe(st.session_state.db.drop(columns=['الصورة']), use_container_width=True)
