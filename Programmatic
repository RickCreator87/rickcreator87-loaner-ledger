
Programmatic

```python
from validation.validate_identity import IdentityValidator

validator = IdentityValidator()
result = validator.validate_file("identity.yaml")

if result["valid"]:
    print("Validation passed")
else:
    print(f"Errors: {result['errors']}")
```

Schema Files

The schema files themselves can be used for validation:

```python
import jsonschema
import yaml

# Load schema
with open("schemas/identity.schema.yaml", "r") as f:
    schema = yaml.safe_load(f)

# Load data
with open("identity.yaml", "r") as f:
    data = yaml.safe_load(f)

# Validate
jsonschema.validate(data, schema)
```