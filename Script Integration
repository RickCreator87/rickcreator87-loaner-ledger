Script Integration

```python
#!/usr/bin/env python3
"""Example script using the CLI programmatically"""

import subprocess
import json

def process_identity_script(identity_file, authority_type):
    """Process identity using CLI"""
    result = subprocess.run(
        ["python", "cli.py", "process", 
         "--type", authority_type,
         identity_file],
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        print("Identity processed successfully")
        
        # Parse output
        for line in result.stdout.split('\n'):
            if "Authority saved to:" in line:
                authority_file = line.split(": ")[1]
                return authority_file
    else:
        print(f"Error: {result.stderr}")
        return None

# Use the function
authority_file = process_identity_script("identity.yaml", "credit_issuer")
```


