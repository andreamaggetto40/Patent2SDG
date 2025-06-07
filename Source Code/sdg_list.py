"""
sdg_list.py

Defines the 17 United Nations Sustainable Development Goals (SDGs) used in the Patent2SDG system.
Each SDG is represented as an instance of SDGNode with a unique ID, name, and descriptive goal.

This list is used throughout the app for:
- Embedding SDG definitions into vector space
- Building the initial SDG graph
- Performing similarity calculations against patent content
"""

from nodes.sdg_node import SDGNode

# List of SDG nodes as defined by the United Nations 2030 Agenda
sdgs = [
    SDGNode("SDG1", "No Poverty", "End poverty in all its forms everywhere."),
    SDGNode("SDG2", "Zero Hunger", "End hunger, achieve food security and improved nutrition and promote sustainable agriculture."),
    SDGNode("SDG3", "Good Health and Well-being", "Ensure healthy lives and promote well-being for all at all ages."),
    SDGNode("SDG4", "Quality Education", "Ensure inclusive and equitable quality education and promote lifelong learning opportunities for all."),
    SDGNode("SDG5", "Gender Equality", "Achieve gender equality and empower all women and girls."),
    SDGNode("SDG6", "Clean Water and Sanitation", "Ensure availability and sustainable management of water and sanitation for all."),
    SDGNode("SDG7", "Affordable and Clean Energy", "Ensure access to affordable, reliable, sustainable and modern energy for all."),
    SDGNode("SDG8", "Decent Work and Economic Growth", "Promote sustained, inclusive and sustainable economic growth, full and productive employment and decent work for all."),
    SDGNode("SDG9", "Industry, Innovation and Infrastructure", "Build resilient infrastructure, promote inclusive and sustainable industrialization and foster innovation."),
    SDGNode("SDG10", "Reduced Inequalities", "Reduce inequality within and among countries."),
    SDGNode("SDG11", "Sustainable Cities and Communities", "Make cities and human settlements inclusive, safe, resilient and sustainable."),
    SDGNode("SDG12", "Responsible Consumption and Production", "Ensure sustainable consumption and production patterns."),
    SDGNode("SDG13", "Climate Action", "Take urgent action to combat climate change and its impacts."),
    SDGNode("SDG14", "Life Below Water", "Conserve and sustainably use the oceans, seas and marine resources for sustainable development."),
    SDGNode("SDG15", "Life on Land", "Protect, restore and promote sustainable use of terrestrial ecosystems, sustainably manage forests, combat desertification, and halt and reverse land degradation and halt biodiversity loss."),
    SDGNode("SDG16", "Peace, Justice and Strong Institutions", "Promote peaceful and inclusive societies for sustainable development, provide access to justice for all and build effective, accountable and inclusive institutions at all levels."),
    SDGNode("SDG17", "Partnerships for the Goals", "Strengthen the means of implementation and revitalize the global partnership for sustainable development.")
]
