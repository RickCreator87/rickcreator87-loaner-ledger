# Permission Matrix
## Richard's Credit Authority - Access Control Reference

Version: 1.0.0  
Last Updated: 2026-01-15  

---
~~~


- [ ] added


~~~
## Overview

This document defines all permissions available in the Credit Authority system, their risk levels, prerequisites, and usage guidelines.

## Permission Categories

### 1. Identity Management (`category: identity_management`)

| Permission ID | Name | Description | Risk Level | Prerequisites |
|--------------|------|-------------|------------|---------------|
| `perm_read_self` | Read Own Identity | View own identity information | Low | None |
| `perm_update_contact` | Update Contact Info | Update own contact information | Low | `perm_read_self` |
| `perm_verify_identity` | Verify Identity | Initiate identity verification | Medium | `perm_update_contact` |
| `perm_view_others` | View Other Identities | View other users' identity info | High | `perm_verify_identity` |

### 2. Credit Operations (`category: credit_operations`)

| Permission ID | Name | Description | Risk Level | Prerequisites |
|--------------|------|-------------|------------|---------------|
| `perm_view_credit_summary` | View Credit Summary | View credit history and summaries | Low | `perm_read_self` |
| `perm_create_request` | Create Credit Request | Submit new credit requests | Medium | `perm_view_credit_summary` |
| `perm_issue_credit` | Issue Credit | Approve and issue new credit | High | `perm_create_request`, `perm_verify_identity` |
| `perm_revoke_credit` | Revoke Credit | Revoke existing credit lines | Critical | `perm_issue_credit` |
| `perm_adjust_limits` | Adjust Credit Limits | Modify credit limits | High | `perm_issue_credit` |

### 3. Financial Transactions (`category: financial_transactions`)

| Permission ID | Name | Description | Risk Level | Prerequisites |
|--------------|------|-------------|------------|---------------|
| `perm_initiate_transfer` | Initiate Transfer | Start fund transfers | Medium | `perm_create_request` |
| `perm_approve_transfer` | Approve Transfer | Approve pending transfers | High | `perm_initiate_transfer` |
| `perm_reverse_transaction` | Reverse Transaction | Reverse completed transactions | Critical | `perm_approve_transfer` |
| `perm_bulk_operations` | Bulk Operations | Perform bulk transactions | High | `perm_approve_transfer` |

### 4. System Administration (`category: system_administration`)

| Permission ID | Name | Description | Risk Level | Prerequisites |
|--------------|------|-------------|------------|---------------|
| `perm_system_config` | System Configuration | Modify system settings | Critical | `perm_audit_access` |
| `perm_user_management` | User Management | Create and manage users | High | `perm_verify_identity` |
| `perm_role_management` | Role Management | Define and assign roles | Critical | `perm_user_management` |
| `perm_backup_restore` | Backup & Restore | Perform system backups | Critical | `perm_system_config` |

### 5. Audit & Compliance (`category: audit_compliance`)

| Permission ID | Name | Description | Risk Level | Prerequisites |
|--------------|------|-------------|------------|---------------|
| `perm_audit_access` | Audit Access | View audit logs | Medium | `perm_view_others` |
| `perm_export_audit` | Export Audit Data | Export audit logs for analysis | High | `perm_audit_access` |
| `perm_compliance_override` | Compliance Override | Override compliance rules | Critical | `perm_audit_access` |
| `perm_generate_reports` | Generate Reports | Create compliance reports | Medium | `perm_audit_access` |

### 6. Tax Operations (`category: tax_operations`)

| Permission ID | Name | Description | Risk Level | Prerequisites |
|--------------|------|-------------|------------|---------------|
| `perm_tax_calculation` | Tax Calculation | Calculate tax obligations | Medium | `perm_create_request` |
| `perm_tax_override` | Tax Override | Override tax calculations | Critical | `perm_tax_calculation` |
| `perm_tax_reporting` | Tax Reporting | Generate tax reports | High | `perm_tax_calculation` |
| `perm_withholding_management` | Withholding Management | Manage tax withholding | High | `perm_tax_calculation` |

### 7. Delegation Management (`category: delegation_management`)

| Permission ID | Name | Description | Risk Level | Prerequisites |
|--------------|------|-------------|------------|---------------|
| `perm_delegate_auth` | Delegate Authority | Delegate permissions to others | High | `perm_issue_credit` |
| `perm_revoke_delegation` | Revoke Delegation | Revoke delegated authority | Critical | `perm_delegate_auth` |
| `perm_view_delegations` | View Delegations | View delegation chains | Medium | `perm_read_self` |

## Risk Level Definitions

### Low Risk
- **Impact**: Minimal financial or operational impact
- **Approval**: Automated or self-service
- **Audit**: Quarterly sampling
- **Examples**: View own data, update contact info

### Medium Risk
- **Impact**: Moderate financial impact (up to $10,000)
- **Approval**: Supervisor approval required
- **Audit**: Monthly review
- **Examples**: Create credit requests, initiate transfers

### High Risk
- **Impact**: Significant financial impact (up to $100,000)
- **Approval**: Manager + Compliance approval
- **Audit**: Weekly review
- **Examples**: Issue credit, approve transfers, bulk operations

### Critical Risk
- **Impact**: Major financial or systemic impact ($100,000+)
- **Approval**: Director + Legal approval
- **Audit**: Daily monitoring
- **Examples**: System configuration, compliance overrides, tax overrides

## Permission Combinations

### Standard User
```yaml
permissions:
  - perm_read_self
  - perm_update_contact
  - perm_view_credit_summary
  - perm_create_request