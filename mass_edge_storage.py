from neo import store_conversion, ConversionRelation

temp_forms = {'question_1': {'from_unit': 'inches', 'to_unit': 'centimeters', 'formula': 'centimeters = inches * 2.54'}, 
              'question_2': {'from_unit': 'feet', 'to_unit': 'meters', 'formula': 'meters = feet * 0.3048'}, 
              'question_3': {'from_unit': 'miles', 'to_unit': 'kilometers', 'formula': 'kilometers = miles * 1.60934'}, 
              'question_4': {'from_unit': 'pounds', 'to_unit': 'kilograms', 'formula': 'kilograms = pounds * 0.45359237'}, 
              'question_4': {'from_unit': 'pounds', 'to_unit': 'kilograms', 'formula': 'kilograms = pounds * 0.45359237'}, 
              'question_5': {'from_unit': 'gallons', 'to_unit': 'liters', 'formula': 'liters = gallons * 3.78541'}, 
              'question_6': {'from_unit': 'quarts', 'to_unit': 'liters', 'formula': 'liters = quarts * 0.946353'}}

def save_all_conversions(formula_dict: dict):
    """
    Iterates through the formula dictionary and tries storing
    each conversion in Neo4j. Errors are logged but do NOT stop execution.
    """
    for key, entry in formula_dict.items():
        print(f"\nProcessing {key} ...")

        try:
            # 1. Validate using Pydantic
            relation = ConversionRelation(**entry)

        except Exception as e:
            print(f"[SKIP] Invalid entry for {key}: {e}")
            continue

        try:
            # 2. Try storing this conversion
            store_conversion(relation)

        except Exception as e:
            print(f"[SKIP] Neo4j storage failed for {key}: {e}")
            continue

    print("\nAll conversions processed.")

#--------------------------------------------------------------------------
import asyncio

async def save_all_conversions_async(formula_dict: dict):
    tasks = []  # list of async tasks

    for key, entry in formula_dict.items():
        print(f"\nProcessing {key} ...")

        # Validate
        try:
            relation = ConversionRelation(**entry)
        except Exception as e:
            print(f"[SKIP] Invalid entry for {key}: {e}")
            continue

        # Create async task for each store operation
        tasks.append(
            asyncio.to_thread(store_conversion, relation)
        )

    # Run all conversions concurrently
    results = await asyncio.gather(*tasks, return_exceptions=True)

    # Log failed ones
    for idx, result in enumerate(results):
        if isinstance(result, Exception):
            print(f"[SKIP] Task {idx} failed: {result}")

    print("\nAll conversions processed (async).")
