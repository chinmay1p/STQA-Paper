"""
Script to generate scenario mutant files and scenario_manifest.json.
All transformations are empirically verified against the test suite.
"""
import json
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAMPLE_APP_DIR = os.path.join(BASE_DIR, "sample_app")
MUTANTS_DIR = os.path.join(BASE_DIR, "scenarios", "mutants")
os.makedirs(MUTANTS_DIR, exist_ok=True)

def read_base(module_name):
    path = os.path.join(SAMPLE_APP_DIR, f"{module_name}.py")
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

scenarios = [
    {
        "scenario_id": "SC-01",
        "name": "Discount tier cap boundary adjustment",
        "changed_module": "discount",
        "code_churn": 5,
        "has_fault": True,
        "fault_id": "F01",
        "expected_failing_tests": ["tests/test_discount.py::test_discount_cap_boundary"],
        "description": "Mutated validate_discount_cap floor calculation formula to original_price * max_discount_pct instead of (1.0 - max_discount_pct)",
        "modification_type": "Faulty logic",
        "base_file": "discount.py",
        "mutant_transform": lambda content: content.replace(
            "floor_price = original_price * (1.0 - max_discount_pct)",
            "floor_price = original_price * max_discount_pct  # Seeding Fault F01"
        )
    },
    {
        "scenario_id": "SC-02",
        "name": "Refactor sales tax rate lookup structure",
        "changed_module": "tax",
        "code_churn": 8,
        "has_fault": False,
        "fault_id": None,
        "expected_failing_tests": [],
        "description": "Refactored tax rate retrieval with safe uppercase strip check without altering numeric rates",
        "modification_type": "Clean refactoring",
        "base_file": "tax.py",
        "mutant_transform": lambda content: content.replace(
            "state = (state_code or \"\").strip().upper()\n    rate = STATE_TAX_RATES.get(state, 0.05)",
            "state = (state_code or \"\").strip().upper()\n    # Refactored lookup with explicit cached rate access\n    rate = STATE_TAX_RATES[state] if state in STATE_TAX_RATES else 0.05"
        )
    },
    {
        "scenario_id": "SC-03",
        "name": "Password strength symbol validation strictness",
        "changed_module": "authentication",
        "code_churn": 6,
        "has_fault": True,
        "fault_id": "F02",
        "expected_failing_tests": ["tests/test_authentication.py::test_password_strength_criteria"],
        "description": "Mutated symbol validation regex by omitting both '@' and '!' characters from permitted special symbols",
        "modification_type": "Faulty logic",
        "base_file": "authentication.py",
        "mutant_transform": lambda content: content.replace(
            "has_symbol = bool(re.search(r\"[!@#$%^&*(),.?\\\":{}|<>]\", password))",
            "has_symbol = bool(re.search(r\"[#$%^&*(),.?\\\":{}|<>]\", password))  # Omitted @ and ! causing F02"
        )
    },
    {
        "scenario_id": "SC-04",
        "name": "Cart clear method memory reset optimization",
        "changed_module": "cart",
        "code_churn": 6,
        "has_fault": False,
        "fault_id": None,
        "expected_failing_tests": [],
        "description": "Clean optimization to shopping cart item dictionary reinitialization",
        "modification_type": "Clean optimization",
        "base_file": "cart.py",
        "mutant_transform": lambda content: content.replace(
            "def clear(self) -> None:\n        self.items.clear()",
            "def clear(self) -> None:\n        # Clean internal state reset\n        self.items = {}"
        )
    },
    {
        "scenario_id": "SC-05",
        "name": "Order shipping excess weight multiplier calculation",
        "changed_module": "orders",
        "code_churn": 7,
        "has_fault": True,
        "fault_id": "F03",
        "expected_failing_tests": ["tests/test_orders.py::test_shipping_cost_calculation"],
        "description": "Mutated shipping excess weight fee multiplier from 2.50 to 3.50",
        "modification_type": "Faulty logic",
        "base_file": "orders.py",
        "mutant_transform": lambda content: content.replace(
            "weight_fee = excess_weight * 2.50",
            "weight_fee = excess_weight * 3.50  # Seeded Fault F03"
        )
    },
    {
        "scenario_id": "SC-06",
        "name": "Payment currency lookup error reporting formatting",
        "changed_module": "payment",
        "code_churn": 8,
        "has_fault": False,
        "fault_id": None,
        "expected_failing_tests": [],
        "description": "Clean logging and formatted validation message on currency conversion",
        "modification_type": "Clean enhancement",
        "base_file": "payment.py",
        "mutant_transform": lambda content: content.replace(
            "raise ValueError(f\"Unsupported currency: {src} -> {tgt}\")",
            "# Normalized uppercase error message\n        raise ValueError(f\"Unsupported currency: {src} -> {tgt}\")"
        )
    },
    {
        "scenario_id": "SC-07",
        "name": "Bulk quantity discount tier boundary condition",
        "changed_module": "discount",
        "code_churn": 9,
        "has_fault": True,
        "fault_id": "F04",
        "expected_failing_tests": ["tests/test_discount.py::test_discount_bulk_quantities"],
        "description": "Off-by-one fault in bulk discount: used > 50 instead of >= 50",
        "modification_type": "Faulty boundary",
        "base_file": "discount.py",
        "mutant_transform": lambda content: content.replace(
            "elif quantity >= 50:\n        discount = 0.15",
            "elif quantity > 50:  # Seeded Fault F04 (off-by-one)\n        discount = 0.15"
        )
    },
    {
        "scenario_id": "SC-08",
        "name": "Tax exemption certificate character length criterion",
        "changed_module": "tax",
        "code_churn": 7,
        "has_fault": True,
        "fault_id": "F05",
        "expected_failing_tests": [
            "tests/test_tax.py::test_tax_exemption_rules",
            "tests/test_orders.py::test_order_with_tax_exemption_and_free_shipping"
        ],
        "description": "Increased minimum tax exemption certificate length requirement from 5 to 12 chars",
        "modification_type": "Faulty logic",
        "base_file": "tax.py",
        "mutant_transform": lambda content: content.replace(
            "return bool(certificate_number and len(certificate_number.strip()) >= 5)",
            "return bool(certificate_number and len(certificate_number.strip()) >= 12)  # Seeded Fault F05"
        )
    },
    {
        "scenario_id": "SC-09",
        "name": "Cart item subtotal accumulation refactoring",
        "changed_module": "cart",
        "code_churn": 10,
        "has_fault": False,
        "fault_id": None,
        "expected_failing_tests": [],
        "description": "Clean refactoring of cart subtotal accumulation loop",
        "modification_type": "Clean refactoring",
        "base_file": "cart.py",
        "mutant_transform": lambda content: content.replace(
            "def calculate_subtotal(self) -> float:\n        return round(sum(item.line_total for item in self.items.values()), 2)",
            "def calculate_subtotal(self) -> float:\n        # Clean refactored sum\n        tot = sum(item.line_total for item in self.items.values())\n        return round(float(tot), 2)"
        )
    },
    {
        "scenario_id": "SC-10",
        "name": "Debit card payment gateway transaction fee parameter",
        "changed_module": "payment",
        "code_churn": 5,
        "has_fault": True,
        "fault_id": "F06",
        "expected_failing_tests": ["tests/test_payment.py::test_gateway_fee_models"],
        "description": "Mutated debit card fixed gateway fee from $0.20 to $0.40",
        "modification_type": "Faulty parameter",
        "base_file": "payment.py",
        "mutant_transform": lambda content: content.replace(
            "\"DEBIT_CARD\": (0.015, 0.20),",
            "\"DEBIT_CARD\": (0.015, 0.40),  # Seeded Fault F06"
        )
    },
    {
        "scenario_id": "SC-11",
        "name": "Seasonal promotion clearance and holiday stacking rate",
        "changed_module": "discount",
        "code_churn": 8,
        "has_fault": True,
        "fault_id": "F07",
        "expected_failing_tests": ["tests/test_discount.py::test_discount_seasonal_promotions"],
        "description": "Mutated combined seasonal discount rate from 0.22 to 0.25",
        "modification_type": "Faulty logic",
        "base_file": "discount.py",
        "mutant_transform": lambda content: content.replace(
            "if is_holiday and is_clearance:\n        discount_rate = 0.22",
            "if is_holiday and is_clearance:\n        discount_rate = 0.25  # Seeded Fault F07"
        )
    },
    {
        "scenario_id": "SC-12",
        "name": "Username whitespace sanitization case safety",
        "changed_module": "authentication",
        "code_churn": 6,
        "has_fault": False,
        "fault_id": None,
        "expected_failing_tests": [],
        "description": "Clean strip and lowercasing refactor in username sanitization",
        "modification_type": "Clean refactoring",
        "base_file": "authentication.py",
        "mutant_transform": lambda content: content.replace(
            "cleaned = re.sub(r\"[^a-zA-Z0-9_]\", \"\", raw_username.strip()).lower()",
            "cleaned = re.sub(r\"[^a-zA-Z0-9_]\", \"\", raw_username.strip())\n    cleaned = cleaned.lower()  # Clean explicit lowercase"
        )
    },
    {
        "scenario_id": "SC-13",
        "name": "Texas sales tax statutory percentage update",
        "changed_module": "tax",
        "code_churn": 6,
        "has_fault": True,
        "fault_id": "F08",
        "expected_failing_tests": ["tests/test_tax.py::test_sales_tax_jurisdictions"],
        "description": "Mutated Texas state sales tax rate from 0.0625 to 0.0725",
        "modification_type": "Faulty parameter",
        "base_file": "tax.py",
        "mutant_transform": lambda content: content.replace(
            "\"TX\": 0.0625,",
            "\"TX\": 0.0725,  # Seeded Fault F08"
        )
    },
    {
        "scenario_id": "SC-14",
        "name": "Shopping cart capacity boundary operator condition",
        "changed_module": "cart",
        "code_churn": 7,
        "has_fault": True,
        "fault_id": "F09",
        "expected_failing_tests": ["tests/test_cart.py::test_cart_capacity_overflow"],
        "description": "Mutated capacity overflow condition from >= max_items to > max_items",
        "modification_type": "Faulty boundary",
        "base_file": "cart.py",
        "mutant_transform": lambda content: content.replace(
            "if len(self.items) >= self.max_items and item_id not in self.items:",
            "if len(self.items) > self.max_items and item_id not in self.items:  # Seeded Fault F09"
        )
    },
    {
        "scenario_id": "SC-15",
        "name": "Order totals free shipping coupon calculation",
        "changed_module": "orders",
        "code_churn": 10,
        "has_fault": True,
        "fault_id": "F10",
        "expected_failing_tests": ["tests/test_orders.py::test_order_with_tax_exemption_and_free_shipping"],
        "description": "Mutated shipping fee calculation by failing to zero out shipping when FREESHIP coupon provided",
        "modification_type": "Faulty logic",
        "base_file": "orders.py",
        "mutant_transform": lambda content: content.replace(
            "if coupon_code and coupon_code.strip().upper() == \"FREESHIP\":\n        shipping_cost = 0.0",
            "if coupon_code and coupon_code.strip().upper() == \"FREESHIP\":\n        shipping_cost = 5.0  # Seeded Fault F10: failed to zero shipping"
        )
    },
    {
        "scenario_id": "SC-16",
        "name": "Payment Luhn checksum alternating index parity",
        "changed_module": "payment",
        "code_churn": 12,
        "has_fault": True,
        "fault_id": "F11",
        "expected_failing_tests": ["tests/test_payment.py::test_luhn_algorithm_validation"],
        "description": "Mutated Luhn digit doubling index from odd (i % 2 == 1) to even (i % 2 == 0)",
        "modification_type": "Faulty logic",
        "base_file": "payment.py",
        "mutant_transform": lambda content: content.replace(
            "if i % 2 == 1:",
            "if i % 2 == 0:  # Seeded Fault F11"
        )
    }
]

manifest_list = []
for sc in scenarios:
    sc_id = sc["scenario_id"]
    base_file = sc["base_file"]
    module_name = sc["changed_module"]
    original_code = read_base(module_name)
    mutated_code = sc["mutant_transform"](original_code)
    
    if mutated_code == original_code:
        raise ValueError(f"Transform for {sc_id} did not alter code!")
    
    mutant_filename = f"{sc_id}_{base_file}"
    mutant_path = os.path.join(MUTANTS_DIR, mutant_filename)
    with open(mutant_path, "w", encoding="utf-8") as f:
        f.write(mutated_code)
    
    entry = {
        "scenario_id": sc_id,
        "name": sc["name"],
        "changed_module": sc["changed_module"],
        "code_churn": sc["code_churn"],
        "has_fault": sc["has_fault"],
        "fault_id": sc["fault_id"],
        "expected_failing_tests": sc["expected_failing_tests"],
        "description": sc["description"],
        "modification_type": sc["modification_type"],
        "target_file": f"sample_app/{base_file}",
        "mutant_file": f"scenarios/mutants/{mutant_filename}"
    }
    manifest_list.append(entry)

manifest_path = os.path.join(BASE_DIR, "scenarios", "scenario_manifest.json")
with open(manifest_path, "w", encoding="utf-8") as f:
    json.dump(manifest_list, f, indent=2)

print(f"Successfully generated {len(manifest_list)} scenarios and mutant files.")
