import os
from email.utils import parseaddr

import requests
from flask import Flask, flash, redirect, render_template, request


app = Flask(
    __name__,
    static_folder="Static",
    static_url_path="/static",
)

app.secret_key = os.environ.get(
    "SECRET_KEY",
    "change-this-secret-key",
)


def is_valid_email(email: str) -> bool:
    """Perform simple validation of the customer's email address."""
    parsed_email = parseaddr(email)[1]

    return (
        bool(parsed_email)
        and "@" in parsed_email
        and "." in parsed_email.split("@")[-1]
    )


def send_enquiry_email(
    name: str,
    customer_email: str,
    phone: str,
    service: str,
    customer_message: str,
) -> None:
    """Send the website enquiry to the SOLIDR inbox via the Mailgun API.

    Render blocks outbound SMTP (ports 25/465/587) on all plans, so this
    goes over HTTPS instead of smtplib.
    """

    mailgun_api_key = os.environ.get("MAILGUN_API_KEY")
    mailgun_domain = os.environ.get("MAILGUN_DOMAIN")
    # Use https://api.eu.mailgun.net if the Mailgun domain is on the EU region.
    mailgun_api_base_url = os.environ.get(
        "MAILGUN_API_BASE_URL",
        "https://api.mailgun.net",
    )
    sender_email = os.environ.get(
        "MAILGUN_FROM_EMAIL",
        f"SOLIDR Website <mailgun@{mailgun_domain}>",
    )
    recipient_email = os.environ.get(
        "RECIPIENT_EMAIL",
        "Admin@SolidR.co.uk",
    )

    if not mailgun_api_key or not mailgun_domain:
        raise RuntimeError(
            "Mailgun environment variables have not been configured."
        )

    text_body = f"""
New customer enquiry received through the SOLIDR website.

CUSTOMER DETAILS
----------------
Name: {name}
Email: {customer_email}
Phone: {phone or "Not provided"}
Service: {service}

MESSAGE
-------
{customer_message}

You can reply directly to this email to contact the customer.
""".strip()

    response = requests.post(
        f"{mailgun_api_base_url}/v3/{mailgun_domain}/messages",
        auth=("api", mailgun_api_key),
        data={
            "from": sender_email,
            "to": [recipient_email],
            # When the client clicks Reply, it will reply to the customer.
            "h:Reply-To": customer_email,
            "subject": f"New SOLIDR enquiry: {service}",
            "text": text_body,
        },
        timeout=20,
    )

    if not response.ok:
        raise RuntimeError(
            f"Mailgun API error {response.status_code}: {response.text}"
        )

    app.logger.info(
        "Mailgun accepted enquiry email for %s: %s",
        recipient_email,
        response.text,
    )


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/contact", methods=["POST"])
def contact():
    name = request.form.get("name", "").strip()
    customer_email = request.form.get("email", "").strip()
    phone = request.form.get("phone", "").strip()
    service = request.form.get("service", "").strip()
    customer_message = request.form.get("message", "").strip()

    # Basic validation
    if not name:
        flash("Please enter your name.", "error")
        return redirect("/#contact")

    if not is_valid_email(customer_email):
        flash("Please enter a valid email address.", "error")
        return redirect("/#contact")

    if not service:
        flash("Please select a service.", "error")
        return redirect("/#contact")

    if not customer_message:
        flash("Please enter a message.", "error")
        return redirect("/#contact")

    try:
        send_enquiry_email(
            name=name,
            customer_email=customer_email,
            phone=phone,
            service=service,
            customer_message=customer_message,
        )

        flash(
            "Thank you! Your enquiry has been sent successfully.",
            "success",
        )

    except Exception as error:
        # This appears in Render logs but does not expose credentials.
        app.logger.exception(
            "Failed to send contact-form email: %s",
            error,
        )

        flash(
            "Sorry, your message could not be sent. "
            "Please call us on 020 8087 1955.",
            "error",
        )

    return redirect("/#contact")


if __name__ == "__main__":
    app.run(
        debug=False,
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 10000)),
    )
