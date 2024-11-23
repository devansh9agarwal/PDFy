import os
import subprocess
import threading
from flask import Flask, request, render_template, send_file, redirect, url_for, flash
from werkzeug.utils import secure_filename
from datetime import datetime
import time

app = Flask(__name__)
app.secret_key = "hello_world"  # Required for flash messages

UPLOAD_FOLDER = "uploads"
CONVERTED_FOLDER = "converted"
ALLOWED_EXTENSIONS = {"docx", "txt", "doc", "pdf", "jpg", "png"}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(CONVERTED_FOLDER, exist_ok=True)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["CONVERTED_FOLDER"] = CONVERTED_FOLDER

# Function to check allowed file types
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

# Function to extract metadata
def extract_metadata(filepath):
    metadata = {}
    metadata["File Name"] = os.path.basename(filepath)
    metadata["File Size"] = f"{os.path.getsize(filepath) / 1024:.2f} KB"
    metadata["Upload Date"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return metadata

# Function to convert DOCX to PDF
def convert_to_pdf(input_path, output_path):
    try:
        subprocess.run(
            [
                "libreoffice",
                "--headless",
                "--convert-to",
                "pdf",
                "--outdir",
                os.path.dirname(output_path),
                input_path,
            ],
            check=True,
        )
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Conversion failed: {e}")

# Function to delete the file after a delay (in seconds)
def delete_file_after_delay(filename, delay_seconds):
    """
    Deletes the file after the specified delay (in seconds).
    """
    time.sleep(delay_seconds)  # Wait for the specified delay
    file_path = os.path.join(CONVERTED_FOLDER, filename)
    
    if os.path.exists(file_path):
        os.remove(file_path)
        print(f"File {filename} has been deleted.")
    else:
        print(f"File {filename} not found.")

# Route for uploading and converting files
@app.route("/", methods=["GET", "POST"])
def upload_file():
    if request.method == "POST":
        # Handle file upload
        if "file" not in request.files:
            flash("No file part", "error")
            return redirect(request.url)
        file = request.files["file"]
        if file.filename == "":
            flash("No selected file", "error")
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            input_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            file.save(input_path)

            # Extract metadata
            metadata = extract_metadata(input_path)

            # Attempt conversion
            output_path = os.path.join(
                app.config["CONVERTED_FOLDER"], f"{os.path.splitext(filename)[0]}.pdf"
            )
            try:
                convert_to_pdf(input_path, output_path)
            except RuntimeError as e:
                flash(str(e), "error")
                return redirect(request.url)

            # Trigger background deletion of the converted file after 10 minutes (600 seconds)
            delete_thread = threading.Thread(target=delete_file_after_delay, args=(os.path.basename(output_path), 300))  # 600 seconds = 10 minutes
            delete_thread.start()

            # Redirect to results page
            return redirect(
                url_for("conversion_result", pdf_filename=os.path.basename(output_path), **metadata)
            )
        else:
            flash("Invalid file type. Only .docx, .doc, .txt, .pdf file types allowed.", "error")
            return redirect(request.url)
    return render_template("upload.html")

# Route to show the result after conversion
@app.route("/result")
def conversion_result():
    # Retrieve metadata and file info from query params
    pdf_filename = request.args.get("pdf_filename")
    metadata = {key: value for key, value in request.args.items() if key != "pdf_filename"}
    pdf_path = os.path.join(app.config["CONVERTED_FOLDER"], pdf_filename)
    return render_template("result.html", metadata=metadata, pdf_filename=pdf_filename)

# Route for downloading the converted file
@app.route("/download/<filename>")
def download_file(filename):
    file_path = os.path.join(app.config["CONVERTED_FOLDER"], filename)
    return send_file(file_path, as_attachment=True)

if __name__ == "__main__":
    app.run()