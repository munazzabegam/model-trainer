# app.py
from flask import Flask, request, redirect, render_template, url_for, send_file
import pandas as pd
import io
# Ensure all required functions are imported
from database import init_db, save_model_metadata, get_model_details, get_all_models, save_model_data, delete_all_data, get_data_for_model, log_prediction, update_prediction_feedback, get_all_data_for_export

app = Flask(__name__)
init_db()

def tuple_to_dict(model_tuple):
    # This must match the SELECT * order: (id, name, data_field, labels)
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
        return redirect(url_for('model_detail', model_id=model_id))
    return render_template("create_model.html")

@app.route("/model/<int:model_id>")
def model_detail(model_id):
    model_tuple = get_model_details(model_id)
    if not model_tuple:
        return "Model not found", 404
    
    model = tuple_to_dict(model_tuple)
    training_data = get_data_for_model(model_id)
    
    return render_template("model_detail.html", model=model, training_data=training_data)

@app.route("/add_data/<int:model_id>", methods=["GET", "POST"])
def add_data(model_id):
    model_tuple = get_model_details(model_id)
    if not model_tuple:
        return "Model not found", 404
    model = tuple_to_dict(model_tuple)

    labels_list = [l.strip() for l in model['labels'].split(',') if l.strip()]

    if request.method == "POST":
        data_value = request.form.get("data_value")
        label = request.form.get("label") 
        
        save_model_data(model_id, data_value, label)
        
        return redirect(url_for('add_data', model_id=model_id))

    return render_template("add_data.html", model=model, labels_list=labels_list) 

@app.route("/model/<int:model_id>/train", methods=["GET", "POST"])
def train_model(model_id):
    from model_manager import train_model_from_db
    model_tuple = get_model_details(model_id)
    if not model_tuple:
        return "Model not found", 404
    model = tuple_to_dict(model_tuple)
    
    message = None

    if request.method == "POST":
        success = train_model_from_db(model['id'], model['name'], model['data_field'])
        
        if success:
            message = f"Model '{model['name']}' training completed successfully!"
        else:
            message = f"Model '{model['name']}' training failed or no data was available. Check logs."
        
    return render_template("train.html", model_name=model['name'], message=message, model_id=model['id'])

@app.route("/model/<int:model_id>/predict", methods=["GET", "POST"])
def predict(model_id):
    from model_manager import predict_model 
    model_tuple = get_model_details(model_id)
    if not model_tuple:
        return "Model not found", 404
    model = tuple_to_dict(model_tuple)
    
    prediction = None
    input_text = None
    prediction_id = None
    labels_list = [l.strip() for l in model['labels'].split(',') if l.strip()]
    
    if request.method == "POST":
        input_text = request.form.get("text")
        
        try:
            prediction = predict_model(model['name'], input_text)
            
            # LOG PREDICTION: Store the prediction result
            prediction_id = log_prediction(model_id, input_text, prediction)
            
        except FileNotFoundError:
            prediction = "Model not trained yet."
        except Exception as e:
            prediction = f"Prediction Error: {e}"
            
    return render_template(
        "predict.html", 
        model=model, 
        input_text=input_text,
        prediction=prediction,
        prediction_id=prediction_id, 
        labels_list=labels_list
    )

@app.route("/feedback/<int:prediction_id>/<int:model_id>", methods=["POST"])
def feedback(prediction_id, model_id):
    model_tuple = get_model_details(model_id)
    if not model_tuple:
        return "Model not found", 404
    
    # Retrieve data from the form
    action = request.form.get("action")
    input_text = request.form.get("input_text") # <-- NEW: Get the input text
    
    # 1. Determine the True Label and correctness status
    if action == "correct":
        is_correct = 1
        true_label = request.form.get("predicted_label")
    elif action == "incorrect":
        is_correct = 0
        true_label = request.form.get("true_label")
    else:
        return redirect(url_for('model_detail', model_id=model_id))

    # 2. Update the prediction log with the feedback
    update_prediction_feedback(prediction_id, is_correct, true_label)
    
    # 3. CRITICAL: Add the new, verified data point to the permanent training data
    if true_label and input_text:
        # This function stores the data in the model_data table for future training
        save_model_data(model_id, input_text, true_label)
    
    return redirect(url_for('model_detail', model_id=model_id))

@app.route("/download_data/<int:model_id>")
def download_data(model_id):
    model_tuple = get_model_details(model_id)
    if not model_tuple:
        return "Model not found", 404
    model = tuple_to_dict(model_tuple)
    
    all_data = get_all_data_for_export(model_id)
    
    if not all_data:
        return "No data to export.", 404

    df = pd.DataFrame(all_data, columns=['Input Text', 'Label', 'Source'])
    
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='Model_Data', index=False)
    output.seek(0)
    
    file_name = f"{model['name'].replace(' ', '_')}_dataset.xlsx"
    return send_file(
        output,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        download_name=file_name,
        as_attachment=True
    )

@app.route("/delete_all", methods=["POST"])
def delete_all():
    delete_all_data()
    return redirect(url_for('index'))

if __name__ == "__main__":
    import os
    if not os.path.exists("models"):
        os.makedirs("models")
    app.run(debug=True)