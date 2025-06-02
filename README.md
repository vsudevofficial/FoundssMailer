# MailStorm Neo - Advanced Email Toolkit

**MailStorm Neo** is an advanced, locally-hosted email toolkit built with Flask and a Neobrutalist UI. It's designed for composing, sending individual emails, managing bulk email campaigns with AI assistance, and includes several productivity tools for email-related tasks.

![MailStorm Neo Screenshot](https://github.com/vsudevofficial/FoundssMailer/raw/main/image.png)


## Key Features

*   **Single Email Sender:** Compose and send individual emails with rich text editing (Quill.js) and attachment support using your Gmail account (via App Password).
*   **MassGo Campaigner:** Send bulk email campaigns using multiple Gmail sender accounts and their corresponding app passwords. Includes recipient list management and attachment support for campaigns.
*   **AI Write Assistant:** Leverage Google's Gemini AI (via your Google AI Studio API key) to help draft, refine, or generate email content directly within the composer.
*   **Email Extractor:** Quickly extract valid email addresses from blocks of text.
*   **Google Dork Generator:** Create advanced Google search queries (dorks) tailored for finding publicly listed email addresses or contact information.
*   **Customizable Themes:** Personalize the dashboard appearance with multiple built-in themes (Light, Dark, Ocean, Forest, etc.).
*   **Neobrutalist UI:** Modern, clean, and responsive user interface.
*   **Local Hosting:** Runs entirely on your local machine, ensuring your primary credentials (for single send) and AI API key are managed locally within your browser's storage.

## Prerequisites

*   Python 3.7+
*   `pip` (Python package installer)
*   A modern web browser (Chrome, Firefox, Edge, Safari)
*   **For sending emails:**
    *   A Gmail account with 2-Step Verification enabled.
    *   A 16-character App Password generated for that Gmail account.
*   **For AI features:**
    *   A Google AI Studio API Key.

## Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/mailstorm-neo.git
    cd mailstorm-neo
    ```
    *(Replace `your-username/mailstorm-neo` with your actual GitHub repository path after you create it)*

2.  **Create and activate a virtual environment (recommended):**
    ```bash
    # For Windows
    python -m venv venv
    .\venv\Scripts\activate

    # For macOS/Linux
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## Running the Application

1.  Ensure your virtual environment is activated (if you created one).
2.  Run the Flask application from the project's root directory:
    ```bash
    python app.py
    ```
3.  The application will start a local server (usually at `http://127.0.0.1:5000/`). It will attempt to open this URL in your default web browser automatically. If not, manually navigate to this address.

## Initial Setup & Usage

### 1. Settings (Crucial First Step!)

Upon first launch, or anytime you need to configure:

*   Navigate to the **⚙️ Settings** tab in the sidebar.
*   **Primary Gmail Account:**
    *   Enter **Your Gmail Email** address.
    *   Enter the **16-character Gmail App Password** (NOT your regular Gmail password).
        *   To get an App Password: Go to your Google Account -> Security -> 2-Step Verification (must be ON) -> App passwords. Select "Mail" for app and "Other (Custom name)" for device, name it (e.g., "MailStormNeo"), and Google will generate the password.
    *   Click **💾 Save Gmail Credentials**. This account is used for sending single emails via the "Compose" and "Send & Monitor" tabs.
*   **Google AI Studio API Key:**
    *   Paste your API key obtained from [Google AI Studio](https://aistudio.google.com/app/apikey).
    *   Click **💾 Save AI Studio Key**. This enables the "✨ AI Write Assistant" feature.
*   **Theme Selection:**
    *   Choose your preferred dashboard theme from the dropdown.
    *   Click **💾 Apply & Save Theme**.

*All credentials and preferences are stored locally in your browser's local storage.*

### 2. Composing & Sending Single Emails

*   **✏️ Compose:** Write your email content in the rich text editor, set your display name, and email subject. Attachments can be added via drag & drop or browsing.
*   **👥 Recipients:** Add recipients manually or by uploading a TXT/CSV file.
*   **🚀 Send & Monitor:** Initiate the sending process. Progress and results will be logged live.

### 3. MassGo Campaigner

*   Navigate to the **⚡ MassGo** tab.
*   **Configuration:**
    *   Set a campaign sender name and subject.
    *   Write the campaign email content in its dedicated rich text editor.
    *   Upload separate `.txt` files: one for Gmail sender email addresses (one per line) and another for their corresponding 16-character App Passwords (one per line, order must match the emails file).
    *   Add attachments for the campaign if needed.
*   **Recipients:** Manage MassGo recipients (manual entry, file upload, or transfer from the main recipients list).
*   **Send Controls:** Initiate the MassGo campaign. The tool will cycle through the provided sender accounts to distribute the email load.

### 4. Productivity Tools

*   **✂️ Email Extractor:** Paste any block of text to quickly extract unique email addresses.
*   **🔍 Dork Generator:** Create targeted Google Dork queries to find publicly listed email addresses or contact information.

### 5. How To Use Guide

*   For more detailed step-by-step instructions on each feature, refer to the **❓ How To Use** tab within the application.

## Troubleshooting

*   **Authentication Failed (SMTP):**
    *   Ensure you're using a valid 16-character App Password from Google, not your regular Gmail password.
    *   Verify 2-Step Verification is enabled for the Gmail account(s).
    *   Check for typos in the email or App Password.
*   **AI Model Errors / API Key Invalid:**
    *   Double-check your Google AI Studio API key for correctness.
    *   Ensure the model `gemini-1.5-flash-latest` is available for your API key and region. You might need to adapt `model_name_to_use` in `app.py` if Google changes model availability for your key.
*   **Gmail Sending Limits:**
    *   Standard Gmail accounts have daily sending limits (e.g., around 500 emails/day for free accounts). MassGo helps distribute sends but does not bypass these fundamental limits. Exceeding limits can lead to temporary account restrictions.
*   **Browser Issues:**
    *   If the UI behaves unexpectedly, try clearing your browser's cache and site data for `127.0.0.1:5000`.
*   **Firewall/Antivirus:**
    *   Ensure your firewall or antivirus software isn't blocking Python or the application from making network connections.

## Disclaimer

*   **Use Responsibly:** This tool is provided for educational and legitimate personal or business use cases. Users are solely responsible for complying with all applicable laws, regulations, and terms of service (including Gmail's) regarding email sending, data privacy, and anti-spam policies.
*   **Local Credential Storage:** Credentials (Gmail App Passwords, Google AI Studio API Key) and theme preferences are stored in your browser's local storage. While this is convenient for local use, be mindful of browser security, especially if using on a shared or public computer. Consider clearing site data after use in such environments.
*   **No Liability:** The developers of MailStorm Neo are not responsible for any misuse of this tool or for any actions taken by the user that violate Gmail's terms of service, any other platform's policies, or any laws or regulations. Use this software at your own risk.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions, issues, and feature requests are welcome! Please feel free to fork the repository, make changes, and submit a pull request. For major changes, please open an issue first to discuss what you would like to change.

## Acknowledgements

*   [Flask](https://flask.palletsprojects.com/)
*   [Quill.js](https://quilljs.com/)
*   [Google Generative AI](https://ai.google.dev/)
*   Neobrutalism design principles for the UI inspiration.
