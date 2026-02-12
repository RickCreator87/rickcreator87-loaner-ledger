
2. Validation Modules

validation/validate_authority.py

```python
# validation/validate_authority.py
"""
Authority validation module for Richard's Credit Authority
Validates authority structures against schema and business rules
"""

import yaml
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List, Tuple, Optional
import re
from pathlib import Path

class AuthorityValidator:
    """Validate authority documents"""
    
    def __init__(self, schema_file: Optional[Path] = None):
        self.schema_file = schema_file
        self.validation_rules = self._load_validation_rules()
        
    def _load_validation_rules(self) -> Dict:
        """Load validation rules for authority structures"""
        return {
            "permission_hierarchy": {
                "perm_issue_credit": ["perm_view_credit_summary", "perm_create_request"],
                "perm_delegate_auth": ["perm_issue_credit"],
                "perm_system_config": ["perm_audit_access", "perm_compliance_override"],
            },
            "risk_based_constraints": {
                "high": {"max_credit_issuance": 50000, "requires_dual_approval": True},
                "medium": {"max_credit_issuance": 100000, "requires_dual_approval": False},
                "low": {"max_credit_issuance": 1000000, "requires_dual_approval": False},
            },
            "authority_durations": {
                "credit_issuer": {"max_days": 365},
                "system_administrator": {"max_days": 90},
                "auditor": {"max_days": 180},
                "delegate": {"max_days": 30},
            }
        }
    
    def validate(self, authority_data: Dict, identity_data: Optional[Dict] = None) -> Dict[str, Any]:
        """Validate authority against schema and business rules"""
        errors = []
        warnings = []
        
        # Basic schema validation
        errors.extend(self._validate_schema_basics(authority_data))
        
        # Business logic validation
        if identity_data:
            errors.extend(self._validate_against_identity(authority_data, identity_data))
        
        # Permission validation
        errors.extend(self._validate_permissions(authority_data))
        
        # Temporal validation
        errors.extend(self._validate_temporal_constraints(authority_data))
        
        # Monetary validation
        errors.extend(self._validate_monetary_constraints(authority_data))
        
        # Check for warnings
        warnings.extend(self._check_warnings(authority_data))
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "validation_timestamp": datetime.utcnow().isoformat() + "Z"
        }
    
    def _validate_schema_basics(self, data: Dict) -> List[str]:
        """Validate basic schema requirements"""
        errors = []
        
        # Check required fields
        required_fields = [
            "authority_id",
            "identity_reference", 
            "granted_at",
            "status",
            "permissions"
        ]
        
        for field in required_fields:
            if field not in data:
                errors.append(f"Missing required field: {field}")
        
        # Validate authority_id format
        authority_id = data.get("authority_id", "")
        if not re.match(r'^auth_[A-Za-z0-9_-]+$', authority_id):
            errors.append(f"Invalid authority_id format: {authority_id}")
        
        # Validate status
        valid_statuses = ["active", "pending", "suspended", "revoked", "expired"]
        status = data.get("status")
        if status and status not in valid_statuses:
            errors.append(f"Invalid status: {status}")
        
        # Validate granted_at format
        granted_at = data.get("granted_at")
        if granted_at:
            try:
                datetime.fromisoformat(granted_at.replace('Z', '+00:00'))
            except ValueError:
                errors.append(f"Invalid granted_at format: {granted_at}")
        
        # Validate expires_at if present
        expires_at = data.get("expires_at")
        if expires_at:
            try:
                datetime.fromisoformat(expires_at.replace('Z', '+00:00'))
            except ValueError:
                errors.append(f"Invalid expires_at format: {expires_at}")
        
        return errors
    
    def _validate_against_identity(self, authority: Dict, identity: Dict) -> List[str]:
        """Validate authority against identity data"""
        errors = []
        
        # Check if authority type matches identity type
        authority_type = authority.get("type")
        identity_type = identity.get("entity_type")
        
        type_restrictions = {
            "individual": ["credit_issuer", "delegate"],
            "business": ["credit_issuer", "credit_verifier", "delegate"],
            "financial_institution": ["credit_issuer", "credit_verifier", "system_administrator", "auditor"],
            "government_entity": ["system_administrator", "compliance_officer", "auditor"],
        }
        
        if identity_type in type_restrictions:
            allowed_types = type_restrictions[identity_type]
            if authority_type and authority_type not in allowed_types:
                errors.append(f"Identity type '{identity_type}' cannot have authority type '{authority_type}'. Allowed: {allowed_types}")
        
        # Check verification level requirements
        verified_status = identity.get("verified_status", {})
        verification_level = verified_status.get("level", "unverified")
        
        min_verification_for_type = {
            "credit_issuer": "kyc_compliant",
            "system_administrator": "fully_verified",
            "auditor": "verified",
            "compliance_officer": "fully_verified",
        }
        
        if authority_type in min_verification_for_type:
            required_level = min_verification_for_type[authority_type]
            verification_order = ["unverified", "basic", "verified", "fully_verified", "kyc_compliant"]
            
            current_index = verification_order.index(verification_level)
            required_index = verification_order.index(required_level)
            
            if current_index < required_index:
                errors.append(f"Authority type '{authority_type}' requires verification level '{required_level}' or higher. Current: '{verification_level}'")
        
        return errors
    
    def _validate_permissions(self, authority: Dict) -> List[str]:
        """Validate permission assignments"""
        errors = []
        permissions = authority.get("permissions", [])
        
        # Check for permission conflicts
        permission_conflicts = {
            "perm_issue_credit": ["perm_audit_access"],
            "perm_system_config": ["perm_delegate_auth"],
        }
        
        for perm in permissions:
            conflicts = permission_conflicts.get(perm, [])
            for conflict in conflicts:
                if conflict in permissions:
                    errors.append(f"Permission conflict: '{perm}' cannot be granted with '{conflict}'")
        
        # Check permission hierarchy
        for perm in permissions:
            prerequisites = self.validation_rules["permission_hierarchy"].get(perm, [])
            for prereq in prerequisites:
                if prereq not in permissions:
                    errors.append(f"Missing prerequisite: '{perm}' requires '{prereq}'")
        
        # Validate permission count based on authority type
        authority_type = authority.get("type")
        if authority_type == "delegate":
            if len(permissions) > 3:
                errors.append(f"Delegate authority cannot have more than 3 permissions. Found: {len(permissions)}")
        
        return errors
    
    def _validate_temporal_constraints(self, authority: Dict) -> List[str]:
        """Validate temporal constraints"""
        errors = []
        
        granted_at_str = authority.get("granted_at")
        expires_at_str = authority.get("expires_at")
        
        if granted_at_str and expires_at_str:
            try:
                granted_at = datetime.fromisoformat(granted_at_str.replace('Z', '+00:00'))
                expires_at = datetime.fromisoformat(expires_at_str.replace('Z', '+00:00'))
                
                if expires_at <= granted_at:
                    errors.append("expires_at must be after granted_at")
                
                # Check maximum duration
                authority_type = authority.get("type")
                if authority_type:
                    max_duration = self.validation_rules["authority_durations"].get(authority_type, {}).get("max_days", 365)
                    max_expiry = granted_at + timedelta(days=max_duration)
                    
                    if expires_at > max_expiry:
                        errors.append(f"Authority type '{authority_type}' cannot exceed {max_duration} days duration")
            
            except ValueError:
                pass  # Already caught by format validation
        
        # Check time constraints if specified
        scope = authority.get("scope", {})
        temporal = scope.get("temporal", {})
        valid_hours = temporal.get("valid_hours", [])
        
        for hours in valid_hours:
            start = hours.get("start")
            end = hours.get("end")
            
            if start and end:
                try:
                    start_hour, start_minute = map(int, start.split(':'))
                    end_hour, end_minute = map(int, end.split(':'))
                    
                    if start_hour > end_hour or (start_hour == end_hour and start_minute >= end_minute):
                        errors.append(f"Invalid time range: {start} to {end}")
                
                except ValueError:
                    errors.append(f"Invalid time format in valid_hours: {start} or {end}")
        
        return errors
    
    def _validate_monetary_constraints(self, authority: Dict) -> List[str]:
        """Validate monetary constraints"""
        errors = []
        
        scope = authority.get("scope", {})
        monetary_limits = scope.get("monetary_limits", {})
        
        max_credit_issuance = monetary_limits.get("max_credit_issuance", 0)
        max_transaction_amount = monetary_limits.get("max_transaction_amount", 0)
        
        # Transaction amount cannot exceed credit issuance limit
        if max_transaction_amount > max_credit_issuance:
            errors.append("max_transaction_amount cannot exceed max_credit_issuance")
        
        # Check against risk-based constraints
        constraints = authority.get("constraints", {})
        requires_dual_approval = constraints.get("requires_dual_approval", False)
        
        if max_credit_issuance > 100000 and not requires_dual_approval:
            errors.append("Credit issuance over $100,000 requires dual approval")
        
        return errors
    
    def _check_warnings(self, authority: Dict) -> List[str]:
        """Check for non-critical warnings"""
        warnings = []
        
        # Warn about permissions without constraints
        permissions = authority.get("permissions", [])
        high_risk_permissions = ["perm_issue_credit", "perm_system_config", "perm_tax_override"]
        
        for perm in permissions:
            if perm in high_risk_permissions:
                constraints = authority.get("constraints", {})
                if not constraints.get("requires_approval", True):
                    warnings.append(f"High-risk permission '{perm}' granted without approval requirement")
        
        # Warn about long durations
        granted_at_str = authority.get("granted_at")
        expires_at_str = authority.get("expires_at")
        
        if granted_at_str and expires_at_str:
            try:
                granted_at = datetime.fromisoformat(granted_at_str.replace('Z', '+00:00'))
                expires_at = datetime.fromisoformat(expires_at_str.replace('Z', '+00:00'))
                
                duration = (expires_at - granted_at).days
                if duration > 180:
                    warnings.append(f"Long authority duration: {duration} days")
            
            except ValueError:
                pass
        
        # Warn about missing geographic restrictions
        scope = authority.get("scope", {})
        geographic = scope.get("geographic", [])
        
        if not geographic:
            warnings.append("No geographic restrictions specified")
        
        return warnings
    
    def validate_file(self, file_path: Path, identity_file: Optional[Path] = None) -> Dict[str, Any]:
        """Validate an authority YAML file"""
        try:
            with open(file_path, 'r') as f:
                authority_data = yaml.safe_load(f)
            
            identity_data = None
            if identity_file and identity_file.exists():
                with open(identity_file, 'r') as f:
                    identity_data = yaml.safe_load(f)
            
            return self.validate(authority_data, identity_data)
        
        except yaml.YAMLError as e:
            return {
                "valid": False,
                "errors": [f"YAML parsing error: {str(e)}"],
                "warnings": [],
                "validation_timestamp": datetime.utcnow().isoformat() + "Z"
            }
        except Exception as e:
            return {
                "valid": False,
                "errors": [f"Validation error: {str(e)}"],
                "warnings": [],
                "validation_timestamp": datetime.utcnow().isoformat() + "Z"
            }
```