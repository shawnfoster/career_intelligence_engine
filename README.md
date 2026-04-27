# 🧠 Career Intelligence Engine

> A decision system that identifies where you are most likely to win—and why.

---

## 🚀 What This Is

Most job seekers ask:
> “Do I qualify for this role?”

That’s the wrong question.

This system reframes it to:
> “What problem is this company trying to solve—and how do I position myself as the answer?”

---

## 🧠 Why This Matters

Most candidates:
- apply blindly  
- rely on keyword matching  
- fail to understand company context  

This system:
- surfaces **real business needs**
- translates them into **actionable positioning**
- increases probability of conversion

---

## ⚙️ What It Does

- Ingests real job postings (Greenhouse API)
- Extracts skills, tools, and role signals
- Scores alignment across weighted dimensions
- Classifies **Hiring Intent** (why the role exists)
- Identifies **Operator Type** (who they actually need)
- Flags **Wrong-Hire Risk**
- Generates **Positioning Strategy**

---

## 🧬 Example Output

**Finance & Strategy - Finance Analytics Analyst @ Stripe**

- **Hiring Intent:** Decision-support analytics  
- **Operator Type:** Analytical translator  
- **Wrong-Hire Risk:** Hiring someone who can build reports but cannot explain what the numbers mean for business action  

**Positioning:**
> Position as a low-ramp operator who translates data into decisions.

---

## 🖥️ Live Demo

Run locally:

```bash
python run_pipeline.py --greenhouse stripe
streamlit run app/streamlit_app.py