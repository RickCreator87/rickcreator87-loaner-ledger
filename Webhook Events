

Webhook Events

The system can send webhook notifications for events:

```python
# Webhook handler example
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/webhooks/authority-granted', methods=['POST'])
def handle_authority_granted():
    """Handle authority granted webhook"""
    event = request.json
    
    if event["event_type"] == "authority.granted":
        authority_id = event["data"]["authority_id"]
        identity_id = event["data"]["identity_id"]
        
        # Process the event
        print(f"Authority {authority_id} granted to identity {identity_id}")
        
        # Send notification, update database, etc.
    
    return jsonify({"status": "received"}), 200
```
