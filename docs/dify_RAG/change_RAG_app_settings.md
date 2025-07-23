# Guide: Managing App Settings, API, and URL in Dify.ai

After creating and publishing your application, Dify.ai provides a central dashboard to manage its settings, access credentials, and sharing options. This guide will walk you through managing the Public URL for the web app.

---

## Step 1: Navigate to Your Application's Dashboard

First, go to the **"Studio"** from the main Dify.ai navigation bar. Here you will see a list of all your applications. Click on the application you wish to manage. This will take you to its main dashboard, as shown in the image below.

![Dify.ai application dashboard overview](https://assets-docs.dify.ai/dify-enterprise-mintlify/en/guides/workflow/node/d90961c6d794d425a8e11df177315188.png)
*Figure 1: The main dashboard for a published application.*

---

## Step 2: Managing the Public Web App URL

The **"Ready-to-Use AI WEB APP"** section provides a shareable link to a standalone web interface for your chatbot.

### Resetting the Chat Interface

The Public URL contains a unique identifier that manages the chat sessions for that link. You may want to reset this to provide a fresh chat experience or invalidate an old link.

1.  Locate the "Public URL" in the web app section.
2.  Click the **Refresh icon (`↻`)** to the right of the URL.
3.  Dify will generate a new, unique URL for your web app.

**Key Consequence:** When you regenerate the URL, the old link will no longer work. **This action effectively archives all chat histories associated with the previous URL.** This is a useful method if an administrator wants to clear all public chat sessions and start fresh without deleting the entire application.

![RAG app settings](https://assets-docs.dify.ai/dify-enterprise-mintlify/en/guides/management/25ce002ef7f0392fc6b3b6975ae137ec.png)
*Figure 2: The main dashboard for a published application.*

---

## Step 3: Other Management Options

The top of the dashboard provides several other useful management functions:

* **Edit Info:** Change the application's name and icon.
* **Duplicate:** Create an exact copy of the application, including its workflow and settings.
* **Export DSL:** Download the application's workflow as a YAML file for backup or version control.
* **More:** Access additional options like **"Archive"** to deactivate the app or **"Delete"** to permanently remove it.

## Conclusion

You now know how to control the public-facing URL for the web app, and how to reset / clear the previous chats in the system.

### Further Reading
For more general information on application management, please refer to the official documentation:

* [Application Management in Dify.ai](https://docs.dify.ai/en/guides/management/app-management)