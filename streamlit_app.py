import streamlit as st
import pandas as pd
import numpy as np
from recommender import SimpleHybridRecommender
from datetime import datetime

st.set_page_config(page_title="Genesis AI Recommendation Engine for Market Simulation", layout="wide", initial_sidebar_state="expanded")

# ---- Load data ----
@st.cache_data
def load_data():
    products = pd.read_csv("products.csv")
    history = pd.read_csv("user_history.csv")
    users = pd.read_csv("user_master.csv")
    return products, history, users

products, history, users = load_data()
reco = SimpleHybridRecommender(products, history)

# ---- Black theme + CSS + transitions ----
st.markdown("""
<style>
:root{
  --bg: #0b0f14;
  --card: #0f1720;
  --muted: #9aa5b1;
  --accent: linear-gradient(90deg,#7C4DFF,#00E5FF);
  --glass: rgba(255,255,255,0.02);
}
html, body, #root > div, .main {
    background: linear-gradient(180deg, #060708, #0b0f14);
    color: #e6eef6;
}
.header {
    padding:18px;
    border-radius:12px;
    background: linear-gradient(90deg, rgba(124,77,255,0.08), rgba(0,229,255,0.04));
    box-shadow: 0 8px 30px rgba(2,6,23,0.6);
    margin-bottom: 18px;
    display:flex;
    justify-content:space-between;
    align-items:center;
}
.title {font-size:28px; font-weight:700; margin:0; color: #fff;}
.subtitle {font-size:13px; color:var(--muted); margin-top:4px;}
.card {background: linear-gradient(180deg, rgba(255,255,255,0.02), rgba(255,255,255,0.01)); border-radius:12px; padding:14px; box-shadow: 0 8px 30px rgba(3,6,10,0.6); border:1px solid rgba(255,255,255,0.03);}
.grid {display:grid; grid-template-columns: repeat(auto-fit, minmax(230px, 1fr)); gap:12px;}
.prod {padding:12px; border-radius:10px; background: linear-gradient(180deg, rgba(255,255,255,0.01), rgba(255,255,255,0.02)); transition: transform .14s ease, box-shadow .14s ease;}
.prod:hover {transform: translateY(-6px); box-shadow: 0 18px 50px rgba(2,6,23,0.7);}
.price {font-weight:700; font-size:16px; color:#fff;}
.muted {color:var(--muted); font-size:13px;}
.conf {height:8px; background:rgba(255,255,255,0.04); border-radius:8px; overflow:hidden;}
.conf > .bar {height:8px; background:linear-gradient(90deg,#7C4DFF,#00E5FF);}
.small {font-size:12px; color:var(--muted);}
.btn {background:transparent; border:1px solid rgba(255,255,255,0.04); padding:8px 12px; border-radius:8px; color:#e6eef6;}
.save-ok {background:linear-gradient(90deg,#16a085,#1abc9c); padding:8px 10px; border-radius:8px; color:white;}
@media (max-width: 768px) {
    .header {flex-direction:column; align-items:flex-start;}
}
</style>
""", unsafe_allow_html=True)

# ---- Header ----
st.markdown(f'<div class="header"><div><div class="title">🧠 Genesis AI Recommendation Engine for Market Simulation</div><div class="left">Sleek demo: personas, recommendations & session simulation</div></div><div><span class="small">Built by Team ZORO</span></div></div>', unsafe_allow_html=True)

# ---- Sidebar Controls ----
with st.sidebar:
    st.header("Controls & Filters")
    # sample IDs for convenience
    try:
        sample_ids = users['user_id'].sample(6, random_state=42).tolist()
    except Exception:
        sample_ids = [1]
    input_id = st.number_input("Customer ID", min_value=1, step=1, value=int(sample_ids[0]))
    input_name = st.text_input("Customer Name (optional)", "")
    st.markdown("---")
    cat_filter = st.multiselect("Category filter (optional)", options=sorted(products['category'].unique()), default=[])
    top_k = st.slider("Number of suggestions", 5, 20, 8)
    st.markdown("---")
    st.write("Export & demo")
    if st.button("Export current recs"):
        recs = reco.recommend(int(input_id), top_k=top_k)
        csv = recs.to_csv(index=False)
        st.download_button("Download CSV", data=csv, file_name=f"recs_user_{input_id}.csv", mime="text/csv")

# ---- Main layout ----
col_left, col_right = st.columns([1,2])

# Left: Persona card + search & save
with col_left:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("👤 Customer Lookup")
    st.write("Search by ID (and optional name).")
    
    existing = users[users["user_id"]==int(input_id)]
    found = (not existing.empty) and (not input_name.strip() or input_name.strip().lower() in existing['name'].str.lower().tolist())
    
    if found:
        row = existing.iloc[0]
        st.markdown(f'**{row["name"]}**  •  {row["city"]}')
        st.markdown(f'<div class="small">Persona: {row["persona"]} • Avg spend: ₹{int(row["avg_price"])}</div>', unsafe_allow_html=True)
        user_hist = history[history['user_id']==int(input_id)]
        st.metric("Past purchases", len(user_hist))
        st.metric("Total spend", f'₹{int(user_hist["price_paid"].sum()) if not user_hist.empty else 0}')
        with st.expander("Last purchases (peek)"):
            st.dataframe(user_hist.sort_values("timestamp", ascending=False).head(6)[["timestamp","product_name","category","price_paid"]])
    else:
        st.markdown("**User not found.**", unsafe_allow_html=True)
        st.info("Would you like to save this person as a new member?")
        if st.button("Save as new member"):
            new_user = {
                "user_id": int(input_id),
                "name": input_name if input_name.strip() else f"User {int(input_id)}",
                "age": 30,
                "gender": "Not specified",
                "city": "Unknown",
                "income_bracket": "Middle",
                "persona": "New Starter",
                "avg_price": 0.0
            }
            users = pd.concat([users, pd.DataFrame([new_user])], ignore_index=True)
            users.to_csv("user_master.csv", index=False)
            
            # Clear cache and reload
            st.cache_data.clear()
            products, history, users = load_data()
            
            st.success("Saved new member ✅ — dataset updated")
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("## 🔎 Filters By Product Category")
    sel_cat = st.multiselect("Category filter (visual + filter)", options=sorted(products["category"].unique()), default=[])
    min_price, max_price = st.slider("Price range", 0, int(products["price"].max()), (0, int(products["price"].max())))
    st.write("---")
    if sel_cat:
        filtered = products[products["category"].isin(sel_cat) & products["price"].between(min_price, max_price)]
        st.markdown(f"### 🔍 {len(filtered)} products in selection")
        st.dataframe(filtered[["product_id", "name", "category", "price"]].head(10))
    st.markdown("## ⚙️ Debug / Info")
    st.text("Dataset stats")
    st.write(f"Products: {len(products)}")
    st.write(f"Users: {len(users)}")
    st.write(f"History rows: {len(history)}")
    st.write("---")
    st.markdown("Made for Genesis AI By Team ZORO")

# Right: Recommendations & session
with col_right:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("✨ Recommendations")
    recs = reco.recommend(int(input_id), top_k=top_k)
    if cat_filter:
        recs = recs[recs['category'].isin(cat_filter)]
        if recs.empty:
            st.warning("No recommendations in selected categories — try clearing the filter.")
    st.markdown('<div class="grid">', unsafe_allow_html=True)
    for _, r in recs.iterrows():
        score = float(r.get("score", 0.6)) if "score" in r else 0.6
        conf = int(np.clip(score, 0, 1)*100)
        st.markdown(f'''
            <div class="prod">
                <div style="display:flex;justify-content:space-between;align-items:start;">
                    <div style="width:68%"><b style="font-size:15px">{r["name"]}</b><div class="muted">{r["category"]} • {r["brand"]}</div></div>
                    <div style="text-align:right"><div class="price">₹{int(r["price"])}</div><div class="small">⭐ {r.get("rating",4.2)}</div></div>
                </div>
                <div style="margin-top:8px" class="small"><i>{r.get("why","Personalized pick")}</i></div>
                <div style="margin-top:10px">
                    <div class="conf"><div class="bar" style="width:{conf}%"></div></div>
                </div>
            </div>
        ''', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown("<hr/>", unsafe_allow_html=True)
    st.subheader("🛒 Simulated Shopping Session")
    session = reco.simulate_session(int(input_id), recs, steps=min(5, len(recs)))
    if session.empty:
        st.info("No simulated session available for this user. Try another ID.")
    else:
        for _, ev in session.iterrows():
            st.markdown(f'<div class="card" style="margin-bottom:8px;padding:10px"><b>Step {int(ev["step"])} — {ev["action"].upper()}</b><div class="small">{ev["name"]} • ₹{int(ev["price"])} • {ev["category"]}</div></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown("<div style='text-align:center;color:var(--muted);padding:12px;margin-top:12px'>Genesis AI — Modern Black UI • Demo ready</div>", unsafe_allow_html=True)
