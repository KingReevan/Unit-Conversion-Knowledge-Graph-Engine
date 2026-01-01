import asyncio
from extract import ExtractUnits
from mass_edge_storage import save_all_conversions_async  
from generate_questions import GeneratedQuestions, genq_async   
from extract import ExtractUnits, ask_formula  
from timing import timeit

extractor = ExtractUnits()

@timeit
async def async_training_loop(cycles: int, questions_per_cycle: int) -> None:
    print(f"Starting async training for {cycles} cycles...\n")

    for i in range(cycles):
        print(f"\n--- Cycle {i+1} ---")

        # STEP 1: Generate questions asynchronously
        generated_questions: GeneratedQuestions = await genq_async(
            count=questions_per_cycle,
            prompt="Give me unit conversion questions using simple, commonly used units."
        )
        print(generated_questions.questions)

        # STEP 2: Extract units (sync ok)
        unit_tasks = []
        unit_pairs = {}
        for key, q in generated_questions.questions.items():
            result = extractor(q)
            unit_pairs[key] = {
                "from_unit": result.from_unit,
                "to_unit": result.to_unit
            }

        print(unit_pairs)

        # STEP 3: Generate conversion formulas concurrently
        tasks = []
        for key, pair in unit_pairs.items():
            tasks.append(
                asyncio.to_thread(
                    ask_formula,
                    pair["from_unit"],
                    pair["to_unit"]
                )
            )

        formula_results = await asyncio.gather(*tasks)

        # Format into dict
        formulas = {}
        for (key, pair), result in zip(unit_pairs.items(), formula_results):
            formulas[key] = {
                "from_unit": pair["from_unit"],
                "to_unit": pair["to_unit"],
                "formula": result.formula
            }

        print(formulas)

        # STEP 4: Save everything to Neo4j asynchronously
        await save_all_conversions_async(formulas)

    print("Async training complete.")

