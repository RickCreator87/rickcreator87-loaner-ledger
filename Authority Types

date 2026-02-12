Authority Types

Type Description Default Duration
credit_issuer Can issue credit 365 days
credit_verifier Can verify credit requests 180 days
system_administrator System management 90 days
auditor Audit access 180 days
delegate Delegated authority 30 days
compliance_officer Compliance oversight 365 days

Status Values

Status Description
active Authority is active
pending Awaiting approval
suspended Temporarily suspended
revoked Permanently revoked
expired Automatically expired

Permission Categories

Permissions are grouped into categories for easier management:

1. Identity Management: read_self, update_contact, verify_identity
2. Credit Operations: view_credit_summary, create_request, issue_credit
3. Financial Transactions: initiate_transfer, approve_transfer
4. System Administration: system_config, user_management
5. Audit & Compliance: audit_access, compliance_override
6. Tax Operations: tax_calculation, tax_override

Scope Definition

The scope object defines where and how authority can be exercised:

```yaml
scope:
  geographic: ["US", "CA"]              # ISO country codes
  monetary_limits:
    max_credit_issuance: 1000000        # Maximum total credit
    max_daily_transactions: 100         # Daily transaction limit
    max_transaction_amount: 50000       # Per-transaction limit
  temporal:
    valid_hours:                        # Time restrictions
      - day: "mon"
        start: "09:00"
        end: "17:00"
    timezone: "America/Denver"
```

Example

```yaml
authority_id: "auth_20240115_143000_abc123"
identity_reference: "550e8400-e29b-41d4-a716-446655440000"
type: "credit_issuer"
granted_at: "2024-01-15T14:30:00Z"
expires_at: "2025-01-15T14:30:00Z"
status: "active"
permissions:
  - "issue_credit"
  - "view_credit_summary"
scope:
  geographic: ["US"]
  monetary_limits:
    max_credit_issuance: 1000000
constraints:
  requires_approval: false
  audit_frequency: "monthly"
```