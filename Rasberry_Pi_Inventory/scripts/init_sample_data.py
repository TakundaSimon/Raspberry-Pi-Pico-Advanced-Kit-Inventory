"""
Script to initialize the database with sample Raspberry Pi kit data
Run this script to populate the database with realistic component data
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db, Box, ComponentType, BoxComponent

def init_sample_data():
    """Initialize database with sample Raspberry Pi kit data"""
    
    with app.app_context():
        # Clear existing data
        BoxComponent.query.delete()
        ComponentType.query.delete()
        Box.query.delete()
        db.session.commit()
        
        print("Creating sample component types...")
        
        # Component types based on the Raspberry Pi Pico Advanced Kit
        sample_components = [
            ('Raspberry Pi Pico', 'Main microcontroller board', 1, 'Controllers'),
            ('IR Tracking Sensor', 'Infrared tracking sensor module', 2, 'Sensors'),
            ('IR Remote Module', 'Infrared remote control module', 1, 'Controllers'),
            ('Infrared Remote Control', 'Remote control device', 1, 'Controllers'),
            ('LED 5mm Red', 'Standard red LED', 10, 'Electronics'),
            ('RGB LED', 'Multi-color LED module', 5, 'Electronics'),
            ('Button Switch', 'Tactile push button', 5, 'Electronics'),
            ('Buzzer Module', 'Active buzzer sound module', 2, 'Electronics'),
            ('PIR Motion Sensor', 'Passive infrared motion detector', 1, 'Sensors'),
            ('Light Sensor (LDR)', 'Light dependent resistor', 2, 'Sensors'),
            ('Red Laser Transmitter', 'Laser diode module', 1, 'Electronics'),
            ('Vibration Sensor', 'SW-420 vibration detection', 2, 'Sensors'),
            ('Reed Switch', 'Magnetic proximity switch', 3, 'Electronics'),
            ('Round Magnet', 'Small neodymium magnet', 5, 'Hardware'),
            ('Soil Moisture Sensor', 'Capacitive soil humidity sensor', 1, 'Sensors'),
            ('Potentiometer 10K', 'Variable resistor', 3, 'Electronics'),
            ('Motor Slow Module', 'Geared DC motor', 2, 'Motors'),
            ('DC Motor 3V', 'Small DC motor', 2, 'Motors'),
            ('Fan Blade', 'Plastic propeller', 2, 'Hardware'),
            ('Servo SG90', '9g micro servo motor', 1, 'Motors'),
            ('Joystick Module', 'Analog XY joystick', 1, 'Controllers'),
            ('RFID RC522 Module', 'Radio frequency ID reader', 1, 'Communication'),
            ('RFID Card', 'Mifare 1K card', 3, 'Communication'),
            ('RFID Key Tag', 'Key fob tag', 2, 'Communication'),
            ('TM1637 Display', '4-digit 7-segment display', 1, 'Display'),
            ('Traffic Light Module', 'RGB LED traffic light', 1, 'Display'),
            ('Rotary Encoder', 'KY-040 rotary encoder', 1, 'Sensors'),
            ('LCD1602 Display', '16x2 character LCD', 1, 'Display'),
            ('DHT11 Sensor', 'Temperature & humidity sensor', 1, 'Sensors'),
            ('Raindrop Sensor', 'Water detection sensor', 1, 'Sensors'),
            ('Flame Sensor', 'IR flame detection sensor', 1, 'Sensors'),
            ('SSD1306 OLED', '0.96" OLED display', 1, 'Display'),
            ('4x4 Keypad', 'Matrix membrane keypad', 1, 'Controllers'),
            ('Ultrasonic HC-SR04', 'Distance measurement sensor', 1, 'Sensors'),
            ('Collision Sensor', 'Limit switch sensor', 2, 'Sensors'),
            ('Car Chassis Kit', 'Robot car frame with wheels', 1, 'Hardware'),
            ('USB Cable Type-C', 'USB-C to USB-A cable', 2, 'Cables'),
            ('Breadboard 400 Point', 'Half-size breadboard', 1, 'Hardware'),
            ('Mini Breadboard', '170 point breadboard', 2, 'Hardware'),
            ('Dupont Wires M-M', 'Male to male jumpers', 20, 'Cables'),
            ('Dupont Wires M-F', 'Male to female jumpers', 20, 'Cables'),
            ('Dupont Wires F-F', 'Female to female jumpers', 20, 'Cables'),
            ('M3 Screws', 'Machine screws 8mm', 20, 'Hardware'),
            ('M3 Nuts', 'Hex nuts', 20, 'Hardware'),
            ('Copper Standoffs', 'M3 threaded spacers', 10, 'Hardware'),
            ('Resistor 220Ω', 'Current limiting resistor', 10, 'Electronics'),
            ('Resistor 1KΩ', 'Pull-up resistor', 10, 'Electronics'),
            ('Resistor 10KΩ', 'High value resistor', 5, 'Electronics')
        ]
        
        for name, desc, max_qty, category in sample_components:
            component = ComponentType(
                name=name,
                description=desc,
                max_per_box=max_qty,
                category=category
            )
            db.session.add(component)
        
        print(f"Created {len(sample_components)} component types")
        
        # Create sample boxes
        sample_boxes = [
            ('Raspberry Pi Pico Kit A', 'Primary development kit with sensors and actuators'),
            ('Raspberry Pi Pico Kit B', 'Secondary kit for advanced projects'),
            ('Electronics Components', 'Basic electronic components and resistors'),
            ('Sensor Collection', 'Specialized sensors for environmental monitoring'),
            ('Motor & Actuator Kit', 'Motors, servos, and mechanical components')
        ]
        
        for name, desc in sample_boxes:
            box = Box(name=name, description=desc)
            db.session.add(box)
        
        db.session.commit()
        print(f"Created {len(sample_boxes)} boxes")
        
        # Add some sample inventory to boxes
        print("Adding sample inventory...")
        
        # Get created objects
        boxes = Box.query.all()
        components = ComponentType.query.all()
        
        # Kit A - Main development kit
        kit_a = boxes[0]
        kit_a_components = [
            ('Raspberry Pi Pico', 1),
            ('Breadboard 400 Point', 1),
            ('LED 5mm Red', 5),
            ('Button Switch', 3),
            ('Resistor 220Ω', 5),
            ('Resistor 1KΩ', 5),
            ('Dupont Wires M-M', 10),
            ('USB Cable Type-C', 1),
            ('Ultrasonic HC-SR04', 1),
            ('Servo SG90', 1),
            ('DHT11 Sensor', 1)
        ]
        
        for comp_name, qty in kit_a_components:
            comp_type = ComponentType.query.filter_by(name=comp_name).first()
            if comp_type:
                box_comp = BoxComponent(
                    box_id=kit_a.id,
                    component_type_id=comp_type.id,
                    quantity=qty
                )
                db.session.add(box_comp)
        
        # Kit B - Secondary kit
        kit_b = boxes[1]
        kit_b_components = [
            ('Raspberry Pi Pico', 1),
            ('Mini Breadboard', 2),
            ('RGB LED', 3),
            ('PIR Motion Sensor', 1),
            ('Light Sensor (LDR)', 1),
            ('Buzzer Module', 1),
            ('Joystick Module', 1),
            ('RFID RC522 Module', 1),
            ('RFID Card', 2),
            ('TM1637 Display', 1)
        ]
        
        for comp_name, qty in kit_b_components:
            comp_type = ComponentType.query.filter_by(name=comp_name).first()
            if comp_type:
                box_comp = BoxComponent(
                    box_id=kit_b.id,
                    component_type_id=comp_type.id,
                    quantity=qty
                )
                db.session.add(box_comp)
        
        # Electronics Components box
        electronics_box = boxes[2]
        electronics_components = [
            ('Resistor 220Ω', 10),
            ('Resistor 1KΩ', 10),
            ('Resistor 10KΩ', 5),
            ('LED 5mm Red', 10),
            ('Button Switch', 5),
            ('Potentiometer 10K', 3),
            ('Reed Switch', 3),
            ('Round Magnet', 5)
        ]
        
        for comp_name, qty in electronics_components:
            comp_type = ComponentType.query.filter_by(name=comp_name).first()
            if comp_type:
                box_comp = BoxComponent(
                    box_id=electronics_box.id,
                    component_type_id=comp_type.id,
                    quantity=qty
                )
                db.session.add(box_comp)
        
        db.session.commit()
        print("Sample inventory added successfully!")
        
        # Print summary
        print("\n=== Database Summary ===")
        print(f"Total Boxes: {Box.query.count()}")
        print(f"Total Component Types: {ComponentType.query.count()}")
        print(f"Total Inventory Entries: {BoxComponent.query.count()}")
        
        print("\nBoxes created:")
        for box in Box.query.all():
            component_count = len(box.components)
            total_items = sum(bc.quantity for bc in box.components)
            print(f"  - {box.name}: {component_count} component types, {total_items} total items")

if __name__ == '__main__':
    init_sample_data()
