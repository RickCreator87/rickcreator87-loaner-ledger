
4. Tax Logic

tax/federal/rules.py

```python
# tax/federal/rules.py
"""
Federal tax rules for Richard's Credit Authority
US federal tax calculations and compliance rules
"""

from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass

@dataclass
class TaxBracket:
    """Tax bracket definition"""
    min_amount: Decimal
    max_amount: Optional[Decimal]
    rate: Decimal
    fixed_amount: Decimal = Decimal('0')

class FederalTaxRules:
    """US Federal tax rules and calculations"""
    
    # 2024 Tax Brackets (Single Filer)
    INCOME_TAX_BRACKETS = [
        TaxBracket(Decimal('0'), Decimal('11000'), Decimal('0.10')),
        TaxBracket(Decimal('11001'), Decimal('44725'), Decimal('0.12'), Decimal('1100')),
        TaxBracket(Decimal('44726'), Decimal('95375'), Decimal('0.22'), Decimal('5147')),
        TaxBracket(Decimal('95376'), Decimal('182100'), Decimal('0.24'), Decimal('16290')),
        TaxBracket(Decimal('182101'), Decimal('231250'), Decimal('0.32'), Decimal('37104')),
        TaxBracket(Decimal('231251'), Decimal('578125'), Decimal('0.35'), Decimal('52832')),
        TaxBracket(Decimal('578126'), None, Decimal('0.37'), Decimal('174238.25')),
    ]
    
    # Standard Deductions 2024
    STANDARD_DEDUCTIONS = {
        "single": Decimal('14600'),
        "married_joint": Decimal('29200'),
        "married_separate": Decimal('14600'),
        "head_of_household": Decimal('21900'),
    }
    
    # Backup Withholding Rate (2026)
    BACKUP_WITHHOLDING_RATE = Decimal('0.24')
    
    # Supplemental Withholding Rate
    SUPPLEMENTAL_WITHHOLDING_RATE = Decimal('0.22')
    
    # Thresholds
    BACKUP_WITHHOLDING_THRESHOLD = Decimal('10')  # Interest payments
    FORM_1099_THRESHOLD = Decimal('600')  # Various 1099 forms
    
    def calculate_income_tax(self, 
                           taxable_income: Decimal,
                           filing_status: str = "single",
                           year: int = 2024) -> Dict[str, Any]:
        """
        Calculate federal income tax
        
        Args:
            taxable_income: Amount subject to tax
            filing_status: Tax filing status
            year: Tax year
        
        Returns:
            Dictionary with tax calculation details
        """
        # Apply standard deduction
        deduction = self.STANDARD_DEDUCTIONS.get(filing_status, Decimal('14600'))
        income_after_deduction = max(Decimal('0'), taxable_income - deduction)
        
        # Calculate tax using brackets
        tax_amount = Decimal('0')
        bracket_details = []
        remaining_income = income_after_deduction
        
        for bracket in self.INCOME_TAX_BRACKETS:
            if remaining_income <= 0:
                break
            
            bracket_max = bracket.max_amount or remaining_income
            taxable_in_bracket = min(remaining_income, bracket_max - bracket.min_amount + Decimal('1'))
            
            if taxable_in_bracket > 0:
                bracket_tax = bracket.fixed_amount + (taxable_in_bracket * bracket.rate)
                tax_amount += bracket_tax
                
                bracket_details.append({
                    "bracket": f"{bracket.min_amount}-{bracket.max_amount or '∞'}",
                    "rate": float(bracket.rate * 100),
                    "amount_in_bracket": float(taxable_in_bracket),
                    "tax_in_bracket": float(bracket_tax)
                })
                
                remaining_income -= taxable_in_bracket
        
        return {
            "taxable_income": float(taxable_income),
            "standard_deduction": float(deduction),
            "income_after_deduction": float(income_after_deduction),
            "total_tax": float(tax_amount),
            "effective_rate": float((tax_amount / taxable_income * 100) if taxable_income > 0 else 0),
            "marginal_rate": float(self.INCOME_TAX_BRACKETS[-1].rate * 100),
            "bracket_details": bracket_details,
            "calculation_date": datetime.utcnow().isoformat() + "Z"
        }
    
    def calculate_withholding(self,
                            payment_amount: Decimal,
                            payment_type: str = "regular",
                            recipient_type: str = "individual",
                            tax_id_provided: bool = True) -> Dict[str, Any]:
        """
        Calculate withholding tax
        
        Args:
            payment_amount: Amount of payment
            payment_type: Type of payment (regular, supplemental, interest, etc.)
            recipient_type: Type of recipient
            tax_id_provided: Whether tax ID was provided
        
        Returns:
            Dictionary with withholding calculation
        """
        withholding_rate = Decimal('0')
        withholding_amount = Decimal('0')
        required = False
        form_required = None
        
        # Determine withholding requirements
        if payment_type == "interest":
            # Backup withholding for interest payments
            if not tax_id_provided or payment_amount > self.BACKUP_WITHHOLDING_THRESHOLD:
                withholding_rate = self.BACKUP_WITHHOLDING_RATE
                required = True
                form_required = "1099-INT"
        
        elif payment_type == "supplemental":
            # Supplemental wage payments
            withholding_rate = self.SUPPLEMENTAL_WITHHOLDING_RATE
            required = True
        
        elif payment_type in ["rent", "royalties", "nonemployee_compensation"]:
            # Various 1099-MISC payments
            if payment_amount >= self.FORM_1099_THRESHOLD:
                if not tax_id_provided:
                    withholding_rate = self.BACKUP_WITHHOLDING_RATE
                    required = True
                form_required = "1099-MISC"
        
        elif payment_type == "credit_issuance_fee":
            # Credit authority specific
            withholding_rate = Decimal('0.10')  # Example rate
            required = payment_amount > Decimal('1000')
        
        # Calculate withholding amount
        if required and withholding_rate > 0:
            withholding_amount = (payment_amount * withholding_rate).quantize(
                Decimal('0.01'), rounding=ROUND_HALF_UP
            )
        
        return {
            "payment_amount": float(payment_amount),
            "payment_type": payment_type,
            "recipient_type": recipient_type,
            "withholding_required": required,
            "withholding_rate": float(withholding_rate * 100),
            "withholding_amount": float(withholding_amount),
            "net_amount": float(payment_amount - withholding_amount),
            "form_required": form_required,
            "tax_id_provided": tax_id_provided,
            "calculation_date": datetime.utcnow().isoformat() + "Z"
        }
    
    def determine_form_requirements(self,
                                  payment_type: str,
                                  payment_amount: Decimal,
                                  recipient_type: str,
                                  cumulative_annual: Decimal = Decimal('0')) -> List[str]:
        """
        Determine which tax forms are required
        
        Args:
            payment_type: Type of payment
            payment_amount: Amount of this payment
            recipient_type: Type of recipient
            cumulative_annual: Cumulative payments for the year
        
        Returns:
            List of required form codes
        """
        forms = []
        
        # Form 1099 series
        if recipient_type in ["individual", "partnership", "llc", "estate"]:
            if payment_type == "interest" and (payment_amount >= Decimal('10') or cumulative_annual >= Decimal('10')):
                forms.append("1099-INT")
            
            elif payment_type == "dividend" and payment_amount >= Decimal('10'):
                forms.append("1099-DIV")
            
            elif payment_type in ["rent", "royalties"] and payment_amount >= Decimal('10'):
                forms.append("1099-MISC")
            
            elif payment_type == "nonemployee_compensation" and payment_amount >= self.FORM_1099_THRESHOLD:
                forms.append("1099-NEC")
        
        # Form W-9 for tax ID collection
        if any(form.startswith("1099") for form in forms):
            forms.append("W-9")
        
        # Form 1042-S for foreign persons
        if recipient_type == "foreign":
            forms.append("1042-S")
        
        return forms
    
    def calculate_penalties(self,
                          violation_type: str,
                          amount_owed: Decimal,
                          days_late: int,
                          is_willful: bool = False) -> Dict[str, Any]:
        """
        Calculate tax penalties
        
        Args:
            violation_type: Type of violation
            amount_owed: Amount of tax owed
            days_late: Number of days late
            is_willful: Whether violation was willful
        
        Returns:
            Dictionary with penalty calculation
        """
        penalties = []
        total_penalty = Decimal('0')
        
        penalty_rules = {
            "failure_to_file": {
                "rate": Decimal('0.05'),  # 5% per month
                "max_months": 5,
                "minimum": Decimal('435') if amount_owed < Decimal('435') else Decimal('0'),
                "cap_percentage": Decimal('0.25')  # 25% cap
            },
            "failure_to_pay": {
                "rate": Decimal('0.005'),  # 0.5% per month
                "max_months": 50,
                "minimum": Decimal('0'),
                "cap_percentage": Decimal('0.25')  # 25% cap
            },
            "failure_to_deposit": {
                "rate": Decimal('0.02'),  # 2% if 1-5 days late, 5% if 6-15 days, 10% if >15 days
                "tiers": {
                    5: Decimal('0.02'),
                    15: Decimal('0.05'),
                },
                "cap": Decimal('0.10')  # 10% cap
            }
        }
        
        rule = penalty_rules.get(violation_type, {})
        
        if violation_type == "failure_to_file":
            months_late = min(max(1, days_late // 30), rule["max_months"])
            penalty = amount_owed * rule["rate"] * Decimal(months_late)
            penalty = min(penalty, amount_owed * rule["cap_percentage"])
            penalty = max(penalty, rule["minimum"])
            
            penalties.append({
                "type": "failure_to_file",
                "rate": float(rule["rate"] * 100),
                "months": months_late,
                "amount": float(penalty)
            })
            total_penalty += penalty
        
        elif violation_type == "failure_to_pay":
            months_late = min(max(1, days_late // 30), rule["max_months"])
            penalty = amount_owed * rule["rate"] * Decimal(months_late)
            penalty = min(penalty, amount_owed * rule["cap_percentage"])
            
            penalties.append({
                "type": "failure_to_pay",
                "rate": float(rule["rate"] * 100),
                "months": months_late,
                "amount": float(penalty)
            })
            total_penalty += penalty
        
        elif violation_type == "failure_to_deposit":
            if days_late <= 5:
                rate = rule["tiers"][5]
            elif days_late <= 15:
                rate = rule["tiers"][15]
            else:
                rate = rule["cap"]
            
            penalty = amount_owed * rate
            
            penalties.append({
                "type": "failure_to_deposit",
                "rate": float(rate * 100),
                "days": days_late,
                "amount": float(penalty)
            })
            total_penalty += penalty
        
        # Additional penalty for willful violations
        if is_willful:
            willful_penalty = amount_owed * Decimal('0.75')  # 75% penalty for willful violations
            penalties.append({
                "type": "willful_penalty",
                "rate": 75.0,
                "amount": float(willful_penalty)
            })
            total_penalty += willful_penalty
        
        return {
            "violation_type": violation_type,
            "amount_owed": float(amount_owed),
            "days_late": days_late,
            "is_willful": is_willful,
            "penalties": penalties,
            "total_penalty": float(total_penalty),
            "total_with_penalty": float(amount_owed + total_penalty),
            "calculation_date": datetime.utcnow().isoformat() + "Z"
        }
    
    def validate_tax_id(self, tax_id: str, tax_id_type: str = "ssn") -> Dict[str, Any]:
        """
        Validate tax ID format
        
        Args:
            tax_id: Tax ID to validate
            tax_id_type: Type of tax ID
        
        Returns:
            Dictionary with validation results
        """
        valid = False
        format_valid = False
        checksum_valid = False
        issues = []
        
        if tax_id_type == "ssn":
            # Basic SSN validation (format only, not validity)
            import re
            ssn_pattern = r'^(?!000|666|9\d\d)\d{3}-(?!00)\d{2}-(?!0000)\d{4}$'
            if re.match(ssn_pattern, tax_id):
                format_valid = True
                
                # Simple checksum (example - not real SSN validation)
                numbers = tax_id.replace('-', '')
                if len(numbers) == 9 and numbers.isdigit():
                    checksum_valid = True
                    valid = True
                else:
                    issues.append("Invalid SSN format")
            else:
                issues.append("SSN format invalid")
        
        elif tax_id_type == "ein":
            # EIN validation
            import re
            ein_pattern = r'^\d{2}-\d{7}$'
            if re.match(ein_pattern, tax_id):
                format_valid = True
                
                # EIN checksum (simplified)
                numbers = tax_id.replace('-', '')
                if len(numbers) == 9 and numbers.isdigit():
                    checksum_valid = True
                    valid = True
                else:
                    issues.append("Invalid EIN format")
            else:
                issues.append("EIN format invalid")
        
        return {
            "tax_id": tax_id,
            "tax_id_type": tax_id_type,
            "valid": valid,
            "format_valid": format_valid,
            "checksum_valid": checksum_valid,
            "issues": issues,
            "validation_date": datetime.utcnow().isoformat() + "Z"
        }
```