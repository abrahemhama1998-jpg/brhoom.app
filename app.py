import streamlit as st
import pandas as pd
import os
from datetime import datetime
import urllib.parse

# --- إعدادات الصفحة ---
st.set_page_config(page_title="الحل للتقنية", layout="wide")

# كود CSS للتحكم في الطباعة
st.markdown("""
    <style>
    @media print {
        header, footer, .stTabs, .stButton, .no-print, [data-testid="stHeader"], [data-testid="stSidebar"] {
            display: none !important;
        }
        .printable {
            display: block !important;
            direction: rtl !important;
            width: 100% !important;
        }
    }
    .printable { display: none; }
    .receipt-box { border: 2px solid #000; padding: 20px; direction: rtl; text-align: right; font-family: Arial; background: white; color: black; }
    .sticker-box { border: 1px solid #000; padding: 5px; width: 250px; text-align: center; direction: rtl; font-family: Arial; background: white; color: black; }
    </style>
    """, unsafe_allow_html=True)

APP_URL = "https://brhoom-tech.streamlit.app" 
DB_FILE = "maintenance_data.csv"

def load_data():
    if os.path.exists(DB_FILE):
        try:
            df = pd.read_csv(DB_FILE)
            # التأكد من وجود الأعمدة الأساسية
            for col in ["ID", "الزبون", "الهاتف", "الماركة", "الموديل", "العطل", "التكلفة", "سعر_القطع", "الحالة", "التاريخ"]:
                if col not in df.columns:
                    df[col] = 0 if "التكلفة" in col or "سعر_القطع" in col else "غير متوفر"
            return df
        except:
            return pd.DataFrame(columns=["ID", "الزبون", "الهاتف", "الماركة", "الموديل", "العطل", "التكلفة", "سعر_القطع", "الحالة", "التاريخ"])
    return pd.DataFrame(columns=["ID", "الزبون", "الهاتف", "الماركة", "الموديل", "العطل", "التكلفة", "سعر_القطع", "الحالة", "التاريخ"])

def save_data(df):
    df.to_csv(DB_FILE, index=False)

if 'db' not in st.session_state:
    st.session_state.db = load_data()

# دالة توليد منطقة الطباعة
def render_printable(id, name, phone, brand, model, cost, issue, mode="receipt"):
    encoded_search = urllib.parse.quote(str(phone))
    qr_link = f"{APP_URL}/?search={encoded_search}"
    qr_img_url = f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data={qr_link}"
    
    if mode == "receipt":
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
            <div style="text-align:center; margin-top:20px;"><img src="{qr_img_url}" width="120"></div>
        </div>
        """
    else:
        content = f"""
        <div class="printable sticker-box">
            <b style="font-size:18px;">{name}</b><br>
            <span style="font-size:14px;">{brand} {model}</span><br>
            <img src="{qr_img_url}" width="90"><br>
            <b>ID: {id}</b>
        </div>
        """
    st.markdown(content, unsafe_allow_html=True)

st.title("🛠️ الحل للتقنية")

query_params = st.query_params
auto_search = query_params.get("search", "")

tabs = st.tabs(["➕ إضافة جهاز", "🔍 بحث وتعديل كامل", "📊 المالية والتقارير"])

# --- 1. إضافة جهاز ---
with tabs[0]:
    st.subheader("تسجيل جهاز جديد")
    with st.form("main_add_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        name = c1.text_input("اسم الزبون")
        phone = c1.text_input("رقم الهاتف")
        brand = c1.selectbox("الماركة", ["iPhone", "Samsung", "Xiaomi", "Infinix", "Techno", "أخرى"])
        model = c2.text_input("الموديل")
        cost = c2.number_input("التكلفة المتفق عليها $", min_value=0)
        issue = c2.text_area("وصف العطل")
        if st.form_submit_button("✅ حفظ الجهاز"):
            if name and phone:
                new_id = len(st.session_state.db) + 1001
                new_entry = {"ID": new_id, "الزبون": name, "الهاتف": phone, "الماركة": brand, "الموديل": model, "العطل": issue, "التكلفة": cost, "سعر_القطع": 0, "الحالة": "تحت الصيانة", "التاريخ": datetime.now().strftime("%Y-%m-%d")}
                st.session_state.db = pd.concat([st.session_state.db, pd.DataFrame([new_entry])], ignore_index=True)
                save_data(st.session_state.db)
                st.success(f"تم الحفظ بنجاح! رقم الجهاز {new_id}. ابحث عنه في التبويب التالي للطباعة.")

# --- 2. البحث والتعديل الكامل ---
with tabs[1]:
    st.subheader("🔍 البحث والتعديل")
    search_query = st.text_input("ادخل اسم الزبون أو رقم هاتفه", value=auto_search)
    
    if search_query:
        df = st.session_state.db
        results = df[df['الزبون'].astype(str).str.contains(search_query) | df['الهاتف'].astype(str).str.contains(search_query)]
        
        if not results.empty:
            for idx, row in results.iterrows():
                with st.expander(f"📋 {row['الزبون']} - {row['الموديل']} (ID: {row['ID']})", expanded=True):
                    # نموذج التعديل
                    with st.form(f"edit_form_{idx}"):
                        col_a, col_b = st.columns(2)
                        u_name = col_a.text_input("الاسم", value=row['الزبون'])
                        u_phone = col_a.text_input("الهاتف", value=row['الهاتف'])
                        u_cost = col_b.number_input("التكلفة $", value=int(row['التكلفة']))
                        u_parts = col_b.number_input("سعر القطع $", value=int(row.get('سعر_القطع', 0)))
                        u_issue = st.text_area("العطل", value=row['العطل'])
                        u_status = st.selectbox("الحالة", ["تحت الصيانة", "تم التسليم"], index=0 if row['الحالة']=="تحت الصيانة" else 1)
                        
                        col_action = st.columns([1, 1])
                        save_btn = col_action[0].form_submit_button("💾 حفظ التعديلات")
                        delete_btn = col_action[1].form_submit_button("🗑️ حذف الجهاز")
                        
                        if save_btn:
                            st.session_state.db.at[idx, 'الزبون'] = u_name
                            st.session_state.db.at[idx, 'الهاتف'] = u_phone
                            st.session_state.db.at[idx, 'التكلفة'] = u_cost
                            st.session_state.db.at[idx, 'سعر_القطع'] = u_parts
                            st.session_state.db.at[idx, 'العطل'] = u_issue
                            st.session_state.db.at[idx, 'الحالة'] = u_status
                            save_data(st.session_state.db)
                            st.success("تم التحديث!")
                            st.rerun()
                        
                        if delete_btn:
                            st.session_state.db = st.session_state.db.drop(idx)
                            save_data(st.session_state.db)
                            st.warning("تم الحذف!")
                            st.rerun()

                    # أزرار الطباعة (خارج النموذج)
                    st.write("---")
                    st.write("🖨️ خيارات الطباعة لهذا الجهاز:")
                    c1, c2 = st.columns(2)
                    if c1.button(f"طباعة إيصال الزبون", key=f"print_receipt_{idx}"):
                        render_printable(row['ID'], row['الزبون'], row['الهاتف'], row['الماركة'], row['الموديل'], row['التكلفة'], row['العطل'], "receipt")
                        st.markdown('<script>window.print();</script>', unsafe_allow_html=True)
                    
                    if c2.button(f"طباعة ستيكر الباركود", key=f"print_sticker_{idx}"):
                        render_printable(row['ID'], row['الزبون'], row['الهاتف'], row['الماركة'], row['الموديل'], row['التكلفة'], row['العطل'], "sticker")
                        st.markdown('<script>window.print();</script>', unsafe_allow_html=True)
        else:
            st.warning("لا توجد نتائج مطابقة.")
    else:
        st.write("استخدم خانة البحث أعلاه للوصول لبيانات الزبائن.")
        st.dataframe(st.session_state.db)

# --- 3. المالية والتقارير ---
with tabs[2]:
    st.subheader("📊 التقارير المالية")
    df_all = st.session_state.db
    if not df_all.empty:
        # حسابات الأرباح
        delivered = df_all[df_all['الحالة'] == "تم التسليم"].copy()
        total_income = delivered['التكلفة'].sum()
        total_parts = delivered['سعر_القطع'].sum()
        net_profit = total_income - total_parts
        
        col_m1, col_m2, col_m3 = st.columns(3)
        col_m1.metric("إجمالي الدخل ($)", f"{total_income}")
        col_m2.metric("تكلفة القطع ($)", f"{total_parts}")
        col_m3.metric("صافي الربح ($)", f"{net_profit}")
        
        st.write("---")
        st.write("### السجل الكامل لجميع العمليات")
        st.dataframe(df_all)
    else:
        st.info("لا توجد بيانات كافية لعرض التقارير حالياً.")
