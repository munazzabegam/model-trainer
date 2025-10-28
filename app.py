from flask import Flask, request, redirect, render_template
from database import init_db, save_model_metadata, get_model_details, get_all_models

app = Flask(__name__)
init_db()

def tuple_to_dict(model_tuple):
    return {
        "id": model_tuple[0],
        "name": model_tuple[1],
        "data_field": model_tuple[2],
        "labels": model_tuple[3]
    }

@app.route("/")
def index():
    models = [tuple_to_dict(m) for m in get_all_models()]
    return render_template("index.html", models=models)

@app.route("/create_model", methods=["GET", "POST"])
def create_model():
    if request.method == "POST":
        model_name = request.form.get("name")
        data_field = request.form.get("data_field")
        labels_str = request.form.get("labels")

        model_id = save_model_metadata(model_name, data_field, labels_str)
        return redirect(f"/model/{model_id}")
    return render_template("create_model.html")

@app.route("/model/<int:model_id>")
def model_detail(model_id):
    model_tuple = get_model_details(model_id)
    if not model_tuple:
        return "Model not found", 404
    model = tuple_to_dict(model_tuple)
    return render_template("model_detail.html", model=model)

@app.route("/add_data/<int:model_id>", methods=["GET", "POST"])
def add_data(model_id):
    model_tuple = get_model_details(model_id)
    if not model_tuple:
        return "Model not found", 404
    model = tuple_to_dict(model_tuple)

    if request.method == "POST":
        data_value = request.form.get("data_value")
        labels = request.form.get("labels")
        # Here you can process or save the data
        return f"Data added to model {model['id']}: {data_value}, Labels: {labels}"

    return render_template("add_data.html", model=model)

if __name__ == "__main__":
    app.run(debug=True)
