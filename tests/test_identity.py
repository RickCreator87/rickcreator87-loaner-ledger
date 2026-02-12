
5. Tests

tests/test_identity.py

```python
# tests/test_identity.py
"""
Unit tests for identity validation in Richard's Credit Authority
"""

import unittest
import tempfile
import yaml
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from validation.validate_identity import IdentityValidator

class TestIdentityValidation(unittest.TestCase):
    """Test identity validation functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.validator = IdentityValidator()
        self.valid_identity = {
            "identity_id": "123e4567-e89b-12d3-a456-426614174000",
            "entity_type": "individual",
            "personal_info": {
                "legal_name": {
                    "first_name": "John",
                    "last_name": "Doe"
                },
                "date_of_birth": "1980-01-15",
                "place_of_birth": {
                    "city": "Denver",
                    "state": "CO",
                    "country": "US"
                }
            },
            "verified_status": {
                "level": "verified",
                "last_verified": "2024-01-15T10:30:00Z",
                "verified_by": ["government_id"],
                "verification_score": 85
            },
            "metadata": {
                "created_at": "2024-01-10T14:30:00Z"
            }
        }
    
    def test_valid_identity(self):
        """Test validation of a valid identity"""
        result = self.validator.validate(self.valid_identity)
        self.assertTrue(result["valid"])
        self.assertEqual(len(result["errors"]), 0)
    
    def test_missing_required_fields(self):
        """Test validation with missing required fields"""
        invalid_identity = self.valid_identity.copy()
        del invalid_identity["identity_id"]
        
        result = self.validator.validate(invalid_identity)
        self.assertFalse(result["valid"])
        self.assertIn("Missing required field: identity_id", result["errors"])
    
    def test_invalid_entity_type(self):
        """Test validation with invalid entity type"""
        invalid_identity = self.valid_identity.copy()
        invalid_identity["entity_type"] = "invalid_type"
        
        result = self.validator.validate(invalid_identity)
        self.assertFalse(result["valid"])
        self.assertIn("Invalid entity_type: invalid_type", result["errors"])
    
    def test_invalid_date_format(self):
        """Test validation with invalid date format"""
        invalid_identity = self.valid_identity.copy()
        invalid_identity["personal_info"]["date_of_birth"] = "15-01-1980"  # Wrong format
        
        result = self.validator.validate(invalid_identity)
        self.assertFalse(result["valid"])
        self.assertIn("Invalid date format", result["errors"][0])
    
    def test_invalid_country_code(self):
        """Test validation with invalid country code"""
        invalid_identity = self.valid_identity.copy()
        invalid_identity["personal_info"]["place_of_birth"]["country"] = "USA"  # Should be US
        
        result = self.validator.validate(invalid_identity)
        self.assertFalse(result["valid"])
        self.assertIn("Invalid country code", result["errors"][0])
    
    def test_individual_missing_personal_info(self):
        """Test that individuals require personal_info"""
        invalid_identity = self.valid_identity.copy()
        del invalid_identity["personal_info"]
        
        result = self.validator.validate(invalid_identity)
        self.assertFalse(result["valid"])
        self.assertIn("Individuals must have personal_info", result["errors"])
    
    def test_future_date_of_birth(self):
        """Test that date of birth cannot be in the future"""
        invalid_identity = self.valid_identity.copy()
        invalid_identity["personal_info"]["date_of_birth"] = "2050-01-01"
        
        result = self.validator.validate(invalid_identity)
        self.assertFalse(result["valid"])
        self.assertIn("Date of birth cannot be in the future", result["errors"])
    
    def test_kyc_compliant_missing_government_ids(self):
        """Test that KYC compliant identities require government IDs"""
        invalid_identity = self.valid_identity.copy()
        invalid_identity["verified_status"]["level"] = "kyc_compliant"
        
        result = self.validator.validate(invalid_identity)
        self.assertFalse(result["valid"])
        self.assertIn("KYC compliant identities must have government_ids", result["errors"])
    
    def test_warnings_for_unverified_contact(self):
        """Test that unverified contact info generates warnings"""
        identity_with_unverified = self.valid_identity.copy()
        identity_with_unverified["contact_info"] = {
            "communication": {
                "email_addresses": [
                    {"address": "test@example.com", "verified": False}
                ]
            }
        }
        
        result = self.validator.validate(identity_with_unverified)
        self.assertTrue(result["valid"])
        self.assertGreater(len(result["warnings"]), 0)
        self.assertIn("unverified email", result["warnings"][0].lower())
    
    def test_file_validation(self):
        """Test validation from YAML file"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(self.valid_identity, f)
            temp_file = Path(f.name)
        
        try:
            result = self.validator.validate_file(temp_file)
            self.assertTrue(result["valid"])
        finally:
            temp_file.unlink()
    
    def test_invalid_yaml_file(self):
        """Test validation with invalid YAML file"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("invalid: yaml: content: [}")
            temp_file = Path(f.name)
        
        try:
            result = self.validator.validate_file(temp_file)
            self.assertFalse(result["valid"])
            self.assertIn("YAML parsing error", result["errors"][0])
        finally:
            temp_file.unlink()
    
    def test_business_entity_validation(self):
        """Test validation of business entity"""
        business_identity = {
            "identity_id": "123e4567-e89b-12d3-a456-426614174001",
            "entity_type": "business",
            "verified_status": {
                "level": "verified",
                "last_verified": "2026-01-15T10:30:00Z"
            },
            "metadata": {
                "created_at": "2026-01-10T14:30:00Z"
            }
        }
        
        result = self.validator.validate(business_identity)
        self.assertTrue(result["valid"])
        self.assertEqual(len(result["errors"]), 0)

if __name__ == '__main__':
    unittest.main()
```