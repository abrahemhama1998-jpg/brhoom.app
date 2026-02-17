import streamlit as st
import pandas as pd
import os
from datetime import datetime
import urllib.parse

# --- إعدادات الصفحة ---
st.set_page_config(page_title="الحل للتقنية", layout="wide")

# كود CSS للطباعة والجمالية
st.markdown("""
    <style>
    @media print {
        header, footer, .stTabs, .stButton, .no-print, [data-testid="stHeader"], [data-testid="stSidebar"] {
            display: none !important;
        }
        .printable {
            display: block !important;
            direction: rtl !important;
        }
    }
    .printable { display: none; }
    .receipt-box { border: 2px solid #000; padding: 20px; direction: rtl; text-align: right; font-family: Arial; background: white; color: black; }
    .sticker-box { border: 1px solid #000; padding: 5px; width: 220px; text-align: center; direction: rtl; font-family: Arial; background: white; color: black; }
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

# دالة توليد منطقة الطباعة
def render_printable(id, name, phone, brand, model, cost, issue, mode="receipt"):
    if mode == "receipt":
        # وصل الزبون (بدون باركود)
        content = f"""
        <div class="printable receipt-box">
            <h1 style="text-align:center;">الحل للتقنية للصيانة</h1>
            <p style="text-align:center;">تواصل: 0916206100</p>
            <hr>
            <p><b>رقم الإيصال:</b> {id}</p>
            <p><b>الزبون:</b> {name} | <b>الهاتف:</b> {phone}</p>
            <p><b>الجهاز:</b> {brand} {model}</p>
            <p><b>العطل:</b> {issue}</p>
            <p><b>التكلفة:</b> {cost} $</p>
            <p><b>التاريخ:</b> {datetime.now().strftime("%Y-%m-%d")}</p>
            <p style="text-align:center; margin-top:30px;">شكراً لثقتكم</p>
        </div>
        """
    else:
        # ستيكر الجهاز (مع باركود للبحث السريع)
        encoded_search = urllib.parse.quote(str(phone))
        qr_link = f"{APP_URL}/?search={encoded_search}"
        qr_img_url = f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data={qr_link}"
        content = f"""
        <div class="printable sticker-box">
            <b style="font-size:16px;">{name}</b><br>
            <span style="font-size:12px;">{brand} {model}</span><br>
            <img src="{qr_img_url}" width="90"><br>
            <b>ID: {id}</b>
        </div>
        """
    st.markdown(content, unsafe_allow_html=True)

st.title("🛠️ الحل للتقنية للصيانة")

query_params = st.query_params
auto_search = query_params.get("search", "")

tabs = st.tabs(["➕ إضافة جهاز", "🔍 بحث وتعديل شامل", "📊 التقارير المالية"])

# --- 1. إضافة جهاز ---
with tabs[0]:
    st.subheader("تسجيل جهاز جديد")
    with st.form("add_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        name = col1.text_input("👤 اسم الزبون")
        phone = col1.text_input("📞 رقم الهاتف")
        brand = col1.selectbox("📦 الماركة", ["iPhone", "Samsung", "Xiaomi", "Infinix", "Techno", "أخرى"])
        model = col2.text_input("📱 الموديل")
        cost = col2.number_input("💰 التكلفة المتفق عليها $", min_value=0)
        issue = col2.text_area("📝 وصف العطل")
        image = st.file_uploader("📸 إضافة صورة للجهاز (اختياري)", type=["jpg", "png", "jpeg"])
        
        submitted = st.form_submit_button("✅ حفظ الجهاز")
        if submitted and name and phone:
            new_id = len(st.session_state.db) + 1001
            new_entry = {"ID": new_id, "الزبون": name, "الهاتف": phone, "الماركة": brand, "الموديل": model, "العطل": issue, "التكلفة": cost, "سعر_القطع": 0, "الحالة": "تحت الصيانة", "التاريخ": datetime.now().strftime("%Y-%m-%d")}
            st.session_state.db = pd.concat([st.session_state.db, pd.DataFrame([new_entry])], ignore_index=True)
            save_data(st.session_state.db)
            st.success(f"تم الحفظ بنجاح! رقم الطلب: {new_id}")

# --- 2. البحث والتعديل الشامل ---
with tabs[1]:
    st.subheader("🔍 البحث والتعديل")
    search_query = st.text_input("ابحث بالاسم أو الهاتف", value=auto_search)
    if search_query:
        df = st.session_state.db
        results = df[df['الزبون'].astype(str).str.contains(search_query) | df['الهاتف'].astype(str).str.contains(search_query)]
        
        for idx, row in results.iterrows():
            with st.expander(f"📋 {row['الزبون']} - {row['الموديل']} (ID: {row['ID']})", expanded=True):
                with st.form(f"edit_all_{idx}"):
                    c1, c2 = st.columns(2)
                    u_name = c1.text_input("الاسم", value=row['الزبون'])
                    u_phone = c1.text_input("الهاتف", value=row['الهاتف'])
                    u_brand = c1.selectbox("الماركة", ["iPhone", "Samsung", "Xiaomi", "Infinix", "Techno", "أخرى"], index=["iPhone", "Samsung", "Xiaomi", "Infinix", "Techno", "أخرى"].index(row['الماركة']) if row['الماركة'] in ["iPhone", "Samsung", "Xiaomi", "Infinix", "Techno", "أخرى"] else 5)
                    u_model = c2.text_input("الموديل", value=row['الموديل'])
                    u_cost = c2.number_input("التكلفة $", value=int(row['التكلفة']))
                    u_parts = c2.number_input("سعر القطع $", value=int(row.get('سعر_القطع', 0)))
                    u_issue = st.text_area("وصف العطل", value=row['العطل'])
                    u_status = st.selectbox("الحالة", ["تحت الصيانة", "تم التسليم"], index=0 if row['الحالة']=="تحت الصيانة" else 1)
                    
                    b1, b2 = st.columns(2)
                    if b1.form_submit_button("💾 حفظ التعديلات"):
                        st.session_state.db.loc[idx] = [row['ID'], u_name, u_phone, u_brand, u_model, u_issue, u_cost, u_parts, u_status, row['التاريخ']]
                        save_data(st.session_state.db)
                        st.success("تم التحديث")
                        st.rerun()
                    if b2.form_submit_button("🗑️ حذف الجهاز"):
                        st.session_state.db = st.session_state.db.drop(idx)
                        save_data(st.session_state.db)
                        st.rerun()

                # أزرار الطباعة
                st.write("---")
                p1, p2 = st.columns(2)
                if p1.button(f"🖨️ طباعة الوصل (بدون باركود)", key=f"p_rec_{idx}"):
                    render_printable(row['ID'], u_name, u_phone, u_brand, u_model, u_cost, u_issue, "receipt")
                    st.markdown('<script>window.print();</script>', unsafe_allow_html=True)
                if p2.button(f"🏷️ طباعة ستيكر (مع باركود)", key=f"p_stk_{idx}"):
                    render_printable(row['ID'], u_name, u_phone, u_brand, u_model, u_cost, u_issue, "sticker")
                    st.markdown('<script>window.print();</script>', unsafe_allow_html=True)

# --- 3. المالية والتقارير ---
with tabs[2]:
    st.subheader("📊 التقارير المالية")
    df_all = st.session_state.db
    if not df_all.empty:
        delivered = df_all[df_all['الحالة'] == "تم التسليم"].copy()
        income = delivered['التكلفة'].sum()
        parts = delivered['سعر_القطع'].sum()
        profit = income - parts
        
        m1, m2, m3 = st.columns(3)
        m1.metric("إجمالي الدخل", f"{income} $")
        m2.metric("تكلفة القطع", f"{parts} $")
        m3.metric("صافي الربح", f"{profit} $")
        
        st.write("---")
        st.dataframe(df_all)
