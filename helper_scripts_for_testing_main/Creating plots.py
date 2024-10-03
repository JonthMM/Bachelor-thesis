# Importing pandas for data manipulation and analysis
import pandas as pd

# Importing geopandas for working with geospatial data, including shapefiles
import geopandas as gpd

# Creates the plots from the data handled by (geo)pandas
import matplotlib.pyplot as plt

# Path to the shapefile containing the information we need fo the plot
shapefile_path = r'D:\Uni\Bachelorarbeit\complete_paper_points\re-analysed paper points with forest\re-analysed_paper_points_with_forest.shp'


def create_bar_chart(shapefile_path, chart_type):
    """
    Creates a bar chart based on the provided chart type (MODIS or Drought).
    https://pandas.pydata.org/docs/user_guide/10min.html#grouping
    https://pandas.pydata.org/docs/user_guide/10min.html#categoricals
    https://pandas.pydata.org/docs/user_guide/10min.html#grouping
    https://geopandas.org/en/stable/docs/user_guide/data_structures.html#geodataframe
    https://geopandas.org/en/stable/docs/user_guide/io.html#reading-and-writing-files
    https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.xlabel.html#matplotlib.pyplot.xlabel
    https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.ylabel.html#matplotlib-pyplot-ylabel
    https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.title.html#matplotlib-pyplot-title
    https://www.geeksforgeeks.org/matplotlib-pyplot-legend-in-python/
    https://www.geeksforgeeks.org/matplotlib-pyplot-xticks-in-python/
    https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.tight_layout.html#matplotlib.pyplot.tight_layout
    https://www.geeksforgeeks.org/matplotlib-pyplot-savefig-in-python/
    https://www.geeksforgeeks.org/matplotlib-pyplot-show-in-python/

    Args:
        shapefile_path (str): The path to the shapefile.
        chart_type (str): Either 'MODIS' or 'Drought' to specify which chart to generate.

    Returns:
        None
    """

    gdf = gpd.read_file(shapefile_path)

    # For drought quantification keywoprds out of the studies and SPEI drought categories
    if chart_type == 'Drought':
        # Group the data by 'dr_quanti' and 'Category', count occurrences for Drought chart
        category_counts = gdf.groupby(['dr_quanti', 'Category']).size().unstack(fill_value=0)
        # X-axis text
        xlabel = 'Given drought category'
        # Title of the plot
        title = 'Distribution of SPEI drought categories in correlation with the given drought quantifications from the studies'
        # Path where the plot is going to be saved
        output_file_path = r'D:\Uni\Bachelorarbeit\Plots\Bar chart for correlation of SPEI drought category and the given drought quantifications of the studies.jpg'

    # For MODIS categories and SPEI drought categories
    elif chart_type == 'MODIS':
        # Group the data by 'MODIS' and 'Category', count occurrences for MODIS chart
        category_counts = gdf.groupby(['MODIS', 'Category']).size().unstack(fill_value=0)
        # X-axis text
        xlabel = 'MODIS category'
        # Title of the plot
        title = 'Distribution of SPEI drought categories within each MODIS category'
        # Path where the plot is going to be saved
        output_file_path = r'D:\Uni\Bachelorarbeit\Plots\Bar chart for correlation MODIS classes and SPEI drought categories.jpg'
    # If there is another keyword given for plot creation
    else:
        raise ValueError("Invalid chart_type. Must be 'Drought' or 'MODIS'.")

    # Change the label for 'Other' category, so it is not too long
    category_counts.rename(
        index={"Other (Mangrove Forest, Open Shrubland, Savannas, Permanent Wetlands, ...)": "Other"}, inplace=True)

    # Define the colors for SPEI drought categories so they match
    color_mapping = {
        'no drought (+1 < SPEI)': '#0000FF',  # blue
        'near normal conditions (-1 < SPEI < +1)': '#ADD8E6',  # light blue
        'moderately dry (-1.5 < SPEI <= -1)': '#FFA500',  # orange
        'severely dry (-2 < SPEI <= -1.5)': '#FF4500',  # red-orange
        'extremely dry (SPEI <= -2)': '#8B0000'  # dark red
    }

    # Reindex the DataFrame using only the categories that exist in the data
    category_order = [
        "no drought (+1 < SPEI)",
        "near normal conditions (-1 < SPEI < +1)",
        "moderately dry (-1.5 < SPEI <= -1)",
        "severely dry (-2 < SPEI <= -1.5)",
        "extremely dry (SPEI <= -2)"
    ]

    # Reindex the DataFrame with the correct category order (if they exist)
    existing_categories = [cat for cat in category_order if cat in category_counts.columns]
    category_counts = category_counts[existing_categories]

    # Sorting the created pivot table by total occurrences (sum of rows), from most to least
    category_counts_sorted = category_counts.loc[
        category_counts.sum(axis=1).sort_values(ascending=False).index]

    # Sorting the columns by total occurrences (sum of columns) for legend and data
    category_sums = category_counts_sorted.sum(axis=0)
    category_counts_sorted = category_counts_sorted[category_sums.sort_values(ascending=False).index]

    # Custom legend labels with counts included for clearer overview
    legend_labels_with_counts = [f"{category} [{count}]" for category, count in
                                 zip(category_sums.index, category_sums.values)]

    # Replace <= with ≤ only in the legend labels for better presentation
    legend_labels_with_counts = [label.replace('<=', '≤') for label in legend_labels_with_counts]

    # Sorting legend labels based on the counts in descending order
    sorted_legend_labels_with_counts = sorted(legend_labels_with_counts, key=lambda x: int(x.split('[')[1][:-1]),
                                              reverse=True)

    # Generate the plot with sorted categories and the customized colors
    category_counts_sorted.plot(kind='bar', stacked=True, figsize=(12, 6),
                                color=[color_mapping[cat] for cat in category_counts_sorted.columns])

    # Add titles and labels that were defined before depending on case
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel('Number of papers')

    # Place the sorted legend with counts inside the plot
    plt.legend(sorted_legend_labels_with_counts, title="SPEI drought category", loc='upper right')

    # Rotate x-axis labels for readability and better plot-text ratio
    plt.xticks(rotation=45, ha='right')

    # Save the plot as a JPG file to use it in the thesis
    plt.tight_layout()
    plt.savefig(output_file_path, format='jpg')

    # Optionally display the plot (for finetuning so adjusting is easier)
    plt.show()

# Generate the drought quantification keyword chart
create_bar_chart(shapefile_path, 'Drought')

# Generate the MODIS category chart
create_bar_chart(shapefile_path, 'MODIS')