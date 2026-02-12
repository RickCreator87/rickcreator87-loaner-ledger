




Authority Operations

Create Authority from Identity

```python
from validation.validate_authority import AuthorityValidator

# Load identity
with open("identity.yaml", "r") as f:
    identity_data = yaml.safe_load(f)

# Create authority request
authority_request = {
    "authority_id": f"auth_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
    "identity_reference": identity_data["identity_id"],
    "type": "credit_issuer",
    "granted_at": datetime.utcnow().isoformat() + "Z",
    "expires_at": (datetime.utcnow() + timedelta(days=365)).isoformat() + "Z",
    "status": "active",
    "granted_by": "system",
    "permissions": ["read_self", "create_request", "issue_credit"],
    "scope": {
        "geographic": ["US"],
        "monetary_limits": {
            "max_credit_issuance": 100000,
            "max_transaction_amount": 10000
        }
    }
}

# Validate authority
validator = AuthorityValidator()
result = validator.validate(authority_request, identity_data)

if result["valid"]:
    print("Authority is valid!")
else:
    print(f"Validation errors: {result['errors']}")
```