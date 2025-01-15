# Meal Rankings Dashboard

A Streamlit-powered web application for analyzing and visualizing meal data with advanced Bayesian ranking algorithms.

 **[View Live App](https://food-unity-meal.streamlit.app/)**

## Features

### Meal Rankings Page
- Interactive Bayesian average ranking system
- Customizable calculation parameters
- Advanced filtering options:
  - Cuisine type
  - Dietary preferences
  - Calorie range
  - Price range
- Grid-based meal display with detailed information
- Image optimization using imgix

### Statistics & Insights Page
- 3D visualization of meal value analysis
- Interactive data filtering
- Distribution analysis of ratings and reviews
- Price vs. calories correlation
- Cuisine popularity metrics
- Summary statistics

## Data Format

The application expects a `meals.csv` file with the following columns:
- name
- chef_name
- rating
- review_count
- price
- calories
- cuisines (comma-separated)
- specifications (pipe-separated)
- image_url
- url
- description
- is_celebrity_chef

##  Usage

1. Navigate between pages using the sidebar
2. Adjust ranking parameters and filters as needed
3. Explore meal details by expanding individual meal cards
4. Analyze trends and insights in the Statistics page

##  How Rankings Work

Uses Bayesian average considering:
- Actual rating
- Review count
- Prior belief
- Minimum reviews threshold