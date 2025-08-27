from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///toolkit_inventory.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Database Models
class Box(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    components = db.relationship('BoxComponent', backref='box', lazy=True, cascade='all, delete-orphan')

class ComponentType(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text)
    max_per_box = db.Column(db.Integer, nullable=False, default=1)
    category = db.Column(db.String(50))

class BoxComponent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    box_id = db.Column(db.Integer, db.ForeignKey('box.id'), nullable=False)
    component_type_id = db.Column(db.Integer, db.ForeignKey('component_type.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=0)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)
    
    component_type = db.relationship('ComponentType', backref='box_components')
    
    __table_args__ = (db.UniqueConstraint('box_id', 'component_type_id'),)

# Routes
@app.route('/')
def index():
    boxes = Box.query.all()
    return render_template('index.html', boxes=boxes)

@app.route('/boxes')
def boxes():
    boxes = Box.query.all()
    return render_template('boxes.html', boxes=boxes)

@app.route('/box/<int:box_id>')
def view_box(box_id):
    box = Box.query.get_or_404(box_id)
    components = db.session.query(BoxComponent, ComponentType).join(ComponentType).filter(BoxComponent.box_id == box_id).all()
    return render_template('box_detail.html', box=box, components=components)

@app.route('/components')
def components():
    component_types = ComponentType.query.all()
    return render_template('components.html', component_types=component_types)

@app.route('/add_box', methods=['GET', 'POST'])
def add_box():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form.get('description', '')
        
        if Box.query.filter_by(name=name).first():
            flash('Box name already exists!', 'error')
            return render_template('add_box.html')
        
        box = Box(name=name, description=description)
        db.session.add(box)
        db.session.commit()
        flash('Box added successfully!', 'success')
        return redirect(url_for('boxes'))
    
    return render_template('add_box.html')

@app.route('/add_component_type', methods=['GET', 'POST'])
def add_component_type():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form.get('description', '')
        max_per_box = int(request.form['max_per_box'])
        category = request.form.get('category', '')
        
        if ComponentType.query.filter_by(name=name).first():
            flash('Component type already exists!', 'error')
            return render_template('add_component_type.html')
        
        component_type = ComponentType(
            name=name, 
            description=description, 
            max_per_box=max_per_box,
            category=category
        )
        db.session.add(component_type)
        db.session.commit()
        flash('Component type added successfully!', 'success')
        return redirect(url_for('components'))
    
    return render_template('add_component_type.html')

@app.route('/manage_inventory/<int:box_id>')
def manage_inventory(box_id):
    box = Box.query.get_or_404(box_id)
    component_types = ComponentType.query.all()
    current_components = {bc.component_type_id: bc.quantity for bc in box.components}
    return render_template('manage_inventory.html', box=box, component_types=component_types, current_components=current_components)

@app.route('/api/add_component', methods=['POST'])
def api_add_component():
    try:
        box_id = int(request.json['box_id'])
        component_type_id = int(request.json['component_type_id'])
        quantity = int(request.json['quantity'])
        
        if quantity <= 0:
            return jsonify({'success': False, 'message': 'Quantity must be positive'})
        
        box = Box.query.get_or_404(box_id)
        component_type = ComponentType.query.get_or_404(component_type_id)
        
        # Check if component already exists in box
        box_component = BoxComponent.query.filter_by(box_id=box_id, component_type_id=component_type_id).first()
        
        if box_component:
            new_quantity = box_component.quantity + quantity
        else:
            new_quantity = quantity
        
        # Check capacity limit
        if new_quantity > component_type.max_per_box:
            return jsonify({
                'success': False, 
                'message': f'Cannot add {quantity} {component_type.name}(s). Maximum allowed: {component_type.max_per_box}, Current: {box_component.quantity if box_component else 0}'
            })
        
        if box_component:
            box_component.quantity = new_quantity
            box_component.last_updated = datetime.utcnow()
        else:
            box_component = BoxComponent(
                box_id=box_id,
                component_type_id=component_type_id,
                quantity=new_quantity
            )
            db.session.add(box_component)
        
        db.session.commit()
        return jsonify({'success': True, 'message': f'Added {quantity} {component_type.name}(s) to {box.name}'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/remove_component', methods=['POST'])
def api_remove_component():
    try:
        box_id = int(request.json['box_id'])
        component_type_id = int(request.json['component_type_id'])
        quantity = int(request.json['quantity'])
        
        if quantity <= 0:
            return jsonify({'success': False, 'message': 'Quantity must be positive'})
        
        box_component = BoxComponent.query.filter_by(box_id=box_id, component_type_id=component_type_id).first()
        
        if not box_component:
            return jsonify({'success': False, 'message': 'Component not found in box'})
        
        if box_component.quantity < quantity:
            return jsonify({'success': False, 'message': f'Cannot remove {quantity} items. Only {box_component.quantity} available'})
        
        box_component.quantity -= quantity
        box_component.last_updated = datetime.utcnow()
        
        # Remove component entry if quantity becomes 0
        if box_component.quantity == 0:
            db.session.delete(box_component)
        
        db.session.commit()
        
        component_type = ComponentType.query.get(component_type_id)
        box = Box.query.get(box_id)
        return jsonify({'success': True, 'message': f'Removed {quantity} {component_type.name}(s) from {box.name}'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})

@app.route('/transfer')
def transfer():
    boxes = Box.query.all()
    return render_template('transfer.html', boxes=boxes)

@app.route('/api/get_box_components/<int:box_id>')
def api_get_box_components(box_id):
    components = db.session.query(BoxComponent, ComponentType).join(ComponentType).filter(BoxComponent.box_id == box_id).all()
    result = []
    for box_component, component_type in components:
        result.append({
            'id': component_type.id,
            'name': component_type.name,
            'quantity': box_component.quantity
        })
    return jsonify(result)

@app.route('/api/transfer_component', methods=['POST'])
def api_transfer_component():
    try:
        from_box_id = int(request.json['from_box_id'])
        to_box_id = int(request.json['to_box_id'])
        component_type_id = int(request.json['component_type_id'])
        quantity = int(request.json['quantity'])
        
        if from_box_id == to_box_id:
            return jsonify({'success': False, 'message': 'Cannot transfer to the same box'})
        
        if quantity <= 0:
            return jsonify({'success': False, 'message': 'Quantity must be positive'})
        
        # Get components and validate
        from_component = BoxComponent.query.filter_by(box_id=from_box_id, component_type_id=component_type_id).first()
        if not from_component or from_component.quantity < quantity:
            return jsonify({'success': False, 'message': 'Insufficient quantity in source box'})
        
        component_type = ComponentType.query.get(component_type_id)
        to_component = BoxComponent.query.filter_by(box_id=to_box_id, component_type_id=component_type_id).first()
        
        # Check capacity in destination box
        current_in_dest = to_component.quantity if to_component else 0
        if current_in_dest + quantity > component_type.max_per_box:
            return jsonify({
                'success': False, 
                'message': f'Transfer would exceed capacity. Max: {component_type.max_per_box}, Current in destination: {current_in_dest}'
            })
        
        # Perform atomic transfer
        # Remove from source
        from_component.quantity -= quantity
        if from_component.quantity == 0:
            db.session.delete(from_component)
        else:
            from_component.last_updated = datetime.utcnow()
        
        # Add to destination
        if to_component:
            to_component.quantity += quantity
            to_component.last_updated = datetime.utcnow()
        else:
            to_component = BoxComponent(
                box_id=to_box_id,
                component_type_id=component_type_id,
                quantity=quantity
            )
            db.session.add(to_component)
        
        db.session.commit()
        
        from_box = Box.query.get(from_box_id)
        to_box = Box.query.get(to_box_id)
        return jsonify({
            'success': True, 
            'message': f'Transferred {quantity} {component_type.name}(s) from {from_box.name} to {to_box.name}'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})

@app.route('/search')
def search():
    query = request.args.get('q', '')
    results = []
    
    if query:
        # Search for components across all boxes
        components = db.session.query(BoxComponent, ComponentType, Box).join(ComponentType).join(Box).filter(
            ComponentType.name.contains(query)
        ).all()
        
        for box_component, component_type, box in components:
            results.append({
                'component_name': component_type.name,
                'box_name': box.name,
                'box_id': box.id,
                'quantity': box_component.quantity
            })
    
    return render_template('search.html', query=query, results=results)

def init_db():
    """Initialize database with sample data"""
    db.create_all()
    
    # Check if data already exists
    if ComponentType.query.first():
        return
    
    # Add sample component types based on the Raspberry Pi kit
    sample_components = [
        ('Raspberry Pi Pico', 'Main microcontroller board', 1, 'Controllers'),
        ('IR Tracking Sensor', 'Infrared tracking sensor module', 2, 'Sensors'),
        ('IR Remote Module', 'Infrared remote control module', 1, 'Controllers'),
        ('Infrared Remote Control', 'Remote control device', 1, 'Controllers'),
        ('LED', 'Light emitting diode', 10, 'Electronics'),
        ('RGB LED', 'Multi-color LED', 5, 'Electronics'),
        ('Button', 'Push button switch', 5, 'Electronics'),
        ('Buzzer', 'Sound buzzer module', 2, 'Electronics'),
        ('PIR Sensor', 'Passive infrared motion sensor', 1, 'Sensors'),
        ('Light Sensor', 'Photoresistor light sensor', 2, 'Sensors'),
        ('Red Laser Transmitter', 'Laser diode module', 1, 'Electronics'),
        ('Vibration Sensor', 'Vibration detection module', 2, 'Sensors'),
        ('Reed Switch', 'Magnetic reed switch', 3, 'Electronics'),
        ('Round Magnet', 'Small round magnet', 5, 'Hardware'),
        ('Soil Moisture Sensor', 'Soil humidity detection', 1, 'Sensors'),
        ('Potentiometer', 'Variable resistor', 3, 'Electronics'),
        ('Motor Slow Module', 'Gear motor module', 2, 'Motors'),
        ('Motor', 'DC motor', 2, 'Motors'),
        ('Fan Blade', 'Propeller for motor', 2, 'Hardware'),
        ('Servo', 'Servo motor', 1, 'Motors'),
        ('Joystick Module', 'Analog joystick controller', 1, 'Controllers'),
        ('RFID Module', 'Radio frequency identification', 1, 'Communication'),
        ('RFID Card/Tag', 'RFID identification tags', 5, 'Communication'),
        ('TM1637 4 Bit Digital Tube', '7-segment display', 1, 'Display'),
        ('Traffic Light Module', 'LED traffic light simulator', 1, 'Display'),
        ('Rotary Encoder', 'Rotary position sensor', 1, 'Sensors'),
        ('LCD1602', '16x2 character LCD display', 1, 'Display'),
        ('DHT11', 'Temperature and humidity sensor', 1, 'Sensors'),
        ('Raindrop Sensor', 'Water detection sensor', 1, 'Sensors'),
        ('Flame Sensor', 'Fire detection sensor', 1, 'Sensors'),
        ('SSD1306 OLED', 'Small OLED display', 1, 'Display'),
        ('4x4 Matrix Membrane Keypad', 'Button matrix keypad', 1, 'Controllers'),
        ('Ultrasonic Sensor', 'Distance measurement sensor', 1, 'Sensors'),
        ('Collision Sensor', 'Impact detection switch', 2, 'Sensors'),
        ('Car Chassis Kit', 'Robot car frame and wheels', 1, 'Hardware'),
        ('USB Cable', 'USB connection cable', 2, 'Cables'),
        ('Medium Breadboard', 'Prototyping breadboard', 1, 'Hardware'),
        ('Small Breadboard', 'Mini breadboard', 2, 'Hardware'),
        ('Dupont Line', 'Jumper wire set', 1, 'Cables'),
        ('Screws', 'Assembly screws', 20, 'Hardware'),
        ('Nuts', 'Hex nuts', 20, 'Hardware'),
        ('Double-pass Copper Column', 'Standoff spacers', 10, 'Hardware'),
        ('Male-male Short Line', 'Short jumper wires', 10, 'Cables'),
        ('Male-male Long Line', 'Long jumper wires', 10, 'Cables')
    ]
    
    for name, desc, max_qty, category in sample_components:
        component = ComponentType(
            name=name,
            description=desc,
            max_per_box=max_qty,
            category=category
        )
        db.session.add(component)
    
    # Add sample boxes
    sample_boxes = [
        ('Raspberry Pi Kit A', 'Primary development kit'),
        ('Raspberry Pi Kit B', 'Secondary backup kit'),
        ('Sensor Collection', 'Specialized sensor toolkit')
    ]
    
    for name, desc in sample_boxes:
        box = Box(name=name, description=desc)
        db.session.add(box)
    
    db.session.commit()

if __name__ == '__main__':
    with app.app_context():
        init_db()
    app.run(debug=True)
