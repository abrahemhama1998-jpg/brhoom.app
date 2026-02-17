import streamlit as st
import pandas as pd
import os
from datetime import datetime
import base64

# --- إعدادات الصفحة الاحترافية ---
st.set_page_config(page_title="الحل للتقنية | Dashboard", layout="wide", initial_sidebar_state="collapsed")

# كود CSS احترافي متكامل للواجهة والطباعة
st.markdown("""
    <style>
    /* تحسين الخطوط والخلفية */
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    html, body, [class*="st-"] { font-family: 'Cairo', sans-serif; direction: rtl; text-align: right; }
    
    /* تصميم البطاقات */
    .stExpander { border: none !important; box-shadow: 0 4px 6px rgba(0,0,0,0.1) !important; border-radius: 12px !important; margin-bottom: 15px !important; background: white !important; }
    
    /* ألوان الحالة */
    .status-badge { padding: 4px 12px; border-radius: 20px; font-size: 14px; font-weight: bold; display: inline-block; }
    .status-repair { background-color: #fff3e0; color: #ef6c00; }
    .status-done { background-color: #e8f5e9; color: #2e7d32; }

    /* تنسيق أزرار الطباعة */
    .btn-print {
        display: block; width: 100%; padding: 12px; background: linear-gradient(90deg, #28a745, #218838);
        color: white !important; text-decoration: none; border-radius: 10px; font-weight: bold; text-align: center; margin: 10px 0; border: none;
    }
    .btn-print:hover { opacity: 0.9; transform: scale(0.99); }
    
    /* تنسيق الوصل عند الطباعة */
    @media print {
        header, footer, .stTabs, .stButton, .no-print, [data-testid="stHeader"], [data-testid="stSidebar"] { display: none !important; }
        .print-area { display: block !important; width: 100% !important; }
        .receipt-card { border: 2px solid #000; padding: 30px; border-radius: 0; }
    }
    .print-area { display: none; }
    .receipt-card { border: 1px dashed #ccc; padding: 20px; border-radius: 15px; background: #fafafa; }
    </style>
    """, unsafe_allow_html=True)

DB_FILE = "maintenance_data.csv"

def load_data():
    if os.path.exists(DB_FILE):
        try:
            df = pd.read_csv(DB_FILE)
            for col in ["ID", "الزبون", "الهاتف", "الماركة", "الموديل", "العطل", "التكلفة", "سعر_القطع", "الحالة", "التاريخ", "الصورة"]:
                if col not in df.columns: df[col] = ""
            return df
        except: pass
    return pd.DataFrame(columns=["ID", "الزبون", "الهاتف", "الماركة", "الموديل", "العطل", "التكلفة", "سعر_القطع", "الحالة", "التاريخ", "الصورة"])

def save_data(df):
    df.to_csv(DB_FILE, index=False)

if 'db' not in st.session_state:
    st.session_state.db = load_data()

def img_to_base64(image_file):
    if image_file: return base64.b64encode(image_file.getvalue()).decode()
    return ""

def render_print_card(row):
    u_name = row['الزبون']
    u_phone = row['الهاتف']
    qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=100x100&data=https://brhoom-tech.streamlit.app/?search={u_phone}"
    
    st.markdown(f"""
    <div class="receipt-card no-print">
        <p style="margin:0; color:#666; font-size:12px;">معاينة الوصل والستيكر</p>
        <hr style="margin:10px 0;">
        <b>{u_name}</b> - {row['الماركة']} {row['الموديل']}
    </div>
    <div class="print-area">
        <div style="border:2px solid #000; padding:20px; direction:rtl; text-align:right;">
            <h2 style="text-align:center; margin:0;">الحل للتقنية للصيانة</h2>
            <p style="text-align:center; margin:5px;">هاتف: 0916206100</p>
            <hr>
            <p><b>رقم الإيصال:</b> {row['ID']} <span style="float:left;">{row['التاريخ']}</span></p>
            <p><b>الزبون:</b> {u_name}</p>
            <p><b>الجهاز:</b> {row['الماركة']} {row['الموديل']}</p>
            <p><b>العطل:</b> {row['العطل']}</p>
            <h3 style="border-top:1px solid #eee; padding-top:10px;">المبلغ المطلوب: {row['التكلفة']} $</h3>
        </div>
        <div style="page-break-before: always; border:1px solid #000; padding:10px; width:250px; text-align:center; margin:20px auto;">
            <b style="font-size:18px;">{u_name}</b><br>{row['الماركة']} {row['الموديل']}<br>
            <img src="{qr_url}" width="100"><br>ID: {row['ID']}
        </div>
    </div>
    <a href="javascript:window.print()" class="btn-print no-print">🖨️ طباعة الوصل والملصق</a>
    """, unsafe_allow_html=True)

# --- الهيدر الاحترافي ---
st.markdown("""<div style="background-color:#0e1117; padding:20px; border-radius:15px; text-align:center; margin-bottom:25px;">
    <h1 style="color:white; margin:0;">🛠️ مـنـظـومـة الـحـل لـلـتـقـنـيـة</h1>
    <p style="color:#aaa; margin:5px;">الإدارة الذكية لمحلات الصيانة</p>
</div>""", unsafe_allow_html=True)

tabs = st.tabs(["➕ تسجيل جديد", "🔍 لوحة التحكم والبحث", "💰 التقارير المالية"])

# --- 1. إضافة جهاز (واجهة نظيفة) ---
with tabs[0]:
    with st.form("add_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        name = c1.text_input("👤 اسم صاحب الجهاز")
        phone = c1.text_input("📞 رقم التواصل")
        brand = c1.selectbox("🏷️ الماركة", ["iPhone", "Samsung", "Xiaomi", "Infinix", "Techno", "أخرى"])
        model = c2.text_input("📱 الموديل")
        cost = c2.number_input("💵 التكلفة المقدرة $", min_value=0)
        issue = c2.text_area("📝 وصف المشكلة")
        img_file = st.file_uploader("📸 صورة حالة الجهاز", type=["jpg", "png", "jpeg"])
        
        st.markdown("<br>", unsafe_allow_html=True)
        submitted = st.form_submit_button("✨ حفظ الجهاز في المنظومة")

    if submitted and name:
        new_id = len(st.session_state.db) + 1001
        img_str = img_to_base64(img_file)
        new_row = {"ID": new_id, "الزبون": name, "الهاتف": phone, "الماركة": brand, "الموديل": model, "العطل": issue, "التكلفة": cost, "سعر_القطع": 0, "الحالة": "تحت الصيانة", "التاريخ": datetime.now().strftime("%Y-%m-%d"), "الصورة": img_str}
        st.session_state.db = pd.concat([st.session_state.db, pd.DataFrame([new_row])], ignore_index=True)
        save_data(st.session_state.db)
        st.balloons()
        st.success(f"تم تسجيل الجهاز بنجاح برقم إيصال: {new_id}")
        render_print_card(new_row)

# --- 2. البحث والتعديل (تصميم البطاقات) ---
with tabs[1]:
    sq = st.text_input("🔍 ابحث عن زبون أو جهاز...")
    if sq:
        df = st.session_state.db
        results = df[df['الزبون'].astype(str).str.contains(sq) | df['الهاتف'].astype(str).str.contains(sq)]
        
        for idx, row in results.iterrows():
            status_class = "status-repair" if row['الحالة'] == "تحت الصيانة" else "status-done"
            with st.expander(f"{row['الزبون']} | {row['الموديل']} | ID: {row['ID']}"):
                st.markdown(f"الحالة: <span class='status-badge {status_class}'>{row['الحالة']}</span>", unsafe_allow_html=True)
                
                # عرض الصورة بشكل دائري أنيق
                img_val = row.get('الصورة', "")
                if isinstance(img_val, str) and len(img_val) > 50:
                    st.image(base64.b64decode(img_val), width=200)

                with st.form(f"edit_pro_{idx}"):
                    c1, c2 = st.columns(2)
                    u_name = c1.text_input("تعديل الاسم", value=row['الزبون'])
                    u_cost = c1.number_input("تعديل السعر $", value=int(row['التكلفة']))
                    u_status = c2.selectbox("تغيير الحالة", ["تحت الصيانة", "تم التسليم"], index=0 if row['الحالة']=="تحت الصيانة" else 1)
                    u_img = c2.file_uploader("تحديث الصورة", type=["jpg", "png", "jpeg"])
                    
                    st.markdown("<br>", unsafe_allow_html=True)
                    col_s, col_d = st.columns([3, 1])
                    if col_s.form_submit_button("💾 حفظ التغييرات"):
                        img_up = img_to_base64(u_img) if u_img else img_val
                        st.session_state.db.at[idx, 'الزبون'] = u_name
                        st.session_state.db.at[idx, 'التكلفة'] = u_cost
                        st.session_state.db.at[idx, 'الحالة'] = u_status
                        st.session_state.db.at[idx, 'الصورة'] = img_up
                        save_data(st.session_state.db)
                        st.rerun()
                    
                    if col_d.form_submit_button("🗑️ حذف"):
                        st.session_state.db = st.session_state.db.drop(idx)
                        save_data(st.session_state.db)
                        st.rerun()
                
                render_print_card(row)

# --- 3. المالية (إحصائيات) ---
with tabs[2]:
    delivered = st.session_state.db[st.session_state.db['الحالة'] == "تم التسليم"]
    active = st.session_state.db[st.session_state.db['الحالة'] == "تحت الصيانة"]
    
    m1, m2, m3 = st.columns(3)
    m1.metric("💰 الأرباح المحققة", f"{delivered['التكلفة'].astype(float).sum()} $")
    m2.metric("🛠️ أجهزة قيد الصيانة", len(active))
    m3.metric("✅ أجهزة تم تسليمها", len(delivered))
    
    st.markdown("### 📋 السجل الكامل للعمليات")
    st.dataframe(st.session_state.db.drop(columns=['الصورة']), use_container_width=True)
