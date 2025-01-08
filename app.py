import os
import json
import time
import threading
from flask import Flask, render_template, request, redirect, url_for, Response, flash
from werkzeug.utils import secure_filename

# Import all validation functions and logger
from main import (
    validate_schema,
    validate_data,
    validate_table_names,
    validate_column_names,
    validate_column_types,
    validate_foreign_keys,
    validate_properties,
    SchemaValidatorLogger
)

app = Flask(__name__)
app.secret_key = "SOME_SUPER_DUPER_TELL_NO_ONE_SECRET_KEY_GO_BUCKEYES"

# Folder to save uploaded files
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Global references for SSE
logger = None  
validation_progress = {
    'steps_completed': 0,
    'total_steps': 0,
    'current_step': '',
    'status': 'idle',
    'logger_messages': None
}

@app.route('/')
def index():
    """
    Renders the home page with a form to upload schema.json and data.json.
    """
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_files():
    """
    Saves the uploaded schema/data files and redirects to the validation page.
    """
    schema_file = request.files.get('schema_file')
    data_file = request.files.get('data_file')

    if not schema_file or not data_file:
        flash('Please upload both schema.json and data.json files.', 'danger')
        return redirect(url_for('index'))

    schema_filename = secure_filename(schema_file.filename)
    data_filename = secure_filename(data_file.filename)

    schema_path = os.path.join(app.config['UPLOAD_FOLDER'], schema_filename)
    data_path = os.path.join(app.config['UPLOAD_FOLDER'], data_filename)

    schema_file.save(schema_path)
    data_file.save(data_path)

    return redirect(url_for('validate', schema_filename=schema_filename, data_filename=data_filename))

@app.route('/validate/<schema_filename>/<data_filename>')
def validate(schema_filename, data_filename):
    """
    Renders the page with a progress bar and SSE stream to perform validation.
    """
    return render_template('validate.html',
                           schema_filename=schema_filename,
                           data_filename=data_filename)

@app.route('/start-validation')
def start_validation():
    """
    Kicks off the validation in a separate thread and returns SSE for progress.
    """
    schema_filename = request.args.get('schema_filename')
    data_filename = request.args.get('data_filename')

    schema_path = os.path.join(app.config['UPLOAD_FOLDER'], schema_filename)
    data_path = os.path.join(app.config['UPLOAD_FOLDER'], data_filename)

    validation_thread = threading.Thread(
        target=run_validation_process,
        args=(schema_path, data_path,)
    )
    validation_thread.start()

    return Response(stream_with_context_sse(), mimetype='text/event-stream')

def run_validation_process(schema_path, data_path):
    """
    Breaks down the validation process into sequential steps,
    updates the validation_progress, and collects logs.
    """
    global logger
    logger = SchemaValidatorLogger()

    global validation_progress
    validation_progress['status'] = 'running'
    validation_progress['steps_completed'] = 0

    steps = [
        'Loading Schema & Data',
        'Validating Schema Structure',
        'Validating Data Structure',
        'Checking Table Names',
        'Checking Column Names',
        'Checking Foreign Keys',
        'Checking Column Types',
        'Checking Properties',
        'Finishing Validation'
    ]
    validation_progress['total_steps'] = len(steps)

    # Step 1: Load schema & data
    validation_progress['current_step'] = steps[0]
    update_progress()
    try:
        with open(schema_path, 'r') as f:
            schema = json.load(f)
        with open(data_path, 'r') as f:
            data = json.load(f)
    except Exception as e:
        logger.add_message(f"Error reading files: {e}", 'error')
        validation_progress['status'] = 'finished'
        finalize_sse_data()
        return
    time.sleep(0.7)
    increment_step()

    # Step 2: Validate schema
    validation_progress['current_step'] = steps[1]
    update_progress()
    try:
        validate_schema(schema, logger)
    except ValueError as e:
        logger.add_message(f"Schema validation error: {e}", 'error')
        validation_progress['status'] = 'finished'
        finalize_sse_data()
        return
    time.sleep(0.7)
    increment_step()

    # Step 3: Validate data structure
    validation_progress['current_step'] = steps[2]
    update_progress()
    try:
        validate_data(data, logger)
    except ValueError as e:
        logger.add_message(f"Data validation error: {e}", 'error')
        validation_progress['status'] = 'finished'
        finalize_sse_data()
        return
    time.sleep(0.7)
    increment_step()

    # Step 4: Check table names
    validation_progress['current_step'] = steps[3]
    update_progress()
    validate_table_names(data, schema, logger)
    time.sleep(0.7)
    increment_step()

    # Step 5: Check column names
    validation_progress['current_step'] = steps[4]
    update_progress()
    validate_column_names(data, schema, logger)
    time.sleep(0.7)
    increment_step()

    # Step 6: Check foreign keys
    validation_progress['current_step'] = steps[5]
    update_progress()
    validate_foreign_keys(data, schema, logger)
    time.sleep(0.7)
    increment_step()

    # Step 7: Check column types
    validation_progress['current_step'] = steps[6]
    update_progress()
    validate_column_types(data, schema, logger)
    time.sleep(0.7)
    increment_step()

    # Step 8: Check properties
    validation_progress['current_step'] = steps[7]
    update_progress()
    validate_properties(data, schema, logger)
    time.sleep(0.7)
    increment_step()

    # Step 9: Finishing
    validation_progress['current_step'] = steps[8]
    update_progress()
    time.sleep(0.5)

    # Print or store final results
    logger.print_messages()

    # Mark the validation as finished
    validation_progress['status'] = 'finished'
    # Store all log messages in the dictionary so they can be displayed in the front end
    finalize_sse_data()

def increment_step():
    """
    Helper function to bump the completed steps count and update SSE.
    """
    validation_progress['steps_completed'] += 1
    update_progress()

def update_progress():
    """
    We rely on the SSE generator to poll these changes every second.
    """
    pass

def finalize_sse_data():
    """
    Adds logger messages to validation_progress with styled formatting.
    Groups identical messages and adds their count.
    """
    global validation_progress
    global logger
    
    def combine_messages(messages, style):
        message_counts = {}
        for msg in messages:
            message_counts[msg] = message_counts.get(msg, 0) + 1
        
        # Add HTML styling to messages with count first
        return [f"<span class='{style}'>"
                f"<span class='message-count'>{f'({count}x)'} </span>"
                f"<span class='message-text'>{msg}</span></span>" 
                for msg, count in message_counts.items()]

    validation_progress['logger_messages'] = {
        'info': combine_messages(logger.info, 'info-message'),
        'warnings': combine_messages(logger.warnings, 'warning-message'),
        'errors': combine_messages(logger.errors, 'error-message'),
        'structural_errors': combine_messages(logger.structural_errors, 'structural-error-message')
    }

def stream_with_context_sse():
    """
    SSE generator that periodically yields the validation_progress as JSON.
    """
    while True:
        data = json.dumps({
            'steps_completed': validation_progress['steps_completed'],
            'total_steps': validation_progress['total_steps'],
            'current_step': validation_progress['current_step'],
            'status': validation_progress['status'],
            'logger_messages': validation_progress['logger_messages']
        })
        yield f"data: {data}\n\n"

        if validation_progress['status'] == 'finished':
            break

        time.sleep(1)

if __name__ == '__main__':
    app.run(debug=True)
