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
import webbrowser # <-- Import webbrowser module
import threading  # <-- For opening the browser in a separate thread

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# For this browser-based approach, IS_BUNDLED is less critical for Flask's static serving,
# but can still be useful if you decide to bundle app.py with PyInstaller later.
IS_BUNDLED = getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS')

# Flask app setup
# The static_folder='.' assumes index.html and other assets that IT might reference
# (if any, beyond CDN links) are in the same directory as app.py.
# If index.html is the only local file served, this is fine.
app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

# --- Helper Functions (send_single_email - remains the same) ---
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
        logging.info(f"Email sent successfully to {recipient}")
        return True, "Success"
    except smtplib.SMTPAuthenticationError as e:
        logging.error(f"Authentication failed for {sender_email}: {e}")
        return False, f"Authentication failed: {e}. Check email/password or app password."
    except smtplib.SMTPServerDisconnected as e:
        logging.error(f"SMTP Server disconnected: {e}")
        return False, f"SMTP Server disconnected: {e}. Try again later."
    except Exception as e:
        logging.error(f"An unexpected error occurred sending email to {recipient}: {e}")
        return False, str(e)

# --- Backend API Endpoint (/send_emails - remains the same) ---
@app.route('/send_emails', methods=['POST'])
def send_emails_api():
    logging.info("Received request for /send_emails")
    sender_name = request.form.get('sender_name')
    sender_email = request.form.get('sender_email')
    sender_password = request.form.get('sender_password')
    email_subject = request.form.get('email_subject')
    recipients_str = request.form.get('recipients')
    email_body_html = request.form.get('email_body_html')

    if not all([sender_name, sender_email, sender_password, email_subject, recipients_str, email_body_html]):
        logging.warning("Missing required form data for /send_emails")
        return jsonify({"message": "Missing required form data.", "results": []}), 400

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
                    logging.info(f"Attachment {file_obj.filename} processed.")
                except Exception as e:
                    logging.error(f"Error reading attachment {file_obj.filename}: {e}")

    successful = 0
    failed = 0
    results_log = []
    for i, recipient in enumerate(recipients):
        logging.info(f"Attempting to send email to {recipient} ({i+1}/{len(recipients)})")
        try:
            success, message = send_single_email(
                sender_email, sender_password, sender_name, recipient, email_subject, email_body_html, attachments_data
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
            logging.error(f"Unexpected error sending to {recipient}: {e}")
        time.sleep(0.5)

    logging.info(f"Email sending process completed. Successful: {successful}, Failed: {failed}")
    return jsonify({
        "message": "Email sending process completed.",
        "total": len(recipients),
        "successful": successful,
        "failed": failed,
        "results": results_log
    }), 200

# --- Serve Frontend (index.html - remains the same) ---
@app.route('/')
def serve_index():
    logging.info("Serving index.html")
    # Ensure index.html is in the same directory as app.py,
    # or adjust the first argument of send_from_directory if it's elsewhere.
    return send_from_directory('.', 'index.html')

# --- Function to open the browser ---
def open_browser():
    """Opens the web browser to the Flask app's URL after a short delay."""
    # Delay slightly to give Flask a moment to fully start
    time.sleep(1)
    webbrowser.open_new("http://127.0.0.1:5000/")
    logging.info("Browser open request sent to http://127.0.0.1:5000/")

if __name__ == '__main__':
    # For development, Flask's reloader is useful.
    # For a PyInstaller bundled app, reloader should generally be off to avoid issues.
    use_reloader = not IS_BUNDLED
    debug_mode = not IS_BUNDLED

    logging.info(f"Starting Flask server. IS_BUNDLED: {IS_BUNDLED}, use_reloader: {use_reloader}, debug_mode: {debug_mode}")

    # Open the browser only when not using the reloader's secondary process
    # The reloader spawns a child process; we only want the main one to open the browser.
    if not use_reloader or os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        # Start open_browser in a new thread so it doesn't block Flask from starting
        threading.Thread(target=open_browser, daemon=True).start()

    app.run(host='127.0.0.1', port=5000, debug=debug_mode, use_reloader=use_reloader)