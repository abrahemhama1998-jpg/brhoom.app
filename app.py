import streamlit as st
import pandas as pd
import os
from datetime import datetime
import base64

# --- إعدادات النظام المتقدمة ---
st.set_page_config(page_title="الحل للتقنية | النظام الذكي", layout="wide")

# --- محرك التصميم (CSS) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;800&display=swap');
    
    * { font-family: 'Cairo', sans-serif; direction: rtl; }
    
    /* خلفية التطبيق */
    .stApp { background-color: #f8f9fa; }
    
    /* تصميم الكروت العلوي */
    .metric-card {
        background: white; padding: 20px; border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05); border-right: 5px solid #007bff;
        text-align: center;
    }
    
    /* تحسين شكل التبويبات */
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] {
        background-color: white; border-radius: 10px; padding: 10px 25px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }
    
    /* زر الطباعة الاحترافي */
    .print-trigger {
        background: linear-gradient(135deg, #28a745 0%, #1e7e34 100%);
        color: white !important; padding: 12px 20px; border-radius: 50px;
        text-decoration: none; display: block; text-align: center;
        font-weight: bold; margin-top: 10px; box-shadow: 0 4px 12px rgba(40, 167, 69, 0.3);
    }

    /* تنسيق الطباعة الحرارية */
    @media print {
        header, footer, .stTabs, [data-testid="stHeader"], .no-print { display: none !important; }
        .print-only { display: block !important; }
        body { background: white; }
    }
    .print-only { display: none; }
    </style>
    """, unsafe_allow_html=True)

# --- محرك البيانات ---
DB_FILE = "advanced_repair_db.csv"

def load_data():
    if os.path.exists(DB_FILE):
        df = pd.read_csv(DB_FILE)
        return df
    return pd.DataFrame(columns=["ID", "الزبون", "الهاتف", "الماركة", "الموديل", "العطل", "التكلفة", "سعر_القطع", "الحالة", "التاريخ", "الصورة"])

def save_data(df):
    df.to_csv(DB_FILE, index=False)

if 'db' not in st.session_state:
    st.session_state.db = load_data()

# --- المساعدات البرمجية ---
def img_to_base64(image_file):
    if image_file: return base64.b64encode(image_file.getvalue()).decode()
    return ""

def render_thermal_print(row):
    u_name = row['الزبون']
    u_phone = row['الهاتف']
    qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=100x100&data=https://brhoom-tech.streamlit.app/?search={u_phone}"
    
    st.markdown(f"""
    <div class="print-only" style="font-family: Arial; width: 300px; padding: 10px;">
        <div style="text-align:center; border-bottom:1px dashed #000; padding-bottom:10px;">
            <h3 style="margin:0;">الحل للتقنية</h3>
            <p style="font-size:12px; margin:5px;">صيانة أجهزة ذكية<br>هاتف: 0916206100</p>
        </div>
        <div style="font-size:14px; margin-top:10px;">
            <p><b>رقم الوصل:</b> #{row['ID']}</p>
            <p><b>التاريخ:</b> {row['التاريخ']}</p>
            <p><b>الزبون:</b> {u_name}</p>
            <p><b>الجهاز:</b> {row['الماركة']} {row['الموديل']}</p>
            <p><b>العطل:</b> {row['العطل']}</p>
            <p style="font-size:18px; text-align:center; border:1px solid #000; padding:5px;">
                <b>المبلغ: {row['التكلفة']} $</b>
            </p>
        </div>
        <div style="text-align:center; margin-top:20px; page-break-before: always;">
            <p style="font-size:12px;">ملصق الجهاز</p>
            <b>{u_name}</b><br>
            <img src="{qr_url}" width="80"><br>
            <span style="font-size:10px;">ID: {row['ID']}</span>
        </div>
    </div>
    <a href="javascript:window.print()" class="print-trigger no-print">🚀 طباعة فورية (وصل + ستيكر)</a>
    """, unsafe_allow_html=True)

# --- واجهة المستخدم الرئيسية ---
st.markdown("<h1 style='text-align: center; color: #1e3a8a;'>💎 نظام الحل للتقنية الاحترافي</h1>", unsafe_allow_html=True)

# لوحة المؤشرات (Dashboard Metrics)
db = st.session_state.db
col_m1, col_m2, col_m3, col_m4 = st.columns(4)
with col_m1:
    st.markdown(f"<div class='metric-card'><h5 style='color:#666;'>💰 إجمالي الأرباح</h5><h2 style='color:#28a745;'>{pd.to_numeric(db[db['الحالة']=='تم التسليم']['التكلفة']).sum()} $</h2></div>", unsafe_allow_html=True)
with col_m2:
    st.markdown(f"<div class='metric-card' style='border-right-color:#fd7e14;'><h5 style='color:#666;'>🛠️ تحت الصيانة</h5><h2 style='color:#fd7e14;'>{len(db[db['الحالة']=='تحت الصيانة'])}</h2></div>", unsafe_allow_html=True)
with col_m3:
    st.markdown(f"<div class='metric-card' style='border-right-color:#007bff;'><h5 style='color:#666;'>📱 إجمالي الأجهزة</h5><h2 style='color:#007bff;'>{len(db)}</h2></div>", unsafe_allow_html=True)
with col_m4:
    st.markdown(f"<div class='metric-card' style='border-right-color:#6f42c1;'><h5 style='color:#666;'>📅 تاريخ اليوم</h5><h4 style='color:#6f42c1;'>{datetime.now().strftime('%Y-%m-%d')}</h4></div>", unsafe_allow_html=True)

st.write("")

tabs = st.tabs(["🆕 استقبال جهاز", "🔍 إدارة المهام", "📊 كشف الحساب"])

# --- التبويب الأول: استقبال جهاز ---
with tabs[0]:
    with st.container():
        st.markdown("### 📝 بيانات الدخول")
        with st.form("pro_add_form", clear_on_submit=True):
            c1, c2, c3 = st.columns([2,2,1])
            name = c1.text_input("اسم الزبون كاملاً")
            phone = c2.text_input("رقم الهاتف")
            cost = c3.number_input("المبلغ $", min_value=0)
            
            c4, c5, c6 = st.columns([1,1,2])
            brand = c4.selectbox("الماركة", ["iPhone", "Samsung", "Xiaomi", "أخرى"])
            model = c5.text_input("الموديل")
            issue = c6.text_input("وصف العطل السريع")
            
            img_file = st.file_uploader("📸 صورة توثيق حالة الجهاز (اختياري)")
            
            if st.form_submit_button("✨ تسجيل الجهاز وإصدار الوصل"):
                if name and phone:
                    new_id = len(st.session_state.db) + 1001
                    img_data = img_to_base64(img_file)
                    new_entry = {"ID": new_id, "الزبون": name, "الهاتف": phone, "الماركة": brand, "الموديل": model, "العطل": issue, "التكلفة": cost, "سعر_القطع": 0, "الحالة": "تحت الصيانة", "التاريخ": datetime.now().strftime("%Y-%m-%d %H:%M"), "الصورة": img_data}
                    st.session_state.db = pd.concat([st.session_state.db, pd.DataFrame([new_entry])], ignore_index=True)
                    save_data(st.session_state.db)
                    st.success(f"تم التسجيل بنجاح! رقم الجهاز: {new_id}")
                    render_thermal_print(new_entry)

# --- التبويب الثاني: إدارة المهام ---
with tabs[1]:
    search = st.text_input("🔍 ابحث برقم الوصل، الاسم، أو الهاتف...")
    if search:
        results = db[db['الزبون'].str.contains(search) | db['الهاتف'].str.contains(search) | db['ID'].astype(str).str.contains(search)]
        for idx, row in results.iterrows():
            with st.container():
                st.markdown(f"""<div style='background:white; padding:15px; border-radius:10px; border:1px solid #eee; margin-bottom:10px;'>
                    <h4 style='margin:0; color:#1e3a8a;'>{row['الزبون']} - {row['الموديل']}</h4>
                </div>""", unsafe_allow_html=True)
                
                col_edit, col_img = st.columns([2,1])
                with col_edit:
                    new_status = st.selectbox("تحديث الحالة", ["تحت الصيانة", "تم التسليم"], index=0 if row['الحالة']=="تحت الصيانة" else 1, key=f"st_{idx}")
                    if st.button("💾 حفظ التغيير", key=f"sv_{idx}"):
                        st.session_state.db.at[idx, 'الحالة'] = new_status
                        save_data(st.session_state.db)
                        st.rerun()
                    if st.button("🗑️ حذف الجهاز", key=f"del_{idx}"):
                        st.session_state.db = st.session_state.db.drop(idx)
                        save_data(st.session_state.db)
                        st.rerun()
                
                with col_img:
                    if row['الصورة']:
                        st.image(base64.b64decode(row['الصورة']), width=150)
                
                render_thermal_print(row)

# --- التبويب الثالث: كشف الحساب ---
with tabs[2]:
    st.markdown("### 📄 تقرير العمليات الكامل")
    st.dataframe(st.session_state.db.drop(columns=['الصورة']), use_container_width=True)
    
    csv = st.session_state.db.to_csv(index=False).encode('utf-8-sig')
    st.download_button("📥 تحميل نسخة Backup (Excel)", data=csv, file_name=f"repairs_{datetime.now().date()}.csv")
