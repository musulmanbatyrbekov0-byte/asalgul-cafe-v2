import streamlit as st
from google.cloud import firestore
from google.oauth2 import service_account
import json
from datetime import datetime

# --- 1. БАЗАГА ТУТАШУУ ---
if "db" not in st.session_state:
    try:
        key_dict = json.loads(st.secrets["firestore"]["key"])
        creds = service_account.Credentials.from_service_account_info(key_dict)
        st.session_state.db = firestore.Client(credentials=creds)
    except Exception as e:
        st.error("Базага туташуу катасы! Secrets бөлүмүн текшериңиз.")
        st.stop()

db = st.session_state.db

# --- 2. ДИЗАЙН ---
st.set_page_config(page_title="🌸 АСАЛГҮЛ 🌸", layout="wide")

# --- 3. ИНТЕРФЕЙС ТАПТАРЫ ---
tab1, tab2, tab3 = st.tabs(["🛒 Заказ берүү", "🔍 Заказды текшерүү", "👨‍🍳 Сатуучу панели"])

# --- 4. КАРДАР: ЗАКАЗ БЕРҮҮ ---
with tab1:
    st.title("🌸 АСАЛГҮЛ Кафеси")
    menu_items = db.collection("menu").stream()
    menu_list = [item.to_dict() | {"id": item.id} for item in menu_items]
    
    if not menu_list:
        st.info("Азырынча меню бош. Сатуучу панелинде тамак кошуңуз.")
    
    selected_items = {}
    cols = st.columns(3)
    for i, item in enumerate(menu_list):
        with cols[i % 3]:
            st.image(item.get('img', 'https://via.placeholder.com/150'), use_container_width=True)
            st.subheader(f"{item['name']}")
            st.write(f"Баасы: {item['price']} сом")
            q = st.number_input(f"Саны:", min_value=0, key=f"order_{item['id']}")
            if q > 0:
                selected_items[item['name']] = q

    if selected_items:
        st.divider()
        phone = st.text_input("📞 Телефонуңуз:")
        address = st.text_input("📍 Стол № же Дарек:")
        if st.button("✅ Заказды жөнөтүү", use_container_width=True):
            if phone and address:
                db.collection("orders").add({
                    "items": str(selected_items),
                    "phone": phone,
                    "address": address,
                    "time": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "status": "Даярдалып жатат 👨‍🍳" # Баштапкы статус
                })
                st.success("Заказыңыз кабыл алынды!")
            else:
                st.warning("Телефон жана даректи толтуруңуз!")

# --- 5. КАРДАР: ЗАКАЗДЫ ТЕКШЕРҮҮ ---
with tab2:
    st.header("🔍 Заказыңыздын абалы")
    search_phone = st.text_input("Катталган номериңизди жазыңыз:", key="search_pt")
    if search_phone:
        results = db.collection("orders").where("phone", "==", search_phone).stream()
        order_data = [res.to_dict() for res in results]
        
        if order_data:
            order_data.sort(key=lambda x: x.get('time', ''), reverse=True)
            for d in order_data[:3]:
                st.divider()
                # Статуска жараша жазууну өзгөртүү
                if d['status'] == "Даяр 🥗":
                    st.balloons()
                    st.success(f"✅ **Заказыңыз даяр болду! Ашыңыз таттуу болсун!**")
                else:
                    st.warning(f"⏳ **Заказыңыз даярдалып жатат... Бир аз күтө туруңуз.**")
                
                st.write(f"⏰ Убактысы: {d['time']}")
                st.write(f"🍴 Заказ: {d['items']}")
        else:
            st.warning("Бул номер менен заказ табылган жок.")

# --- 6. САТУУЧУ: БАШКАРУУ ПАНЕЛИ ---
with tab3:
    st.header("🔐 Сатуучунун кирүүсү")
    pwd = st.text_input("Пароль:", type="password")
    
    if pwd == "777":
        admin_tab1, admin_tab2 = st.tabs(["📥 Заказдарды башкаруу", "🍴 Менюну башкаруу"])
        
        with admin_tab1:
            st.subheader("Келген заказдар")
            orders = db.collection("orders").stream()
            order_list = [o.to_dict() | {"id": o.id} for o in orders]
            order_list.sort(key=lambda x: x.get('time', ''), reverse=True)
            
            for d in order_list:
                doc_id = d['id']
                with st.expander(f"{d['time']} | Тел: {d['phone']} | {d['status']}"):
                    st.write(f"**Заказ:** {d['items']}")
                    st.write(f"**Дарек:** {d['address']}")
                    
                    # Сатуучу үчүн "Даяр" баскычы
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("🥗 ДАЯР БОЛДУ", key=f"ready_{doc_id}"):
                            db.collection("orders").document(doc_id).update({"status": "Даяр 🥗"})
                            st.rerun()
                    with col2:
                        if st.button("❌ Өчүрүү", key=f"del_ord_{doc_id}"):
                            db.collection("orders").document(doc_id).delete()
                            st.rerun()

        with admin_tab2:
            st.subheader("Менюну башкаруу")
            # (Меню кошуу коддору мурункудай калат...)
            new_name = st.text_input("Тамактын аты:")
            new_price = st.number_input("Баасы (сом):", min_value=0)
            new_img = st.text_input("Сүрөт URL:")
            if st.button("➕ Кош"):
                db.collection("menu").add({"name": new_name, "price": new_price, "img": new_img})
                st.rerun()
            
            st.divider()
            m_items = db.collection("menu").stream()
            for m in m_items:
                md = m.to_dict()
                c1, c2 = st.columns([3, 1])
                c1.write(f"{md['name']} - {md['price']} сом")
                if c2.button("Өчүрүү", key=f"m_del_{m.id}"):
                    db.collection("menu").document(m.id).delete()
                    st.rerun()



