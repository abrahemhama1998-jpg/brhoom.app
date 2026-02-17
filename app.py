import streamlit as st
import pandas as pd
import os
from datetime import datetime
from PIL import Image

# --- إعدادات الصفحة ---
st.set_page_config(page_title="منظومة إبراهيم الاحترافية", layout="wide")

DB_FILE = "maintenance_data.csv"
IMAGE_DIR = "device_images"

# إنشاء مجلد للصور إذا لم يكن موجوداً
if not os.path.exists(IMAGE_DIR):
    os.makedirs(IMAGE_DIR)

def load_data():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE)
    return pd.DataFrame(columns=["ID", "الزبون", "الهاتف", "الماركة", "الموديل", "العطل", "التكلفة", "سعر_القطع", "الحالة", "التاريخ", "الصورة"])

def save_data(df):
    df.to_csv(DB_FILE, index=False)

# تحميل البيانات في الحالة (Session State) لضمان التحديث الفوري
if 'db' not in st.session_state:
    st.session_state.db = load_data()

st.title("🛠️ منظومة إبراهيم المتكاملة (صيانة + صور + ملصقات)")

tab1, tab2, tab3 = st.tabs(["➕ إضافة جهاز", "🔍 بحث وتعديل", "📊 التقارير والأرباح"])

# --- 1. إضافة جهاز ---
with tab1:
    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            customer = st.text_input("👤 اسم الزبون")
            phone = st.text_input("📞 رقم الهاتف")
            brand = st.selectbox("📦 الماركة", ["iPhone", "Samsung", "Xiaomi", "Infinix", "Techno", "أخرى"])
            model = st.text_input("📱 الموديل (اكتبه يدوياً)")
        with col2:
            cost = st.number_input("💰 التكلفة المتفق عليها", min_value=0)
            parts = st.number_input("🔧 سعر القطع (اختياري)", min_value=0)
            issue = st.text_area("📝 وصف العطل")
            uploaded_file = st.file_uploader("📸 تصوير الجهاز أو رفع صورة", type=["jpg", "png", "jpeg"])

        if st.button("✅ حفظ الجهاز وتوليد وصل"):
            if customer and phone:
                new_id = len(st.session_state.db) + 1001
                img_path = ""
                if uploaded_file:
                    img_path = os.path.join(IMAGE_DIR, f"{new_id}.jpg")
                    with open(img_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                
                new_entry = {
                    "ID": new_id, "الزبون": customer, "الهاتف": phone, "الماركة": brand,
                    "الموديل": model, "العطل": issue, "التكلفة": cost, "سعر_القطع": parts,
                    "الحالة": "تحت الصيانة", "التاريخ": datetime.now().strftime("%Y-%m-%d"),
                    "الصورة": img_path
                }
                
                st.session_state.db = pd.concat([st.session_state.db, pd.DataFrame([new_entry])], ignore_index=True)
                save_data(st.session_state.db)
                
                # عرض ملصق الاستلام للطباعة
                st.success(f"تم الحفظ! رقم العملية: {new_id}")
                st.markdown(f"""
                <div style="border:2px dashed #000; padding:10px; background-color:#fff; color:#000; text-align:right;">
                    <h3>وصل استلام جهاز - صيانة إبراهيم</h3>
                    <p><b>رقم الجهاز:</b> {new_id}</p>
                    <p><b>الزبون:</b> {customer}</p>
                    <p><b>الجهاز:</b> {brand} {model}</p>
                    <p><b>العطل:</b> {issue}</p>
                    <p><b>التاريخ:</b> {datetime.now().strftime("%Y-%m-%d")}</p>
                    <p style="text-align:center;">يرجى الاحتفاظ بالرقم عند الاستلام</p>
                </div>
                """, unsafe_allow_html=True)
                st.info("💡 يمكنك أخذ لقطة شاشة (Screenshot) للوصل أعلاه وإرسالها للزبون.")
            else:
                st.error("الرجاء إدخال الاسم ورقم الهاتف")

# --- 2. البحث والتعديل ---
with tab2:
    search = st.text_input("🔍 ابحث برقم الهاتف أو الاسم")
    if search:
        results = st.session_state.db[st.session_state.db['الزبون'].str.contains(search) | st.session_state.db['الهاتف'].str.contains(search)]
        for idx, row in results.iterrows():
            with st.expander(f"جهاز: {row['الزبون']} - {row['الموديل']}"):
                col_a, col_b = st.columns(2)
                with col_a:
                    st.write(f"**العطل:** {row['العطل']}")
                    st.write(f"**الحالة الحالية:** {row['الحالة']}")
                    new_status = st.selectbox("تغيير الحالة", ["تحت الصيانة", "تم التسليم"], key=f"st_{idx}")
                    if st.button("تحديث الحالة", key=f"up_{idx}"):
                        st.session_state.db.at[idx, 'الحالة'] = new_status
                        save_data(st.session_state.db)
                        st.rerun()
                with col_b:
                    if row['الصورة'] and os.path.exists(str(row['الصورة'])):
                        st.image(row['الصورة'], caption="صورة الجهاز", width=200)

# --- 3. التقارير ---
with tab3:
    df = st.session_state.db
    if not df.empty:
        total_revenue = df[df['الحالة'] == "تم التسليم"]['التكلفة'].sum()
        total_parts = df[df['الحالة'] == "تم التسليم"]['سعر_القطع'].sum()
        net_profit = total_revenue - total_parts
        
        c1, c2, c3 = st.columns(3)
        c1.metric("إجمالي الدخل", f"{total_revenue} $")
        c2.metric("تكلفة القطع", f"{total_parts} $")
        c3.metric("صافي الربح", f"{net_profit} $")
        
        st.write("### قائمة جميع الأجهزة")
        st.dataframe(df)
    else:
        st.write("لا توجد بيانات حالياً.")
