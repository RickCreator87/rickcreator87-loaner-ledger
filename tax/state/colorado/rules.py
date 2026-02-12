tax/state/colorado/rules.py

```python
# tax/state/colorado/rules.py
"""
Colorado state tax rules for Richard's Credit Authority
Colorado-specific tax calculations and compliance rules
"""

from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

@dataclass
class ColoradoTaxBracket:
    """Colorado tax bracket definition"""
    min_amount: Decimal
    max_amount: Optional[Decimal]
    rate: Decimal

class ColoradoTaxRules:
    """Colorado state tax rules and calculations"""
    
    # 2026 Colorado Income Tax
    INCOME_TAX_RATE = Decimal('0.0440')  # 4.4% flat rate starting 2026
    
    # Prior years had different rates
    HISTORICAL_RATES = {
        2023: Decimal('0.0440'),
        2022: Decimal('0.0455'),
        2021: Decimal('0.0465'),
        2020: Decimal('0.0463'),
    }
    
    # Colorado Sales Tax (state portion)
    SALES_TAX_RATE = Decimal('0.029')  # 2.9% state sales tax
    
    # Local sales tax rates (example cities)
    LOCAL_SALES_TAX_RATES = {
        "DENVER": Decimal('0.0415'),  # 4.15% Denver local tax
        "BOULDER": Decimal('0.0389'),  # 3.89% Boulder local tax
        "COLORADO_SPRINGS": Decimal('0.0307'),  # 3.07% Colorado Springs
        "AURORA": Decimal('0.038'),  # 3.8% Aurora
    }
    
    # Thresholds
    INCOME_TAX_FILING_THRESHOLD = Decimal('12500')  # Single filer
    SALES_TAX_THRESHOLD = Decimal('100000')  # Economic nexus threshold
    
    def calculate_income_tax(self,
                           taxable_income: Decimal,
                           filing_status: str = "single",
                           year: int = 2026) -> Dict[str, Any]:
        """
        Calculate Colorado income tax
        
        Args:
            taxable_income: Colorado taxable income
            filing_status: Tax filing status
            year: Tax year
        
        Returns:
            Dictionary with tax calculation details
        """
        # Get tax rate for year
        tax_rate = self.HISTORICAL_RATES.get(year, self.INCOME_TAX_RATE)
        
        # Colorado uses federal taxable income with adjustments
        colorado_taxable_income = taxable_income
        
        # Apply Colorado-specific adjustments (simplified)
        colorado_adjustments = self._calculate_adjustments(taxable_income, filing_status, year)
        colorado_taxable_income += colorado_adjustments.get("net_adjustment", Decimal('0'))
        
        # Calculate tax
        tax_amount = (colorado_taxable_income * tax_rate).quantize(
            Decimal('0.01'), rounding=ROUND_HALF_UP
        )
        
        # Minimum tax check
        if tax_amount < Decimal('1'):
            tax_amount = Decimal('0')
        
        return {
            "taxable_income": float(taxable_income),
            "colorado_taxable_income": float(colorado_taxable_income),
            "tax_rate": float(tax_rate * 100),
            "tax_amount": float(tax_amount),
            "filing_required": colorado_taxable_income >= self.INCOME_TAX_FILING_THRESHOLD,
            "adjustments": colorado_adjustments,
            "calculation_date": datetime.utcnow().isoformat() + "Z",
            "jurisdiction": "US-CO"
        }
    
    def _calculate_adjustments(self,
                             taxable_income: Decimal,
                             filing_status: str,
                             year: int) -> Dict[str, Any]:
        """Calculate Colorado-specific adjustments to federal taxable income"""
        adjustments = {
            "additions": [],
            "subtractions": [],
            "net_adjustment": Decimal('0')
        }
        
        # Common Colorado additions
        additions = [
            ("state_income_tax_refund", Decimal('0')),  # Example
            ("municipal_bond_interest", Decimal('0')),  # Example
        ]
        
        # Common Colorado subtractions
        subtractions = [
            ("social_security_benefits", Decimal('0')),  # Social Security benefits not taxed in CO
            ("us_government_interest", Decimal('0')),    # US Government interest
            ("colorado_capital_gains", Decimal('0')),    # Colorado capital gains deduction
        ]
        
        # Calculate net adjustment
        total_additions = sum(amount for _, amount in additions)
        total_subtractions = sum(amount for _, amount in subtractions)
        net_adjustment = total_additions - total_subtractions
        
        adjustments["additions"] = [{"description": desc, "amount": float(amt)} for desc, amt in additions]
        adjustments["subtractions"] = [{"description": desc, "amount": float(amt)} for desc, amt in subtractions]
        adjustments["net_adjustment"] = float(net_adjustment)
        
        return adjustments
    
    def calculate_sales_tax(self,
                          purchase_amount: Decimal,
                          location: str = "DENVER",
                          product_type: str = "general") -> Dict[str, Any]:
        """
        Calculate Colorado sales tax
        
        Args:
            purchase_amount: Purchase amount
            location: Location within Colorado
            product_type: Type of product/service
        
        Returns:
            Dictionary with sales tax calculation
        """
        # State sales tax
        state_tax = (purchase_amount * self.SALES_TAX_RATE).quantize(
            Decimal('0.01'), rounding=ROUND_HALF_UP
        )
        
        # Local sales tax
        local_rate = self.LOCAL_SALES_TAX_RATES.get(location.upper(), Decimal('0'))
        local_tax = (purchase_amount * local_rate).quantize(
            Decimal('0.01'), rounding=ROUND_HALF_UP
        )
        
        # Special district taxes (simplified)
        special_district_tax = Decimal('0')
        
        # Check for exemptions
        exemptions = self._get_sales_tax_exemptions(product_type)
        if exemptions:
            # Apply exemptions
            exempt_amount = Decimal('0')
            for exemption in exemptions:
                if exemption.get("applicable", True):
                    exempt_amount += Decimal(str(exemption.get("amount", 0)))
            
            taxable_amount = max(Decimal('0'), purchase_amount - exempt_amount)
            state_tax = (taxable_amount * self.SALES_TAX_RATE).quantize(
                Decimal('0.01'), rounding=ROUND_HALF_UP
            )
            local_tax = (taxable_amount * local_rate).quantize(
                Decimal('0.01'), rounding=ROUND_HALF_UP
            )
        
        total_tax = state_tax + local_tax + special_district_tax
        total_rate = self.SALES_TAX_RATE + local_rate
        
        return {
            "purchase_amount": float(purchase_amount),
            "location": location,
            "product_type": product_type,
            "state_rate": float(self.SALES_TAX_RATE * 100),
            "state_tax": float(state_tax),
            "local_rate": float(local_rate * 100),
            "local_tax": float(local_tax),
            "special_district_tax": float(special_district_tax),
            "total_tax_rate": float(total_rate * 100),
            "total_tax": float(total_tax),
            "total_amount": float(purchase_amount + total_tax),
            "exemptions_applied": exemptions,
            "calculation_date": datetime.utcnow().isoformat() + "Z",
            "jurisdiction": "US-CO"
        }
    
    def _get_sales_tax_exemptions(self, product_type: str) -> List[Dict[str, Any]]:
        """Get sales tax exemptions for product type"""
        exemptions = []
        
        # Colorado sales tax exemptions
        if product_type in ["groceries", "food"]:
            exemptions.append({
                "type": "grocery_exemption",
                "description": "Colorado grocery exemption",
                "rate": 0.0,
                "applicable": True
            })
        
        elif product_type == "prescription_drugs":
            exemptions.append({
                "type": "prescription_drug_exemption",
                "description": "Prescription drugs exempt",
                "rate": 0.0,
                "applicable": True
            })
        
        elif product_type in ["manufacturing_equipment", "industrial_machinery"]:
            exemptions.append({
                "type": "manufacturing_exemption",
                "description": "Manufacturing equipment exempt",
                "rate": 0.0,
                "applicable": True
            })
        
        return exemptions
    
    def determine_nexus(self,
                       revenue: Decimal,
                       transactions: int,
                       physical_presence: bool = False) -> Dict[str, Any]:
        """
        Determine if business has Colorado sales tax nexus
        
        Args:
            revenue: Annual revenue from Colorado
            transactions: Number of transactions in Colorado
            physical_presence: Whether business has physical presence in CO
        
        Returns:
            Dictionary with nexus determination
        """
        # Economic nexus threshold
        economic_nexus = revenue >= self.SALES_TAX_THRESHOLD
        
        # Transaction count threshold (simplified)
        transaction_nexus = transactions >= 200
        
        # Physical presence nexus
        physical_nexus = physical_presence
        
        has_nexus = economic_nexus or transaction_nexus or physical_nexus
        
        nexus_details = []
        if economic_nexus:
            nexus_details.append(f"Economic nexus: Revenue ${revenue:,} >= ${self.SALES_TAX_THRESHOLD:,}")
        if transaction_nexus:
            nexus_details.append(f"Transaction nexus: {transactions} transactions >= 200")
        if physical_nexus:
            nexus_details.append("Physical presence nexus")
        
        return {
            "has_nexus": has_nexus,
            "economic_nexus": economic_nexus,
            "transaction_nexus": transaction_nexus,
            "physical_nexus": physical_nexus,
            "revenue": float(revenue),
            "transactions": transactions,
            "physical_presence": physical_presence,
            "nexus_details": nexus_details,
            "determination_date": datetime.utcnow().isoformat() + "Z",
            "jurisdiction": "US-CO"
        }
    
    def calculate_use_tax(self,
                         purchase_amount: Decimal,
                         location: str = "DENVER",
                         product_type: str = "general") -> Dict[str, Any]:
        """
        Calculate Colorado use tax (for out-of-state purchases)
        
        Args:
            purchase_amount: Purchase amount
            location: Location where item will be used
            product_type: Type of product
        
        Returns:
            Dictionary with use tax calculation
        """
        # Use tax rate is same as sales tax rate
        sales_tax_calc = self.calculate_sales_tax(purchase_amount, location, product_type)
        
        return {
            "purchase_amount": float(purchase_amount),
            "location": location,
            "product_type": product_type,
            "use_tax_rate": sales_tax_calc["total_tax_rate"],
            "use_tax_amount": sales_tax_calc["total_tax"],
            "equivalent_sales_tax": sales_tax_calc["total_tax"],
            "calculation_date": datetime.utcnow().isoformat() + "Z",
            "jurisdiction": "US-CO",
            "note": "Use tax due when sales tax not paid to another jurisdiction"
        }
    
    def get_filing_requirements(self,
                              business_type: str,
                              revenue: Decimal,
                              has_employees: bool = False) -> Dict[str, Any]:
        """
        Get Colorado tax filing requirements
        
        Args:
            business_type: Type of business
            revenue: Annual revenue
            has_employees: Whether business has employees
        
        Returns:
            Dictionary with filing requirements
        """
        requirements = {
            "forms": [],
            "frequencies": [],
            "registrations": [],
            "deadlines": []
        }
        
        # Income tax filing
        if revenue > Decimal('0'):
            requirements["forms"].append("DR 0104 - Colorado Income Tax Return")
            requirements["frequencies"].append("Annually")
            requirements["deadlines"].append("April 15 (following year)")
        
        # Sales tax filing (if nexus exists)
        nexus_result = self.determine_nexus(revenue, 0, False)
        if nexus_result["has_nexus"]:
            requirements["forms"].append("DR 0100 - Colorado Sales Tax Return")
            
            # Determine filing frequency based on revenue
            if revenue > Decimal('1000000'):
                requirements["frequencies"].append("Monthly")
            elif revenue > Decimal('100000'):
                requirements["frequencies"].append("Quarterly")
            else:
                requirements["frequencies"].append("Annually")
            
            requirements["registrations"].append("Colorado Sales Tax License")
        
        # Withholding tax (if has employees)
        if has_employees:
            requirements["forms"].append("DR 1094 - Colorado Withholding Tax Return")
            requirements["frequencies"].append("Quarterly")
            requirements["registrations"].append("Colorado Withholding Account")
        
        # Business registration
        requirements["registrations"].append("Colorado Secretary of State Registration")
        
        return {
            "business_type": business_type,
            "revenue": float(revenue),
            "has_employees": has_employees,
            "requirements": requirements,
            "determination_date": datetime.utcnow().isoformat() + "Z",
            "jurisdiction": "US-CO"
        }
```


