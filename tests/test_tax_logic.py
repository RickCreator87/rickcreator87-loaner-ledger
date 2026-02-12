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