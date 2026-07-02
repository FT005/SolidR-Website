from flask import Flask, render_template, request, flash, redirect

app = Flask(__name__)
app.secret_key = "solidr_secret"

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

    print("New Enquiry")
    print(name)
    print(email)
    print(phone)
    print(service)
    print(message)

    flash("Thank you! Your enquiry has been sent successfully.")

    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)