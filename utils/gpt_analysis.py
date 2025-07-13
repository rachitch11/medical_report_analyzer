import pandas as pd
import streamlit as st
from openai import OpenAI

# ✅ Initialize OpenAI client
client = OpenAI(api_key=st.secrets["openai"]["api_key"])

def analyze_reports(report_data):
    impressions = []
    trends = []
    prev_params = None
    prev_tumor = None
    tumor_summaries = []

    for i, report in enumerate(report_data):
        # ✅ Truncate input to avoid token overload (GPT-4 limit ≈ 8k tokens input)
        max_chars = 6000
        safe_text = report['text'][:max_chars]

        # ✅ Use GPT-3.5
        model_name ="gpt-3.5-turbo"

        prompt = f"""
You are a medical assistant. Analyze the following medical report dated {report['date']}.

Report Text (truncated to {max_chars} characters):
{safe_text}

1. Identify abnormal parameters with values.
2. Explain possible causes (if any).
3. Provide a short layman-friendly impression.
"""

        try:
            response = client.chat.completions.create(
                model=model_name,
                messages=[{"role": "user", "content": prompt}]
            )
            impressions.append({
                "Date": report["date"].strftime('%Y-%m-%d') if report["date"] else "Unknown",
                "Filename": report["filename"],
                "Impression": response.choices[0].message.content
            })

        except Exception as e:
            impressions.append({
                "Date": report["date"].strftime('%Y-%m-%d') if report["date"] else "Unknown",
                "Filename": report["filename"],
                "Impression": f"❌ Error: {str(e)}"
            })
            continue

        # ✅ Track parameter trends
        if prev_params:
            trend = compare_parameter_trends(prev_params, report["parameters"])
            trends.append(f"\nBetween {report_data[i-1]['date'].date()} and {report['date'].date()}:\n{trend}")
        prev_params = report["parameters"]

        # ✅ MRI Tumor trend tracking
        if report['tumor_sizes']:
            if prev_tumor:
                tumor_prompt = f"""
Compare the tumor sizes:
Before: {prev_tumor}
Now: {report['tumor_sizes'][0]}
Explain if it has grown, shrunk, or is stable in layman terms.
"""
                try:
                    tumor_resp = client.chat.completions.create(
                        model=model_name,
                        messages=[{"role": "user", "content": tumor_prompt}]
                    )
                    tumor_summary = tumor_resp.choices[0].message.content
                    tumor_summaries.append(f"{report['date'].date()}: {tumor_summary}")
                except:
                    tumor_summaries.append(f"{report['date'].date()}: ❌ Error during tumor analysis.")
            prev_tumor = report['tumor_sizes'][0]

    final_summary = "\n\n".join([row["Impression"] for row in impressions])
    trend_summary = "\n\n".join(trends)
    tumor_summary = "\n\n".join(tumor_summaries)

    return {
        "summary": final_summary + "\n\n📈 Trends:\n" + trend_summary + "\n\n🧠 MRI Findings:\n" + tumor_summary,
        "abnormal_table": pd.DataFrame(impressions)
    }

def compare_parameter_trends(prev, curr):
    output = []
    for key in curr:
        if key in prev:
            diff = curr[key] - prev[key]
            direction = "improved" if diff < 0 else "worsened" if diff > 0 else "unchanged"
            output.append(f"{key}: {direction} ({prev[key]} → {curr[key]})")
    return "\n".join(output)
