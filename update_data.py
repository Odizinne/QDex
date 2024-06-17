import json
import os
import requests

# Define base directory for sprites
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SPRITES_DIR = os.path.join(BASE_DIR, 'sprites')

def fetch_pokemon_details(pokemon_index):
    """Fetch details for a specific Pokémon from the API and save sprites."""
    url = f"https://pokeapi.co/api/v2/pokemon/{pokemon_index}"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        species_url = data['species']['url']
        species_response = requests.get(species_url)
        
        if species_response.status_code == 200:
            species_data = species_response.json()

            # Fetch normal sprite
            sprite_url = data['sprites']['front_default']
            sprite_filename = f"pokemon_{pokemon_index}.png"
            sprite_path = os.path.join(SPRITES_DIR, sprite_filename)
            download_and_save_sprite(sprite_url, sprite_path)

            # Fetch shiny sprite if available
            shiny_sprite_path = None
            if 'front_shiny' in data['sprites'] and data['sprites']['front_shiny']:
                shiny_sprite_url = data['sprites']['front_shiny']
                shiny_sprite_filename = f"pokemon_{pokemon_index}_shiny.png"
                shiny_sprite_path = os.path.join(SPRITES_DIR, shiny_sprite_filename)
                download_and_save_sprite(shiny_sprite_url, shiny_sprite_path)
            
            pokemon_details = extract_pokemon_details(data, species_data)
            pokemon_details['sprite_path'] = f"./sprites/{sprite_filename}"
            pokemon_details['descriptions'] = fetch_pokemon_descriptions(species_data)
            pokemon_details['national_pokedex_number'] = species_data['id']

            # Fetch and calculate gender rate
            gender_rate = species_data.get('gender_rate', -1)
            if gender_rate == -1:
                pokemon_details['gender_rate'] = None  # No gender rate available
            else:
                female_rate = (gender_rate / 8) * 100  # Convert to percentage
                male_rate = 100 - female_rate
                pokemon_details['gender_rate'] = {
                    'female': round(female_rate),
                    'male': round(male_rate)
                }

            return pokemon_details
        else:
            print(f"Failed to retrieve species data for Pokemon index {pokemon_index}: {species_response.status_code}")
    else:
        print(f"Failed to retrieve data for Pokemon index {pokemon_index}: {response.status_code}")
    return None


def fetch_pokemon_descriptions(species_data):
    """Fetch Pokémon descriptions in all available languages."""
    descriptions = {}
    for entry in species_data['flavor_text_entries']:
        language = entry['language']['name']
        description = entry['flavor_text']
        if language not in descriptions:
            descriptions[language] = description
    return descriptions

def extract_pokemon_details(data, species_data):
    """Extract and structure Pokémon details from API response."""
    pokemon_details = {}

    names = species_data['names']
    pokemon_details['names'] = {entry['language']['name']: entry['name'] for entry in names}
    pokemon_details['species'] = species_data['name']

    pokemon_details['types'] = [poke_type['type']['name'] for poke_type in data['types']]
    pokemon_details['abilities'] = [ability['ability']['name'] for ability in data['abilities']]
    pokemon_details['stats'] = [{stat['stat']['name']: stat['base_stat']} for stat in data['stats']]
    pokemon_details['descriptions'] = fetch_pokemon_descriptions(species_data)

    return pokemon_details

def download_and_save_sprite(sprite_url, sprite_path):
    """Download sprite from URL and save it to sprite_path."""
    response = requests.get(sprite_url)
    if response.status_code == 200:
        with open(sprite_path, 'wb') as f:
            f.write(response.content)
        print(f"Saved sprite: {sprite_path}")
    else:
        print(f"Failed to download sprite from {sprite_url}")

def fetch_and_save_all_pokemon_details(limit=None, output_file="pokemon_details.json"):
    """Fetch and save details for all Pokémon up to the specified limit to a JSON file."""
    all_pokemon_details = {}
    pokemon_index = 1
    
    while True:
        if limit and pokemon_index > limit:
            break
        
        pokemon_details = fetch_pokemon_details(pokemon_index)
        if pokemon_details:
            all_pokemon_details[f"pokemon_{pokemon_index}"] = pokemon_details
            print(f"Fetched details for Pokemon index {pokemon_index}")
            pokemon_index += 1
        else:
            break 

    with open(output_file, 'w') as f:
        json.dump(all_pokemon_details, f, indent=4)
    
    print(f"Pokemon details have been saved to {output_file}.")

def fetch_and_save_abilities(limit=None, output_file="abilities.json"):
    """Fetch abilities data from the API up to the specified limit and save to a file."""
    abilities = {}
    i = 1
    while True:
        if limit and i > limit:
            break
        
        url = f"https://pokeapi.co/api/v2/ability/{i}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            ability_names = {entry['language']['name']: entry['name'] for entry in data['names']}
            abilities[data['name']] = ability_names
            print(f"Fetched data for Ability index {i}")
            i += 1
        else:
            print(f"Failed to retrieve data for Ability index {i}: {response.status_code}")
            break

    with open(output_file, 'w') as f:
        json.dump(abilities, f, indent=4)
    
    print(f"Abilities have been refreshed and saved to {output_file}.")

if __name__ == "__main__":
    if not os.path.exists(SPRITES_DIR):
        os.makedirs(SPRITES_DIR)
        
    fetch_and_save_all_pokemon_details(limit=151)
    #fetch_and_save_abilities(limit=10)
