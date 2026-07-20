import logging
import os
from flask import Flask, render_template, request, flash, redirect

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__, static_folder="Static", static_url_path="/static")
app.secret_key = os.environ.get("SECRET_KEY", "solidr_secret")

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/contact", methods=["POST"])
def contact():
    name = request.form.get("name")
    email = request.form.get("email")
    phone = request.form.get("phone")
    service = request.form.get("service")
    message = request.form.get("message")

    logger.info(
        "New enquiry: name=%s email=%s phone=%s service=%s message=%s",
        name, email, phone, service, message,
    )

    flash("Thank you! Your enquiry has been sent successfully.")

    return redirect("/")


if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))