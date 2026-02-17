import streamlit as st
import pandas as pd
import os
from datetime import datetime
import urllib.parse

# --- إعدادات الصفحة ---
st.set_page_config(page_title="منظومة إبراهيم", layout="wide")

# استخراج رابط الموقع الحالي لجعل الباركود يفتح صفحة البحث تلقائياً
# استبدل الرابط أدناه برابط موقعك الحقيقي ليفتح الباركود بشكل صحيح
APP_URL = "https://brhoom-fix.streamlit.app" 

DB_FILE = "maintenance_data.csv"

def load_data():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE)
    return pd.DataFrame(columns=["ID", "الزبون", "الهاتف", "الماركة", "الموديل", "العطل", "التكلفة", "سعر_القطع", "الحالة", "التاريخ"])

def save_data(df):
    df.to_csv(DB_FILE, index=False)

if 'db' not in st.session_state:
    st.session_state.db = load_data()

st.title("🛠️ منظومة إبراهيم - نظام الإيصالات والباركود الذكي")

tab1, tab2 = st.tabs(["➕ إضافة جهاز", "🔍 بحث وتقارير"])

with tab1:
    col1, col2 = st.columns(2)
    with col1:
        customer = st.text_input("اسم الزبون")
        phone = st.text_input("رقم الهاتف")
        brand = st.selectbox("الماركة", ["iPhone", "Samsung", "Xiaomi", "Infinix", "Techno", "أخرى"])
    with col2:
        model = st.text_input("الموديل")
        cost = st.number_input("تكلفة الصيانة", min_value=0)
        issue = st.text_area("وصف العطل")

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
            
            st.success("تم الحفظ!")
            
            # رابط الباركود الذكي: يفتح الموقع ويبحث عن رقم الهاتف تلقائياً
            encoded_search = urllib.parse.quote(phone)
            qr_link = f"{APP_URL}/?search={encoded_search}"
            qr_img_url = f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data={qr_link}"
            
            col_print1, col_print2 = st.columns(2)
            
            with col_print1:
                st.subheader("📄 وصل الزبون")
                ticket_html = f"""
                <div style="border:2px solid #000; padding:15px; direction:rtl; text-align:right; background-color:#fff; color:#000;">
                    <h2 style="text-align:center;">إيصال استلام - صيانة إبراهيم</h2>
                    <hr>
                    <p><b>رقم الطلب:</b> {new_id}</p>
                    <p><b>الزبون:</b> {customer}</p>
                    <p><b>الهاتف:</b> {phone}</p>
                    <p><b>نوع الجهاز:</b> {brand} {model}</p>
                    <p><b>التكلفة المتفق عليها:</b> {cost} $</p>
                    <p><b>التاريخ:</b> {datetime.now().strftime("%Y-%m-%d")}</p>
                    <p style="text-align:center; font-size:12px;">يرجى إبراز هذا الوصل عند الاستلام</p>
                </div>
                """
                st.markdown(ticket_html, unsafe_allow_html=True)
                st.info("💡 للطباعة من الكمبيوتر اضغط Ctrl + P")

            with col_print2:
                st.subheader("🏷️ ستيكر الجهاز (باركود ذكي)")
                sticker_html = f"""
                <div style="border:1px solid #000; padding:10px; width:200px; text-align:center; background-color:#fff; color:#000;">
                    <b style="font-size:16px;">{customer}</b><br>
                    <span style="font-size:12px;">{brand} {model}</span><br>
                    <img src="{qr_img_url}" width="100"><br>
                    <b>ID: {new_id}</b><br>
                    <span style="font-size:10px;">امسح الكاميرا للتعديل</span>
                </div>
                """
                st.markdown(sticker_html, unsafe_allow_html=True)

with tab2:
    # ميزة البحث التلقائي من الباركود
    query_params = st.query_params
    search_val = query_params.get("search", "")
    
    st.write("### سجل الأجهزة")
    search_input = st.text_input("🔍 ابحث عن زبون أو رقم هاتف", value=search_val)
    
    df = st.session_state.db
    if search_input:
        results = df[df['الزبون'].astype(str).str.contains(search_input) | df['الهاتف'].astype(str).str.contains(search_input)]
        st.dataframe(results)
        
        if not results.empty:
            st.write("---")
            st.write("📝 **تعديل الحالة سرياً:**")
            for idx, row in results.iterrows():
                with st.expander(f"تحديث جهاز: {row['الزبون']}"):
                    new_status = st.selectbox("الحالة", ["تحت الصيانة", "تم التسليم"], key=f"status_{idx}")
                    if st.button("حفظ التعديل", key=f"save_{idx}"):
                        st.session_state.db.at[idx, 'الحالة'] = new_status
                        save_data(st.session_state.db)
                        st.rerun()
    else:
        st.dataframe(df)
