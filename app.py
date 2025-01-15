import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.figure_factory as ff
from urllib.parse import urlparse
import re

# Set page config for wide layout
st.set_page_config(layout="wide")

# Add this near the top of your file, after st.set_page_config
st.markdown("""
<style>
.meal-name {
    height: 5rem;
    overflow: hidden;
    text-overflow: ellipsis;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
}
</style>
""", unsafe_allow_html=True)

# Load and prepare data
@st.cache_data
def load_data():
    df = pd.read_csv('meals.csv')
    # Fill NaN values for review count and rating
    df['review_count'] = df['review_count'].fillna(0)
    df['rating'] = df['rating'].fillna(0)
    
    # Filter out items with 0 ratings
    df = df[df['rating'] > 0]
    
    # Handle price data - mark missing, zero, or unrealistically low prices as NaN
    df['price'] = df['price'].mask(df['price'] < 7, pd.NA)
    
    # Transform image URLs with imgix parameters for optimization
    df['image_url'] = df['image_url'].apply(lambda x: x.replace(
        'www.cookunity.com', 
        'cu-media.imgix.net'
    ) + '?height=500&width=500&fit=crop&format=webp&quality=90' if isinstance(x, str) else x)
    
    return df

# Add caching for Bayesian calculations
@st.cache_data
def calculate_bayesian_ratings(df, C, m):
    R = df['rating']
    v = df['review_count']
    bayesian_avg = (v * R + m * C) / (v + m)
    return bayesian_avg

def transform_image_url(url):
    if not url or pd.isna(url):
        st.write(f"Skipping invalid URL: {url}")
        return None
        
    try:
        meal_id_match = re.search(r'/meals/(\d+)/', url)
        if meal_id_match:
            meal_id = meal_id_match.group(1)
            filename = url.split('/')[-1]
            transformed_url = f"https://cu-media.imgix.net/meal-service/meals/{meal_id}/main_image/{filename}"
            return transformed_url
        else:
            st.write(f"No meal ID found in URL: {url}")
            return None
    except Exception as e:
        st.write(f"Error transforming URL {url}: {str(e)}")
        return None

# Load data
df = load_data()

# Create pages
pages = {
    "Meal Rankings": "rankings",
    "Statistics & Insights": "stats"
}
page = st.sidebar.radio("Navigate", pages.keys())

if page == "Meal Rankings":
    st.title("Meal Rankings - Bayesian Average")
    
    # Sidebar controls
    st.sidebar.header("Calculation Parameters")
    global_mean_rating = df['rating'].mean()

    C = st.sidebar.number_input(
        "Prior belief (C) - Global mean rating",
        min_value=1.0,
        max_value=5.0,
        value=float(global_mean_rating),
        help="The assumed average rating for items with few reviews"
    )

    m = st.sidebar.number_input(
        "Minimum reviews weight (m)",
        min_value=1,
        max_value=2000,
        value=100,
        help="Higher values give more weight to the prior belief"
    )

    # Calculate Bayesian average using cached function
    df['bayesian_avg'] = calculate_bayesian_ratings(df, C, m)

    # Enhanced meal display
    sorted_meals = df.sort_values('bayesian_avg', ascending=False)
    
    # Add display options
    display_options = st.columns(4)
    with display_options[0]:
        cuisine_filter = st.multiselect(
            "Filter by Cuisine",
            options=sorted(set([cuisine.strip() 
                              for cuisines in df['cuisines'].dropna() 
                              for cuisine in cuisines.split(',')]))
        )
    with display_options[1]:
        diet_filter = st.multiselect(
            "Dietary Preferences",
            options=sorted(set([spec.strip() 
                              for specs in df['specifications'].dropna() 
                              for spec in specs.split('|')]))
        )
    with display_options[2]:
        calorie_range = st.slider(
            "Calorie Range",
            int(df['calories'].min()),
            int(df['calories'].max()),
            (int(df['calories'].min()), int(df['calories'].max()))
        )
    with display_options[3]:
        price_range = st.slider(
            "Price Range ($)",
            float(df['price'].min()),
            float(df['price'].max()),
            (float(df['price'].min()), float(df['price'].max()))
        )

    # Apply filters
    if cuisine_filter:
        sorted_meals = sorted_meals[sorted_meals['cuisines'].str.contains('|'.join(cuisine_filter), na=False)]
    if diet_filter:
        sorted_meals = sorted_meals[sorted_meals['specifications'].str.contains('|'.join(diet_filter), na=False)]
    sorted_meals = sorted_meals[
        (sorted_meals['price'] >= price_range[0]) & 
        (sorted_meals['price'] <= price_range[1]) &
        (sorted_meals['calories'] >= calorie_range[0]) &
        (sorted_meals['calories'] <= calorie_range[1])
    ]

    # Display meals in a grid
    cols_per_row = 4
    for i in range(0, len(sorted_meals), cols_per_row):
        row = st.columns(cols_per_row)
        for j, col in enumerate(row):
            if i + j < len(sorted_meals):
                meal = sorted_meals.iloc[i + j]
                with col:
                    with st.container():
                        # Debug image URLs
                        if pd.notna(meal['image_url']):
                            st.image(meal['image_url'], use_column_width=True)
                        else:
                            st.write("⚠️ No image available")
                            st.write(f"Original URL in data: {meal['url']}")
                        
                        st.markdown(f"""
                            <div class="meal-name">
                                <h3>{meal['name']}</h3>
                            </div>
                        """, unsafe_allow_html=True)
                        
                        # Create columns for metrics with adjusted widths
                        metric_cols = st.columns([1, 1, 1])  # Now just 3 columns
                        with metric_cols[0]:
                            st.metric("Score", f"{meal['bayesian_avg']:.2f}")
                        with metric_cols[1]:
                            st.metric("Rating", f"{meal['rating']:.1f}")
                        with metric_cols[2]:
                            st.metric("Reviews", f"{int(meal['review_count'])}")
                        
                        # Move details into expander
                        with st.expander("Meal Details"):
                            # Display meal details
                            st.markdown(f"**Price:** ${meal['price']:.2f}")
                            st.markdown(f"**Chef:** {meal['chef_name']}")
                            st.markdown(f"**Calories:** {meal['calories']}")
                            
                            # Display cuisines and specifications as tags
                            st.markdown("**Cuisines:**")
                            cuisines = meal['cuisines'].split(',')
                            st.markdown(' '.join([f"`{cuisine.strip()}`" for cuisine in cuisines]))
                            
                            st.markdown("**Features:**")
                            specs = meal['specifications'].split('|')
                            st.markdown(' '.join([f"`{spec.strip()}`" for spec in specs]))
                            
                            # Show description if available
                            if 'description' in meal and pd.notna(meal['description']):
                                st.markdown(f"_{meal['description']}_")
                            
                            # Add a link to the original
                            if pd.notna(meal['url']):
                                st.markdown(f"[View Details]({meal['url']})")
                        
                        st.divider()

else:  # Statistics & Insights page
    st.title("Statistics & Insights")
    
    # Set default values for C and m
    global_mean_rating = df['rating'].mean()
    C = global_mean_rating  # Prior belief
    m = 100  # Minimum reviews weight
    
    # Calculate Bayesian average for coloring
    df['bayesian_avg'] = calculate_bayesian_ratings(df, C, m)
    
    col1, col2 = st.columns(2)
    
    # Add this new section before the existing columns
    st.subheader("Meal Value Analysis")
    
    # Create 3D scatter plot
    valid_price_data = df.dropna(subset=['price'])
    fig_3d = px.scatter_3d(
        valid_price_data,
        x='calories',
        y='price',
        z='bayesian_avg',
        color='bayesian_avg',
        hover_data=['name', 'chef_name'],
        title='Meal Value Analysis (3D)',
        labels={
            'calories': 'Calories',
            'price': 'Price ($)',
            'bayesian_avg': 'Rating Score'
        },
        color_continuous_scale='viridis',
        height=800
    )
    
    # Customize the 3D plot
    fig_3d.update_traces(
        marker=dict(size=5),
        hovertemplate="<br>".join([
            "Meal: %{customdata[0]}",
            "Chef: %{customdata[1]}",
            "Calories: %{x}",
            "Price: $%{y:.2f}",
            "Score: %{z:.2f}"
        ])
    )
    
    # Add value score calculation
    valid_price_data['value_score'] = (valid_price_data['bayesian_avg'] / valid_price_data['price']) * 1000
    
    # Add filters for interactive analysis
    col_filter1, col_filter2, col_filter3 = st.columns(3)
    with col_filter1:
        min_rating = st.slider("Minimum Rating Score", 
                             float(valid_price_data['bayesian_avg'].min()), 
                             float(valid_price_data['bayesian_avg'].max()), 
                             float(valid_price_data['bayesian_avg'].mean()))
    with col_filter2:
        max_price = st.slider("Maximum Price ($)", 
                            float(valid_price_data['price'].min()), 
                            float(valid_price_data['price'].max()), 
                            float(valid_price_data['price'].max()))
    with col_filter3:
        max_calories = st.slider("Maximum Calories", 
                               float(valid_price_data['calories'].min()), 
                               float(valid_price_data['calories'].max()), 
                               float(valid_price_data['calories'].max()))
    
    # Filter and display top value meals
    filtered_meals = valid_price_data[
        (valid_price_data['bayesian_avg'] >= min_rating) &
        (valid_price_data['price'] <= max_price) &
        (valid_price_data['calories'] <= max_calories)
    ].sort_values('value_score', ascending=False)
    
    st.plotly_chart(fig_3d, use_container_width=True)
    
    # Display top value meals based on filters
    st.subheader("Top Value Meals (Based on Filters)")
    if not filtered_meals.empty:
        for _, meal in filtered_meals.head(10).iterrows():
            with st.expander(f"{meal['name']} (Value Score: {meal['value_score']:.1f})"):
                st.write(f"• Rating Score: {meal['bayesian_avg']:.2f}")
                st.write(f"• Price: ${meal['price']:.2f}")
                st.write(f"• Calories: {meal['calories']}")
                st.write(f"• Chef: {meal['chef_name']}")
    else:
        st.write("No meals match the selected criteria.")
    
    with col1:
        # Rating Distribution
        fig_rating = px.histogram(
            df,
            x="rating",
            title="Distribution of Ratings",
            nbins=100,
            color_discrete_sequence=['#1f77b4']
        )
        st.plotly_chart(fig_rating, use_container_width=True)
        
        # Calories vs Rating with Bayesian coloring
        fig_calories = px.scatter(
            df,
            x="calories",
            y="rating",
            color="bayesian_avg",
            title="Calories vs Rating (colored by Bayesian Score)",
            trendline="ols",
            hover_data=['name'],
            color_continuous_scale="viridis"
        )
        st.plotly_chart(fig_calories, use_container_width=True)

    with col2:
        # Review Count Distribution
        fig_reviews = px.histogram(
            df,
            x="review_count",
            title="Distribution of Review Counts",
            nbins=100,
            color_discrete_sequence=['#2ca02c']
        )
        st.plotly_chart(fig_reviews, use_container_width=True)
        
        # Price vs Calories with Bayesian coloring
        valid_price_data = df.dropna(subset=['price'])
        fig_price_cal = px.scatter(
            valid_price_data,
            x="calories",
            y="price",
            color="bayesian_avg",
            title="Price vs Calories (colored by Bayesian Score)",
            trendline="ols",
            hover_data=['name'],
            labels={'price': 'Price ($)', 'calories': 'Calories'},
            color_continuous_scale="viridis"
        )
        st.plotly_chart(fig_price_cal, use_container_width=True)
        
        # Top Cuisines
        cuisines = df['cuisines'].str.split(', ').explode().value_counts()
        fig_cuisines = px.bar(
            x=cuisines.index,
            y=cuisines.values,
            title="Most Common Cuisines",
            labels={'x': 'Cuisine', 'y': 'Count'}
        )
        st.plotly_chart(fig_cuisines, use_container_width=True)

    # Additional Statistics
    st.subheader("Summary Statistics")
    col3, col4, col5 = st.columns(3)
    
    with col3:
        st.metric("Average Rating", f"{df['rating'].mean():.2f}")
        st.metric("Median Calories", f"{df['calories'].median():.0f}")
    
    with col4:
        st.metric("Average Reviews", f"{df['review_count'].mean():.0f}")
        st.metric("Total Meals", len(df))
    
    with col5:
        st.metric("Celebrity Chefs", df['is_celebrity_chef'].sum())
        # Format price with fewer decimal places and ensure valid prices
        valid_prices = df['price'].dropna()
        avg_price = valid_prices.mean()
        st.metric("Average Price", f"${avg_price:.1f}")

# Add explanation in sidebar
st.sidebar.markdown("""
### How it works
The Bayesian average combines:
- The meal's actual rating
- Number of reviews
- Prior belief (C)
- Minimum reviews weight (m)

This helps balance between:
- Meals with few but high ratings
- Meals with many reviews but lower ratings
""") 