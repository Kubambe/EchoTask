from flask import render_template, flash, redirect, url_for, request, jsonify
from flask_login import current_user, login_required
from app import db
from app.main import bp
from app.models import Task, User
from datetime import datetime
import json

@bp.route('/')
@bp.route('/index')
@login_required
def index():
    tasks = current_user.tasks.order_by(Task.due_date.asc()).all()
    return render_template('main/index.html', title='Home', tasks=tasks)

@bp.route('/create_task', methods=['GET', 'POST'])
@login_required
def create_task():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form.get('description', '')
        due_date_str = request.form.get('due_date')
        due_date = datetime.strptime(due_date_str, '%Y-%m-%dT%H:%M') if due_date_str else None
        categories = request.form.get('categories', '')
        reminders = json.dumps(request.form.getlist('reminders'))
        
        task = Task(
            title=title,
            description=description,
            due_date=due_date,
            categories=categories,
            reminders=reminders,
            user_id=current_user.id
        )
        db.session.add(task)
        db.session.commit()
        flash('Task created successfully!')
        return redirect(url_for('main.index'))
    return render_template('main/create_task.html', title='Create Task')

@bp.route('/edit_task/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_task(id):
    task = Task.query.get_or_404(id)
    if task.user_id != current_user.id:
        flash('You do not have permission to edit this task.')
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        task.title = request.form['title']
        task.description = request.form.get('description', '')
        due_date_str = request.form.get('due_date')
        task.due_date = datetime.strptime(due_date_str, '%Y-%m-%dT%H:%M') if due_date_str else None
        task.categories = request.form.get('categories', '')
        task.reminders = json.dumps(request.form.getlist('reminders'))
        task.completed = 'completed' in request.form
        
        db.session.commit()
        flash('Task updated successfully!')
        return redirect(url_for('main.index'))
    
    # Format the due_date for the datetime-local input
    due_date = task.due_date.strftime('%Y-%m-%dT%H:%M') if task.due_date else ''
    return render_template('main/edit_task.html', title='Edit Task', task=task, due_date=due_date)

@bp.route('/delete_task/<int:id>', methods=['POST'])
@login_required
def delete_task(id):
    task = Task.query.get_or_404(id)
    if task.user_id != current_user.id:
        flash('You do not have permission to delete this task.')
        return redirect(url_for('main.index'))
    
    db.session.delete(task)
    db.session.commit()
    flash('Task deleted successfully!')
    return redirect(url_for('main.index'))

@bp.route('/share_task/<int:id>', methods=['GET', 'POST'])
@login_required
def share_task(id):
    task = Task.query.get_or_404(id)
    if task.user_id != current_user.id:
        flash('You do not have permission to share this task.')
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        username = request.form['username']
        user = User.query.filter_by(username=username).first()
        if not user:
            flash('User not found.')
            return redirect(url_for('main.share_task', id=id))
        
        # Append the user ID to the shared_with string (comma separated)
        if task.shared_with:
            shared_list = task.shared_with.split(',')
            if str(user.id) not in shared_list:
                shared_list.append(str(user.id))
                task.shared_with = ','.join(shared_list)
        else:
            task.shared_with = str(user.id)
        
        db.session.commit()
        flash(f'Task shared with {username}!')
        return redirect(url_for('main.index'))
    
    return render_template('main/share_task.html', title='Share Task', task=task)

@bp.route('/toggle_dark_mode', methods=['POST'])
@login_required
def toggle_dark_mode():
    current_user.dark_mode = not current_user.dark_mode
    db.session.commit()
    return jsonify({'dark_mode': current_user.dark_mode})