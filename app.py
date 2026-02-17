import streamlit as st
import pandas as pd
import os
from datetime import datetime
import urllib.parse

# --- إعدادات الصفحة ---
st.set_page_config(page_title="الحل للتقنية", layout="wide")

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

# دالة توليد الوصل والستيكر (لإعادة استخدامها في الإضافة والبحث)
def show_receipts(id, name, phone, brand, model, cost, issue):
    encoded_search = urllib.parse.quote(str(phone))
    # الرابط يوجه لتبويب البحث (Index 1) مع قيمة البحث
    qr_link = f"{APP_URL}/?search={encoded_search}"
    qr_img_url = f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data={qr_link}"
    
    c_print1, c_print2 = st.columns(2)
    with c_print1:
        st.markdown(f"""
        <div style="border:2px solid #333; padding:15px; direction:rtl; text-align:right; background-color:#f9f9f9; color:#000; border-radius:10px;">
            <h2 style="text-align:center; color:#1E88E5; margin-bottom:0;">الحل للتقنية</h2>
            <p style="text-align:center; margin-top:0; font-weight:bold;">تواصل: 0916206100</p>
            <hr>
            <p><b>رقم الإيصال:</b> {id}</p>
            <p><b>الزبون:</b> {name}</p>
            <p><b>الهاتف:</b> {phone}</p>
            <p><b>الجهاز:</b> {brand} {model}</p>
            <p><b>التكلفة:</b> {cost} $</p>
            <p><b>العطل:</b> {issue}</p>
            <p><b>التاريخ:</b> {datetime.now().strftime("%Y-%m-%d")}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with c_print2:
        st.markdown(f"""
        <div style="border:1px dashed #000; padding:10px; width:220px; text-align:center; background-color:#fff; color:#000; margin:auto;">
            <b style="font-size:18px;">{name}</b><br>
            <span style="font-size:14px;">{brand} {model}</span><br>
            <img src="{qr_img_url}" width="120"><br>
            <b>ID: {id}</b><br>
            <span style="font-size:10px;">امسح بالهاتف للتعديل</span>
        </div>
        """, unsafe_allow_html=True)

st.title("🛠️ الحل للتقنية للصيانة الذكية")

# استلام معلمات الرابط (Query Params) للبحث التلقائي
query_params = st.query_params
auto_search = query_params.get("search", "")

# تحديد التبويب الافتراضي: إذا كان هناك بحث تلقائي نذهب للتبويب الثاني
default_tab = 1 if auto_search else 0
tabs = st.tabs(["➕ إضافة جهاز جديد", "🔍 بحث وتعديل كامل", "📊 التقارير المالية"])

# --- 1. إضافة جهاز ---
with tabs[0]:
    st.subheader("تسجيل جهاز جديد")
    with st.form("add_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("👤 اسم الزبون")
            phone = st.text_input("📞 رقم هاتف الزبون")
            brand = st.selectbox("📦 الماركة", ["iPhone", "Samsung", "Xiaomi", "Infinix", "Techno", "أخرى"])
        with col2:
            model = st.text_input("📱 الموديل")
            cost = st.number_input("💰 التكلفة الكلية $", min_value=0)
            issue = st.text_area("📝 وصف العطل")
        
        submitted = st.form_submit_button("✅ حفظ الجهاز")
        
        if submitted:
            # التحقق من منع التكرار
            duplicate = st.session_state.db[
                (st.session_state.db['الزبون'] == name) & 
                (st.session_state.db['الهاتف'] == phone) & 
                (st.session_state.db['الموديل'] == model) & 
                (st.session_state.db['العطل'] == issue)
            ]
            
            if not duplicate.empty:
                st.error("⚠️ هذا الجهاز مسجل مسبقاً بنفس البيانات!")
            elif name and phone:
                new_id = len(st.session_state.db) + 1001
                new_entry = {
                    "ID": new_id, "الزبون": name, "الهاتف": phone, "الماركة": brand, 
                    "الموديل": model, "العطل": issue, "التكلفة": cost, "سعر_القطع": 0, 
                    "الحالة": "تحت الصيانة", "التاريخ": datetime.now().strftime("%Y-%m-%d")
                }
                st.session_state.db = pd.concat([st.session_state.db, pd.DataFrame([new_entry])], ignore_index=True)
                save_data(st.session_state.db)
                st.success("تم الحفظ!")
                show_receipts(new_id, name, phone, brand, model, cost, issue)
            else:
                st.error("يرجى إدخال الاسم ورقم الهاتف")

# --- 2. البحث والتعديل الكامل والحذف ---
with tabs[1]:
    st.subheader("🔍 البحث، التعديل، والحذف")
    search_query = st.text_input("ابحث بالاسم أو الهاتف", value=auto_search)
    
    if search_query:
        # البحث في قاعدة البيانات
        df = st.session_state.db
        results = df[df['الزبون'].astype(str).str.contains(search_query) | df['الهاتف'].astype(str).str.contains(search_query)]
        
        if not results.empty:
            for idx, row in results.iterrows():
                with st.expander(f"📋 {row['الزبون']} - {row['الموديل']} (ID: {row['ID']})", expanded=True):
                    with st.form(f"edit_form_{idx}"):
                        c1, c2 = st.columns(2)
                        u_name = c1.text_input("الاسم", value=row['الزبون'])
                        u_phone = c1.text_input("الهاتف", value=row['الهاتف'])
                        u_brand = c1.selectbox("الماركة", ["iPhone", "Samsung", "Xiaomi", "Infinix", "Techno", "أخرى"], index=["iPhone", "Samsung", "Xiaomi", "Infinix", "Techno", "أخرى"].index(row['الماركة']))
                        u_model = c2.text_input("الموديل", value=row['الموديل'])
                        u_cost = c2.number_input("التكلفة $", value=int(row['التكلفة']))
                        u_parts = c2.number_input("سعر القطع $", value=int(row['سعر_القطع']))
                        u_issue = st.text_area("العطل", value=row['العطل'])
                        u_status = st.selectbox("الحالة", ["تحت الصيانة", "تم التسليم"], index=0 if row['الحالة'] == "تحت الصيانة" else 1)
                        
                        btn_col1, btn_col2, btn_col3 = st.columns(3)
                        save_btn = btn_col1.form_submit_button("💾 حفظ التعديلات")
                        print_btn = btn_col2.form_submit_button("🖨️ عرض الوصل")
                        delete_btn = btn_col3.form_submit_button("🗑️ حذف الجهاز")
                        
                        if save_btn:
                            st.session_state.db.loc[idx, ['الزبون', 'الهاتف', 'الماركة', 'الموديل', 'التكلفة', 'سعر_القطع', 'العطل', 'الحالة']] = [u_name, u_phone, u_brand, u_model, u_cost, u_parts, u_issue, u_status]
                            save_data(st.session_state.db)
                            st.success("تم تحديث البيانات")
                            st.rerun()
                        
                        if print_btn:
                            show_receipts(row['ID'], u_name, u_phone, u_brand, u_model, u_cost, u_issue)
                            
                        if delete_btn:
                            st.session_state.db = st.session_state.db.drop(idx)
                            save_data(st.session_state.db)
                            st.warning("تم حذف الجهاز!")
                            st.rerun()
        else:
            st.warning("لا توجد نتائج.")
    else:
        st.dataframe(st.session_state.db)

# --- 3. التقارير ---
with tabs[2]:
    st.subheader("📊 التقارير المالية")
    df_rep = st.session_state.db
    if not df_rep.empty:
        delivered = df_rep[df_rep['الحالة'] == "تم التسليم"].copy()
        delivered['profit'] = delivered['التكلفة'] - delivered['سعر_القطع']
        c1, c2, c3 = st.columns(3)
        c1.metric("إجمالي الدخل", f"{delivered['التكلفة'].sum()} $")
        c2.metric("تكلفة القطع", f"{delivered['سعر_القطع'].sum()} $")
        c3.metric("صافي الربح", f"{delivered['profit'].sum()} $")
        st.write("---")
        st.dataframe(df_rep)
