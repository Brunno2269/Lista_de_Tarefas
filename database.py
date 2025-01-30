from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import SQLAlchemyError
from contextlib import contextmanager

db = SQLAlchemy()

class Task(db.Model):
    __tablename__ = 'tasks'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'completed': self.completed,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

@contextmanager
def session_scope():
    """Fornece um escopo de sessão para operações no banco de dados."""
    session = db.session
    try:
        yield session
        session.commit()
    except SQLAlchemyError as e:
        session.rollback()
        raise e
    finally:
        session.close()

def init_db(app):
    """Inicializa o banco de dados e cria as tabelas necessárias."""
    db.init_app(app)
    with app.app_context():
        db.create_all()

def add_task(title):
    """Adiciona uma nova tarefa ao banco de dados."""
    with session_scope() as session:
        new_task = Task(title=title)
        session.add(new_task)
        session.flush()
        return new_task.to_dict()

def get_all_tasks():
    """Retorna todas as tarefas do banco de dados."""
    with session_scope() as session:
        tasks = session.query(Task).order_by(Task.created_at.desc()).all()
        return [task.to_dict() for task in tasks]

def update_task(task_id, **kwargs):
    """Atualiza uma tarefa existente."""
    with session_scope() as session:
        task = session.query(Task).get(task_id)
        if not task:
            raise ValueError(f"Tarefa com ID {task_id} não encontrada.")
        
        if 'title' in kwargs:
            task.title = kwargs['title']
        if 'completed' in kwargs:
            task.completed = kwargs['completed']
        
        session.flush()
        return task.to_dict()

def delete_task(task_id):
    """Remove uma tarefa do banco de dados."""
    with session_scope() as session:
        task = session.query(Task).get(task_id)
        if not task:
            raise ValueError(f"Tarefa com ID {task_id} não encontrada.")
        
        session.delete(task)
        session.flush()
        return True