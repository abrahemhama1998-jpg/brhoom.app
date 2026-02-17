import streamlit as st
import pandas as pd
import os
from datetime import datetime
import base64

# --- إعدادات الصفحة ---
st.set_page_config(page_title="الحل للتقنية | النظام المتكامل", layout="wide")

# CSS احترافي للطباعة والواجهة
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    * { font-family: 'Cairo', sans-serif; direction: rtl; }
    
    .metric-card {
        background: white; padding: 20px; border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1); text-align: center;
        border-bottom: 5px solid #007bff;
    }

    /* تحسين إعدادات الطباعة */
    @media print {
        header, footer, .stTabs, button, .no-print, [data-testid="stHeader"], .stMarkdown:not(.printable) {
            display: none !important;
        }
        .printable { display: block !important; width: 100% !important; height: auto !important; position: absolute; top: 0; right: 0; }
    }
    .printable { display: none; }
    .preview-box { border: 1px solid #ddd; padding: 10px; border-radius: 8px; background: #fafafa; margin-bottom: 5px; }
    </style>
    """, unsafe_allow_html=True)

DB_FILE = "solution_ultimate_v9.csv"

def load_data():
    if os.path.exists(DB_FILE):
        df = pd.read_csv(DB_FILE)
        cols = ["ID", "الزبون", "الهاتف", "الماركة", "الموديل", "العطل", "التكلفة", "سعر_القطع", "الحالة", "التاريخ", "الصورة"]
        for col in cols:
            if col not in df.columns: 
                df[col] = 0 if col in ["التكلفة", "سعر_القطع"] else ""
        return df
    return pd.DataFrame(columns=["ID", "الزبون", "الهاتف", "الماركة", "الموديل", "العطل", "التكلفة", "سعر_القطع", "الحالة", "التاريخ", "الصورة"])

def save_data(df):
    df.to_csv(DB_FILE, index=False)

if 'db' not in st.session_state:
    st.session_state.db = load_data()

def img_to_base64(image_file):
    if image_file: return base64.b64encode(image_file.getvalue()).decode()
    return ""

# دالة عرض الطباعة المحسنة
def render_ui_with_print(row, unique_id):
    qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=100x100&data=ID_{row['ID']}"
    col_v1, col_v2 = st.columns(2)
    
    with col_v1:
        st.markdown(f"""<div class="preview-box">📄 <b>معاينة الوصل:</b> {row['الزبون']}</div>""", unsafe_allow_html=True)
        # منطقة الطباعة للوصل
        st.markdown(f"""
        <div class="printable">
            <div style="border:3px solid #000; padding:25px; text-align:right; direction:rtl; font-family: 'Cairo', sans-serif;">
                <h1 style="text-align:center;">إيصال صيانة - الحل للتقنية</h1>
                <hr>
                <p style="font-size:22px;"><b>رقم الإيصال:</b> {row['ID']}</p>
                <p style="font-size:22px;"><b>الزبون:</b> {row['الزبون']} | <b>الهاتف:</b> {row['الهاتف']}</p>
                <p style="font-size:22px;"><b>الجهاز:</b> {row['الماركة']} {row['الموديل']}</p>
                <p style="font-size:22px;"><b>العطل:</b> {row['العطل']}</p>
                <h2 style="text-align:center; background:#eee; padding:10px;">المبلغ المطلوب: {row['التكلفة']} $</h2>
                <div style="text-align:center;"><img src="{qr_url}" width="120"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        # زر الطباعة المباشر
        if st.button(f"🖨️ طباعة الوصل", key=f"p_rec_{unique_id}"):
            st.components.v1.html("<script>window.print();</script>", height=0)

    with col_v2:
        st.markdown(f"""<div class="preview-box">🏷️ <b>معاينة الستيكر:</b> {row['ID']}</div>""", unsafe_allow_html=True)
        # منطقة الطباعة للستيكر
        st.markdown(f"""
        <div class="printable">
            <div style="border:2px solid #000; padding:10px; width:260px; text-align:center; margin:0 auto; font-family: 'Cairo', sans-serif;">
                <h3>الحل للتقنية</h3>
                <b style="font-size:18px;">{row['الزبون']}</b><br><span>{row['الموديل']}</span><br>
                <img src="{qr_url}" width="100"><br><b>ID: {row['ID']}</b>
            </div>
        </div>
        """, unsafe_allow_html=True)
        # زر الطباعة المباشر
        if st.button(f"🖨️ طباعة الستيكر", key=f"p_stk_{unique_id}"):
            st.components.v1.html("<script>window.print();</script>", height=0)

# --- الواجهة ---
st.title("💎 نظام الحل للتقنية - الإدارة والتحليلات")

tabs = st.tabs(["➕ إضافة جهاز", "🔍 إدارة وبحث", "📊 التحليلات المالية"])

# 1. إضافة جهاز
with tabs[0]:
    with st.form("add_form"):
        c1, c2 = st.columns(2)
        name = c1.text_input("اسم الزبون")
        phone = c1.text_input("رقم الهاتف")
        brand = c2.selectbox("الماركة", ["iPhone", "Samsung", "Xiaomi", "Infinix", "أخرى"])
        model = c2.text_input("الموديل")
        cost = c1.number_input("التكلفة المتفق عليها $", min_value=0)
        issue = c2.text_area("وصف العطل")
        img_f = st.file_uploader("📸 صورة أولية للجهاز")
        if st.form_submit_button("✅ حفظ وإصدار"):
            new_id = len(st.session_state.db) + 1001
            new_row = {"ID": new_id, "الزبون": name, "الهاتف": phone, "الماركة": brand, "الموديل": model, "العطل": issue, "التكلفة": cost, "سعر_القطع": 0, "الحالة": "تحت الصيانة", "التاريخ": datetime.now().strftime("%Y-%m-%d"), "الصورة": img_to_base64(img_f)}
            st.session_state.db = pd.concat([st.session_state.db, pd.DataFrame([new_row])], ignore_index=True)
            save_data(st.session_state.db)
            st.success(f"تم التسجيل! رقم الوصل: {new_id}")
            render_ui_with_print(new_row, "new")

# 2. بحث وتعديل شامل
with tabs[1]:
    sq = st.text_input("🔎 ابحث بالاسم، الهاتف أو رقم الوصل")
    if sq:
        df = st.session_state.db
        results = df[df['الزبون'].astype(str).str.contains(sq) | df['ID'].astype(str).str.contains(sq)]
        for idx, row in results.iterrows():
            with st.expander(f"🛠️ إدارة: {row['الزبون']} - {row['الموديل']}"):
                if row['الصورة'] and len(str(row['الصورة'])) > 50:
                    st.image(base64.b64decode(row['الصورة']), width=250)
                with st.form(f"edit_{idx}"):
                    c1, c2 = st.columns(2)
                    u_name = c1.text_input("تعديل الاسم", value=row['الزبون'])
                    u_cost = c1.number_input("تعديل التكلفة $", value=int(row['التكلفة']))
                    u_parts = c2.number_input("سعر القطع $", value=int(row['سعر_القطع']))
                    u_status = c2.selectbox("الحالة", ["تحت الصيانة", "تم التسليم"], index=0 if row['الحالة']=="تحت الصيانة" else 1)
                    u_issue = st.text_area("تعديل العطل", value=row['العطل'])
                    u_img = st.file_uploader("📸 تحديث الصورة", key=f"u_img_{idx}")
                    if st.form_submit_button("💾 حفظ التعديلات"):
                        img_up = img_to_base64(u_img) if u_img else row['الصورة']
                        st.session_state.db.loc[idx] = [row['ID'], u_name, row['الهاتف'], row['الماركة'], row['الموديل'], u_issue, u_cost, u_parts, u_status, row['التاريخ'], img_up]
                        save_data(st.session_state.db)
                        st.rerun()
                render_ui_with_print(row, f"edit_ui_{idx}")

# 3. التحليلات المالية
with tabs[2]:
    st.header("📊 ملخص الحسابات المالية")
    df_f = st.session_state.db.copy()
    delivered = df_f[df_f['الحالة'] == "تم التسليم"]
    c1, c2, c3 = st.columns(3)
    c1.markdown(f"<div class='metric-card'><h5>💰 إجمالي المقبوضات</h5><h2>{pd.to_numeric(delivered['التكلفة']).sum()} $</h2></div>", unsafe_allow_html=True)
    c2.markdown(f"<div class='metric-card' style='border-bottom-color:red;'><h5>📉 تكلفة القطع</h5><h2>{pd.to_numeric(delivered['سعر_القطع']).sum()} $</h2></div>", unsafe_allow_html=True)
    profit = pd.to_numeric(delivered['التكلفة']).sum() - pd.to_numeric(delivered['سعر_القطع']).sum()
    c3.markdown(f"<div class='metric-card' style='border-bottom-color:green;'><h5>✅ صافي الأرباح</h5><h2>{profit} $</h2></div>", unsafe_allow_html=True)
    st.write("---")
    st.dataframe(df_f.drop(columns=['الصورة']), use_container_width=True)
