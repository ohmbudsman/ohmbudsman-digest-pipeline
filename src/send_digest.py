import os
import requests

BUTTONDOWN_API_KEY = os.getenv("BUTTONDOWN_API_KEY")
BUTTONDOWN_API_URL = "https://api.buttondown.email/v1/emails"

def send_digest(subject, body, pdf_url=None):
    """
    Sends the digest email to Buttondown in DRAFT mode.

    Args:
        subject (str): The subject line of the email.
        body (str): The body content of the email in Markdown.
        pdf_url (str, optional): URL to the downloadable PDF version of the digest.
    """
    headers = {
        "Authorization": f"Token {BUTTONDOWN_API_KEY}"
    }

    if pdf_url:
        body += f"\n\n---\n\n[📄 View the PDF version of this digest]({pdf_url})"

    data = {
        "subject": subject,
        "body": body,
        "status": "draft"
    }

    response = requests.post(BUTTONDOWN_API_URL, headers=headers, json=data)

    try:
        response.raise_for_status()
        print(f"✅ Draft created successfully with ID: {response.json().get('id')}")
    except requests.HTTPError as err:
        print(f"❌ Failed to create draft: {err.response.text}")
        raise
