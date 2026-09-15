
import streamlit as st

# --- GLOBAL STATE (Shared for Canteen Manager) ---
@st.cache_resource


def get_global_state():
    return {
        "orders": [],
        "canteen_menu": {
            "Samosa 🥟": {"price": 15, "available": True, "category": "Food"},
            "Cold Coffee 🧋": {"price": 30, "available": True, "category": "Food"},
            "Blue Ball Pen 🖋️": {"price": 10, "available": True, "category": "Stationary"},
            "Lab Record Notebook 📖": {"price": 40, "available": True, "category": "Stationary"}
        },
        "student_requests": [],
        "token_counter": 100
    }

global_state = get_global_state()

# --- LOCAL STATE (Per Student Session) ---
if "orders" not in st.session_state:
    st.session_state.orders = []
if "student_requests" not in st.session_state:
    st.session_state.student_requests = []

st.set_page_config(page_title="GRABIT", layout="wide", initial_sidebar_state="collapsed")

st.title("🏪 GRABIT: Unified Utility & Food Ecosystem")
st.caption("CSE 3rd Year Mini Project Expo Prototype by Nida")
st.markdown("---")

# ==========================================
# SIMPLE ROLE-BASED LOGIN SYSTEM
# ==========================================
role = st.radio("Login as:", ["Student/College User", "Canteen Manager"])

# ==========================================
# STUDENT INTERFACE (Local State)
# ==========================================
if role == "Student/College User":
    st.success("✅ Logged in as Student/College User (Buyer)")
    app_tab_student = st.tabs(["📱 Open Student App View"])[0]

    with app_tab_student:
        st.subheader("Student Terminal Panel")
        st_tab_shop, st_tab_request = st.tabs(["🛒 Browse & Order Store Items", "💡 Request Custom Utility/Item"])

        # --- SHOPPING ---
        with st_tab_shop:
            st.write("### Store Catalog")
            cat_food = {k: v for k, v in global_state["canteen_menu"].items() if v["category"] == "Food"}
            cat_stat = {k: v for k, v in global_state["canteen_menu"].items() if v["category"] == "Stationary"}
            cart = {}

            st.markdown("#### 📝 Stationary & Utilities")
            for item, details in cat_stat.items():
                if details["available"]:
                    qty = st.number_input(f"{item} (₹{details['price']})", min_value=0, max_value=5, value=0, key=f"st_stat_{item}")
                    if qty > 0:
                        cart[item] = {"qty": qty, "price": details["price"]}
                else:
                    st.text(f"❌ {item} (Out of Stock)")

            st.markdown("---")
            st.markdown("#### 🍔 Refreshments & Food")
            for item, details in cat_food.items():
                if details["available"]:
                    qty = st.number_input(f"{item} (₹{details['price']})", min_value=0, max_value=5, value=0, key=f"st_food_{item}")
                    if qty > 0:
                        cart[item] = {"qty": qty, "price": details["price"]}
                else:
                    st.text(f"❌ {item} (Out of Stock)")

            total_bill = sum(details["qty"] * details["price"] for details in cart.values())
            if total_bill > 0:
                st.write(f"### Total Bill: **₹{total_bill}**")
                if st.button("🛒 Place Order & Generate Token", type="primary", key="submit_order"):
                    global_state["token_counter"] += 1
                    new_token = global_state["token_counter"]
                    items_ordered = {item: {"qty": details["qty"], "status": "Pending"} for item, details in cart.items()}
                    global_state["orders"].append({
                        "token": new_token,
                        "items": items_ordered,
                        "status": "⌛ Processing at Counter"
                    })
                    st.session_state.orders.append({
                        "token": new_token,
                        "items": items_ordered,
                        "status": "⌛ Processing at Counter"
                    })
                    st.success(f"🎉 Order Confirmed! Your Token is **#{new_token}**")
                    st.balloons()

        # --- REQUEST ---
        with st_tab_request:
            st.write("### Suggest an Item to the Canteen")
            req_name = st.text_input("What item do you need?", key="req_item_input")
            if st.button("🚀 Send Request to Store Manager"):
                if req_name.strip() != "":
                    global_state["student_requests"].append(req_name.strip())
                    st.session_state.student_requests.append(req_name.strip())
                    st.success(f"Sent request for '{req_name}' to the manager dashboard!")
                    st.rerun()
                else:
                    st.error("Please fill in the item field first.")

        # --- ORDER STATUS ---
        st.write("### 📦 My Orders Status")
        if st.session_state.orders:
            for order in st.session_state.orders:
                item_status_list = [f"{details['qty']}x {item} ({details['status']})" for item, details in order["items"].items()]
                st.markdown(f"**Token #{order['token']}** - {', '.join(item_status_list)} - Status: {order['status']}")
        else:
            st.info("No active orders yet.")

# ==========================================
# CANTEEN DASHBOARD (Shared Global State)
# ==========================================
elif role == "Canteen Manager":
    st.success("✅ Logged in as Canteen Manager (Seller)")
    app_tab_canteen = st.tabs(["👨‍🍳 Open Counter/Chef View"])[0]

    with app_tab_canteen:
        st.subheader("Canteen / Store Counter Dashboard")
        tab_orders, tab_inventory, tab_inbox = st.tabs(["📥 Active Orders Queue", "⚙️ Inventory Stocks Control", "📥 Student Request Inbox"])

        # --- ORDERS QUEUE ---
        with tab_orders:
            st.write("### Live Processing Queue")
            active_orders = [o for o in global_state["orders"] if o["status"] != "✅ Collected"]
            if not active_orders:
                st.write("✨ *No pending customer orders.*")
            else:
                for idx, order in enumerate(global_state["orders"]):
                    if order["status"] == "✅ Collected":
                        continue
                    st.markdown(f"#### **Token #{order['token']}**")
                    for item, details in order["items"].items():
                        col1, col2 = st.columns([2,1])
                        with col1:
                            st.write(f"{details['qty']}x {item} → Status: {details['status']}")
                        with col2:
                            if st.button(f"✅ Available {item}", key=f"avail_{order['token']}_{item}"):
                                order["items"][item]["status"] = "Available"
                                st.rerun()
                            if st.button(f"❌ Unavailable {item}", key=f"unavail_{order['token']}_{item}"):
                                order["items"][item]["status"] = "Unavailable"
                                st.rerun()

                    if order["status"] == "⌛ Processing at Counter":
                        if st.button(f"🔥 Pack Items #{order['token']}", key=f"pack_{idx}"):
                            order["status"] = "🍳 Preparing Order"
                            st.rerun()
                    elif order["status"] == "🍳 Preparing Order":
                        if st.button(f"🔔 Mark Ready #{order['token']}", key=f"ready_{idx}"):
                            order["status"] = "📦 Ready for Pickup"
                            st.rerun()
                    elif order["status"] == "📦 Ready for Pickup":
                        if st.button(f"✅ Dispense #{order['token']}", key=f"done_{idx}"):
                            order["status"] = "✅ Collected"
                            st.rerun()
                    st.markdown("---")

        # --- INVENTORY ---
        

        # --- INVENTORY ---
        with tab_inventory:
            st.write("### Catalog Management & Stock Configuration")
            c1, c2, c3 = st.columns(3)
            with c1:
                new_name = st.text_input("Name", key="inv_add_name")
            with c2:
                new_price = st.number_input("Price (₹)", min_value=1, value=10, key="inv_add_price")
            with c3:
                new_cat = st.selectbox("Category", ["Stationary", "Food"], key="inv_add_cat")
            if st.button("➕ Push to Live Catalog"):
                if new_name.strip() != "":
                    global_state["canteen_menu"][new_name.strip()] = {"price": new_price, "available": True, "category": new_cat}
                    st.success(f"Added {new_name} to the dashboard catalog.")
                    st.rerun()

            st.markdown("---")
            st.write("📝 **Live Stock & Price Configuration Matrix**")
            items_to_del = []
            for item, data in list(global_state["canteen_menu"].items()):
                col_i, col_p, col_a, col_d = st.columns(4)
                with col_i:
                    st.write(f"**{item}** ({data['category']})")
                with col_p:
                    edited_price = st.number_input("Price", min_value=1, value=int(data['price']), key=f"pr_{item}")
                    if edited_price != data['price']:
                        global_state["canteen_menu"][item]['price'] = edited_price
                with col_a:
                    stock_label = "In Stock" if data['available'] else "Out of Stock"
                    is_avail = st.checkbox(stock_label, value=data['available'], key=f"av_{item}")
                    if is_avail != data['available']:
                        global_state["canteen_menu"][item]['available'] = is_avail
                        st.rerun()
                with col_d:
                    if st.button("🗑️ Delete", key=f"del_{item}"):
                        items_to_del.append(item)

            if items_to_del:
                for item in items_to_del:
                    del global_state["canteen_menu"][item]
                    st.rerun()

        # --- STUDENT REQUEST INBOX ---
        with tab_inbox:
            st.write("### Incoming Student Utility Demands")
            st.caption("These items were typed directly by students because they weren't in your inventory catalog.")

            if not global_state["student_requests"]:
                st.info("✨ No pending custom item requests from students.")
            else:
                for idx, item_requested in enumerate(global_state["student_requests"]):
                    col_req_text, col_req_action = st.columns(2)
                    with col_req_text:
                        st.warning(f"🚨 Student needs: **{item_requested}**")
                    with col_req_action:
                        if st.button(f"Add to Catalog", key=f"add_req_{idx}"):
                            global_state["canteen_menu"][item_requested] = {"price": 20, "available": True, "category": "Stationary"}
                            global_state["student_requests"].pop(idx)
                            st.success(f"'{item_requested}' is now added to the catalog!")
                            st.rerun()
