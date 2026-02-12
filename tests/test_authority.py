tests/test_authority.py

```python
# tests/test_authority.py
"""
Unit tests for authority validation in Richard's Credit Authority
"""

import unittest
import tempfile
import yaml
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from validation.validate_authority import AuthorityValidator

class TestAuthorityValidation(unittest.TestCase):
    """Test authority validation functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.validator = AuthorityValidator()
        self.valid_authority = {
            "authority_id": "auth_20240115_143000_abc123",
            "identity_reference": "550e8400-e29b-41d4-a716-446655440000",
            "type": "credit_issuer",
            "granted_at": "2026-01-15T14:30:00Z",
            "expires_at": "2027-01-15T14:30:00Z",
            "status": "active",
            "granted_by": "system",
            "permissions": ["view_credit_summary", "create_request", "issue_credit"],
            "scope": {
                "geographic": ["US", "CA"],
                "monetary_limits": {
                    "max_credit_issuance": 1000000,
                    "max_daily_transactions": 100,
                    "max_transaction_amount": 50000
                }
            },
            "constraints": {
                "requires_approval": False,
                "audit_frequency": "monthly"
            }
        }
        
        self.valid_identity = {
            "identity_id": "550e8400-e29b-41d4-a716-446655440000",
            "entity_type": "individual",
            "verified_status": {
                "level": "kyc_compliant"
            },
            "credit_authority_tags": {
                "risk_level": "low"
            }
        }
    
    def test_valid_authority(self):
        """Test validation of a valid authority"""
        result = self.validator.validate(self.valid_authority, self.valid_identity)
        self.assertTrue(result["valid"])
        self.assertEqual(len(result["errors"]), 0)
    
    def test_missing_required_fields(self):
        """Test validation with missing required fields"""
        invalid_authority = self.valid_authority.copy()
        del invalid_authority["authority_id"]
        
        result = self.validator.validate(invalid_authority, self.valid_identity)
        self.assertFalse(result["valid"])
        self.assertIn("Missing required field: authority_id", result["errors"])
    
    def test_invalid_authority_id_format(self):
        """Test validation with invalid authority_id format"""
        invalid_authority = self.valid_authority.copy()
        invalid_authority["authority_id"] = "invalid_format"
        
        result = self.validator.validate(invalid_authority, self.valid_identity)
        self.assertFalse(result["valid"])
        self.assertIn("Invalid authority_id format", result["errors"][0])
    
    def test_invalid_status(self):
        """Test validation with invalid status"""
        invalid_authority = self.valid_authority.copy()
        invalid_authority["status"] = "invalid_status"
        
        result = self.validator.validate(invalid_authority, self.valid_identity)
        self.assertFalse(result["valid"])
        self.assertIn("Invalid status", result["errors"][0])
    
    def test_invalid_date_format(self):
        """Test validation with invalid date format"""
        invalid_authority = self.valid_authority.copy()
        invalid_authority["granted_at"] = "2026-01-15 14:30:00"  # Missing TZ
        
        result = self.validator.validate(invalid_authority, self.valid_identity)
        self.assertFalse(result["valid"])
        self.assertIn("Invalid granted_at format", result["errors"][0])
    
    def test_expires_before_granted(self):
        """Test that expires_at must be after granted_at"""
        invalid_authority = self.valid_authority.copy()
        invalid_authority["granted_at"] = "2025-01-15T14:30:00Z"
        invalid_authority["expires_at"] = "2026-01-15T14:30:00Z"
        
        result = self.validator.validate(invalid_authority, self.valid_identity)
        self.assertFalse(result["valid"])
        self.assertIn("expires_at must be after granted_at", result["errors"])
    
    def test_permission_conflicts(self):
        """Test permission conflict validation"""
        invalid_authority = self.valid_authority.copy()
        invalid_authority["permissions"] = ["perm_issue_credit", "perm_audit_access"]
        
        result = self.validator.validate(invalid_authority, self.valid_identity)
        self.assertFalse(result["valid"])
        self.assertIn("Permission conflict", result["errors"][0])
    
    def test_permission_prerequisites(self):
        """Test permission prerequisite validation"""
        invalid_authority = self.valid_authority.copy()
        invalid_authority["permissions"] = ["perm_issue_credit"]  # Missing prerequisites
        
        result = self.validator.validate(invalid_authority, self.valid_identity)
        self.assertFalse(result["valid"])
        self.assertIn("Missing prerequisite", result["errors"][0])
    
    def test_delegate_permission_limit(self):
        """Test delegate permission count limit"""
        invalid_authority = self.valid_authority.copy()
        invalid_authority["type"] = "delegate"
        invalid_authority["permissions"] = ["perm1", "perm2", "perm3", "perm4"]  # 4 permissions
        
        result = self.validator.validate(invalid_authority, self.valid_identity)
        self.assertFalse(result["valid"])
        self.assertIn("Delegate authority cannot have more than 3 permissions", result["errors"][0])
    
    def test_transaction_exceeds_credit_limit(self):
        """Test that transaction amount cannot exceed credit limit"""
        invalid_authority = self.valid_authority.copy()
        invalid_authority["scope"]["monetary_limits"]["max_transaction_amount"] = 2000000
        
        result = self.validator.validate(invalid_authority, self.valid_identity)
        self.assertFalse(result["valid"])
        self.assertIn("max_transaction_amount cannot exceed max_credit_issuance", result["errors"][0])
    
    def test_high_credit_requires_dual_approval(self):
        """Test that high credit amounts require dual approval"""
        invalid_authority = self.valid_authority.copy()
        invalid_authority["scope"]["monetary_limits"]["max_credit_issuance"] = 200000
        invalid_authority["constraints"]["requires_dual_approval"] = False
        
        result = self.validator.validate(invalid_authority, self.valid_identity)
        self.assertFalse(result["valid"])
        self.assertIn("Credit issuance over $100,000 requires dual approval", result["errors"][0])
    
    def test_identity_authority_type_compatibility(self):
        """Test authority type compatibility with identity type"""
        invalid_identity = self.valid_identity.copy()
        invalid_identity["entity_type"] = "individual"
        
        invalid_authority = self.valid_authority.copy()
        invalid_authority["type"] = "system_administrator"  # Individuals can't be system admins
        
        result = self.validator.validate(invalid_authority, invalid_identity)
        self.assertFalse(result["valid"])
        self.assertIn("cannot have authority type", result["errors"][0])
    
    def test_verification_level_requirement(self):
        """Test verification level requirements for authority types"""
        invalid_identity = self.valid_identity.copy()
        invalid_identity["verified_status"]["level"] = "basic"
        
        result = self.validator.validate(self.valid_authority, invalid_identity)
        self.assertFalse(result["valid"])
        self.assertIn("requires verification level", result["errors"][0])
    
    def test_warnings_for_long_duration(self):
        """Test warnings for long authority durations"""
        authority_with_long_duration = self.valid_authority.copy()
        authority_with_long_duration["granted_at"] = "2026-01-01T00:00:00Z"
        authority_with_long_duration["expires_at"] = "2027-12-31T23:59:59Z"  # ~2 years
        
        result = self.validator.validate(authority_with_long_duration, self.valid_identity)
        self.assertTrue(result["valid"])
        self.assertGreater(len(result["warnings"]), 0)
        self.assertIn("Long authority duration", result["warnings"][0])
    
    def test_warnings_for_missing_geographic_restrictions(self):
        """Test warnings for missing geographic restrictions"""
        authority_no_geo = self.valid_authority.copy()
        authority_no_geo["scope"]["geographic"] = []
        
        result = self.validator.validate(authority_no_geo, self.valid_identity)
        self.assertTrue(result["valid"])
        self.assertIn("No geographic restrictions specified", result["warnings"][0])
    
    def test_file_validation(self):
        """Test validation from YAML file"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(self.valid_authority, f)
            temp_file = Path(f.name)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f2:
            yaml.dump(self.valid_identity, f2)
            temp_identity_file = Path(f2.name)
        
        try:
            result = self.validator.validate_file(temp_file, temp_identity_file)
            self.assertTrue(result["valid"])
        finally:
            temp_file.unlink()
            temp_identity_file.unlink()

if __name__ == '__main__':
    unittest.main()
```

tests/test_tax_logic.py

```python
# tests/test_tax_logic.py
"""

Unit tests for tax logic in Richard's Credit Authority
"""

import unittest
from decimal import Decimal
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from tax.federal.rules import FederalTaxRules
from tax.state.colorado.rules import ColoradoTaxRules

class TestFederalTaxRules(unittest.TestCase):
    """Test federal tax rules functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.tax_rules = FederalTaxRules()
    
    def test_income_tax_calculation(self):
        """Test income tax calculation"""
        # Test with various income levels
        test_cases = [
            (Decimal('50000'), "single", 2024, 4167.50),  # Approximate expected tax
            (Decimal('100000'), "single", 2024, 14704.50),  # Approximate expected tax
            (Decimal('0'), "single", 2024, 0),
        ]
        
        for income, status, year, expected_tax in test_cases:
            with self.subTest(income=income, status=status, year=year):
                result = self.tax_rules.calculate_income_tax(income, status, year)
                self.assertAlmostEqual(result["total_tax"], expected_tax, delta=10)
    
    def test_withholding_calculation(self):
        """Test withholding tax calculation"""
        # Test interest payments with tax ID
        result = self.tax_rules.calculate_withholding(
            payment_amount=Decimal('1000'),
            payment_type="interest",
            recipient_type="individual",
            tax_id_provided=True
        )
        self.assertFalse(result["withholding_required"])
        self.assertEqual(result["withholding_amount"], 0)
        
        # Test interest payments without tax ID
        result = self.tax_rules.calculate_withholding(
            payment_amount=Decimal('1000'),
            payment_type="interest",
            recipient_type="individual",
            tax_id_provided=False
        )
        self.assertTrue(result["withholding_required"])
        self.assertAlmostEqual(result["withholding_amount"], 240.0, delta=0.01)  # 24% of 1000
        
        # Test supplemental payments
        result = self.tax_rules.calculate_withholding(
            payment_amount=Decimal('5000'),
            payment_type="supplemental",
            recipient_type="individual",
            tax_id_provided=True
        )
        self.assertTrue(result["withholding_required"])
        self.assertAlmostEqual(result["withholding_amount"], 1100.0, delta=0.01)  # 22% of 5000
    
    def test_form_requirements(self):
        """Test form requirement determination"""
        # Test 1099-INT requirement
        forms = self.tax_rules.determine_form_requirements(
            payment_type="interest",
            payment_amount=Decimal('100'),
            recipient_type="individual",
            cumulative_annual=Decimal('0')
        )
        self.assertIn("1099-INT", forms)
        self.assertIn("W-9", forms)
        
        # Test 1099-NEC requirement
        forms = self.tax_rules.determine_form_requirements(
            payment_type="nonemployee_compensation",
            payment_amount=Decimal('1000'),
            recipient_type="individual",
            cumulative_annual=Decimal('0')
        )
        self.assertIn("1099-NEC", forms)
        
        # Test no form requirement for small amounts
        forms = self.tax_rules.determine_form_requirements(
            payment_type="interest",
            payment_amount=Decimal('5'),
            recipient_type="individual",
            cumulative_annual=Decimal('0')
        )
        self.assertEqual(len(forms), 0)
    
    def test_penalty_calculations(self):
        """Test tax penalty calculations"""
        # Test failure to file penalty
        result = self.tax_rules.calculate_penalties(
            violation_type="failure_to_file",
            amount_owed=Decimal('10000'),
            days_late=90,  # 3 months
            is_willful=False
        )
        self.assertGreater(result["total_penalty"], 0)
        self.assertAlmostEqual(result["total_penalty"], 1500.0, delta=10)  # 5% per month * 3 months
        
        # Test willful violation penalty
        result = self.tax_rules.calculate_penalties(
            violation_type="failure_to_file",
            amount_owed=Decimal('10000'),
            days_late=90,
            is_willful=True
        )
        self.assertGreater(result["total_penalty"], 7500)  # 75% willful penalty
    
    def test_tax_id_validation(self):
        """Test tax ID validation"""
        # Test valid SSN
        result = self.tax_rules.validate_tax_id("123-45-6789", "ssn")
        self.assertTrue(result["valid"])
        
        # Test invalid SSN format
        result = self.tax_rules.validate_tax_id("123456789", "ssn")
        self.assertFalse(result["valid"])
        
        # Test valid EIN
        result = self.tax_rules.validate_tax_id("12-3456789", "ein")
        self.assertTrue(result["valid"])

class TestColoradoTaxRules(unittest.TestCase):
    """Test Colorado tax rules functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.tax_rules = ColoradoTaxRules()
    
    def test_income_tax_calculation(self):
        """Test Colorado income tax calculation"""
        # Test with 2024 flat rate
        result = self.tax_rules.calculate_income_tax(
            taxable_income=Decimal('50000'),
            filing_status="single",
            year=2024
        )
        
        expected_tax = 50000 * Decimal('0.0440')  # 4.4% flat rate
        self.assertAlmostEqual(result["tax_amount"], float(expected_tax), delta=0.01)
        self.assertEqual(result["tax_rate"], 4.4)
    
    def test_sales_tax_calculation(self):
        """Test Colorado sales tax calculation"""
        # Test Denver sales tax
        result = self.tax_rules.calculate_sales_tax(
            purchase_amount=Decimal('100'),
            location="DENVER",
            product_type="general"
        )
        
        # Denver total rate = 2.9% state + 4.15% local = 7.05%
        expected_tax = 100 * Decimal('0.0705')
        self.assertAlmostEqual(result["total_tax"], float(expected_tax), delta=0.01)
        self.assertEqual(result["total_tax_rate"], 7.05)
        
        # Test grocery exemption
        result = self.tax_rules.calculate_sales_tax(
            purchase_amount=Decimal('100'),
            location="DENVER",
            product_type="groceries"
        )
        self.assertEqual(result["total_tax"], 0)  # Groceries exempt
    
    def test_nexus_determination(self):
        """Test Colorado nexus determination"""
        # Test economic nexus
        result = self.tax_rules.determine_nexus(
            revenue=Decimal('200000'),
            transactions=50,
            physical_presence=False
        )
        self.assertTrue(result["has_nexus"])
        self.assertTrue(result["economic_nexus"])
        
        # Test transaction nexus
        result = self.tax_rules.determine_nexus(
            revenue=Decimal('50000'),
            transactions=250,
            physical_presence=False
        )
        self.assertTrue(result["has_nexus"])
        self.assertTrue(result["transaction_nexus"])
        
        # Test physical presence nexus
        result = self.tax_rules.determine_nexus(
            revenue=Decimal('0'),
            transactions=0,
            physical_presence=True
        )
        self.assertTrue(result["has_nexus"])
        self.assertTrue(result["physical_nexus"])
        
        # Test no nexus
        result = self.tax_rules.determine_nexus(
            revenue=Decimal('50000'),
            transactions=50,
            physical_presence=False
        )
        self.assertFalse(result["has_nexus"])
    
    def test_use_tax_calculation(self):
        """Test Colorado use tax calculation"""
        result = self.tax_rules.calculate_use_tax(
            purchase_amount=Decimal('100'),
            location="DENVER",
            product_type="general"
        )
        
        # Should be same as sales tax
        self.assertEqual(result["use_tax_rate"], 7.05)
        self.assertGreater(result["use_tax_amount"], 0)
    
    def test_filing_requirements(self):
        """Test filing requirement determination"""
        # Test with revenue but no employees
        result = self.tax_rules.get_filing_requirements(
            business_type="llc",
            revenue=Decimal('500000'),
            has_employees=False
        )
        
        self.assertIn("DR 0104 - Colorado Income Tax Return", result["requirements"]["forms"])
        self.assertIn("Colorado Secretary of State Registration", result["requirements"]["registrations"])
        
        # Test with employees
        result = self.tax_rules.get_filing_requirements(
            business_type="corporation",
            revenue=Decimal('500000'),
            has_employees=True
        )
        
        self.assertIn("DR 1094 - Colorado Withholding Tax Return", result["requirements"]["forms"])
        self.assertIn("Colorado Withholding Account", result["requirements"]["registrations"])
        
        # Test with sales tax nexus
        result = self.tax_rules.get_filing_requirements(
            business_type="llc",
            revenue=Decimal('1500000'),  # Above economic nexus threshold
            has_employees=False
        )
        
        self.assertIn("DR 0100 - Colorado Sales Tax Return", result["requirements"]["forms"])

if __name__ == '__main__':
    unittest.main()
```