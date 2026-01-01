import dspy
from dotenv import load_dotenv
from pydantic import BaseModel, field_validator

load_dotenv()

dspy.configure(
    lm=dspy.LM(
        model="openai/gpt-4o-mini",
    )
)

#Pydantics Models
class ExtractedUnits(BaseModel):
    from_unit: str
    to_unit: str


class FormulaResult(BaseModel):
    formula: str

#Signature to extract and validate conversion units, returns pydantic
class ExtractUnits(dspy.Module):
    def __init__(self):
        super().__init__()
        self.extract = dspy.Predict("question -> from_unit, to_unit")

    def forward(self, question: str):
        raw = self.extract(question=question)
        ext = ExtractedUnits.model_validate(raw.toDict())
        return ext


class AskFormula(dspy.Module):

    class FormulaSignature(dspy.Signature):
        """
        Task: Return a mathematical formula for converting one unit into another.
        IMPORTANT:
        - Always use FULL unit names (e.g., "meters per second", NOT "m/s").
        - Never abbreviate or shorten units.
        - Always return clean, readable unit names.
        - Always Use '*' for multiplication and '/' for Division and '**' for power. No other alternative is allowed.
        - Return formulas in such a way that I have to use less number of mathematical operations.
        - Always put the to_unit on the LHS and from_unit on the RHS of the equation.
        """
        from_unit: str = dspy.InputField(
            desc="The full unit name to convert FROM. Never abbreviated."
        )
        to_unit: str = dspy.InputField(
            desc="The full unit name to convert TO. Never abbreviated."
        )
        formula: str = dspy.OutputField(
            desc="The conversion formula using full unit names only. No abbreviations.",
            type=str
        )

    def __init__(self):
        super().__init__()
        self.predict = dspy.Predict(self.FormulaSignature)

    def forward(self, from_unit, to_unit):
        """
        Docstring for forward
        
        :param self: The AskFormula Instance
        :param from_unit: The unit to be converted from
        :param to_unit: The unit to be converted to
        """

        ExtractedUnits.model_validate({
            "from_unit": from_unit,
            "to_unit": to_unit
        })

        raw = self.predict(from_unit=from_unit, to_unit=to_unit)
        print(raw)

        # Validate output after LLM prediction
        validated = FormulaResult.model_validate(raw.toDict())
        return validated


ask_formula = AskFormula()


