Governance Rules

Applying Governance Rules

```python
from governance.engine import GovernanceEngine

# Initialize governance engine
engine = GovernanceEngine()

# Load identity and authority
with open("identity.yaml", "r") as f:
    identity = yaml.safe_load(f)

with open("authority.yaml", "r") as f:
    authority = yaml.safe_load(f)

# Evaluate authority request
decision = engine.evaluate_authority_request(
    authority_request=authority,
    identity_data=identity,
    context={"requested_by": "user123"}
)

# Print decision
print(f"Decision: {decision.decision}")
print(f"Reasons: {decision.reasons}")

if decision.decision == "approved":
    print("Authority can be granted!")
else:
    print(f"Required actions: {decision.required_actions}")
    
    # Save decision for audit
    engine.save_decision(decision, Path("decisions/"))
```
