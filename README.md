# 🏛️ Colombo Market Signal: CSE Sentiment Engine

An institutional-grade Natural Language Processing (NLP) pipeline designed to track macroeconomic sentiment for the Colombo Stock Exchange (CSE). 

This engine solves a critical problem in FinTech: **pre-trained financial AI models are biased toward Wall Street.** To accurately read a frontier market like Sri Lanka, this project wraps a robust machine learning model (FinBERT) inside a custom, configuration-driven rule engine to apply local macroeconomic realities.

## ✨ Key Engineering Features

* **🧠 Hybrid NLP Architecture:** Combines the deep-learning contextual power of `ProsusAI/finbert` with hard-coded macroeconomic rule overrides (e.g., teaching the AI that "falling oil prices" and "low inflation" are highly bullish for an importing nation).
* **⚙️ Configuration-Driven Design:** The entire system's logic (geo-blocks, noise filters, financial lexicon, and multipliers) is decoupled from the core application code via a master configuration dictionary, preventing software decay and allowing for instant updates.
* **🛡️ Dynamic Geo-Blocking:** Advanced keyword and symbol isolation prevents geopolitical cross-contamination (e.g., successfully filtering out Indian index news, `₹` symbols, and `paise` currency data that usually bypass generic regional filters).
* **⚖️ Reality-Weighted Failsafes:** Implements a dynamic 75/25 weighting system prioritizing domestic macro signals over global noise. Features an automated "Data Starvation Failsafe" that rebalances mathematical weights to 50/50 if local data volume drops below safe thresholds.

## 🛠️ Tech Stack
* **Language:** Python
* **Frontend/Deployment:** Streamlit
* **Machine Learning:** HuggingFace `transformers` (PyTorch)
* **Data Visualization:** Plotly
* **Data Ingestion:** NewsAPI REST endpoint

## 🚀 How to Run Locally

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/VisuraLokithaDeSilva/cse-sentiment-engine.git](https://github.com/VisuraLokithaDeSilva/cse-sentiment-engine.git)
   cd cse-sentiment-engine
