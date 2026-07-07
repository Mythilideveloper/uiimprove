from flask import Flask, render_template, request, send_file
import os

from detector import detect_duplicates

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/detect", methods=["POST"])
def detect():

    try:

        # Check whether a file was uploaded
        if "file" not in request.files:
            return render_template(
                "index.html",
                error="Please upload a CSV file."
            )

        file = request.files["file"]

        # Check whether user selected a file
        if file.filename == "":
            return render_template(
                "index.html",
                error="Please select a CSV file."
            )

        # Allow only CSV files
        if not file.filename.lower().endswith(".csv"):
            return render_template(
                "index.html",
                error="Only CSV files are allowed."
            )

        filepath = os.path.join(
            app.config["UPLOAD_FOLDER"],
            file.filename
        )

        file.save(filepath)

        duplicates, stats = detect_duplicates(filepath)

        return render_template(
            "result.html",
            duplicates=duplicates,
            stats=stats
        )

    except Exception as e:

        print(e)

        message = str(e)

        if "Business Name" in message or "BusinessName" in message:
            message = "Business Name column is missing."

        elif "Phone" in message:
            message = "Phone column is missing."

        elif "Address" in message:
            message = "Address column is missing."

        elif "No columns" in message:
            message = "The uploaded CSV is empty."

        elif "EmptyDataError" in message:
            message = "The uploaded CSV is empty."

        elif "ParserError" in message:
            message = "Invalid CSV format."

        return render_template(
            "index.html",
            error=message
        )


@app.route("/download")
def download():

    if os.path.exists("duplicate_report.csv"):

        return send_file(
            "duplicate_report.csv",
            as_attachment=True
        )

    return render_template(
        "index.html",
        error="No report available for download."
    )


if __name__ == "__main__":
    app.run(debug=True)