# Research Protocol: Cross-Lingual PLC Retrieval Performance Study

## 1. Study Overview

**Title**: Comparative Analysis of German vs. English Query Performance in PLC Technical Documentation Retrieval

**Principal Researcher(s)**: Veysel Serifoglu, supervised by Jusif Schmid

**Timeline**: 80 total hours allocated (30 hours spent on workflow understanding and DifyAI setup, 50 hours remaining)

**Publication Plans**: Entry-level academic paper

**Background**: 
This study examines retrieval performance differences when querying PLC technical documentation in German versus English. By controlling variables such as embedding models and chunking strategies, we aim to quantify the impact of query language on retrieval effectiveness.

**Research Questions**:
- Primary: How does retrieval performance differ between German and English queries on PLC technical documentation?
- Secondary: How do embedding models, chunking strategies, and LLM integration affect cross-lingual retrieval results?

**Hypotheses Framework**:

1. **H1: Language Impact Hypothesis (Root)**
   - German queries will demonstrate measurable performance differences compared to English queries when retrieving PLC documentation

2. **H2: Embedding Model Branch (Primary Focus)**
   - **H2.1: Model Type Performance**
     - Multilingual models will outperform monolingual models for German queries
   - **H2.2: Cross-lingual Performance Gap**
     - The performance gap between languages will be smaller with multilingual models
   - **H2.3: Query Complexity Effect**
     - Performance differences between models will increase with query complexity

3. **Future Work Branches** (to be documented but not tested in current study)
   - H3: Chunking Strategy Branch
   - H4: LLM Integration Branch
   - H5: Domain Specificity Branch

## 2. Knowledge Base Configuration

**Source Content**: 
- Content type: Scraped website content focused on PLC programming topics (coding samples, questions and answers)
- Format: Converted to Markdown file

**Language Distribution**:
- 100% German text

**Storage Format**:
- Stored in ChromaDB vector database

**Preprocessing Steps**:
- HTML text cleaning
- Conversion to Markdown format
- Duplicate removal using difflib.SequenceMatcher with 0.98 similarity threshold

## 3. Experimental Design

### 3.1 Independent Variables
- **Query Language**: German, English
- **Embedding Models**:
  - Monolingual: mxbai-embed-large:latest
  - Multilingual: jina/jina-embedding-v2-base-de:latest
  - **Additional models to be evaluated**: [TO BE DETERMINED]

- **Chunking Strategy**: 
  - Parent-child strategy
  - Parent: full document
  - Child: text divided by "\n\n" delimiter with max character length of 1024
  - **Future consideration**: Semantic chunking approaches

- **LLM Integration**:
  - Model: Gemma3:27b
  - **Potential future models**: [TO BE DETERMINED]

### 3.2 Dependent Variables
- **Evaluation Metrics**: [TO BE DETERMINED]
  - Considering: Precision@k, Recall@k, MRR, MAP, NDCG

### 3.3 Control Variables
- Consistent retrieval parameters (k=5)
- Identical query semantics across languages
- Consistent knowledge base

## 4. Technical Implementation

**Vector Database**: ChromaDB
- **Version**: [TO BE DETERMINED]
- **Similarity Metric**: [TO BE DETERMINED]

**Hardware Specifications**:
- Server with 32 CPUs
- 20GB RAM
- 700GB boot disk
- GPU: [TO BE DETERMINED]

**Retrieval Parameters**:
- k=5 results retrieved per query

## 5. Query Set Construction

**Query Count**:
- 10 distinct queries, each in both English and German (20 total queries)

**Query Selection Criteria**: [TO BE DETERMINED]

**Translation Process**:
- Google Translate with manual verification for semantic equivalence

**Query Topics**: General PLC-related questions [specific topics to be determined]

**Query List**: [TO BE DETERMINED - will include all 10 queries in both languages]

## 6. Evaluation Framework

**Ground Truth Establishment**: [TO BE DETERMINED]

**Human Evaluation**:
- Will employ human evaluators by the end of testing phase
- **Evaluation Protocol**: [TO BE DETERMINED]

**Statistical Analysis**: [TO BE DETERMINED]

**Bias Control Measures**: [TO BE DETERMINED]

## 7. Testing Protocol for Primary Branch

1. **Test Setup**:
   - Apply the 10 queries in both German and English
   - Test both monolingual (mxbai-embed-large) and multilingual (jina-embedding-v2-base-de) models
   - Maintain consistent chunking (parent-child strategy)
   - Retrieve k=5 results for each query

2. **Measurements**:
   - Precision@k and Recall@k for each query
   - Average performance across query sets
   - Performance delta between languages per model

3. **Analysis**:
   - Statistical significance testing of differences
   - Error analysis of specific query performance
   - Qualitative assessment of retrieved chunks

## 8. Documentation and Reporting

**Pre-registration Plan**: [TO BE DETERMINED]

**Results Documentation Format**: [TO BE DETERMINED]

**Version Control**: All code and configuration maintained in version control

**Experiment Logging**: Detailed logs of all experimental conditions and results