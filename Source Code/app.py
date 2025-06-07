# Load required standard and third-party libraries
import os
import sys
import tempfile
import re
import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import xml.etree.ElementTree as ET
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from itertools import combinations
from pyvis.network import Network
from collections import defaultdict

# Extend sys.path to import modules from root
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sdg_list import sdgs
from graph_builder import build_sdg_graph
from utils.input_manager import (
    extract_texts_from_pdf_batch,
    extract_texts_from_zip_any_structure,
    extract_text_from_ep_xml_file
)
from nodes.opportunity_node import OpportunityNode
from nodes.startup_node import StartupNode
from utils.narrative_generator import describe_opportunity, describe_startup

# Configure Streamlit app
st.set_page_config(page_title="Patent2SDG", layout="wide")
st.title("Patent2SDG – Patent Classification by SDGs")

# Initialize session state
if 'ready' not in st.session_state:
    st.session_state.update({
        'ready': False,
        'text_data': {},
        'graph': None,
        'results_df': None,
        'opp_links': {},
        'startup_node': None
    })

# Load a pretrained SBERT model for text embeddings; cached for performance
@st.cache_resource
def load_model():
    return SentenceTransformer('all-MiniLM-L6-v2')

model = load_model()

# Instructions section
with st.expander("How to use this tool"):
    st.markdown("""
    1. Paste your patent abstract manually or upload one or more **PDF, XML or EPO ZIP** files.  
    2. Click the button to classify and visualize SDG relevance.  
    3. Explore the graph and download the results.
    """)

# Reset button logic
if st.button("Reset Batch"):
    keys_to_clear = [
        "ready", "text_data", "graph", "results_df",
        "opp_links", "startup_node", "user_text", "uploaded_files", "startup_description"
    ]
    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]
    st.rerun()

# User input for text or file upload
st.text_area("Enter patent abstract here", height=250, key="user_text")
st.file_uploader(
    "Or upload one or more PDF, XML or EPO ZIP files",
    type=["pdf", "zip", "xml"], accept_multiple_files=True, key="uploaded_files"
)

# File format helper functions
def is_zip(file): return file.name.lower().endswith(".zip")
def is_pdf(file): return file.name.lower().endswith(".pdf")
def is_xml(file): return file.name.lower().endswith(".xml")

# Pyvis graph rendering function
def show_pyvis_graph(G, height=800, min_affinity=0.3):
    net = Network(height=f"{height}px", width='100%', bgcolor='#ffffff', font_color='black', notebook=False)

    net.set_options("""
        var options = {
        "layout": {"improvedLayout": true},
        "interaction": {
            "zoomView": true,
            "dragView": true,
            "hover": true,
            "navigationButtons": true,
            "tooltipDelay": 200
        },
        "physics": {
            "forceAtlas2Based": {
            "gravitationalConstant": -50,
            "centralGravity": 0.005,
            "springLength": 100,
            "springConstant": 0.08
            },
            "minVelocity": 0.75,
            "solver": "forceAtlas2Based"
        },
        "nodes": {
            "scaling": {
            "min": 10,
            "max": 30,
            "label": {"enabled": true,"min": 14,"max": 30}
            },
            "font": {"size": 14,"face": "arial","background": "white","strokeWidth": 0}
        }
        }
    """)

    for node, data in G.nodes(data=True):
        color = {"opportunity": "yellow", "startup": "red", "sdg": "green", "patent": "lightblue"}.get(data.get('type', ''), "gray")
        degree = G.degree(node)
        size = 15 + degree * 2
        label = data.get('label', node)
        font_color = {"opportunity": "#666600", "startup": "#990000", "sdg": "#006600", "patent": "#003366"}.get(data.get('type', ''), "black")
        net.add_node(node, label=label, color=color, size=size, font={'color': font_color})

    for u, v, data in G.edges(data=True):
        weight = float(data.get("weight", 0.1))
        show_label = G.nodes[u].get("type") == "patent" and G.nodes[v].get("type") == "sdg" or G.nodes[v].get("type") == "patent" and G.nodes[u].get("type") == "sdg"
        title = f"Affinity: {weight:.2f}" if show_label and weight >= min_affinity else ""
        net.add_edge(u, v, value=weight, title=title, label=title)

    tmp_path = tempfile.NamedTemporaryFile(delete=False, suffix=".html").name
    net.write_html(tmp_path)
    with open(tmp_path, 'r', encoding='utf-8') as f:
        components.html(f.read(), height=height + 50, scrolling=True)

# Main logic button
if st.button("Classify and Display Graph"):
    used_text = st.session_state.user_text.strip()
    uploaded_files = st.session_state.uploaded_files
    pdfs = [f for f in uploaded_files or [] if is_pdf(f)]
    zips = [f for f in uploaded_files or [] if is_zip(f)]
    xmls = [f for f in uploaded_files or [] if is_xml(f)]

    all_names = [f.name for f in pdfs + zips + xmls]
    duplicates = set(name for name in all_names if all_names.count(name) > 1)
    if duplicates:
        st.error(f"Duplicate file(s) detected: {', '.join(duplicates)}. Please upload unique files only.")
        st.stop()

    if sum([bool(used_text), bool(pdfs), bool(zips), bool(xmls)]) != 1:
        st.warning("Please provide exactly one input type.")
        st.stop()

    if zips:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".zip") as tmp:
            tmp.write(zips[0].read())
            text_data = extract_texts_from_zip_any_structure(tmp.name, st_ref=st)
    elif pdfs:
        text_data = extract_texts_from_pdf_batch(pdfs, st_ref=st)
    elif xmls:
        text_data = {}
        for x in xmls:
            text_data.update(extract_text_from_ep_xml_file(x))
    else:
        if len(used_text) < 20 or used_text.count(" ") < 5:
            st.warning("Input text is too short or invalid.")
            st.stop()
        text_data = {"User_Text_Input": used_text.strip()}

    if not text_data:
        st.warning("No valid text extracted.")
        st.stop()

    st.session_state.update({"text_data": text_data})

    sdg_embeddings = [model.encode(sdg.description) for sdg in sdgs]
    full_G = build_sdg_graph(sdgs)
    for sdg in sdgs:
        full_G.nodes[sdg.id]['type'] = 'sdg'

    patent_embeddings = {}
    batch_table_data = defaultdict(list)

    for filename, text in text_data.items():
        node_id = f"PATENT_{filename}"
        emb = model.encode(text)
        patent_embeddings[filename] = emb
        sims = cosine_similarity([emb], sdg_embeddings)[0]
        top_indices = sims.argsort()[::-1][:5]
        for i in top_indices:
            sim_score = sims[i]
            batch_table_data[filename].append({
                "Patent File": filename,
                "SDG ID": sdgs[i].id,
                "SDG Name": sdgs[i].name,
                "Affinity": round(sim_score, 4)
            })
            full_G.add_node(node_id, label=filename, type="patent")
            full_G.add_edge(node_id, sdgs[i].id, weight=float(sim_score))

    for (f1, e1), (f2, e2) in combinations(patent_embeddings.items(), 2):
        sim = cosine_similarity([e1], [e2])[0][0]
        if sim > 0.75:
            full_G.add_edge(f"PATENT_{f1}", f"PATENT_{f2}", weight=float(sim))

    opp_nodes, opp_links = OpportunityNode.generate_shared_opportunity_nodes(patent_embeddings, threshold=0.35)
    st.session_state['opp_links'] = opp_links

    for i, node in enumerate(opp_nodes, start=1):
        related_texts = [text_data[pid] for pid in opp_links[node.id]]
        raw = describe_opportunity(related_texts)
        node.label = f"Opportunity_{i}"
        node.id = f"OPPORTUNITY_{i}"
        full_G.add_node(node.id, label=node.label, type="opportunity")
        for pid in opp_links[node.id]:
            full_G.add_edge(f"PATENT_{pid}", node.id, weight=1.0)

    patents_for_startup = list(opp_links[max(opp_links, key=lambda k: len(opp_links[k]))]) if opp_links else list(patent_embeddings.keys())
    startup_raw = describe_startup([text_data[pid] for pid in patents_for_startup])
    st.session_state['startup_description'] = startup_raw

    match = re.search(r"^## Startup Idea: (.+)", startup_raw.strip(), re.MULTILINE)
    startup_name = match.group(1).strip() if match else "startup_idea"

    startup_node = StartupNode(
        node_id="STARTUP_ID",
        name=startup_name,
        business_model="-",
        pain_point="-",
        impact="-"
    )
    st.session_state['startup_node'] = startup_node
    full_G.add_node(startup_node.id, label=startup_node.name, type="startup")
    for pid in patents_for_startup:
        full_G.add_edge(f"PATENT_{pid}", startup_node.id, weight=1.0)

    df_all = pd.concat([pd.DataFrame(v) for v in batch_table_data.values()], ignore_index=True)
    st.session_state.update({"graph": full_G, "results_df": df_all, "ready": True})

# UI rendering if graph is ready
if st.session_state["ready"]:
    st.subheader("Graph Visualization")
    affinity_threshold = st.slider("Minimum Affinity to Display (graph edges)", 0.0, 1.0, 0.3, 0.05)
    show_pyvis_graph(st.session_state["graph"], min_affinity=affinity_threshold)

    with st.expander("Node Color Legend"):
        st.markdown("""
        - 🔵 **Light Blue**: Patent Node  
        - 🟢 **Green**: SDG Node  
        - 🔴 **Red**: Startup Idea  
        - 🟡 **Yellow**: Opportunity Node
        """)

    st.subheader("Top SDGs")
    st.dataframe(st.session_state["results_df"].style.set_properties(**{'border': '1px solid black'}), use_container_width=True)

    with st.expander("What is the Affinity Score?"):
        st.markdown("""
        The **Affinity** score represents the degree of semantic similarity between a patent's abstract and the textual definition of a specific United Nations Sustainable Development Goal (SDG).  
        - It ranges from **0 to 1**, where:  
          - **1** means a perfect semantic match  
          - **0** means no semantic similarity  
        """)

    csv_body = st.session_state["results_df"].to_csv(index=False)
    st.download_button(
        label="Download CSV",
        data=csv_body.encode('utf-8'),
        file_name='patent2sdg_results.csv',
        mime='text/csv'
    )

    def dataframe_to_xml(df):
        root = ET.Element("Results")
        for _, row in df.iterrows():
            entry = ET.SubElement(root, "Result")
            for col, val in row.items():
                child = ET.SubElement(entry, col.replace(" ", "_"))
                child.text = str(val)
        return ET.tostring(root, encoding='utf-8', method='xml')

    xml_data = dataframe_to_xml(st.session_state["results_df"])
    st.download_button(
        label="Download XML",
        data=xml_data,
        file_name='patent2sdg_results.xml',
        mime='application/xml'
    )

    st.subheader("Opportunity Nodes Information")
    for idx, (opp_id, patent_ids) in enumerate(st.session_state["opp_links"].items(), start=1):
        if len(patent_ids) >= 2:
            title = f"Opportunity_{idx} from: ({' + '.join(patent_ids)})"
            texts = [st.session_state["text_data"][pid] for pid in patent_ids]
            description = describe_opportunity(texts)
            st.markdown(f"### {title}")
            for line in description.splitlines():
                st.markdown(line, unsafe_allow_html=True)
            st.markdown("---")

    st.subheader("Startup Idea Generated")
    st.markdown(st.session_state.get("startup_description", "No startup idea generated."))