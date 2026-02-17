import streamlit as st
import pandas as pd
import os
from datetime import datetime
import urllib.parse

# --- إعدادات الصفحة ---
st.set_page_config(page_title="منظومة صيانة إبراهيم", layout="wide")

# رابط موقعك الذي زودتني به (تم التعديل)
APP_URL = "https://brhoom-tech.streamlit.app" 

DB_FILE = "maintenance_data.csv"

# دالة تحميل البيانات
def load_data():
    if os.path.exists(DB_FILE):
        try:
            return pd.read_csv(DB_FILE)
        except:
            return pd.DataFrame(columns=["ID", "الزبون", "الهاتف", "الماركة", "الموديل", "العطل", "التكلفة", "سعر_القطع", "الحالة", "التاريخ"])
    return pd.DataFrame(columns=["ID", "الزبون", "الهاتف", "الماركة", "الموديل", "العطل", "التكلفة", "سعر_القطع", "الحالة", "التاريخ"])

# دالة حفظ البيانات
def save_data(df):
    df.to_csv(DB_FILE, index=False)

if 'db' not in st.session_state:
    st.session_state.db = load_data()

st.title("🛠️ منظومة إبراهيم الذكية للصيانة")

# --- ميزة البحث التلقائي من الباركود ---
# إذا فتحت الرابط من الباركود، سيقوم النظام بالبحث تلقائياً
query_params = st.query_params
auto_search = query_params.get("search", "")

tab1, tab2, tab3 = st.tabs(["➕ إضافة جهاز جديد", "🔍 بحث وتعديل سريع", "📊 التقارير المالية"])

# --- القسم الأول: إضافة جهاز ---
with tab1:
    st.subheader("تسجيل جهاز جديد")
    col1, col2 = st.columns(2)
    with col1:
        customer = st.text_input("👤 اسم الزبون")
        phone = st.text_input("📞 رقم الهاتف")
        brand = st.selectbox("📦 الماركة", ["iPhone", "Samsung", "Xiaomi", "Infinix", "Techno", "أخرى"])
    with col2:
        model = st.text_input("📱 الموديل")
        cost = st.number_input("💰 تكلفة الصيانة المتفق عليها", min_value=0)
        issue = st.text_area("📝 وصف العطل")

    if st.button("✅ حفظ وتوليد الملصقات"):
        if customer and phone:
            new_id = len(st.session_state.db) + 1001
            new_entry = {
                "ID": new_id, "الزبون": customer, "الهاتف": phone, "الماركة": brand, 
                "الموديل": model, "العطل": issue, "التكلفة": cost, "سعر_القطع": 0, 
                "الحالة": "تحت الصيانة", "التاريخ": datetime.now().strftime("%Y-%m-%d")
            }
            st.session_state.db = pd.concat([st.session_state.db, pd.DataFrame([new_entry])], ignore_index=True)
            save_data(st.session_state.db)
            
            st.success(f"تم تسجيل الجهاز بنجاح! رقم: {new_id}")
            
            # رابط الباركود الذكي الذي يفتح صفحة البحث مباشرة
            encoded_search = urllib.parse.quote(str(phone))
            qr_link = f"{APP_URL}/?search={encoded_search}"
            qr_img_url = f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data={qr_link}"
            
            # عرض الوصل والستيكر
            c_print1, c_print2 = st.columns(2)
            with c_print1:
                st.markdown(f"""
                <div style="border:2px solid #333; padding:15px; direction:rtl; text-align:right; background-color:#f9f9f9; color:#000; border-radius:10px;">
                    <h2 style="text-align:center; color:#1E88E5;">إيصال صيانة - إبراهيم</h2>
                    <hr>
                    <p><b>رقم الإيصال:</b> {new_id}</p>
                    <p><b>الزبون:</b> {customer}</p>
                    <p><b>الهاتف:</b> {phone}</p>
                    <p><b>الجهاز:</b> {brand} {model}</p>
                    <p><b>التكلفة:</b> {cost} $</p>
                    <p><b>التاريخ:</b> {datetime.now().strftime("%Y-%m-%d")}</p>
                    <p style="text-align:center; font-size:12px;">يرجى تصوير الوصل والاحتفاظ به</p>
                </div>
                """, unsafe_allow_html=True)
            
            with c_print2:
                st.markdown(f"""
                <div style="border:1px dashed #000; padding:10px; width:220px; text-align:center; background-color:#fff; color:#000; margin:auto;">
                    <b style="font-size:18px;">{customer}</b><br>
                    <span style="font-size:14px;">{brand} {model}</span><br>
                    <img src="{qr_img_url}" width="120"><br>
                    <b>ID: {new_id}</b><br>
                    <span style="font-size:10px;">امسح بالهاتف للتعديل</span>
                </div>
                """, unsafe_allow_html=True)
                st.info("💡 نصيحة: إذا كنت تستخدم الكمبيوتر، اضغط Ctrl + P لطباعة الملصقات.")

# --- القسم الثاني: البحث والتعديل ---
with tab2:
    st.subheader("🔍 البحث عن الأجهزة وتحديثها")
    search_query = st.text_input("ابحث بالاسم أو رقم الهاتف", value=auto_search)
    
    df = st.session_state.db
    if search_query:
        results = df[df['الزبون'].astype(str).str.contains(search_query) | df['الهاتف'].astype(str).str.contains(search_query)]
        
        if not results.empty:
            for idx, row in results.iterrows():
                with st.expander(f"📋 {row['الزبون']} - {row['الماركة']} {row['الموديل']} ({row['الحالة']})", expanded=True):
                    col_edit1, col_edit2 = st.columns(2)
                    with col_edit1:
                        st.write(f"**العطل:** {row['العطل']}")
                        st.write(f"**التاريخ:** {row['التاريخ']}")
                    with col_edit2:
                        current_status = ["تحت الصيانة", "تم التسليم"]
                        new_status = st.selectbox("تحديث الحالة", current_status, index=current_status.index(row['الحالة']), key=f"up_status_{idx}")
                        parts_cost = st.number_input("سعر القطع المشتراة", min_value=0, value=int(row['سعر_القطع']), key=f"parts_{idx}")
                        
                        if st.button("حفظ التعديلات", key=f"btn_{idx}"):
                            st.session_state.db.at[idx, 'الحالة'] = new_status
                            st.session_state.db.at[idx, 'سعر_القطع'] = parts_cost
                            save_data(st.session_state.db)
                            st.success("تم تحديث البيانات!")
                            st.rerun()
        else:
            st.warning("لم يتم العثور على نتائج.")
    else:
        st.dataframe(df)

# --- القسم الثالث: التقارير ---
with tab3:
    st.subheader("📊 إحصائيات الأرباح")
    df_reports = st.session_state.db
    if not df_reports.empty:
        # حساب الأرباح فقط للأجهزة التي تم تسليمها
        delivered = df_reports[df_reports['الحالة'] == "تم التسليم"].copy()
        delivered['profit'] = delivered['التكلفة'] - delivered['سعر_القطع']
        
        c1, c2, c3 = st.columns(3)
        c1.metric("إجمالي المداخيل", f"{delivered['التكلفة'].sum()} $")
        c2.metric("تكلفة القطع", f"{delivered['سعر_القطع'].sum()} $")
        c3.metric("صافي أرباحك", f"{delivered['profit'].sum()} $", delta_color="normal")
        
        st.write("---")
        st.write("### السجل الكامل")
        st.dataframe(df_reports)
    else:
        st.info("لا توجد بيانات مالية حتى الآن.")
