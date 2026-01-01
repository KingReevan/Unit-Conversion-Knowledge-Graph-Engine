import dspy
from extract import ExtractUnits, ask_formula
from neo import lookup_conversion, store_conversion, ConversionRelation
from engine import evaluate_formula

#The pipeline
class KGAgent(dspy.Module):
    def __init__(self):
        super().__init__()
        self.extract_units = ExtractUnits()

    def forward(self, question: str) -> str:
        # STEP 1: Extract units
        units = self.extract_units(question)  #A pydantic instance is returned
        u1: str = units.from_unit
        u2: str = units.to_unit

        # STEP 2: Check the knowledge graph
        formula = lookup_conversion(u1, u2)

        if formula:
            print("Formula found in Knowledge Graph")
            choice = input("Do you want to use the formula now? (Y/n): ").strip().lower()
            if choice == "y":
                # Ask user for the input value
                var_name = formula.split("=")[1].strip().split()[0]  # extract 'centimeters'
                value = float(input(f"Enter value for {var_name}: "))

                result = evaluate_formula(formula, **{var_name: value})
                print(f"Result: {result} {u2}")

            return f"From the knowledge graph: {formula}"

        #ONE MORE STEP IN THE MIDDLE: IF THE EDGE IS MISSING BUT BOTH NODES ARE PRESENT IN GRAPH THEN USE HOPPING ALGORITHM
        
        # STEP 3: If missing → Ask LLM for the formula
        result = ask_formula(u1, u2)  # returns an object
        
        # STEP 4: Store it in the knowledge graph
        data = ConversionRelation.model_validate(
        {
                "from_unit":u1,
                "to_unit": u2,
                "formula": result.formula,
                "author": "Reevan"
            }
        )

        store_conversion(data)

        return f"I learned this rule from GPT: {result.formula}"


agent = KGAgent()


