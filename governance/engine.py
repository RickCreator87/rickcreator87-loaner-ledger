3. Governance Engine

governance/engine.py

```python
# governance/engine.py
"""
Governance engine for Richard's Credit Authority
Applies business rules and policies to authority and identity decisions
"""

import json
import yaml
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class RuleType(Enum):
    """Types of governance rules"""
    VALIDATION = "validation"
    APPROVAL = "approval"
    ESCALATION = "escalation"
    COMPLIANCE = "compliance"
    RISK = "risk"
    TAX = "tax"

class RuleSeverity(Enum):
    """Rule severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

@dataclass
class RuleResult:
    """Result of applying a governance rule"""
    rule_id: str
    rule_type: RuleType
    severity: RuleSeverity
    passed: bool
    message: str
    details: Dict[str, Any]
    timestamp: str

@dataclass
class GovernanceDecision:
    """Final governance decision"""
    decision: str  # "approved", "rejected", "requires_review", "needs_escalation"
    reasons: List[str]
    required_actions: List[str]
    rule_results: List[RuleResult]
    timestamp: str

class GovernanceEngine:
    """Main governance engine that applies rules and policies"""
    
    def __init__(self, rules_file: Optional[Path] = None):
        self.rules_file = rules_file or Path(__file__).parent / "rules.json"
        self.rules = self._load_rules()
        self.rule_processors = self._register_rule_processors()
        
    def _load_rules(self) -> Dict:
        """Load governance rules from file"""
        default_rules = {
            "version": "1.0.0",
            "rules": {
                "validation": [],
                "approval": [],
                "escalation": [],
                "compliance": [],
                "risk": [],
                "tax": []
            }
        }
        
        try:
            if self.rules_file.exists():
                with open(self.rules_file, 'r') as f:
                    loaded_rules = json.load(f)
                    # Merge with defaults
                    default_rules.update(loaded_rules)
            
            return default_rules
        
        except Exception as e:
            logger.error(f"Error loading governance rules: {e}")
            return default_rules
    
    def _register_rule_processors(self) -> Dict[str, Callable]:
        """Register rule processor functions"""
        return {
            "validate_identity_verification": self._validate_identity_verification,
            "check_authority_duration": self._check_authority_duration,
            "validate_permission_hierarchy": self._validate_permission_hierarchy,
            "check_risk_thresholds": self._check_risk_thresholds,
            "validate_tax_compliance": self._validate_tax_compliance,
            "check_geographic_restrictions": self._check_geographic_restrictions,
            "validate_monetary_limits": self._validate_monetary_limits,
            "check_delegation_depth": self._check_delegation_depth,
            "validate_audit_requirements": self._validate_audit_requirements,
            "check_conflict_of_interest": self._check_conflict_of_interest,
        }
    
    def evaluate_authority_request(self, 
                                  authority_request: Dict,
                                  identity_data: Dict,
                                  context: Optional[Dict] = None) -> GovernanceDecision:
        """
        Evaluate an authority request against all governance rules
        
        Args:
            authority_request: The authority being requested
            identity_data: The identity requesting the authority
            context: Additional context for evaluation
        
        Returns:
            GovernanceDecision with the evaluation results
        """
        rule_results = []
        context = context or {}
        
        # Apply all rule categories
        for rule_type in RuleType:
            category_rules = self.rules["rules"].get(rule_type.value, [])
            for rule in category_rules:
                if rule.get("enabled", True):
                    result = self._apply_rule(rule, authority_request, identity_data, context)
                    rule_results.append(result)
        
        # Make final decision based on rule results
        decision = self._make_decision(rule_results)
        
        return GovernanceDecision(
            decision=decision["decision"],
            reasons=decision["reasons"],
            required_actions=decision["actions"],
            rule_results=rule_results,
            timestamp=datetime.utcnow().isoformat() + "Z"
        )
    
    def _apply_rule(self, 
                   rule: Dict,
                   authority_request: Dict,
                   identity_data: Dict,
                   context: Dict) -> RuleResult:
        """Apply a single rule"""
        rule_id = rule.get("id", "unknown")
        rule_type = RuleType(rule.get("type", "validation"))
        processor_name = rule.get("processor")
        
        try:
            if processor_name and processor_name in self.rule_processors:
                processor = self.rule_processors[processor_name]
                result = processor(authority_request, identity_data, context, rule.get("parameters", {}))
                
                return RuleResult(
                    rule_id=rule_id,
                    rule_type=rule_type,
                    severity=RuleSeverity(result.get("severity", "info")),
                    passed=result.get("passed", True),
                    message=result.get("message", ""),
                    details=result.get("details", {}),
                    timestamp=datetime.utcnow().isoformat() + "Z"
                )
            else:
                # Default rule application
                return RuleResult(
                    rule_id=rule_id,
                    rule_type=rule_type,
                    severity=RuleSeverity.WARNING,
                    passed=True,
                    message=f"No processor for rule: {rule_id}",
                    details={},
                    timestamp=datetime.utcnow().isoformat() + "Z"
                )
        
        except Exception as e:
            logger.error(f"Error applying rule {rule_id}: {e}")
            return RuleResult(
                rule_id=rule_id,
                rule_type=rule_type,
                severity=RuleSeverity.ERROR,
                passed=False,
                message=f"Rule application error: {str(e)}",
                details={"error": str(e)},
                timestamp=datetime.utcnow().isoformat() + "Z"
            )
    
    def _validate_identity_verification(self, 
                                       authority_request: Dict,
                                       identity_data: Dict,
                                       context: Dict,
                                       parameters: Dict) -> Dict[str, Any]:
        """Validate identity verification level"""
        required_level = parameters.get("minimum_verification_level", "verified")
        current_level = identity_data.get("verified_status", {}).get("level", "unverified")
        
        verification_order = ["unverified", "basic", "verified", "fully_verified", "kyc_compliant"]
        
        current_index = verification_order.index(current_level)
        required_index = verification_order.index(required_level)
        
        passed = current_index >= required_index
        
        return {
            "passed": passed,
            "severity": "error" if not passed else "info",
            "message": f"Verification level check: {current_level} {'>=' if passed else '<'} {required_level}",
            "details": {
                "current_level": current_level,
                "required_level": required_level,
                "verification_order": verification_order
            }
        }
    
    def _check_authority_duration(self,
                                 authority_request: Dict,
                                 identity_data: Dict,
                                 context: Dict,
                                 parameters: Dict) -> Dict[str, Any]:
        """Check authority duration limits"""
        max_days = parameters.get("maximum_days", 365)
        
        granted_at_str = authority_request.get("granted_at")
        expires_at_str = authority_request.get("expires_at")
        
        if not granted_at_str or not expires_at_str:
            return {
                "passed": False,
                "severity": "error",
                "message": "Missing granted_at or expires_at",
                "details": {}
            }
        
        try:
            granted_at = datetime.fromisoformat(granted_at_str.replace('Z', '+00:00'))
            expires_at = datetime.fromisoformat(expires_at_str.replace('Z', '+00:00'))
            
            duration_days = (expires_at - granted_at).days
            passed = duration_days <= max_days
            
            return {
                "passed": passed,
                "severity": "error" if not passed else "info",
                "message": f"Authority duration: {duration_days} days (max: {max_days})",
                "details": {
                    "duration_days": duration_days,
                    "maximum_days": max_days,
                    "granted_at": granted_at_str,
                    "expires_at": expires_at_str
                }
            }
        
        except ValueError:
            return {
                "passed": False,
                "severity": "error",
                "message": "Invalid date format",
                "details": {}
            }
    
    def _validate_permission_hierarchy(self,
                                      authority_request: Dict,
                                      identity_data: Dict,
                                      context: Dict,
                                      parameters: Dict) -> Dict[str, Any]:
        """Validate permission hierarchy"""
        permissions = authority_request.get("permissions", [])
        hierarchy = parameters.get("hierarchy", {})
        
        errors = []
        
        for permission, prerequisites in hierarchy.items():
            if permission in permissions:
                for prereq in prerequisites:
                    if prereq not in permissions:
                        errors.append(f"{permission} requires {prereq}")
        
        passed = len(errors) == 0
        
        return {
            "passed": passed,
            "severity": "error" if not passed else "info",
            "message": f"Permission hierarchy check: {len(errors)} violations" if errors else "Permission hierarchy OK",
            "details": {
                "errors": errors,
                "hierarchy": hierarchy,
                "permissions": permissions
            }
        }
    
    def _check_risk_thresholds(self,
                              authority_request: Dict,
                              identity_data: Dict,
                              context: Dict,
                              parameters: Dict) -> Dict[str, Any]:
        """Check risk thresholds"""
        risk_level = identity_data.get("credit_authority_tags", {}).get("risk_level", "unknown")
        
        thresholds = parameters.get("thresholds", {})
        max_amounts = thresholds.get(risk_level, {})
        
        scope = authority_request.get("scope", {})
        monetary_limits = scope.get("monetary_limits", {})
        
        requested_max = monetary_limits.get("max_credit_issuance", 0)
        allowed_max = max_amounts.get("max_credit_issuance", 0)
        
        passed = requested_max <= allowed_max
        
        return {
            "passed": passed,
            "severity": "critical" if not passed else "info",
            "message": f"Risk threshold check: ${requested_max:,} <= ${allowed_max:,} for risk level {risk_level}",
            "details": {
                "risk_level": risk_level,
                "requested_max": requested_max,
                "allowed_max": allowed_max,
                "thresholds": thresholds
            }
        }
    
    def _validate_tax_compliance(self,
                                authority_request: Dict,
                                identity_data: Dict,
                                context: Dict,
                                parameters: Dict) -> Dict[str, Any]:
        """Validate tax compliance"""
        jurisdictions = authority_request.get("scope", {}).get("geographic", [])
        tax_implications = authority_request.get("tax_implications", {})
        
        withholding_required = tax_implications.get("withholding_required", False)
        
        # Check if US jurisdiction requires withholding
        us_jurisdiction = any(j.startswith("US") for j in jurisdictions)
        
        if us_jurisdiction and not withholding_required:
            return {
                "passed": False,
                "severity": "warning",
                "message": "US jurisdiction detected but no withholding specified",
                "details": {
                    "jurisdictions": jurisdictions,
                    "withholding_required": withholding_required
                }
            }
        
        return {
            "passed": True,
            "severity": "info",
            "message": "Tax compliance check passed",
            "details": {
                "jurisdictions": jurisdictions,
                "withholding_required": withholding_required
            }
        }
    
    def _check_geographic_restrictions(self,
                                      authority_request: Dict,
                                      identity_data: Dict,
                                      context: Dict,
                                      parameters: Dict) -> Dict[str, Any]:
        """Check geographic restrictions"""
        restricted_countries = parameters.get("restricted_countries", [])
        scope = authority_request.get("scope", {})
        geographic = scope.get("geographic", [])
        
        violations = [country for country in geographic if country in restricted_countries]
        passed = len(violations) == 0
        
        return {
            "passed": passed,
            "severity": "error" if not passed else "info",
            "message": f"Geographic restrictions: {len(violations)} violations" if violations else "Geographic restrictions OK",
            "details": {
                "violations": violations,
                "geographic": geographic,
                "restricted_countries": restricted_countries
            }
        }
    
    def _validate_monetary_limits(self,
                                 authority_request: Dict,
                                 identity_data: Dict,
                                 context: Dict,
                                 parameters: Dict) -> Dict[str, Any]:
        """Validate monetary limits"""
        scope = authority_request.get("scope", {})
        monetary_limits = scope.get("monetary_limits", {})
        
        max_credit = monetary_limits.get("max_credit_issuance", 0)
        max_transaction = monetary_limits.get("max_transaction_amount", 0)
        
        # Transaction limit cannot exceed credit limit
        passed = max_transaction <= max_credit
        
        return {
            "passed": passed,
            "severity": "error" if not passed else "info",
            "message": f"Monetary limits: ${max_transaction:,} <= ${max_credit:,}",
            "details": {
                "max_credit_issuance": max_credit,
                "max_transaction_amount": max_transaction
            }
        }
    
    def _check_delegation_depth(self,
                               authority_request: Dict,
                               identity_data: Dict,
                               context: Dict,
                               parameters: Dict) -> Dict[str, Any]:
        """Check delegation depth"""
        max_depth = parameters.get("maximum_depth", 3)
        
        delegation_chain = authority_request.get("delegation_chain", [])
        current_depth = len(delegation_chain)
        
        passed = current_depth <= max_depth
        
        return {
            "passed": passed,
            "severity": "warning" if not passed else "info",
            "message": f"Delegation depth: {current_depth} (max: {max_depth})",
            "details": {
                "current_depth": current_depth,
                "maximum_depth": max_depth,
                "delegation_chain": delegation_chain
            }
        }
    
    def _validate_audit_requirements(self,
                                    authority_request: Dict,
                                    identity_data: Dict,
                                    context: Dict,
                                    parameters: Dict) -> Dict[str, Any]:
        """Validate audit requirements"""
        constraints = authority_request.get("constraints", {})
        audit_frequency = constraints.get("audit_frequency", "monthly")
        
        required_frequency = parameters.get("minimum_frequency", "monthly")
        
        frequency_order = ["daily", "weekly", "monthly", "quarterly", "annually"]
        
        try:
            current_index = frequency_order.index(audit_frequency)
            required_index = frequency_order.index(required_frequency)
            
            passed = current_index <= required_index  # More frequent is better
            
            return {
                "passed": passed,
                "severity": "warning" if not passed else "info",
                "message": f"Audit frequency: {audit_frequency} (required: {required_frequency})",
                "details": {
                    "current_frequency": audit_frequency,
                    "required_frequency": required_frequency,
                    "frequency_order": frequency_order
                }
            }
        
        except ValueError:
            return {
                "passed": False,
                "severity": "error",
                "message": f"Invalid audit frequency: {audit_frequency}",
                "details": {}
            }
    
    def _check_conflict_of_interest(self,
                                   authority_request: Dict,
                                   identity_data: Dict,
                                   context: Dict,
                                   parameters: Dict) -> Dict[str, Any]:
        """Check for conflicts of interest"""
        # This is a simplified example - in reality, this would check against
        # a database of relationships and previous transactions
        
        authority_type = authority_request.get("type")
        identity_id = identity_data.get("identity_id")
        
        # Example: System administrators cannot have certain financial authorities
        if authority_type == "system_administrator":
            financial_permissions = ["perm_issue_credit", "perm_revoke_credit"]
            permissions = authority_request.get("permissions", [])
            
            conflicts = [p for p in permissions if p in financial_permissions]
            passed = len(conflicts) == 0
            
            return {
                "passed": passed,
                "severity": "critical" if not passed else "info",
                "message": f"Conflict of interest check: {len(conflicts)} conflicts found" if conflicts else "No conflicts detected",
                "details": {
                    "conflicts": conflicts,
                    "authority_type": authority_type,
                    "financial_permissions": financial_permissions
                }
            }
   