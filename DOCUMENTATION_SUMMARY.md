Dynamic API Documentation Generator

The Dynamic API Documentation Generator is an AI-powered automation tool designed to streamline the creation of comprehensive API documentation. Built using Streamlit for the frontend and LangChain for orchestration, this application leverages Azure OpenAI's GPT-5 model to transform raw API specifications into professional, structured documentation instantly.

Traditionally, writing API documentation is time-consuming and prone to inconsistencies. This solution addresses that challenge by automating the workflow: users simply input an API endpoint, method, and parameters, and the system generates detailed descriptions, request/response examples, error codes, and usage notes.

Key Features:

    AI-Driven Generation: Uses advanced LLMs to analyze API context and generate technical content with minimal human intervention.

Secure & Lightweight: Operates with a localized, in-memory architecture (Streamlit session state) requiring no external database.

Configuration Management: tailored for security with environment variable support (.env) for Azure credentials.

Export Capabilities: Allows users to download generated documentation history as JSON files.
