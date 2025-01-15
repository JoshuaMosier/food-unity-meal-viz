import json
import csv
import pandas as pd
from typing import Dict, List, Any

def extract_meal_data(meal: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract relevant information from a meal entry.
    """
    # Get specifications as a list
    specifications = [spec['label'] for spec in meal.get('specifications_detail', [])]
    
    # Get ingredients as a list
    ingredients = [ing['name'] for ing in meal.get('ingredients_data', [])]
    
    # Get cuisines as a comma-separated string
    cuisines = ', '.join(meal.get('cuisines', []))
    
    # Create URL from SKU
    meal_url = f"https://www.cookunity.com/meals/{meal['sku'].lower().replace('ny-', '')}"
    
    # Create full image URL if path is relative
    image_url = meal['image']
    if image_url and image_url.startswith('/'):
        image_url = f"https://www.cookunity.com{image_url}"
    
    # Create full banner URL if path is relative
    banner_url = meal['bannerpic']
    if banner_url and banner_url.startswith('/'):
        banner_url = f"https://www.cookunity.com{banner_url}"
    
    return {
        'meal_id': meal['entity_id'],
        'name': meal['name'],
        'description': meal['short_description'],
        'cuisines': cuisines,
        'calories': meal['calories'],
        'price': meal['price'],
        'premium_fee': meal['premium_fee'],
        'meat_type': meal['meat_type'],
        'chef_id': meal['chef_id'],
        'chef_name': f"{meal['chef_firstname']} {meal['chef_lastname']}",
        'is_celebrity_chef': meal['is_celebrity_chef'],
        'rating': meal['stars'],
        'review_count': meal['reviews'],
        'stock': meal['stock'],
        'in_stock': meal['inStock'],
        'specifications': '|'.join(specifications),
        'ingredients': '|'.join(ingredients),
        'url': meal_url,
        'image_url': image_url,
        'image_path': meal['image_path'],
        'category_id': meal['category_id'],
        'feature': meal['feature'],
        'banner_pic': banner_url,
        'weight': meal['weight'],
        'warning': meal['warning'],
        'sidedish': meal['sidedish']
    }

def process_menu_data(json_file: str, output_csv: str) -> None:
    """
    Process the menu JSON file and create a CSV with relevant information.
    
    Args:
        json_file: Path to input JSON file
        output_csv: Path for output CSV file
    """
    # Read JSON file
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Extract meals data
    meals = data['data']['sampleMenuByStore']['meals']
    
    # Process each meal
    processed_meals = [extract_meal_data(meal) for meal in meals]
    
    # Convert to DataFrame for easy CSV handling
    df = pd.DataFrame(processed_meals)
    
    # Save to CSV
    df.to_csv(output_csv, index=False)
    
    # Print summary statistics
    print(f"\nProcessed {len(processed_meals)} meals")
    print("\nSummary Statistics:")
    print(f"Average calories: {df['calories'].mean():.1f}")
    print(f"Average rating: {df['rating'].mean():.2f}")
    print(f"Celebrity chefs: {df['is_celebrity_chef'].sum()}")
    print(f"Unique cuisines: {len(set(df['cuisines'].str.split(', ').sum()))}")
    print(f"Most common meat types:")
    print(df['meat_type'].value_counts().head())

if __name__ == "__main__":
    process_menu_data('recipes.json', 'meals.csv')