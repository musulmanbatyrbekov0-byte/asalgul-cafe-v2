import streamlit as st
from google.cloud import firestore
from google.oauth2 import service_account
import json
from datetime import datetime

# --- БАЗАГА ТУТАШУУ ---
if "db" not in st.session_state:
    try:
        key_dict = json.loads(st.secrets["firestore"]["key"])
        creds = service_account.Credentials.from_service_account_info(key_dict)
        st.session_state.db = firestore.Client(credentials=creds)
    except Exception as e:
        st.error("Базага туташуу катасы! Secrets бөлүмүн текшериңиз.")

db = st.session_state.db

# --- МЕНЮ МААЛЫМАТТАРЫ ---
menu = [
    {"name": "Плов", "price": 220, "img": "https://img.freepik.com/free-photo/pilaf-with-meat-and-carrots-in-a-bowl_2829-13554.jpg"},
    {"name": "Манты", "price": 200, "img": "https://img.freepik.com/free-photo/traditional-uzbek-manti-dumplings_2829-19106.jpg"}
]

st.set_page_config(page_title="🌸 АСАЛГҮЛ 🌸", layout="wide")

# --- ИНТЕРФЕЙС ТАПТАРЫ ---
tab1, tab2, tab3 = st.tabs(["🛒 Заказ берүү", "🔍 Заказды текшерүү", "👨‍🍳 Сатуучу"])

# 1. ЗАКАЗ БЕРҮҮ БӨЛҮМҮ
with tab1:
    st.title("🌸 АСАЛГҮЛ Кафеси")
    selected_items = {}
    cols = st.columns(2)
    for i, item in enumerate(menu):
        with cols[i%2]:
            st.image(item['img'], use_container_width=True)
            st.subheader(f"{item['name']} - {item['price']} сом")
            q = st.number_input(f"Саны:", min_value=0, key=f"food_{i}")
            if q > 0: selected_items[item['name']] = q

    if selected_items:
        phone = st.text_input("Телефонуңуз (Мисалы: 0700123456):", key="order_phone")
        table = st.text_input("Стол № же Дарек:")
        if st.button("✅ Заказды жөнөтүү"):
            db.collection("orders").add({
                "items": str(selected_items),
                "phone": phone,
                "table": table,
                "time": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "status": "Жаңы 🟢"
            })
            st.success(f"Заказыңыз кетти! 'Заказды текшерүү' бөлүмүнөн {phone} номери аркылуу биле аласыз.")

# 2. КАРДАР ҮЧҮН ТЕКШЕРҮҮ БӨЛҮМҮ
with tab2:
    st.header("🔍 Заказыңыздын абалы")
    search_phone = st.text_input("Катталган номериңизди жазыңыз:")
    if search_phone:
        results = db.collection("orders").where("phone", "==", search_phone).order_by("time", direction="DESCENDING").limit(1).stream()
        found = False
        for res in results:
            found = True
            d = res.to_dict()
            st.markdown(f"""
            ### Сиздин акыркы заказыңыз:
            * **Убактысы:** {d['time']}
            * **Заказ:** {d['items']}
            * **Абалы (Статус):** <h2 style='color: blue;'>{d['status']}</h2>
            """, unsafe_allow_html=True)
        if not found:
            st.warning("Бул номер менен заказ табылган жок.")

# 3. САТУУЧУ БӨЛҮМҮ
with tab3:
    pwd = st.text_input("Пароль:", type="password")
    if pwd == "777":
        st.header("📥 Бардык заказдар")
        orders = db.collection("orders").order_by("time", direction="DESCENDING").stream()
        
        for o in orders:
            d = o.to_dict()
            doc_id = o.id
            with st.expander(f"Заказ: {d['time']} | Тел: {d['phone']} | Статус: {d['status']}"):
                st.write(f"**Эмне алды:** {d['items']}")
                st.write(f"**Каякка:** {d['table']}")
                
                # Статусту өзгөртүү
                new_status = st.selectbox("Статусту өзгөртүү:", 
                                         ["Жаңы 🟢", "Даярдалууда 👨‍🍳", "Жолдо 🚚", "Бүттү ✅", "Жокко чыгарылды ❌"], 
                                         key=f"status_{doc_id}")
                
                if st.button("Статусту сактоо", key=f"btn_{doc_id}"):
                    db.collection("orders").document(doc_id).update({"status": new_status})
                    st.success("Статус жаңырды!")
                    st.rerun()
