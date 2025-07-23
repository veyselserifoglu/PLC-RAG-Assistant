# Guide: Building a RAG Application Workflow in Dify.ai

This document outlines the process of creating a complete Retrieval-Augmented Generation (RAG) application in Dify.ai. We will use the visual orchestrator to connect user input, a knowledge base, a Large Language Model (LLM), and the final output.

---

## Step 1: Create a New Chat Application

First, you need to create the application that will house your workflow.

1.  Navigate to the **"Studio"** section from the main dashboard.
2.  Click on **"Create New App"**.
3.  Choose the **"Chat App"** type. This template is ideal for building conversational RAG applications.
4.  Give your application a name and a brief description. Click **"Create"**.

![Creating a new Chat App in Dify.ai](https://assets-docs.dify.ai/dify-enterprise-mintlify/en/guides/application-orchestrate/5a29c89223d559eb67801d57895628c1.png)
*Figure 1: Selecting the Chat App template.*

---

## Step 2: Navigate to the Orchestrate View

Once the app is created, you will be taken to its configuration page. To build the visual workflow. 

![Orchestrate tab in the application view](https://assets-docs.dify.ai/dify-enterprise-mintlify/en/guides/workflow/node/d90961c6d794d425a8e11df177315188.png)
*Figure 2: The visual workflow canvas.*

---

## Step 3: Construct the RAG Workflow

The core of your RAG application is a sequence of connected nodes. We will build the exact workflow shown in your example.

### 1. The `Start` Node
This node is present by default. It represents the initial user input. You can configure input variables here, but for a basic chat app, the default `sys.query` (the user's message) is all you need.

### 2. The `Knowledge Retrieval` Node
This node fetches relevant context from your knowledge base.

1.  Click the **"+"** button on the canvas or drag from the `Start` node's output to open the node menu.
2.  Select **"Knowledge Retrieval"**.
3.  In the node's settings, click inside the "Knowledge" field and **select the knowledge base** you created previously (e.g., `knowledge_base.md`).
4.  The node will automatically use the user's query to search the selected knowledge base.

![The prompt you need to write for the LLM to follow](https://assets-docs.dify.ai/2025/03/fbd43d558f83b355a1b18ac26a253b84.png)

### 3. The `LLM` Node
This node processes the user's query and the retrieved knowledge to generate an answer.

1.  Connect the output of the `Knowledge Retrieval` node to a new node.
2.  Select **"LLM"** from the menu.
3.  In the node's settings, choose the **LLM provider and model** you configured earlier in (e.g., `configure_model_provider.md`).
4.  Crucially, ensure the `CONTEXT` variable in the prompt template is connected to the output of the `Knowledge Retrieval` node. Dify typically handles this connection automatically.

![The prompt you need to write for the LLM to follow](https://assets-docs.dify.ai/dify-enterprise-mintlify/en/guides/workflow/node/85730fbfa1d441d12d969b89adf2670e.png)

### 4. The `Answer` Node
This is the final node that delivers the generated response to the user.

### The Final Workflow

After connecting all the nodes, your workflow should look like this:

![A complete RAG workflow in Dify: Start -> Knowledge Retrieval -> LLM -> Answer](https://assets-docs.dify.ai/dify-enterprise-mintlify/en/guides/workflow/node/d90961c6d794d425a8e11df177315188.png)
*Figure 3: The complete visual RAG workflow.*

---

## Step 4: Adding More Features

The visual orchestrator makes it easy to enhance your application. You can add nodes to handle more complex logic.

* **To Add a Feature:** Click the `+` button on the connection line between two nodes where you want to insert a new step.

<h3>Add Feature</h3>
<video controls width="100%">
  <source src="https://slickwid-public.s3.amazonaws.com/walkthrough/6773d34ad27e58127b913945" type="video/mp4">
  Sorry, your browser doesn't support embedded videos. You can <a href="https://slickwid-public.s3.amazonaws.com/walkthrough/6773d34ad27e58127b913945">download it here</a>.
</video>

---

## Step 5: Test Your Application

After designing your workflow, click the **"Publish"** button in the top-right corner. You can then go to the **"Preview"** tab to interact with your RAG chatbot and test its responses to ensure it's using the knowledge base correctly.

![Preview](https://assets-docs.dify.ai/2025/06/8e7933b45a69241a9861a09fa47d5c62.png)

## Conclusion

You have successfully designed and built a functional RAG application workflow in Dify.ai. By visually connecting the `Start`, `Knowledge Retrieval`, `LLM`, and `Answer` nodes, you have created a powerful chatbot that can answer questions based on your custom knowledge base.

### Further Reading

For more advanced orchestration and application types, refer to the official Dify.ai documentation:

* [Application Orchestration Overview](https://docs.dify.ai/en/guides/application-orchestrate/readme)
* [Creating and Configuring Chatbot Applications](https://docs.dify.ai/en/guides/application-orchestrate/chatbot-application)
* [start-node](https://docs.dify.ai/en/guides/workflow/node/start)
* [end-node](https://docs.dify.ai/en/guides/workflow/node/end)
* [answer-node](https://docs.dify.ai/en/guides/workflow/node/answer)
* [llm-node](https://docs.dify.ai/en/guides/workflow/node/llm)
* [knowledge-base-node](https://docs.dify.ai/en/guides/workflow/node/knowledge-retrieval)