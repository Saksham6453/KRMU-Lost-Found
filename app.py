from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS # Import CORS
from datetime import datetime
import os
from functools import wraps

app = Flask(__name__)
CORS(app) # Enable CORS for the entire app

# IMPORTANT: Change this to a long, random string!
app.config['SECRET_KEY'] = 'a-very-secret-and-random-key-for-sessions'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///lost_found.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# --- Hardcoded Admin Credentials (for simplicity) ---
ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'password123' # Change this in your real project!

db = SQLAlchemy(app)

# Database Models (Your Item class remains the same)
class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(20), nullable=False)  # 'lost' or 'found'
    location = db.Column(db.String(100), nullable=False)
    contact_name = db.Column(db.String(100), nullable=False)
    contact_email = db.Column(db.String(100), nullable=False)
    contact_phone = db.Column(db.String(20))
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    date_resolved = db.Column(db.DateTime)
    is_resolved = db.Column(db.Boolean, default=False)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'category': self.category,
            'status': self.status,
            'location': self.location,
            'contact_name': self.contact_name,
            'contact_email': self.contact_email,
            'contact_phone': self.contact_phone,
            'date_created': self.date_created.strftime('%Y-%m-%d %H:%M:%S'),
            'is_resolved': self.is_resolved
        }

# --- Login Required Decorator ---
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            return jsonify({'success': False, 'message': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return decorated_function

# --- Routes ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
        session['logged_in'] = True
        return jsonify({'success': True})
    
    return jsonify({'success': False, 'message': 'Invalid credentials'}), 401

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('index'))

@app.route('/api/auth_status')
def auth_status():
    return jsonify({'logged_in': 'logged_in' in session})

# --- API Routes ---
# This route is public
@app.route('/api/items', methods=['GET'])
def get_items():
    status_filter = request.args.get('status', 'all')
    category_filter = request.args.get('category', 'all')
    resolved_filter = request.args.get('resolved', 'active')
    
    query = Item.query
    
    if status_filter != 'all':
        query = query.filter(Item.status == status_filter)
    
    if category_filter != 'all':
        query = query.filter(Item.category == category_filter)
    
    if resolved_filter == 'active':
        query = query.filter(Item.is_resolved == False)
    elif resolved_filter == 'resolved':
        query = query.filter(Item.is_resolved == True)
    
    items = query.order_by(Item.date_created.desc()).all()
    return jsonify([item.to_dict() for item in items])

# This route is public
@app.route('/api/items', methods=['POST'])
def create_item():
    try:
        data = request.get_json()
        new_item = Item(
            title=data.get('title'),
            description=data.get('description'),
            category=data.get('category'),
            location=data.get('location'),
            contact_name=data.get('contact_name'),
            contact_email=data.get('contact_email'),
            contact_phone=data.get('contact_phone', ''),
            status=data.get('status'),
            is_resolved=False
        )
        db.session.add(new_item)
        db.session.commit()
        return jsonify({"success": True, "message": "Item created successfully"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)}), 400

# --- PROTECTED ADMIN ROUTES ---
@app.route('/api/items/<int:item_id>', methods=['PUT'])
@login_required
def update_item(item_id):
    try:
        item = Item.query.get_or_404(item_id)
        data = request.get_json()
        
        item.title = data.get('title', item.title)
        item.description = data.get('description', item.description)
        item.category = data.get('category', item.category)
        item.status = data.get('status', item.status)
        item.location = data.get('location', item.location)
        item.contact_name = data.get('contact_name', item.contact_name)
        item.contact_email = data.get('contact_email', item.contact_email)
        item.contact_phone = data.get('contact_phone', item.contact_phone)
        
        if 'is_resolved' in data:
            item.is_resolved = data['is_resolved']
            if item.is_resolved:
                item.date_resolved = datetime.utcnow()
            else:
                item.date_resolved = None
        
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Item updated successfully', 'item': item.to_dict()})
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 400


@app.route('/api/items/<int:item_id>', methods=['DELETE'])
@login_required
def delete_item(item_id):
    try:
        item = Item.query.get_or_404(item_id)
        db.session.delete(item)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Item deleted successfully'})
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 400

# This route is public
@app.route('/api/stats')
def get_stats():
    total_items = Item.query.count()
    lost_items = Item.query.filter(Item.status == 'lost', Item.is_resolved == False).count()
    found_items = Item.query.filter(Item.status == 'found', Item.is_resolved == False).count()
    resolved_items = Item.query.filter(Item.is_resolved == True).count()
    
    return jsonify({
        'total_items': total_items,
        'lost_items': lost_items,
        'found_items': found_items,
        'resolved_items': resolved_items
    })

# Create tables if they don't exist
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run()
