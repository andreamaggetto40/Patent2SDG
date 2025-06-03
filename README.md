# Patent2SDG – Patent Classification by Sustainable Development Goals

**Patent2SDG** is an open-source tool designed to semantically classify patent texts according to the 17 United Nations Sustainable Development Goals (SDGs).  
It supports PDF, XML (EPO), and ZIP file formats, offering graph-based visualizations and automatic generation of innovation opportunities and startup ideas.  
Developed as a submission for the **EPO CodeFest Spring 2025**.

---
## Features
- Semantic classification using Sentence-BERT embeddings  
- Input support for PDF, XML (EPO format), and ZIP (including nested archives)  
- Interactive SDG-patent graph visualization (via Pyvis)  
- Identification of shared innovation opportunities  
- Automatic narrative generation for startup ideas and opportunities  
- Export of results in CSV and XML format  
- Intuitive web interface built with Streamlit
---

## Installation and Setup
Follow these steps to set up and run the Patent2SDG application locally:

### 1. Clone the repository
```bash
git clone https://github.com/epo/CFS25-Andrea-Maggetto.git
cd CFS25-Andrea-Maggetto
```
## 2. Create and activate a virtual environment 

**Linux/macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows**
```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install Dependencies
Navigate into the Source Code directory and install the required packages:
```bash
cd "Source Code"
pip install -r requirements.txt
```
### 4. Launch the Application
```bash
streamlit run "Source Code/app.py"
```
---

## How to Use

 1. Launch the app using Streamlit
 2. Paste a patent abstract or upload one or more patent files (PDF, XML, or ZIP).
 3. Click **“Classify and Display Graph”** to:
	 -   View the interactive graph with SDG-patent mappings
	    
	-   Discover shared innovation opportunities
	    
	-   Generate a startup idea based on the most relevant patents
	    
	-   Export results as CSV and XML
---

## Dependencies

The project relies on the following Python packages:

-   `streamlit`
    
-   `sentence-transformers`
    
-   `scikit-learn`
    
-   `pandas`
    
-   `networkx`
    
-   `pyvis`
    
-   `PyMuPDF`
    
-   `python-docx`
    
-   `PyPDF2`
    

All dependencies are listed in the `requirements.txt` file.

---
## Code

This submission complies with all rules outlined in the EPO CodeFest Spring 2025:

- Fully open-source
    
- Developed entirely within the challenge timeframe (March–May 2025)
    
-  Self-contained and testable with provided sample inputs
    
-  No use of commercial APIs or non-open tools

---

**Contact**
**Email**: [andreamaggetto](mailto:andreamaggetto40@gmail.com)