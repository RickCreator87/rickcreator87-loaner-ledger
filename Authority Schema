Authority Schema

Overview

The Authority schema defines permissions granted to identities, including scope, constraints, and validity periods.

Schema Location

· File: schemas/authority.schema.yaml
· JSON Schema ID: https://github.com/RickCreator87/richards-credit-authority/schemas/authority.schema.yaml

Structure

```yaml
authority_id: string(pattern)           # Pattern: ^auth_[A-Za-z0-9_-]+$
identity_reference: string              # Reference to identity
type: string(enum)                      # Authority type
granted_at: string(date-time)           # Grant timestamp
expires_at: string(date-time)           # Expiration timestamp
status: string(enum)                    # Current status
granted_by: string                      # Grantor reference
permissions: array(string)              # Granted permissions
scope: object                           # Authority scope
constraints: object                     # Operational constraints
delegation_chain: array                 # Delegation history
audit_trail: array                      # Audit events
tax_implications: object                # Tax considerations
metadata: object                        # Metadata
```