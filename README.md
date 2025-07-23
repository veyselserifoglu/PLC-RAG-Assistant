# PLC-RAG-Assistant

A Retrieval-Augmented Generation (RAG) system for Programmable Logic Controller (PLC) programming assistance, specifically designed to work with German technical documentation and support multilingual queries.

## Project Overview

This project investigates the effectiveness of RAG retrieval techniques when the knowledge base consists of German-language technical documentation. The system is designed to handle two primary scenarios:

- **Cross-lingual retrieval**: Retrieving relevant German text based on English queries
- **Monolingual retrieval**: Retrieving relevant German text based on German queries

## Research Focus

The project serves as a research platform to study:

- Performance comparison between monolingual and multilingual embedding models
- Effectiveness of different chunking strategies (parent-child vs. delimiter-based)
- Quality of semantic similarity retrieval across language boundaries
- Reproducible experimental methodology for academic research

## Key Features

- **Web Content Extraction**: Automated scraping and processing of German PLC documentation
- **Document Processing**: Advanced text cleaning and normalization for technical content
- **Multilingual Support**: Testing with both monolingual and multilingual embedding models
- **Chunking Strategies**: Implementation of multiple text segmentation approaches
- **Experimental Framework**: Structured logging and metrics collection for research reproducibility

## Technical Stack

- **Platform**: DifyAI (open-source workflow platform)
- **Language**: Python 3.x
- **Key Libraries**: 
  - BeautifulSoup4 (web scraping)
  - tqdm (progress tracking)
  - hashlib (content deduplication)
  - difflib (similarity detection)

## Data Processing Pipeline

1. **HTML Extraction**: Parse and extract content from downloaded web pages
2. **Content Cleaning**: Remove boilerplate text, navigation elements, and metadata
3. **Deduplication**: Eliminate exact and near-duplicate documents
4. **Text Consolidation**: Merge titles, headings, breadcrumbs, and body content
5. **Metadata Extraction**: Parse publication information and technical details
6. **Output Generation**: Create clean markdown content and structured metadata

## File Structure

```
├── cleaned_website.py          # Main processing script
├── www.seitz.et.hs-mannheim.de/  # Downloaded HTML content
└── README.md                  # This file
```

## Usage

### Processing Web Content

```bash
python cleaned_website.py
```

This script will:
- Extract content from HTML files in the `www.seitz.et.hs-mannheim.de/` directory
- Remove duplicate and similar documents
- Filter out non-content pages (login, sitemap, etc.)
- Generate `cleaned_content.md` with consolidated text
- Create `metadata.json` with document metadata

## Research Methodology

### Experimental Design

The project follows a systematic approach to ensure reproducible results:

1. **Data Preparation**: Standardized cleaning and processing pipeline
2. **Model Comparison**: Testing with both monolingual and multilingual embedding models
3. **Query Generation**: Curated test questions in both German and English
4. **Evaluation Metrics**: Standardized information retrieval metrics
5. **Documentation**: Complete experimental configuration logging

### Chunking Strategies

- **Parent-Child Chunking**: Full documents as parents, paragraph-level children
- **Delimiter-Based Chunking**: Simple text splitting using predefined separators

### Embedding Models

- **Monolingual**: German-specific embedding models
- **Multilingual**: Cross-language embedding models supporting German-English

## Academic Applications

This project is designed to support academic research in:

- **Information Retrieval**: Cross-lingual search effectiveness
- **Natural Language Processing**: Multilingual semantic similarity
- **Technical Documentation**: Domain-specific RAG applications
- **Reproducible Research**: Standardized experimental frameworks

## License

This project is intended for academic research purposes. Please respect the original content sources and their licensing terms.

## Citation

When using this project in academic work, please ensure proper attribution and consider the experimental framework for reproducibility in your own research.