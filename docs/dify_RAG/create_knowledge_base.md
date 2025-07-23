# Guide: Creating a Knowledge Base in Dify.ai

This document provides a step-by-step guide to creating a new knowledge base from scratch within the Dify.ai platform. A knowledge base is a collection of your custom data that a Large Language Model (LLM) can use to provide accurate, context-specific answers in a RAG (Retrieval-Augmented Generation) application.

---

## Step 1: Navigate to the Knowledge Section

First, log in to your Dify.ai account. On the main dashboard, locate and click on the **"Knowledge"** tab in the top navigation bar. This is the central hub for managing all your knowledge bases.

![Dify.ai dashboard with the 'Knowledge' tab highlighted](https://assets-docs.dify.ai/2024/12/effc826d2584d5f2983cdcd746099bb6.png)
*Figure 1: The main navigation bar in Dify.ai.*

---

## Step 2: Initiate Knowledge Base Creation

In the Knowledge section, you will see a list of your existing knowledge bases. To create a new one, click on the **"Create Knowledge Base"** button, which is typically located in the top-right corner of the page.

---

## Step 3: Upload Your Documents

After clicking the create button, you will be prompted to upload your data. Dify supports various file formats, including `.txt`, `.md`, `.pdf`, `.html`, and more.

1.  Click on **"Upload from Computer"** or drag and drop your files into the designated area.
2.  Select the document(s) you wish to include in this knowledge base. For this guide, we'll proceed with a single file upload.

![The document upload interface in Dify.ai](https://assets-docs.dify.ai/2024/12/effc826d2584d5f2983cdcd746099bb6.png)
*Figure 2: Uploading a local file to the new knowledge base.*

---

## Step 4: Configure Processing Settings

Once your document is uploaded, it needs to be processed and indexed. This involves two key stages: **Chunking** and **Indexing**. For a minimal setup, the default settings are highly effective.

1.  **Chunking:** This process breaks down your large documents into smaller, manageable "chunks." The LLM uses these chunks to find the most relevant information.
    * **Setting:** Leave this on **"Automatic"** mode. Dify will intelligently determine the best way to segment your document based on its content and structure.

2.  **Indexing:** This creates a searchable structure for your chunks, allowing for fast and efficient retrieval.
    * **Setting:** Select the **"High Quality"** mode. This uses a powerful embedding model to capture the semantic meaning of your text, resulting in more relevant search results for the RAG application.

![Chunking and Indexing settings panel](https://assets-docs.dify.ai/2024/12/b3ec2ce860550563234ca22967abdd17.png)
*Figure 3: Default processing settings are usually sufficient for a great start.*

---

## Step 5: Save and Process

After reviewing the settings, click the **"Save & Process"** button at the bottom of the page. Dify will begin the ingestion process, which may take a few moments depending on the size and number of your documents.

You will see a progress bar indicating the status. Once completed, the status will change to "Available," meaning your knowledge base is ready to be integrated into an application.

---

## Conclusion

You have successfully created and processed a new knowledge base in Dify.ai. This knowledge base is now a foundational component, ready to be connected to an LLM within a Dify application or workflow to answer questions based on your specific data.

### Further Reading

For more advanced topics and detailed explanations of the various settings and options available, please refer to the official Dify.ai documentation:

* [Introduction to Knowledge Bases](https://docs.dify.ai/en/guides/knowledge-base/readme)
* [Text Chunking and Cleaning](https://docs.dify.ai/en/guides/knowledge-base/create-knowledge-and-upload-documents/chunking-and-cleaning-text)
* [Setting Indexing Methods](https://docs.dify.ai/en/guides/knowledge-base/create-knowledge-and-upload-documents/setting-indexing-methods)