from flask import Flask, render_template, request, redirect, url_for, send_file
import os
import pandas as pd
from datetime import datetime
from io import BytesIO

app = Flask(__name__)

# ✅ Database directory
DB_DIR = "database"
os.makedirs(DB_DIR, exist_ok=True)


# 🧩 Home Page – Create or Load Model
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        model_name = request.form["model_name"].strip().replace(" ", "_")
        question_col = request.form["question_col"]
        answer_col = request.form["answer_col"]

        model_path = os.path.join(DB_DIR, f"{model_name}.xlsx")

        # If file doesn't exist, create a new dataset
        if not os.path.exists(model_path):
            df = pd.DataFrame(columns=[question_col, answer_col, "Feedback"])
            df.to_excel(model_path, index=False)

        # ✅ Redirect to add data page
        return redirect(url_for("add_data_route", model_name=model_name))
    return render_template("index.html")


# 🧾 Add Data Page – Enter Question and Answer Options
@app.route("/add_data/<model_name>", methods=["GET", "POST"])
def add_data_route(model_name):
    model_path = os.path.join(DB_DIR, f"{model_name}.xlsx")

    if not os.path.exists(model_path):
        return "Model not found. Please go back and create one."

    df = pd.read_excel(model_path)

    if request.method == "POST":
        question = request.form["question"]
        answer = request.form["answer"]
        feedback = request.form.get("feedback", "")

        # ✅ Append data to Excel
        new_data = pd.DataFrame([[question, answer, feedback]], columns=df.columns)
        df = pd.concat([df, new_data], ignore_index=True)
        df.to_excel(model_path, index=False)

    # ✅ Display existing dataset
    data_preview = pd.read_excel(model_path).to_dict(orient="records")
    return render_template("add_data.html", model_name=model_name, data=data_preview, columns=df.columns)


# 🔁 Submit feedback for correction
@app.route("/feedback/<model_name>", methods=["POST"])
def feedback_route(model_name):
    model_path = os.path.join(DB_DIR, f"{model_name}.xlsx")
    df = pd.read_excel(model_path)

    index = int(request.form["index"])
    feedback = request.form["feedback"]

    df.loc[index, "Feedback"] = feedback
    df.to_excel(model_path, index=False)

    return redirect(url_for("add_data_route", model_name=model_name))


# 📥 Download Excel Dataset
@app.route("/download/<model_name>")
def download_route(model_name):
    model_path = os.path.join(DB_DIR, f"{model_name}.xlsx")
    if not os.path.exists(model_path):
        return "Dataset not found."

    return send_file(model_path, as_attachment=True)


# 🗑️ Delete dataset after training
@app.route("/delete/<model_name>")
def delete_route(model_name):
    model_path = os.path.join(DB_DIR, f"{model_name}.xlsx")
    if os.path.exists(model_path):
        os.remove(model_path)
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
