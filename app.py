import os
import smtplib
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email import encoders
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import time
import base64
import logging
import sys
import webbrowser
import threading
import json
import google.generativeai as genai

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

IS_BUNDLED = getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS')

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

# --- Helper Functions (send_single_email) ---
def send_single_email(sender_email, sender_password, sender_name, recipient, subject, body_html, attachments_data):
    msg = MIMEMultipart()
    msg['From'] = f"{sender_name} <{sender_email}>"
    msg['To'] = recipient
    msg['Subject'] = subject
    msg.attach(MIMEText(body_html, 'html'))
    for filename, content_base64, content_type in attachments_data:
        try:
            decoded_content = base64.b64decode(content_base64)
            main_type, sub_type = content_type.split('/', 1)
            part = MIMEBase(main_type, sub_type)
            part.set_payload(decoded_content)
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f'attachment; filename="{filename}"')
            msg.attach(part)
        except Exception as e:
            logging.error(f"Error processing attachment {filename}: {e}")
            continue
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, recipient, msg.as_string())
        server.quit()
        logging.info(f"Email sent successfully to {recipient} from {sender_email}")
        return True, "Success"
    except smtplib.SMTPAuthenticationError as e:
        logging.error(f"Authentication failed for {sender_email}: {e}")
        return False, f"Authentication failed for {sender_email}: {e}. Check email/password or app password in Settings."
    except smtplib.SMTPServerDisconnected as e:
        logging.error(f"SMTP Server disconnected for {sender_email}: {e}")
        return False, f"SMTP Server disconnected for {sender_email}: {e}. Try again later."
    except Exception as e:
        logging.error(f"An unexpected error occurred sending email to {recipient} from {sender_email}: {e}")
        return False, str(e)

# --- Backend API Endpoint (/send_emails) ---
@app.route('/send_emails', methods=['POST'])
def send_emails_api():
    logging.info("Received request for /send_emails")
    sender_name = request.form.get('sender_name')
    sender_email_account = request.form.get('sender_email_account') 
    sender_app_password = request.form.get('sender_app_password')
    email_subject = request.form.get('email_subject')
    recipients_str = request.form.get('recipients')
    email_body_html = request.form.get('email_body_html')

    if not all([sender_name, sender_email_account, sender_app_password, email_subject, recipients_str, email_body_html]):
        logging.warning("Missing required form data for /send_emails. Required: sender_name, sender_email_account, sender_app_password, email_subject, recipients, email_body_html")
        return jsonify({"message": "Missing required form data. Ensure sender account, app password (from Settings), name, subject, recipients, and body are provided.", "results": []}), 400

    recipients = [r.strip() for r in recipients_str.split(',') if r.strip()]
    if not recipients:
        logging.warning("No recipients provided for /send_emails")
        return jsonify({"message": "No recipients provided.", "results": []}), 400

    attachments_data = []
    if 'attachments' in request.files:
        files = request.files.getlist('attachments')
        for file_obj in files:
            if file_obj.filename:
                try:
                    file_content = file_obj.read()
                    encoded_content = base64.b64encode(file_content).decode('utf-8')
                    attachments_data.append((file_obj.filename, encoded_content, file_obj.content_type))
                    logging.info(f"Attachment {file_obj.filename} processed for /send_emails.")
                except Exception as e:
                    logging.error(f"Error reading attachment {file_obj.filename} for /send_emails: {e}")

    successful = 0
    failed = 0
    results_log = []
    for i, recipient in enumerate(recipients):
        logging.info(f"Attempting to send email to {recipient} ({i+1}/{len(recipients)}) for /send_emails")
        try:
            success, message = send_single_email(
                sender_email_account, sender_app_password, sender_name, recipient, email_subject, email_body_html, attachments_data
            )
            if success:
                successful += 1
                results_log.append(f"✅ {recipient} - Success")
            else:
                failed += 1
                results_log.append(f"❌ {recipient} - Failed: {message}")
        except Exception as e:
            failed += 1
            results_log.append(f"❌ {recipient} - Unexpected error: {str(e)}")
            logging.error(f"Unexpected error sending to {recipient} for /send_emails: {e}")
        time.sleep(0.5)

    logging.info(f"Email sending process completed for /send_emails. Successful: {successful}, Failed: {failed}")
    return jsonify({
        "message": "Email sending process completed.",
        "total": len(recipients),
        "successful": successful,
        "failed": failed,
        "results": results_log
    }), 200

# --- Backend API Endpoint (/send_massgo_emails) ---
@app.route('/send_massgo_emails', methods=['POST'])
def send_massgo_emails_api():
    logging.info("Received request for /send_massgo_emails")
    campaign_sender_name = request.form.get('campaign_sender_name')
    app_passwords_list_str = request.form.get('app_passwords_list')
    sender_emails_list_str = request.form.get('sender_emails_list')
    email_subject = request.form.get('email_subject')
    mass_go_recipients_str = request.form.get('recipients')
    email_body_html = request.form.get('email_body_html')

    if not all([campaign_sender_name, app_passwords_list_str, sender_emails_list_str, email_subject, mass_go_recipients_str, email_body_html]):
        logging.warning("Missing required form data for /send_massgo_emails")
        return jsonify({"message": "Missing required form data for MassGo.", "results": []}), 400

    try:
        app_passwords = json.loads(app_passwords_list_str)
        sender_emails = json.loads(sender_emails_list_str)
        mass_go_recipients = json.loads(mass_go_recipients_str)
    except json.JSONDecodeError as e:
        logging.error(f"Error decoding JSON data for MassGo: {e}")
        return jsonify({"message": f"Invalid JSON data provided: {e}", "results": []}), 400

    if not app_passwords or not sender_emails:
        return jsonify({"message": "App passwords list or sender emails list is empty.", "results": []}), 400
    if len(app_passwords) != len(sender_emails):
        return jsonify({"message": "Mismatch between number of app passwords and sender emails.", "results": []}), 400
    if not mass_go_recipients:
        return jsonify({"message": "No recipients provided for MassGo.", "results": []}), 400

    attachments_data = []
    if 'attachments' in request.files:
        files = request.files.getlist('attachments')
        for file_obj in files:
            if file_obj.filename:
                try:
                    file_content = file_obj.read()
                    encoded_content = base64.b64encode(file_content).decode('utf-8')
                    attachments_data.append((file_obj.filename, encoded_content, file_obj.content_type))
                    logging.info(f"[MassGo] Attachment {file_obj.filename} processed.")
                except Exception as e:
                    logging.error(f"[MassGo] Error reading attachment {file_obj.filename}: {e}")
    
    overall_successful = 0
    overall_failed = 0
    results_log = []
    current_recipient_idx = 0
    total_recipients_count = len(mass_go_recipients)
    emails_per_account_limit = 480 

    logging.info(f"[MassGo] Starting campaign. Senders: {len(sender_emails)}, Recipients: {total_recipients_count}")

    for sender_idx, (current_sender_email, current_sender_password) in enumerate(zip(sender_emails, app_passwords)):
        if current_recipient_idx >= total_recipients_count:
            logging.info("[MassGo] All recipients processed.")
            break

        logging.info(f"[MassGo] Using sender account: {current_sender_email} ({sender_idx+1}/{len(sender_emails)})")
        sends_from_this_account = 0
        
        try: 
            test_server = smtplib.SMTP('smtp.gmail.com', 587)
            test_server.ehlo()
            test_server.starttls()
            test_server.ehlo()
            test_server.login(current_sender_email, current_sender_password)
            test_server.quit()
            logging.info(f"[MassGo] Authentication successful for {current_sender_email}.")
        except smtplib.SMTPAuthenticationError:
            logging.error(f"[MassGo] Authentication FAILED for sender {current_sender_email}. Skipping this sender.")
            results_log.append(f"⚠️ Sender Account {current_sender_email}: Authentication FAILED. This account will be skipped.")
            continue
        except Exception as e: 
            logging.error(f"[MassGo] Error testing SMTP for {current_sender_email}: {e}. Skipping this sender.")
            results_log.append(f"⚠️ Sender Account {current_sender_email}: SMTP Test Error ({e}). This account will be skipped.")
            continue

        while sends_from_this_account < emails_per_account_limit and current_recipient_idx < total_recipients_count:
            recipient = mass_go_recipients[current_recipient_idx]
            logging.info(f"[MassGo] Attempting email to {recipient} from {current_sender_email} (Account send {sends_from_this_account+1}/{emails_per_account_limit}, Overall {current_recipient_idx+1}/{total_recipients_count})")
            
            success, message = send_single_email(
                current_sender_email, current_sender_password, campaign_sender_name, 
                recipient, email_subject, email_body_html, attachments_data
            )

            if success:
                overall_successful += 1
                sends_from_this_account += 1
                results_log.append(f"✅ {recipient} (from {current_sender_email}) - Success")
            else:
                overall_failed += 1
                results_log.append(f"❌ {recipient} (from {current_sender_email}) - Failed: {message}")
                if "Authentication failed" in message or "Account restricted" in message or "Too many messages" in message or "limit" in message.lower():
                    logging.warning(f"[MassGo] Sending issue (likely auth/limit) for {current_sender_email} mid-batch. Moving to next sender.")
                    results_log.append(f"⚠️ Sender Account {current_sender_email}: Sending issue ({message}). Further sends from this account stopped.")
                    break 

            current_recipient_idx += 1
            time.sleep(0.75) 

    logging.info(f"[MassGo] Campaign completed. Successful: {overall_successful}, Failed: {overall_failed}, Total Recipients Attempted: {current_recipient_idx}")
    
    final_message = "MassGo campaign process completed."
    if current_recipient_idx < total_recipients_count: 
        unprocessed_recipients = total_recipients_count - current_recipient_idx
        final_message += f" {unprocessed_recipients} recipients were not attempted, possibly due to exhaustion of sender accounts or errors."
        logging.warning(f"[MassGo] {unprocessed_recipients} recipients were not attempted.")

    return jsonify({
        "message": final_message,
        "total_recipients_in_list": total_recipients_count,
        "recipients_processed": current_recipient_idx,
        "successful": overall_successful,
        "failed": overall_failed,
        "results": results_log
    }), 200

# --- API Endpoint for AI Text Generation (Google AI Studio / Gemini) ---
@app.route('/api/ai_generate', methods=['POST'])
def ai_generate_api():
    data = request.json
    api_key = data.get('api_key') # This is the Google AI Studio API Key
    prompt_text = data.get('prompt')

    if not api_key or not prompt_text:
        return jsonify({"error": "Google AI Studio API key and prompt are required."}), 400

    try:
        genai.configure(api_key=api_key)
        # Using gemini-1.5-flash-latest as it's cost-effective and good for general tasks.
        # User might need to change if this specific model isn't available for their key/region.
        model_name_to_use = 'gemini-1.5-flash-latest' 
        logging.info(f"Using Gemini model: {model_name_to_use}")
        model = genai.GenerativeModel(model_name=model_name_to_use) 
        
        safety_settings = [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        ]
        
        response = model.generate_content(prompt_text, safety_settings=safety_settings)
        
        generated_text = ""
        if hasattr(response, 'text') and response.text:
            generated_text = response.text
        elif response.parts: 
            generated_text = "".join(part.text for part in response.parts if hasattr(part, 'text'))
        
        if not generated_text and response.prompt_feedback and response.prompt_feedback.block_reason:
            block_reason_message = response.prompt_feedback.block_reason_message if hasattr(response.prompt_feedback, 'block_reason_message') else str(response.prompt_feedback.block_reason)
            logging.warning(f"Gemini content generation blocked. Reason: {block_reason_message}")
            return jsonify({"error": f"Content generation blocked by AI. Reason: {block_reason_message}"}), 400
        
        if not generated_text and not (response.prompt_feedback and response.prompt_feedback.block_reason):
             logging.warning(f"Gemini generated empty text without explicit block. Prompt: {prompt_text[:100]}")
             # It's possible the model genuinely produced no output for a valid prompt.
             # To the user, this might still seem like an error or an unhelpful response.

        return jsonify({"generated_text": generated_text}), 200
    except Exception as e:
        logging.error(f"Error with Google AI Studio API (Gemini): {e}")
        err_str = str(e).lower()
        if "api key not valid" in err_str or "permission_denied" in err_str or "api_key_invalid" in err_str:
             return jsonify({"error": "Google AI Studio API key is not valid or has insufficient permissions. Please check your key in Settings."}), 401
        if "model" in err_str and ("not found" in err_str or "is not supported" in err_str):
            return jsonify({"error": f"The AI model ('{model_name_to_use}') was not found or is not supported with your API key. Check Google AI Studio for available models. Error: {str(e)}"}), 404
        if "quota" in err_str:
            return jsonify({"error": "API quota exceeded. Please check your Google AI Studio project quotas."}), 429
        return jsonify({"error": f"Error generating text with AI: {str(e)}"}), 500


# --- Serve Frontend (index.html) ---
@app.route('/')
def serve_index():
    logging.info("Serving index.html")
    return send_from_directory('.', 'index.html')

# --- Function to open the browser ---
def open_browser():
    time.sleep(1.5) 
    webbrowser.open_new("http://127.0.0.1:5000/")
    logging.info("Browser open request sent to http://127.0.0.1:5000/")

if __name__ == '__main__':
    use_reloader = not IS_BUNDLED
    debug_mode = not IS_BUNDLED
    logging.info(f"Starting Flask server. IS_BUNDLED: {IS_BUNDLED}, use_reloader: {use_reloader}, debug_mode: {debug_mode}")
    
    if not use_reloader or os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        if not (IS_BUNDLED is False and os.environ.get("WERKZEUG_RUN_MAIN") != "true"):
             threading.Thread(target=open_browser, daemon=True).start()
            
    app.run(host='127.0.0.1', port=5000, debug=debug_mode, use_reloader=use_reloader)
