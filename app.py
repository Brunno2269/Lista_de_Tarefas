import threading
from flask import Flask, render_template, request, jsonify, abort
from flask_sqlalchemy import SQLAlchemy
import webbrowser
import os
import signal

app = Flask(__name__)
app.config.from_pyfile('config.py')
db = SQLAlchemy(app)

class Task(db.Model):
    __tablename__ = 'tasks'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    def to_dict(self):
        """Converte o objeto Task em um dicionário para serialização JSON."""
        return {
            'id': self.id,
            'title': self.title,
            'completed': self.completed,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

def shutdown_server():
    os.kill(os.getpid(), signal.SIGINT)

@app.route('/shutdown', methods=['POST'])
def shutdown():
    shutdown_server()
    return jsonify({'message': 'Server shutting down...'})

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/tasks', methods=['GET'])
def get_tasks():
    try:
        tasks = Task.query.order_by(Task.created_at.desc()).all()
        return jsonify([task.to_dict() for task in tasks])
    except Exception as e:
        app.logger.error(f'Error fetching tasks: {str(e)}')
        abort(500, description='Failed to fetch tasks')

@app.route('/tasks', methods=['POST'])
def create_task():
    data = request.get_json()
    if not data or 'title' not in data or len(data['title'].strip()) < 1:
        abort(400, description='Invalid task title')

    try:
        new_task = Task(title=data['title'].strip())
        db.session.add(new_task)
        db.session.commit()
        return jsonify(new_task.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        app.logger.error(f'Error adding task: {str(e)}')
        abort(500, description='Failed to add task')

@app.route('/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    task = Task.query.get_or_404(task_id)
    data = request.get_json()

    if 'title' in data:
        if len(data['title'].strip()) < 1:
            abort(400, description='Invalid task title')
        task.title = data['title'].strip()

    if 'completed' in data:
        if not isinstance(data['completed'], bool):
            abort(400, description='Invalid completed status')
        task.completed = data['completed']

    try:
        db.session.commit()
        return jsonify(task.to_dict())
    except Exception as e:
        db.session.rollback()
        app.logger.error(f'Error updating task: {str(e)}')
        abort(500, description='Failed to update task')

@app.route('/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    try:
        db.session.delete(task)
        db.session.commit()
        return jsonify({'message': 'Task deleted successfully'})
    except Exception as e:
        db.session.rollback()
        app.logger.error(f'Error deleting task: {str(e)}')
        abort(500, description='Failed to delete task')

def open_browser():
    webbrowser.open_new('http://localhost:5000')

if __name__ == '__main__':
    with app.app_context():
        db.create_all() 
    threading.Timer(1, open_browser).start()  
    app.run(debug=True, use_reloader=False) 