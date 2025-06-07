"""
narrative_generator.py

Open-source functions to generate:
- Descriptions of innovation opportunities
- Startup idea outlines
- Naming suggestions

Uses TF-IDF with filtering, heuristic summary cleaning, and randomized narrative templates.
"""

from typing import List
import re
import random
from sklearn.feature_extraction.text import TfidfVectorizer

# --- TEXT CLEANING & SUMMARIZATION ---

def clean_text(text: str) -> str:
    """
    Cleans the raw patent text by removing codes, legal terms, and formatting noise.

    Args:
        text (str): Raw text extracted from patents.

    Returns:
        str: Cleaned text suitable for keyword extraction and summarization.
    """
    # Remove metadata, patent codes, and INID tags
    text = re.sub(r'\([0-9]{2}\)', '', text)
    text = re.sub(r'\bEP\d+[A-Z]?\d*\b', '', text)
    text = re.sub(r'[A-Z]{2,}\d{4,}', '', text)

    # Remove publication-related boilerplate
    text = re.sub(r'\b(Patent|Application|Filed|Bulletin|Gazette|Number|Date|Publication)\b.*?(\.|\n)', '', text, flags=re.IGNORECASE)

    # Add spaces between joined words (e.g. "increasedUsage" → "increased Usage")
    text = re.sub(r'(?<=[a-z])(?=[A-Z])', ' ', text)

    # Normalize whitespace and punctuation
    text = text.replace('\n', ' ')
    text = re.sub(r'\s+', ' ', text).strip()

    return text


def summarize_text(text: str, max_sentences: int = 3) -> str:
    """
    Produces a summary by selecting meaningful sentences from the cleaned text.

    Args:
        text (str): Cleaned text.
        max_sentences (int): Number of sentences to include in summary.

    Returns:
        str: Concise, readable summary.
    """
    sentences = re.split(r'(?<=[.!?])\s+', text)
    good_sentences = [
        s for s in sentences if len(s) > 40 and not any(c.isdigit() for c in s)
    ]
    return ' '.join(good_sentences[:max_sentences]) if good_sentences else text[:300]


# --- KEYWORD EXTRACTION ---

def extract_keywords(texts: List[str], max_keywords: int = 5) -> List[str]:
    """
    Extracts relevant keywords from patent texts using TF-IDF, filtering out noise.

    Args:
        texts (List[str]): Patent texts.
        max_keywords (int): Maximum number of keywords to return.

    Returns:
        List[str]: Cleaned keyword list.
    """
    stopwords = set([
        "development", "technology", "system", "method", "device",
        "approach", "solution", "innovation", "data", "information",
        "application", "product", "field", "based", "process", "unit"
    ])

    vectorizer = TfidfVectorizer(stop_words="english", max_features=100)
    tfidf_matrix = vectorizer.fit_transform(texts)
    feature_array = vectorizer.get_feature_names_out()
    tfidf_scores = tfidf_matrix.toarray().sum(axis=0)

    keywords = sorted(zip(feature_array, tfidf_scores), key=lambda x: x[1], reverse=True)

    cleaned = [
        kw for kw, _ in keywords
        if kw not in stopwords and len(kw) > 3 and kw.isalpha()
    ]
    return cleaned[:max_keywords]


# --- DESCRIPTION COMPOSER ---

def compose_description(summary: str, keywords: List[str]) -> str:
    """
    Builds a meaningful paragraph by blending keywords and summary with different narrative templates.

    Args:
        summary (str): Short summary of the text.
        keywords (List[str]): Extracted keywords.

    Returns:
        str: Narrative description.
    """
    if not keywords:
        return "This innovation addresses sustainability challenges through a novel approach. Summary: " + summary

    kw1 = keywords[0]
    kw2 = keywords[1] if len(keywords) > 1 else "technology"
    kw3 = keywords[2] if len(keywords) > 2 else "impact"

    templates = [
        f"This solution targets {kw1} and {kw2}, enhancing real-world performance and impact. It improves {kw3} and aligns with SDGs. Summary: {summary}",
        f"A novel advancement in {kw1} and {kw2}, this innovation offers practical benefits for {kw3}. It supports sustainability goals through technology integration. Summary: {summary}",
        f"Focused on {kw1} applications combined with {kw2}, the system introduces improvements in {kw3}. This contributes to the Sustainable Development Goals. Summary: {summary}",
        f"This work combines {kw1} and {kw2} to address emerging challenges in {kw3}. It supports innovation aligned with global SDG priorities. Summary: {summary}"
    ]

    return random.choice(templates)


# --- OPPORTUNITY GENERATION ---

def describe_opportunity(patent_texts: List[str]) -> str:
    """
    Creates a structured opportunity narrative from patent content.

    Args:
        patent_texts (List[str]): List of texts from combined patents.

    Returns:
        str: Named opportunity block with description.
    """
    cleaned = [clean_text(t) for t in patent_texts]
    combined = " ".join(cleaned)
    summary = summarize_text(combined)
    keywords = extract_keywords(cleaned)

    name = " + ".join([kw.title() for kw in keywords[:2]]) if keywords else "Sustainable Opportunity"
    description = compose_description(summary, keywords)

    return f"""---
Name: {name}
Description: {description}
---"""


# --- STARTUP IDEA GENERATION ---

def describe_startup(patent_texts: List[str]) -> str:
    """
    Generates a narrative startup idea based on patents.

    Args:
        patent_texts (List[str]): Texts from selected patents.

    Returns:
        str: Formatted startup pitch.
    """
    cleaned = [clean_text(t) for t in patent_texts]
    combined = " ".join(cleaned)
    summary = summarize_text(combined)
    keywords = extract_keywords(cleaned)

    if len(keywords) < 3:
        keywords += ["sustainability", "impact", "access"]

    description = compose_description(summary, keywords)

    return f"""
## Startup Idea: {keywords[0].title()}Tech

**One-liner**: Leveraging {keywords[0]} and {keywords[1]} for real-world sustainability.

**Business Model**: A digital service helping organizations align technologies with SDGs.

**Pain Point Solved**: Lack of tools to map innovation to sustainability impact.

**Impact on SDGs**: Direct alignment with SDGs like {keywords[2].upper()} and beyond.

**Description**: {description}
"""


# --- NAMING UTILITIES ---

def generate_opportunity_name(seed: str = "") -> str:
    """
    Heuristic name generator for opportunity.

    Args:
        seed (str): Optional seed keyword.

    Returns:
        str: Opportunity name.
    """
    return f"{seed.title()} Opportunity" if seed else "Green Synergy"


def generate_startup_name(seed: str = "") -> str:
    """
    Heuristic name generator for startup.

    Args:
        seed (str): Optional keyword.

    Returns:
        str: Startup name.
    """
    return f"{seed.title()}Tech" if seed else "EcoNova"
