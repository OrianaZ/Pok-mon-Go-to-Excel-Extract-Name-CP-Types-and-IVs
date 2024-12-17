import pandas as pd

def load_valid_pokemon_types(file_path="ValidatePGO/pokemon_types.csv"):
    df = pd.read_csv(file_path)
    pokemon_types = {}
    
    for _, row in df.iterrows():
        type1 = row['Type1'].strip()  
        types = [type1]
        
        if pd.notna(row['Type2']):
            type2 = row['Type2'].strip()
            types.append(type2)
        
        if row['Name'] in pokemon_types:
            pokemon_types[row['Name']].append(types)
        else:
            pokemon_types[row['Name']] = [types]
    return pokemon_types

def validate_pokemon_types(input_file):
    valid_pokemon_types = load_valid_pokemon_types()
    df = pd.read_excel(input_file)

    df['Validation'] = "Valid"

    for index, row in df.iterrows():
        pokemon = row['Name']
        type1 = row['Main Type'].strip()
        type2 = row['Secondary Type'].strip() if pd.notna(row['Secondary Type']) else None

        if pokemon not in valid_pokemon_types:
            df.at[index, 'Validation'] = "Invalid Pokémon"
            continue

        valid_types = valid_pokemon_types[pokemon]

        valid_combination_found = False

        for valid_type_combo in valid_types:
            valid_type1 = valid_type_combo[0]
            valid_type2 = valid_type_combo[1] if len(valid_type_combo) > 1 else None
            
            if type1 == valid_type1:
                if type2 is None or type2 == valid_type2:
                    valid_combination_found = True
                    break

        if not valid_combination_found:
            validation_message = ""
            if type1 not in [valid_type_combo[0] for valid_type_combo in valid_types]:
                validation_message = f"Invalid Main Type: {type1}"
            if type2 and type2 not in [valid_type_combo[1] for valid_type_combo in valid_types if len(valid_type_combo) > 1]:
                if validation_message:
                    validation_message += f", Invalid Secondary Type: {type2}"
                else:
                    validation_message = f"Invalid Secondary Type: {type2}"
            df.at[index, 'Validation'] = validation_message

    output_file = input_file.replace('.xlsx', '_validated.xlsx')
    df.to_excel(output_file, index=False)
    print(f"Validation complete. Results saved to {output_file}")

file_path = "ValidatePGO/pokemon_data.xlsx"
validate_pokemon_types(file_path)
