import streamlit as st
from datetime import datetime

# Баракчанын дизайны
st.set_page_config(page_title="🌸 АСАЛГҮЛ 🌸", layout="wide")

# Кооздук үчүн CSS (3D карта стили)
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 20px; height: 3em; background-color: #ff4b4b; color: white; }
    .food-card {
        border: 1px solid #ddd; border-radius: 15px; padding: 20px;
        box-shadow: 10px 10px 20px rgba(0,0,0,0.1); text-align: center;
        background: white; transition: 0.3s;
    }
    .food-card:hover { transform: translateY(-10px); box-shadow: 15px 15px 30px rgba(0,0,0,0.2); }
    </style>
    """, unsafe_allow_html=True)

# --- УБАКТЫЛУУ БАЗА (Сайт иштеп турганда маалымат сакталат) ---
if 'orders' not in st.session_state:
    st.session_state.orders = []
if 'menu' not in st.session_state:
    st.session_state.menu = [
        {"аты": "Плов", "баасы": 220, "сүрөт": "https://img.freepik.com/free-photo/pilaf-with-meat-and-carrots-in-a-bowl_2829-13554.jpg"},
        {"аты": "Манты", "баасы": 200, "сүрөт": "https://img.freepik.com/free-photo/traditional-uzbek-manti-dumplings_2829-19106.jpg"}
    ]

# --- БАШКЫ БЕТ (WELCOME) ---
if 'started' not in st.session_state:
    st.session_state.started = False

if not st.session_state.started:
    st.title("🌸 АСАЛГҮЛ Кафесине Кош Келиңиз! 🌸")
    st.image("https://img.freepik.com/free-photo/delicious-uzbek-food-set_2829-19100.jpg", use_container_width=True)
    st.subheader("Бизде эң даамдуу жана эң таза тамактар! Төмөнкү баскычты басып, заказ бериңиз.")
    if st.button("🚀 ЗАКАЗ БЕРҮҮГӨ ӨТҮҮ"):
        st.session_state.started = True
        st.rerun()

else:
    # Меню жана Сатуучу бөлүмдөрүнө бөлүү
    mode = st.sidebar.selectbox("Бөлүмдү тандаңыз:", ["🍽️ Меню", "👨‍🍳 Сатуучу Панели"])

    if mode == "🍽️ Меню":
        st.title("🍽️ Биздин Меню")
        st.write("Каалаган тамагыңызды тандап, санын белгилеңиз.")
        
        cols = st.columns(2)
        cart = {}
        total = 0
        
        for i, item in enumerate(st.session_state.menu):
            with cols[i % 2]:
                st.markdown(f"""
                <div class="food-card">
                    <img src="{item['сүрөт']}" style="width:100%; border-radius:10px; height:200px; object-fit:cover;">
                    <h3>{item['аты']}</h3>
                    <h4 style="color: #ff4b4b;">{item['баасы']} сом</h4>
                </div>
                """, unsafe_allow_html=True)
                qty = st.number_input(f"Саны ({item['аты']}):", min_value=0, key=f"user_qty_{i}")
                if qty > 0:
                    cart[item['аты']] = qty
                    total += item['баасы'] * qty
        
        if total > 0:
            st.divider()
            st.subheader(f"Жалпы сумма: {total} сом")
            phone = st.text_input("Телефон номериңиз:")
            table = st.text_input("Стол № же Дарек:")
            
            if st.button("✅ ЗАКАЗДЫ ЖӨНӨТҮҮ"):
                new_order = {
                    "убакыт": datetime.now().strftime("%H:%M"),
                    "заказ": cart,
                    "сумма": total,
                    "телефон": phone,
                    "жайы": table,
                    "статус": "Даярдалууда ⏳"
                }
                # Маанилүү: Бул жерде маалымат базага кетет
                st.session_state.orders.append(new_order)
                st.success("Заказыңыз кабыл алынды! Сатуучуга билдирүү жөнөтүлдү.")

    elif mode == "👨‍🍳 Сатуучу Панели":
        st.title("🔐 Сатуучунун Кирүүсү")
        pwd = st.text_input("Пароль:", type="password")
        
        if pwd == "777":
            st.success("Кош келиңиз, Кожоюн!")
            action = st.radio("Эмне кылабыз?", ["📥 Заказдарды көрүү", "➕ Тамак кошуу", "📊 Отчет"])
            
            if action == "📥 Заказдарды көрүү":
                st.subheader("Жаңы түшкөн заказдар")
                if not st.session_state.orders:
                    st.info("Азырынча заказ жок.")
                else:
                    for order in st.session_state.orders:
                        with st.expander(f"Заказ - {order['убакыт']} (Стол: {order['жайы']})"):
                            st.write(f"**Заказ:** {order['заказ']}")
                            st.write(f"**Сумма:** {order['сумма']} сом")
                            st.write(f"**Тел:** {order['телефон']}")
                            st.write(f"**Статус:** {order['статус']}")
                            
            elif action == "➕ Тамак кошуу":
                st.subheader("Менюга жаңы тамак кошуу")
                n_name = st.text_input("Тамактын аты:")
                n_price = st.number_input("Баасы:", min_value=0)
                n_img = st.text_input("Сүрөт шилтемеси (URL):")
                if st.button("Кошуу ➕"):
                    st.session_state.menu.append({"аты": n_name, "баасы": n_price, "сүрөт": n_img})
                    st.success(f"{n_name} менюга ийгиликтүү кошулду!")
