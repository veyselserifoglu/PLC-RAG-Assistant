# Guide: Configuring Models in Dify.ai

To power your RAG application, you need to connect a Large Language Model (LLM) to your Dify.ai workspace. This guide explains how to configure model providers at the system level, making them available for use in any of your applications.

This process is typically handled by a workspace administrator.

---

## Step 1: Navigate to Model Provider Settings

First, log in to your Dify.ai account. On the main dashboard, click on **"Settings"** in the top-left corner of the navigation sidebar. From the settings menu, select **"Model Providers"**.

![Dify.ai settings menu with 'Model Providers' highlighted](https://assets-docs.dify.ai/dify-enterprise-mintlify/en/guides/model-configuration/941524058c800a06d39290c48d14673b.png)
*Figure 1: Accessing the Model Providers section.*

---

## Step 2: Select a Model Provider

You will see a list of supported LLM providers, such as OpenAI, Anthropic, Ollama, and others. Click on the provider you wish to configure. For this example, we will select **OpenAI**.

![List of available model providers in Dify.ai](https://assets-docs.dify.ai/dify-enterprise-mintlify/en/guides/model-configuration/c5ac5f32deb020a8aae46045d3ee9c8d.png)
*Figure 2: Choosing a provider from the list.*

---

## Step 3: Add Your API Credentials

After selecting a provider, you need to add your API key to authenticate your requests.

1.  A dialog box will appear asking for your credentials.
2.  Paste your **API Key** into the designated field. For some providers, you might need additional information.
3.  Click **"Save"** to store the credentials securely.

**Note:** Your API key is a sensitive credential. Ensure you are using a key with the appropriate permissions and store it securely.

---

## Step 4: Enable and Configure Specific Models

Once your API key is validated, Dify will display a list of all models available from that provider (e.g., `gpt-4`, `gpt-4o`, `gpt-3.5-turbo` for OpenAI).

1.  **Enable Models:** Use the toggles to enable the specific models you want to make available for use within your applications.
2.  **Set Permissions:** You can configure which tools (like "Chat" or "Completion") each model can be used for. For most RAG applications, enabling them for "Chat" is the primary goal.

Click **"Save"** after making your selections.

![Model list with toggles to enable specific models](https://assets-docs.dify.ai/dify-enterprise-mintlify/en/guides/model-configuration/6e74424124cfcfe224d3c083f90b54d2.png)
*Figure 3: Activating and configuring the desired models.*

---

## Conclusion

You have successfully added and configured an LLM provider in Dify.ai. The selected models are now ready to be used to power RAG chat functionalities across your applications.

### Further Reading

For a comprehensive overview of all supported models and advanced configuration options, please refer to the official Dify.ai documentation:

* [Model Configuration & Integration](https://docs.dify.ai/en/guides/model-configuration/readme)