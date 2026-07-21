import os
import smtplib
from email.message import EmailMessage
from email.utils import parseaddr

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
    """Send the website enquiry to the SOLIDR Gmail inbox."""

    email_user = os.environ.get("EMAIL_USER")
    email_app_password = os.environ.get("EMAIL_APP_PASSWORD")
    recipient_email = os.environ.get(
        "RECIPIENT_EMAIL",
        "solidr89@gmail.com",
    )

    if not email_user or not email_app_password:
        raise RuntimeError(
            "Email environment variables have not been configured."
        )

    message = EmailMessage()

    message["Subject"] = f"New SOLIDR enquiry: {service}"
    message["From"] = email_user
    message["To"] = recipient_email

    # When the client clicks Reply, it will reply to the customer.
    message["Reply-To"] = customer_email

    message.set_content(
        f"""
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
    )

    with smtplib.SMTP_SSL(
        "smtp.gmail.com",
        465,
        timeout=20,
    ) as smtp:
        smtp.login(email_user, email_app_password)
        smtp.send_message(message)


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
