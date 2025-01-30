from flask import render_template, request, jsonify, abort
from models import db, Task
from utils import validate_task_data

def init_routes(app):
    @app.route('/shutdown', methods=['POST'])
    def shutdown():
        """Encerra o servidor Flask."""
        from utils import shutdown_server
        shutdown_server()
        return jsonify({'message': 'Server shutting down...'})

    @app.route('/')
    def index():
        """Rota principal que renderiza o frontend."""
        return render_template('index.html')

    @app.route('/tasks', methods=['GET'])
    def get_tasks():
        """Retorna todas as tarefas."""
        try:
            tasks = Task.query.order_by(Task.created_at.desc()).all()
            return jsonify([task.to_dict() for task in tasks])
        except Exception as e:
            app.logger.error(f'Error fetching tasks: {str(e)}')
            abort(500, description='Failed to fetch tasks')

    @app.route('/tasks', methods=['POST'])
    def create_task():
        """Adiciona uma nova tarefa."""
        data = request.get_json()
        if not validate_task_data(data):
            abort(400, description='Invalid task data')

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
        """Atualiza uma tarefa existente."""
        task = Task.query.get_or_404(task_id)
        data = request.get_json()

        if 'title' in data and not validate_task_data(data):
            abort(400, description='Invalid task title')

        if 'completed' in data and not isinstance(data['completed'], bool):
            abort(400, description='Invalid completed status')

        try:
            if 'title' in data:
                task.title = data['title'].strip()
            if 'completed' in data:
                task.completed = data['completed']
            db.session.commit()
            return jsonify(task.to_dict())
        except Exception as e:
            db.session.rollback()
            app.logger.error(f'Error updating task: {str(e)}')
            abort(500, description='Failed to update task')

    @app.route('/tasks/<int:task_id>', methods=['DELETE'])
    def delete_task(task_id):
        """Exclui uma tarefa."""
        task = Task.query.get_or_404(task_id)
        try:
            db.session.delete(task)
            db.session.commit()
            return jsonify({'message': 'Task deleted successfully'})
        except Exception as e:
            db.session.rollback()
            app.logger.error(f'Error deleting task: {str(e)}')
            abort(500, description='Failed to delete task')