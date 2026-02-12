
Multi-Jurisdiction Tax Calculation

```python
def calculate_multi_jurisdiction_tax(amount, jurisdictions):
    """Calculate tax for multiple jurisdictions"""
    total_tax = Decimal('0')
    tax_details = []
    
    # Federal tax
    federal_rules = FederalTaxRules()
    federal_withholding = federal_rules.calculate_withholding(
        payment_amount=amount,
        payment_type="interest"
    )
    
    if federal_withholding["withholding_required"]:
        total_tax += Decimal(str(federal_withholding["withholding_amount"]))
        tax_details.append({
            "jurisdiction": "US",
            "type": "withholding",
            "amount": federal_withholding["withholding_amount"]
        })
    
    # State taxes
    for jurisdiction in jurisdictions:
        if jurisdiction.startswith("US-"):
            state_code = jurisdiction.split("-")[1]
            
            # Import appropriate state module
            module_name = f"tax.state.{state_code.lower()}.rules"
            try:
                module = __import__(module_name, fromlist=[''])
                state_rules = module.__dict__[f"{state_code}TaxRules"]()
                
                state_tax = state_rules.calculate_income_tax(
                    taxable_income=amount,
                    filing_status="single"
                )
                
                total_tax += Decimal(str(state_tax["tax_amount"]))
                tax_details.append({
                    "jurisdiction": jurisdiction,
                    "type": "income",
                    "amount": state_tax["tax_amount"]
                })
                
            except ImportError:
                print(f"No tax rules for {jurisdiction}")
    
    return {
        "total_tax": float(total_tax),
        "tax_details": tax_details,
        "net_amount": float(amount - total_tax)
    }
```