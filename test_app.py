import pytest
from app import app, db, Todo

# Create a test client and temporary in-memory database
@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'  # In-memory DB
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client
        with app.app_context():
            db.drop_all()


def test_home_page(client):
    """Test that the home page loads successfully."""
    response = client.get('/')
    assert response.status_code == 200
    assert b'Todo' in response.data or b'todo' in response.data


def test_add_todo(client):
    """Test adding a new todo item."""
    response = client.post('/', data={'title': 'Test Task', 'desc': 'Test Description'}, follow_redirects=True)
    assert response.status_code == 200
    with app.app_context():
        todo = Todo.query.filter_by(title='Test Task').first()
        assert todo is not None
        assert todo.desc == 'Test Description'


def test_update_todo(client):
    """Test updating an existing todo item."""
    with app.app_context():
        todo = Todo(title='Old Title', desc='Old Desc')
        db.session.add(todo)
        db.session.commit()
        sno = todo.sno

    response = client.post(f'/update/{sno}', data={'title': 'New Title', 'desc': 'New Desc'}, follow_redirects=True)
    assert response.status_code == 200
    with app.app_context():
        updated = Todo.query.filter_by(sno=sno).first()
        assert updated.title == 'New Title'
        assert updated.desc == 'New Desc'


def test_delete_todo(client):
    """Test deleting a todo item."""
    with app.app_context():
        todo = Todo(title='Delete Me', desc='Temp')
        db.session.add(todo)
        db.session.commit()
        sno = todo.sno

    response = client.get(f'/delete/{sno}', follow_redirects=True)
    assert response.status_code == 200
    with app.app_context():
        deleted = Todo.query.filter_by(sno=sno).first()
        assert deleted is None
