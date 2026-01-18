import streamlit as st
import time
import re
from pypdf import PdfReader
from google import genai
from langchain_community.tools.tavily_search import TavilySearchResults

# --------------------------------------------------
# API SETUP
# --------------------------------------------------
if "GEMINI_API_KEY" not in st.secrets or "TAVILY_API_KEY" not in st.secrets:
    st.error("Missing API keys.")
    st.stop()

client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
MODEL_ID = "gemini-flash-latest"

search_tool = TavilySearchResults(
    max_results=3,
    api_key=st.secrets["TAVILY_API_KEY"]
)

# --------------------------------------------------
# PDF SECTION EXTRACTION
# --------------------------------------------------
def extract_sections(file):
    reader = PdfReader(file)
    text = ""

    for page in reader.pages:
        if page.extract_text():
            text += page.extract_text() + "\n"

    lines = [l.strip() for l in text.split("\n") if l.strip()]
    sections = []
    header, body = None, []

    header_pattern = re.compile(r"^\d+\.\s+")

    for line in lines:
        if header_pattern.match(line):
            if header:
                sections.append((header, " ".join(body)))
            header = line
            body = []
        else:
            body.append(line)

    if header:
        sections.append((header, " ".join(body)))

    return sections

# --------------------------------------------------
# UI
# --------------------------------------------------
st.set_page_config(page_title="Fact Checker", layout="wide")
st.title(" AI Fact Checker")

uploaded_file = st.file_uploader("Upload PDF Report", type="pdf")

if uploaded_file:
    sections = extract_sections(uploaded_file)
    st.success(f"Detected {len(sections)} sections.")

    for i, (header, content) in enumerate(sections, start=1):

        claim = content.split(".")[0].strip() + "."

        with st.expander(f"Section {i}: {header}", expanded=True):

            st.markdown("### PDF Content")
            st.info(content[:600] + "...")

            st.markdown("### Claim")
            st.write(claim)

            # --------------------------------------------------
            # SEARCH (1 call)
            # --------------------------------------------------
            search_results = search_tool.invoke({"query": claim})
            evidence = "\n".join([r["content"] for r in search_results])
            sources = [r["url"] for r in search_results]

            # --------------------------------------------------
            # GEMINI PROMPT (CAUTIOUS BY DESIGN)
            # --------------------------------------------------
            prompt = f"""
You are a cautious professional fact-checker.

Rules you MUST follow:
- Use **Verified** only if the claim is explicitly confirmed by the evidence.
- Use **False** only if the evidence clearly contradicts the claim.
- If evidence is partial, outdated, mixed, forecast-based, or unclear,
  you MUST label the claim as **Inaccurate**.
- When in doubt, prefer **Inaccurate** over False.

Return EXACTLY in this format:

Status: Verified | Inaccurate | False
Explanation: brief, neutral reasoning

Claim:
{claim}

Evidence:
{evidence}
"""

            time.sleep(5)  # free-tier safety

            response = client.models.generate_content(
                model=MODEL_ID,
                contents=prompt
            )

            # --------------------------------------------------
            # OUTPUT PARSING
            # --------------------------------------------------
            lines = response.text.strip().split("\n", 1)

            status = lines[0].replace("Status:", "").strip()
            explanation = lines[1].replace("Explanation:", "").strip()

            st.markdown("### Status")
            if status == "Verified":
                st.success(status)
            elif status == "False":
                st.error(status)
            else:
                st.warning(status)

            st.markdown("### Explanation")
            st.write(explanation)

            if sources:
                st.markdown("### Sources")
                for s in sources:
                    st.write(s)

