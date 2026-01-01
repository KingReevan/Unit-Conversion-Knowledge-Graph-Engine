
from neo4j import GraphDatabase
from pydantic import BaseModel
from typing import List, Optional
from engine import evaluate_formula, parse_formula # your function
from sympy import symbols

driver = GraphDatabase.driver(
    "bolt://localhost:7687",
    auth=("neo4j", "reevantheking19$$")
)

# -----------------------------
# Pydantic Models
# -----------------------------

class ConversionPath(BaseModel):
    path: List[str]
    edge_formulas: List[str]


# -----------------------------
# Neo4j Query: Shortest Path
# -----------------------------

def find_shortest_conversion_path(unit1: str, unit2: str):
    """
    Returns:
        nodes: list of Unit node names
        formulas: list of formula strings on the edges or None if no path.
    """

    query = """
        MATCH (start:Unit {name: $u1}), (end:Unit {name: $u2})
        OPTIONAL MATCH p = shortestPath((start)-[:CONVERTS_TO*]->(end))
        RETURN 
            CASE WHEN p IS NULL THEN NULL ELSE [n IN nodes(p) | n.name] END AS nodes,
            CASE WHEN p IS NULL THEN NULL ELSE [r IN relationships(p) | r.formula] END AS formulas
    """

    with driver.session() as session:
        result = session.run(query, u1=unit1.lower(), u2=unit2.lower()).single()

    if result is None or result["nodes"] is None:
        return None

    print(result)

    return ConversionPath(
        path=result["nodes"],
        edge_formulas=result["formulas"]
    )





# -----------------------------
# Example Test
# -----------------------------

def run_algorithm() -> None:
    from_unit: str = input("Enter the unit you want to convert from: ")
    to_unit: str = input("Enter the unit you want to convert to: ")

    formulas = find_shortest_conversion_path(from_unit,to_unit)
    if formulas is None:
        print("Path between Units is not found")
        return
    
    value:int = int(input(f"Enter the value for {from_unit}: "))

    current_value = value
    current_unit = from_unit.lower()
    formula_num = 0

    for formula in formulas.edge_formulas:
        # Parse left-hand variable from the formula
        lhs_str, lhs, rhs_expr = parse_formula(formula)
        
        formula_num += 1
        # Provide the current unit value
        print(f"Formula {formula_num}:")
        print(formula)
        current_value = evaluate_formula(
            formula,
            **{current_unit: current_value}
        )
        print(f"Result {formula_num}: ", current_value)
        current_unit = lhs_str  # move to next unit

    print("Final Result: ")
    print(f"{value} {from_unit} = {current_value} {to_unit}")
    
    