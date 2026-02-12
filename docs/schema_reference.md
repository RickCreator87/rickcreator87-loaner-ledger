
### `docs/schema_reference.md`

```markdown
# Schema Reference
## Richard's Credit Authority - Data Structure Definitions

Version: 1.0.0  
Last Updated: 2026-01-15  











## Table of Contents

1. [Introduction](#introduction)
2. [Identity Schema](#identity-schema)
3. [Authority Schema](#authority-schema)
4. [Permission Schema](#permission-schema)
5. [Tax Schema](#tax-schema)
6. [Validation Rules](#validation-rules)
7. [Examples](#examples)
8. [Field Reference](#field-reference)

## Introduction

This document provides detailed reference information for all schemas used in Richard's Credit Authority. Each schema defines the structure and constraints for a specific type of data in the system.

All schemas are defined using JSON Schema Draft 7 and can be validated programmatically.

## Identity Schema

### Overview
The Identity schema defines digital identities for individuals, businesses, and other entities.

### Schema Location
- File: `schemas/identity.schema.yaml`
- JSON Schema ID: `https://github.com/RickCreator87/richards-credit-authority/schemas/identity.schema.yaml`

### Structure

```yaml
identity_id: string(uuid)                 # Unique identifier
entity_type: string(enum)                # Type of entity
personal_info: object                    # Personal information (individuals)
government_ids: array                    # Government-issued IDs
contact_info: object                     # Contact information
verified_status: object                  # Verification status
credit_authority_tags: object            # System-specific tags
metadata: object                         # Metadata
external_references: array               # Links to external systems