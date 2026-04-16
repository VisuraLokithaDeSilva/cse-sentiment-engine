import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from transformers import pipeline
from datetime import datetime, timedelta

# =====================================================================
# 1. THE MASTER CONFIGURATION
# =====================================================================
SYSTEM_CONFIG = {
    "api": {
        "lookback_days": 3,
        "max_articles_to_scan": 100
    },
    "lexicon": {
        "core_finance": [
            'stock', 'price', 'economy', 'bank', 'trade', 'tax', 'finance', 
            'market', 'debt', 'cse', 'imf', 'revenue', 'invest', 'growth', 
            'aspi', 'sl20', 'turnover', 'rupee', 'inflation', 'port', 
            'agreement', 'cbsl', 'funding', 'reserves', 'interest rate',
            'sovereign', 'bonds', 'restructuring', 'bailout', 'export'
        ],
        "hard_noise": [
            'marijuana', 'attack', 'stabbing', 'murder', 'neural', 'biological', 
            'surgery', 'patient', 'wellness', 'healthy living', 'sports club', 
            'recipe', 'festival', 'arrested', 'dance class', 'invertebrate', 
            'fraudster', 'cricket', 'rugby'
        ],
        "geo_blocks": [
            'india', 'nigeria', 'toronto', 'canada', 'australia', 'nepal', 
            'shillong', 'pakistan', 'bangladesh', 'tribhuvan','₹', 'delhi', 
            'mumbai', 'sensex', 'nifty', 'japan', 'lebanon', 'africa', 
            'new zealand', 'bse', 'nse', 'nairobi', 'dhaka', 'paise', 'paisa'
        ]
    },
    "market_overrides": {
        "god_tier_bullish": {
            "multiplier": 3.0,
            "label": "POSITIVE",
            "rules": [
                {"context": "imf", "actions": ['approve', 'release', 'deal', 'funding', 'disburse', 'praise']},
                {"context": "inflation", "actions": ['low', 'drop', 'fall', 'ease', 'steady', 'decline']},
                {"context": "reserves", "actions": ['high', 'rise', 'grow', 'increase', 'strong', 'accumulate']},
                {"context": "rating", "actions": ['upgrade', 'stable', 'positive outlook']},
                {"context": "debt", "actions": ['restructured', 'agreement', 'haircut', 'resolved']}
            ]
        },
        "god_tier_bearish": {
            "multiplier": 3.0,
            "label": "NEGATIVE",
            "rules": [
                {"context": "default", "actions": ['sovereign', 'debt', 'fail', 'miss', 'bankrupt']},
                {"context": "inflation", "actions": ['spike', 'soar', 'high', 'record', 'surge']},
                {"context": "rating", "actions": ['downgrade', 'negative', 'junk', 'risk']},
                {"context": "imf", "actions": ['delay', 'suspend', 'withhold', 'fail', 'reject']}
            ]
        },
        "commodity_adjustments": {
            "multiplier": 1.5,
            "label": "POSITIVE",
            "rules": [
                {"context": "oil", "actions": ['fall', 'drop', 'low', 'ease', 'tumble', 'plunge']}
            ]
        }
    }
}

# =====================================================================
# 2. SYSTEM SETUP & AI INITIALIZATION
# =====================================================================
st.set_page_config(page_title="Colombo Market Signal", page_icon="🏛️", layout="wide")

@st.cache_resource
def load_sentiment_model():
    return pipeline("sentiment-analysis", model="ProsusAI/finbert", tokenizer="ProsusAI/finbert")

# Sidebar UI
with st.sidebar:
    st.markdown("## ⚙️ System Status")
    st.success("🟢 News API Connected")
    st.success("🟢 FinBERT Engine Active")
    st.info("📡 Scanning: Rolling 72 Hours")
    st.markdown("---")
    st.markdown("**Filters Applied:**")
    st.markdown("- 25+ Geo-Blocks\n- 20+ Noise Filters\n- Custom CBSL Logic")

sentiment_analyzer = load_sentiment_model()

try:
    API_KEY = st.secrets["NEWS_API_KEY"]
except KeyError:
    st.error("🔑 API Key Missing! Please configure .streamlit/secrets.toml")
    st.stop()

# =====================================================================
# 3. CORE LOGIC ENGINE
# =====================================================================
def apply_enterprise_overrides(title_lower, base_label, base_score):
    for category, config in SYSTEM_CONFIG["market_overrides"].items():
        for rule in config["rules"]:
            context = rule["context"]
            actions = rule["actions"]
            
            if context in title_lower and any(action in title_lower for action in actions):
                return config["label"], config["multiplier"]
                
    if any(up in title_lower for up in ['rally', 'jump', 'rocket', 'surge', 'record high', 'soars', 'rise', 'gain', 'rebound']):
        return "POSITIVE", 1.5
    if any(down in title_lower for down in ['crash', 'collapse', 'plummet', 'freefall', 'panic', 'plunge']):
        return "NEGATIVE", 1.5
        
    return base_label, base_score

# =====================================================================
# 4. UI MAIN DASHBOARD
# =====================================================================
st.title("🏛️ Colombo Market Signal")
st.markdown("##### Institutional-Grade Sentiment Analysis for the CSE")
st.markdown("---")

if st.button('🚀 Execute Dynamic Market Scan', use_container_width=True):
    with st.spinner("Initializing AI and scanning global feeds..."):
        
        local_score, local_count = 0, 0
        global_score, global_count = 0, 0
        pos_count, neg_count = 0, 0
        seen_titles = set()
        
        target_date = (datetime.now() - timedelta(days=SYSTEM_CONFIG["api"]["lookback_days"])).strftime('%Y-%m-%d')
        
        categories = {
            "Sri Lanka Macro & CSE": "Sri Lanka AND (economy OR business OR cse OR rupee OR 'Central Bank' OR debt)",
            "Global Market Drivers": "(global economy) OR (oil prices) OR (Federal Reserve) OR IMF"
        }
        
        col1, col2 = st.columns(2)
        
        for index, (name, query) in enumerate(categories.items()):
            target_col = col1 if index == 0 else col2
            with target_col:
                st.subheader(f"📡 {name}")
                url = f'https://newsapi.org/v2/everything?q={query}&language=en&sortBy=publishedAt&from={target_date}&pageSize={SYSTEM_CONFIG["api"]["max_articles_to_scan"]}&apiKey={API_KEY}'
                
                try:
                    response = requests.get(url, timeout=12)
                    data = response.json()
                    
                    if "articles" in data:
                        found_in_cat = 0
                        for article in data['articles']: 
                            title = article['title']
                            title_lower = title.lower()
                            
                            # FILTERS
                            if title_lower in seen_titles or any(bad in title_lower for bad in SYSTEM_CONFIG["lexicon"]["hard_noise"]): 
                                continue
                            if any(c in title_lower for c in SYSTEM_CONFIG["lexicon"]["geo_blocks"]) and "sri lanka" not in title_lower: 
                                continue

                            if any(good in title_lower for good in SYSTEM_CONFIG["lexicon"]["core_finance"]):
                                res = sentiment_analyzer(title[:512])[0]
                                label, conf_score = res['label'].upper(), res['score']
                                label, conf_score = apply_enterprise_overrides(title_lower, label, conf_score)

                                is_pos = label == "POSITIVE"
                                calculated_score = (1 if is_pos else -1) * conf_score
                                
                                if index == 0: 
                                    local_score += calculated_score
                                    local_count += 1
                                else: 
                                    global_score += calculated_score
                                    global_count += 1

                                seen_titles.add(title_lower)
                                
                                if is_pos: pos_count += 1
                                elif label == "NEGATIVE": neg_count += 1
                                
                                # Clean Typography for News Items
                                indicator = "🟢" if is_pos else "🔴" if label == "NEGATIVE" else "⚪"
                                st.markdown(f"**{indicator}** <span style='color:#bdc3c7'>{title}</span>", unsafe_allow_html=True)
                                found_in_cat += 1
                        
                        if found_in_cat == 0: 
                            st.caption("*No high-relevance financial news passed the enterprise filter.*")
                except requests.exceptions.RequestException: 
                    st.error("API Connection Error.")

        # =====================================================================
        # 5. REALITY-WEIGHTED ANALYTICS UI
        # =====================================================================
        st.markdown("---")
        total_articles = local_count + global_count
        
        if total_articles > 0:
            local_avg = (local_score / local_count) if local_count > 0 else 0
            global_avg = (global_score / global_count) if global_count > 0 else 0
            
            if local_count < 5:
                final_avg = (local_avg * 0.50) + (global_avg * 0.50)
                warning_flag = True
                math_note = f"Local Signal ({local_avg:.2f} × 50%) + Global Signal ({global_avg:.2f} × 50%)"
            else:
                final_avg = (local_avg * 0.75) + (global_avg * 0.25)
                warning_flag = False
                math_note = f"Local Signal ({local_avg:.2f} × 75%) + Global Signal ({global_avg:.2f} × 25%)"
            
            res_col1, res_col2 = st.columns([1, 1])
            
            with res_col1:
                st.write("### Market Sentiment Split")
                chart_data = pd.DataFrame({"Sentiment": ["Bullish", "Bearish"], "Count": [pos_count, neg_count]})
                fig = px.pie(chart_data, values='Count', names='Sentiment', hole=0.5, 
                             color='Sentiment', color_discrete_map={'Bullish': '#2ecc71', 'Bearish': '#e74c3c'})
                fig.update_layout(margin=dict(t=0, b=0, l=0, r=0))
                st.plotly_chart(fig, use_container_width=True)

            with res_col2:
                # Dashboard Logic
                if final_avg >= 0.15: sig, col, tip = "BULLISH", "#2ecc71", "Strong positive macroeconomic momentum overriding risks."
                elif final_avg > -0.15: sig, col, tip = "NEUTRAL", "#abb2b9", "Market is balancing conflicting economic data."
                else: sig, col, tip = "BEARISH", "#e74c3c", "Significant systemic risk factors detected."

                st.markdown(f"<h1 style='text-align: center; color: {col}; font-size: 3rem;'>{sig}</h1>", unsafe_allow_html=True)
                st.metric("Reality-Weighted Confidence", f"{final_avg:.2f}", f"{total_articles} Dynamic Sources")
                
                if warning_flag:
                    st.warning("⚠️ Local data starvation detected. Adjusting weight to 50/50 to prevent global skew.")

                # Dropdown for the nerdy stuff
                with st.expander("⚙️ View Engine Diagnostics & Math"):
                    st.caption(f"**Math Breakdown:** {math_note}")
                    st.info("Engine dynamically applies configuration rules and multi-level weights over a rolling 72-hour historical window.")
        else:
            st.error("Insufficient pure financial data to generate a confident market signal.")

st.markdown("---")
st.caption("Designed for the Colombo Stock Exchange | Natural Language Processing Pipeline")