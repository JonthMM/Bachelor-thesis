# Importing pandas for data manipulation and analysis and and giving it the alias pd for further usage
import pandas as pd

# Importing geopandas for working with geospatial data, including shapefiles and giving it the alias geopd for further usage
import geopandas as geopd

# Creates the plots from the data handled by (geo)pandas by using patplotlib.pyplot and giving it the alias plot for further usage
import matplotlib.pyplot as plot
import matplotlib.patches as mpatches


# Path to the shapefile containing the information needed for all plots depending on the re-analysis data
reanalysis_shapefile_path = r"D:\Uni\Bachelorarbeit\complete_paper_points\re-analysed paper points with forest\re-analysed_paper_points_with_forest.shp"

all_studies_shapefile_path = (
    r"D:\Uni\Bachelorarbeit\complete_paper_points\complete_paper_points_with_forest.shp"
)

# Path to the Excel file containing all data
excel_file_path = r"D:\Uni\Bachelorarbeit\2024Apr_Mana_Review_v2i - paper_coords_area_years_plotkeywords_speireanalysis_month_finished.xlsx"


# Probably not needed since a pie chart looks way better and has a better overview for this type of analysis
def create_drought_keywords_bar_chart(shape_or_excel_file_path, chart_type):
    """
    Generates a stacked bar chart to visualize the distribution of drought quantification keywords, currently only with
    each MODIS forest type from a given dataset.
    This function is used for bar charts with the given drought quantification keywords from the papers
    The function is designed to combine bar chart creation logic for different cases which all have
    "drought quantification keyword for plots" as stacked bars into a single function.
    This allows for easy extension if more bar charts are needed in the future from the same shapefile data,
    without requiring the creation of additional functions.


    Args:
        shape_or_excel_file_path (str): The path to the Excel file (.xlsx) or shapefile (.shp) to be used for data extraction.
        chart_type (str): Specifies the type of bar chart to generate. Options are "Drought"
                          (correlates SPEI drought categories with drought quantification keywords)
                          or "MODIS SPEI" (correlates SPEI drought categories with MODIS forest types).

    Returns:
        None: The function saves the generated bar chart as a JPG image.
    """

    # Read the given shapefile for all pie chart cases using geopandas read_file() method and storing it as geodataframe
    # https://geopandas.org/en/stable/docs/user_guide/data_structures.html#geodataframe
    # https://geopandas.org/en/stable/docs/user_guide/io.html#reading-and-writing-files
    complete_gdf = geopd.read_file(shape_or_excel_file_path)

    # Clean up the "drought quantification keyword for plots" to remove quotes (because python gives an error for "dry" if there are quotes) and extra spaces
    # https://pandas.pydata.org/docs/reference/api/pandas.Series.str.strip.html
    # https://pandas.pydata.org/docs/reference/api/pandas.Series.str.replace.html
    complete_gdf["drouquanti"] = (
        complete_gdf["drouquanti"].str.strip().str.replace('"', "")
    )

    # For MODIS categories and SPEI drought categories
    if chart_type == "MODIS drought keyword":
        # Grouping the data by "MODIS" and "dr_quanti" to count occurrences of the drought quantifications
        # https://pandas.pydata.org/docs/user_guide/10min.html#grouping
        # https://note.nkmk.me/en/python-pandas-len-shape-size/#get-the-number-of-elements-dfsize
        # https://www.statology.org/pandas-unstack/
        drought_keywords_counts = (
            complete_gdf.groupby(["forest", "drouquanti"]).size().unstack(fill_value=0)
        )

        # X-axis text
        xaxisdescription = "Forest type"
        # Title of the plot
        title = "Distribution of given drought quantification keywords within each MODIS category from all paper locations"
        # Path where the plot is going to be saved
        output_file_path = r"D:\Uni\Bachelorarbeit\Plots\NEW Bar chart for correlation between MODIS classes and given drought quantification keywords from complete paper points shapefile.jpg"

    # For the (currently only) case with MODIS forest cover on the X-Axis and the given drought keywords as stacked bars
    if chart_type in ["MODIS drought keyword"]:
        # Change the label for "Other" category, so it is not too long (only for bar plots with MODIS involved)
        # https://pandas.pydata.org/docs/user_guide/basics.html#renaming-mapping-labels
        drought_keywords_counts.rename(
            index={
                "Other (Mangrove Forest, Open Shrubland, Savannas, Permanent Wetlands, ...)": "Other"
            },
            inplace=True,
        )

        # Sorting the created pivot table by total occurrences (sum of rows), from most to least in descending order for all stacked bar plots for the custom legend
        # https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.loc.html#pandas-dataframe-loc
        # https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.sort_values.html
        # https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.sort_values.html
        drought_keywords_counts_sorted = drought_keywords_counts.loc[
            drought_keywords_counts.sum(axis=1).sort_values(ascending=False).index
        ]

        # Sorting the columns by total occurrences (sum of columns) for legend and data
        # https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.sort_values.html
        drought_keywords_sums = drought_keywords_counts_sorted.sum(axis=0)
        drought_keywords_counts_sorted = drought_keywords_counts_sorted[
            drought_keywords_sums.sort_values(ascending=False).index
        ]

        # Create custom legend labels by combining each drought quantification keyword (category)
        # with its corresponding count using zip(). Dry is changed back to "Dry"
        # https://www.geeksforgeeks.org/matplotlib-pyplot-legend-in-python/
        # https://www.geeksforgeeks.org/create-pandas-dataframe-from-lists-using-zip/
        legend_labels_with_counts = [
            f'"{category}": {count}' if category == "Dry" else f"{category}: {count}"
            for category, count in zip(
                drought_keywords_sums.index, drought_keywords_sums.values
            )
        ]

        # Sorting legend labels based on the counts numeric in descending order
        # https://docs.python.org/3/howto/sorting.html
        sorted_legend_labels_with_counts = sorted(
            legend_labels_with_counts,
            key=lambda x: int(x.split()[-1]),
            reverse=True,
        )

        # Define consistent colors for each drought quantification keyword across all charts
        # https://stackoverflow.com/questions/26139423/plot-different-color-for-different-categorical-levels
        drought_keywords_color_mapping = {
            "Dry": "#ff7f0e",  # Dark Orange
            "Differs from normal": "#ff4500",  # Orange-Red
            "Dry season": "#87CEEB",  # Sky Blue
            "Low soil moisture": "#00ced1",  # Dark Turquoise
            "Low water flow/depth": "#4682b4",  # Steel Blue
            "Plant water stress": "#32cd32",  # Lime Green
            "Reduced rainfall": "#adff2f",  # Green Yellow
            "Standardized Index": "#9370db",  # Medium Purple
        }

        # Generate the plot with sorted categories and the customized colors
        # https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.bar.html
        drought_keywords_counts_sorted.plot(
            kind="bar",
            stacked=True,
            figsize=(12, 6),
            color=[
                drought_keywords_color_mapping[cat]
                for cat in drought_keywords_counts_sorted.columns
            ],
        )

        # Add titles and axis labels that were defined before depending automatically from the titels
        # https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.title.html#matplotlib-pyplot-title
        # https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.xlabel.html#matplotlib.pyplot.xlabel
        plot.title(title)
        plot.xlabel(xaxisdescription)

        # Add manual y-axis label for all studies
        # https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.ylabel.html#matplotlib-pyplot-ylabel
        plot.ylabel("Number of occurrences")

        # Place the sorted legend with counts inside the plot on the upper right
        # https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.legend.html
        plot.legend(
            sorted_legend_labels_with_counts, title="Drought Keyword", loc="upper right"
        )

        # Rotate x-axis labels for readability and better plot-text ratio
        # https://www.geeksforgeeks.org/matplotlib-pyplot-xticks-in-python/
        plot.xticks(
            ticks=range(len(drought_keywords_counts_sorted.index)),
            labels=drought_keywords_counts_sorted.index,
            rotation=45,
            ha="right",
        )

        # Ensure that the tight layout is used for a better visualisation
        # https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.tight_layout.html#matplotlib.pyplot.tight_layout
        plot.tight_layout()

        # Save the plot as a JPG file to use it in the bachelor-thesis
        # https://www.geeksforgeeks.org/matplotlib-pyplot-savefig-in-python/
        # plot.savefig(output_file_path, format="jpg")

        # Optionally display the plot (for finetuning so adjusting is easier)
        # https://www.geeksforgeeks.org/matplotlib-pyplot-show-in-python/
        plot.show()


# DONE but not needed
# Generate the MODIS and given drought category keyword bar chart
# create_drought_keywords_bar_chart(all_studies_shapefile_path, "MODIS drought keyword")


def create_reanalysis_based_bar_chart(shapefile_path, chart_type):
    """
    Generates a stacked bar chart to visualize the distribution of SPEI (Standardized Precipitation
    Evapotranspiration Index) drought categories in correlation with either drought quantification
    keywords or MODIS forest categories. The function processes the data from a shapefile, groups it,
    calculates percentages, and generates a stacked bar chart that is saved as a JPG image.
    The function is designed to combine bar chart creation logic for different cases which all use the SPEI drought category
    from the re-analysis into a single function.
    This allows for easy extension if more bar charts are needed in the future from the same re-analysis shapefile data,
    without requiring the creation of additional function.

    Args:
        shapefile_path (str): The path to the shapefile that contains the data for analysis.
        chart_type (str): Specifies the type of bar chart to generate.
                        Options are:
                            - "Drought": Correlates SPEI drought categories with drought quantification keywords.
                            - "MODIS SPEI": Correlates SPEI drought categories with MODIS forest types.
                            - "Continent SPEI": Correlates SPEI drought categories with the continent of locations.
    Returns:
        None: The function saves the generated bar chart as a JPG image.
    """

    # Reading the given shapefile using geopandas read_file() method and storing it as geodataframe
    # https://geopandas.org/en/stable/docs/user_guide/data_structures.html#geodataframe
    # https://geopandas.org/en/stable/docs/user_guide/io.html#reading-and-writing-files
    gdf = geopd.read_file(shapefile_path)


    # For the given drought quantification keywords from the studies and SPEI drought categories
    if chart_type == "Drought":
        # Grouping the data by "dr_quanti" and "Category" to count occurrences for the drought chart
        # https://pandas.pydata.org/docs/user_guide/10min.html#grouping
        # https://www.statology.org/pandas-unstack/
        # https://note.nkmk.me/en/python-pandas-len-shape-size/#get-the-number-of-elements-dfsize
        category_counts = (
            gdf.groupby(["dr_quanti", "Category"]).size().unstack(fill_value=0)
        )
        # X-axis text
        xaxisdescription = "Given drought category"
        # Title of the plot
        title = "Distribution of SPEI drought categories in correlation with the given drought quantification keywords from the studies"
        # Path where the plot is going to be saved
        output_file_path = r"D:\Uni\Bachelorarbeit\Plots\NEW Bar chart for correlation of SPEI drought category and the given drought quantifications of the studies  in percent.jpg"

    # For MODIS categories and SPEI drought categories
    if chart_type == "MODIS SPEI":
        # Grouping the data by "MODIS" and "Category" to count occurrences for the MODIS chart
        # https://pandas.pydata.org/docs/user_guide/10min.html#grouping
        # https://www.statology.org/pandas-unstack/
        # https://note.nkmk.me/en/python-pandas-len-shape-size/#get-the-number-of-elements-dfsize
        category_counts = (
            gdf.groupby(["MODIS", "Category"]).size().unstack(fill_value=0)
        )
        # X-axis text
        xaxisdescription = "Forest type"
        # Title of the plot
        title = "Distribution of SPEI drought categories within each MODIS category"
        # Path where the plot is going to be saved
        output_file_path = r"D:\Uni\Bachelorarbeit\Plots\NEW Bar chart for correlation MODIS classes and SPEI drought categories in percent.jpg"

    # For all cases that somehow use "Category" (The SPEI categories)
    if chart_type in ["Drought", "MODIS SPEI"]:
        # Change the label for "Other" category, so it is not too long (only for bar plots with MODIS involved)
        # https://pandas.pydata.org/docs/user_guide/basics.html#renaming-mapping-labels
        category_counts.rename(
            index={
                "Other (Mangrove Forest, Open Shrubland, Savannas, Permanent Wetlands, ...)": "Other"
            },
            inplace=True,
        )

        # Define the colors for SPEI drought categories, so they match in every plot (and with the QGIS map) from
        # https://spei.csic.es/map/maps.html
        # https://stackoverflow.com/questions/26139423/plot-different-color-for-different-categorical-levels
        spei_color_mapping = {
            "no drought (+1 < SPEI)": "#0000FF",  # Blue
            "near normal conditions (-1 < SPEI < +1)": "#ADD8E6",  # Light Blue
            "moderately dry (-1.5 < SPEI <= -1)": "#FFA500",  # Orange
            "severely dry (-2 < SPEI <= -1.5)": "#FF4500",  # Orange-Red
            "extremely dry (SPEI <= -2)": "#8B0000",  # Dark Red
        }

        # Calculate the percentage for each category by dividing each value by the global total (sum of all counts)
        # https://www.w3schools.com/python/pandas/ref_df_sum.asp
        # https://www.w3schools.com/python/pandas/ref_df_div.asp
        global_total = category_counts.values.sum()
        category_counts_percentage = category_counts.div(global_total) * 100

        # Sorting the created pivot table by total occurrences (sum of rows), from most to least in descending order for all stacked bar plots
        # https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.loc.html#pandas-dataframe-loc
        # https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.sort_values.html
        category_counts_sorted = category_counts_percentage.loc[
            category_counts_percentage.sum(axis=1).sort_values(ascending=False).index
        ]

        # Sorting the columns by total occurrences (sum of columns) for legend and data
        # https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.sort_values.html
        category_sums = category_counts.sum(axis=0)
        category_counts_sorted = category_counts_sorted[
            category_sums.sort_values(ascending=False).index
        ]


        # Create a list for the desired order of the spei categories inside the bars
        # https://pandas.pydata.org/docs/user_guide/indexing.html#indexing-and-selecting-data
        spei_desired_order = [
            "extremely dry (SPEI <= -2)",
            "severely dry (-2 < SPEI <= -1.5)",
            "moderately dry (-1.5 < SPEI <= -1)",
            "near normal conditions (-1 < SPEI < +1)",
            "no drought (+1 < SPEI)"
        ]

        # Reindex the columns of my "category_counts_sorted" DataFrame with the created list
        # https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.reindex.html
        category_counts_sorted = category_counts_sorted.reindex(columns=spei_desired_order)

        # Generate the plot with sorted categories and the customized colors
        # https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.bar.html
        category_counts_sorted.plot(
            kind="bar",
            stacked=True,
            figsize=(14, 8),
            color=[spei_color_mapping[cat] for cat in category_counts_sorted.columns],
        )

        # Create custom legend labels by combining each SPEI category with its corresponding count using zip()
        # https://www.geeksforgeeks.org/matplotlib-pyplot-legend-in-python/
        # https://www.geeksforgeeks.org/create-pandas-dataframe-from-lists-using-zip/
        legend_labels_with_counts = [
            f"{category}: {int(category_sums[category])}"
            for category in spei_desired_order
        ]

        # Replace "<=" with "≤" in the legend labels for the display inside the legend
        # https://docs.python.org/3/library/stdtypes.html#str.replace
        legend_labels_with_counts_display = [
            label.replace("<=", "≤") for label in legend_labels_with_counts
        ]

        # Sorting legend labels (SPEI categories) based on the counts numeric in descending order by taking the last string number into account
        # https://docs.python.org/3/howto/sorting.html
        sorted_legend_labels_with_counts = sorted(
            legend_labels_with_counts_display,
            key=lambda x: int(x.split()[-1]),
            reverse=True,
        )

        # Create a list to lign the SPEI categories with the sorted legend labels based on their counts
        sorted_spei_categories = [
            spei_desired_order[legend_labels_with_counts_display.index(label)]
            for label in sorted_legend_labels_with_counts
        ]

        # Creates custom legend handles with colors matching the sorted SPEI categories and labels
        # Use zip() to combine the two lists to align the colors with the sorted legend labels
        # https://matplotlib.org/stable/users/explain/axes/legend_guide.html#creating-artists-specifically-for-adding-to-the-legend-aka-proxy-artists
        # https://www.geeksforgeeks.org/create-pandas-dataframe-from-lists-using-zip/
        legend_handles = [
            mpatches.Patch(color=spei_color_mapping[category], label=label)
            for category, label in zip(sorted_spei_categories, sorted_legend_labels_with_counts)
        ]

        # Place the sorted legend with counts inside the plot on the upper right
        # https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.legend.html
        plot.legend(
            handles=legend_handles,
            title="SPEI drought category",
            loc="upper right",
        )

        # Add titles and axis labels that were defined before automatically from the titels
        # https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.title.html#matplotlib-pyplot-title
        # https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.xlabel.html#matplotlib.pyplot.xlabel
        # plot.title(title)
        plot.xlabel(xaxisdescription)

        # Add manual y-axis label for all studies
        # https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.ylabel.html#matplotlib-pyplot-ylabel
        plot.ylabel("Percentage of re-analysed study locations (%)")

        # Rotate x-axis labels for readability and better plot-text ratio and replace "<=" with "≤"
        # https://www.geeksforgeeks.org/matplotlib-pyplot-xticks-in-python/
        # https://docs.python.org/3/library/stdtypes.html#str.replace
        plot.xticks(
            ticks=range(len(category_counts_sorted.index)),
            labels=[label.replace("<=", "≤") for label in category_counts_sorted.index],
            rotation=45,
            ha="right",
        )

        # Ensure that the tight layout is used for a better visualisation
        # https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.tight_layout.html#matplotlib.pyplot.tight_layout
        plot.tight_layout()

        # Save the plot as a JPG file to use it in the bachelor-thesis
        # https://www.geeksforgeeks.org/matplotlib-pyplot-savefig-in-python/
        # plot.savefig(output_file_path, format="jpg")

        # Optionally display the plot (for finetuning so adjusting is easier)
        # https://www.geeksforgeeks.org/matplotlib-pyplot-show-in-python/
        plot.show()


# DONE
# Generate the drought quantification keyword bar chart
# create_reanalysis_based_bar_chart(reanalysis_shapefile_path, "Drought")

# DONE
# Generate the MODIS SPEI category bar chart
# create_reanalysis_based_bar_chart(reanalysis_shapefile_path, "MODIS SPEI")


def create_pie_chart(shape_or_excel_file_path, chart_type):
    """
    Generates pie charts based on the specified `chart_type` using data from either an Excel file or a
    shapefile. The function supports multiple types of pie charts, such as study type distributions,
    drought classifications, MODIS categories, and SPEI drought categories.
    Additional pie chart types can be implemented easily by adding new cases based on the same input data.

    Args:
        shape_or_excel_file_path (str): The path to the Excel file (.xlsx) or shapefile (.shp) to be used for data extraction.
        chart_type (str): Specifies the type of pie chart to generate.
                        Options are:
                            - "study type": Distribution of study types.
                            - "breakdown": Breakdown of drought quantification keywords by study type.
                            - "MODIS drought sphere": Drought sphere categories for MODIS forest types.
                            - "MODIS drought category": Breakdown of drought categories for MODIS forest types.
                            - "MODIS percentage": Percentage distribution of MODIS forest types.
                            - "SPEI category percentage": Percentage of re-analysed study locations by SPEI category.
                            - "Spheres drought category": Drought quantification breakdown for each sphere.
                            - "spheres": Percentage overview of drought spheres.
                            - "Spheres SPEI": Breakdown of SPEI categories for each sphere.
                            - "Continent percentage": Percentage distribution by continent.

    Returns:
        None: The function saves the generated pie chart(s) as a JPG image.
    """

    # Cases for the pie charts that need data from the Excel file
    if chart_type in [
        "study type",
        "breakdown",
        "MODIS drought sphere",
        "spheres",
        "Spheres drought category",
    ]:
        # Load the Excel file and "relevantInfo" sheet where the data for the pie charts is stored
        # https://pandas.pydata.org/docs/reference/api/pandas.read_excel.html
        excel_df = pd.read_excel(excel_file_path, sheet_name="relevantInfo")

        # Clean up the "study type" column to avoid duplicates due to capitalization or extra spaces and make the filtering for the breakdown pie charts easier
        # https://pandas.pydata.org/docs/reference/api/pandas.Series.str.strip.html
        excel_df["study type"] = excel_df["study type"].str.strip()

        # Clean up the "drought_sphere" column to avoid duplicates due to capitalization or extra spaces and make the filtering for the pie charts easier
        # https://pandas.pydata.org/docs/reference/api/pandas.Series.str.strip.html
        excel_df["drought_sphere"] = excel_df["drought_sphere"].str.strip()

        # Clean up the "drought quantification keyword for plots" and remove quotes (because python gives an error for "Dry" if there are quotes) and extra spaces
        # https://pandas.pydata.org/docs/reference/api/pandas.Series.str.strip.html
        # https://pandas.pydata.org/docs/reference/api/pandas.Series.str.replace.html
        excel_df["drought quantification keyword for plots"] = (
            excel_df["drought quantification keyword for plots"]
            .str.strip()
            .str.replace('"', "")
        )

        # Define consistent colors for each drought quantification keyword across all plots, globally defined because of multiple use cases
        # https://stackoverflow.com/questions/26139423/plot-different-color-for-different-categorical-levels
        drought_keywords_color_mapping = {
            "Dry": "#ff7f0e",  # Dark Orange
            "Differs from normal": "#ff4500",  # Orange-Red
            "Dry season": "#87CEEB",  # Sky Blue
            "Low soil moisture": "#00ced1",  # Dark Turquoise
            "Low water flow/depth": "#4682b4",  # Steel Blue
            "Plant water stress": "#32cd32",  # Lime Green
            "Reduced rainfall": "#adff2f",  # Green Yellow
            "Standardized Index": "#9370db",  # Medium Purple
        }

        # If "Spheres drought category" is selected, create the drought quantification breakdown pie charts for each MODIS forest type
        if chart_type == "Spheres drought category":

            # Group the data by "drought_sphere" and clean the drought quantification keywords and then count its occurrences with size()
            # Remove quotes with replace() (because python gives an error for "dry" keyword if there are quotes)
            # Also create the pivot table to have drought_sphere as columns and fill missing with 0
            # https://pandas.pydata.org/docs/user_guide/10min.html#grouping
            # https://pandas.pydata.org/docs/reference/api/pandas.Series.str.replace.html
            # https://pandas.pydata.org/docs/reference/api/pandas.Series.str.strip.html
            # https://www.geeksforgeeks.org/list-size-method-in-java-with-examples/
            # https://www.statology.org/pandas-unstack/
            # https://note.nkmk.me/en/python-pandas-len-shape-size/#get-the-number-of-elements-dfsize
            spheres_breakdown_data = (
                excel_df.groupby(
                    [
                        "drought_sphere",
                        excel_df["drought quantification keyword for plots"]
                        .str.strip()
                        .str.replace('"', ""),
                    ]
                )
                .size()
                .unstack(fill_value=0)
            )

            # Set the size of the figure and define the number of subplots based on the number of relevant drought spheres
            # manually because we need one pie chart for each sphere
            # https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.subplots.html
            fig, axes = plot.subplots(1, 4, figsize=(20, 5))

            # Flatten the axes for easier iteration and a faster plot creation
            # https://stackoverflow.com/questions/46862861/what-does-axes-flat-in-matplotlib-do
            # axes = axes.flatten()

            # Iterate over the final dataframe that holds the wanted information to filter out zero values and assign the wanted colors
            # https://www.w3schools.com/python/pandas/ref_df_iterrows.asp
            for i, (drought_sphere, row) in enumerate(
                spheres_breakdown_data.iterrows()
            ):
                # Filter out redundant zero values in the rows (Given drought categories) so only the drought categories that are given for the study types are displayed
                row = row[row > 0]
                # Use consistent colors for each keyword, so it is not confusing (using the colors declared before globally
                breakdown_colors = [
                    drought_keywords_color_mapping[label] for label in row.index
                ]

                # Display percentages inside the pieces and assign the labels and colors to the pie chart pieces
                # Also add the "" back to the "Dry" label since it had to be removed for python rules before
                # https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.pie.html
                axes[i].pie(
                    row,
                    labels=[
                        f'"{label}"' if label == "Dry" else label for label in row.index
                    ],
                    autopct="%1.1f%%",
                    colors=breakdown_colors,
                )

                # Display a title for every single pie chart containing its drought sphere type as title
                # https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.set_title.html
                axes[i].set_title(f"{drought_sphere.title()}")

            # Set the main title for the entire figure (has to be done separately because every pie chart has its own title) aswell as the file name
            # https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.suptitle.html
            fig.suptitle(
                "Breakdown of the given drought quantification the drought spheres",
                fontsize=16,
            )

            sphere_category_output_file_path = r"D:\Uni\Bachelorarbeit\Plots\NEW Breakdown pie charts for percentages of drought definitions for the drought spheres from the Excel.jpg"

            # Ensure that the tight layout is used for a better visualisation (the single pie charts are too close to another if not used)
            # https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.tight_layout.html#matplotlib.pyplot.tight_layout
            plot.tight_layout()

            # Save the pie chart(s) as one JPG file to use it in the thesis
            # https://www.geeksforgeeks.org/matplotlib-pyplot-savefig-in-python/
            # plot.savefig(sphere_category_output_file_path, format="jpg")

            # Optionally display the pie chart(s) (for finetuning so adjusting is easier)
            # https://www.geeksforgeeks.org/matplotlib-pyplot-show-in-python/
            plot.show()

        # If "spheres" is selected, this case is used to create the percentage overview pie chart for the drought spheres
        if chart_type == "spheres":
            # Count the occurrences of each sphere to create the percentages
            # https://pandas.pydata.org/docs/reference/api/pandas.Series.str.strip.html
            # https://pandas.pydata.org/docs/reference/api/pandas.Series.value_counts.html
            spheres_count = excel_df["drought_sphere"].str.strip().value_counts()

            # Set colors for every sphere for a good overview
            # https://proclusacademy.com/blog/customize_matplotlib_piechart/#slice-colors
            sphere_colors = [
                "#8B4513",  # brown
                "#ADD8E6",  # light blue
                "#3232d1",  # dark blue
                "#808080",  # grey
            ]

            # Adjust the size of the plot so the picture is better usable later on
            # https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.figure.html
            plot.figure(figsize=(6.5, 6))

            # # Create the pie chart with percentages and white lines between the pieces
            # https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.pie.html
            wedges, texts, autotexts = plot.pie(
                spheres_count,
                autopct="%1.1f%%",
                colors=sphere_colors,
                startangle=90,
            )

            # Set label positions manually for the "Meteorological" sphere, by iterating over all labels by using .index to enumerate them
            # https://stackoverflow.com/a/43916835 (set_position())
            # https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.title.html
            # https://www.w3schools.com/python/pandas/ref_df_index.asp
            # https://matplotlib.org/stable/api/text_api.html#module-matplotlib.text
            for i, label in enumerate(spheres_count.index):
                # Re-capitalize labels for the pie chart by defining them as titles
                label = label.title()
                # Adjusting the position of "Review" by using specific coordinates
                if label == "Meteorological":
                    texts[i].set_position((-0.25, 1.05))
                else:
                    # Keep default position for other labels since they are fine on default
                    texts[i].set_position(texts[i].get_position())

                # Adding back the other spheres label text (since set_position overrides them)
                # https://www.tutorialspoint.com/how-to-add-title-to-subplots-in-matplotlib#:~:text=The%20Matplotlib%20set_text()%20function,in%20a%20subplot%20or%20plot.
                texts[i].set_text(label)

            # Draw the plot as circle and ensure equal aspect ratio
            # https://matplotlib.org/stable/gallery/subplots_axes_and_figures/axis_equal_demo.html
            plot.axis("equal")

            # Set the title and filename for this pie chart
            # https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.title.html#matplotlib-pyplot-title
            plot.title("Distribution of the drought spheres out of all used studies")
            study_type_output_path = r"D:\Uni\Bachelorarbeit\Plots\NEW main pie chart with complete drought sphere percentages.jpg"

            # Save the pie chart as a JPG file to use it in the thesis
            # https://www.geeksforgeeks.org/matplotlib-pyplot-savefig-in-python/
            # plot.savefig(study_type_output_path, format="jpg")

            # Optionally display the plot (for finetuning so adjusting is easier)
            # https://www.geeksforgeeks.org/matplotlib-pyplot-show-in-python/
            plot.show()

        # If "study type" is selected, this case is used to create the percentage overview pie chart for the study types
        elif chart_type == "study type":
            # Count the occurrences of each study type to create the percentages
            # https://pandas.pydata.org/docs/reference/api/pandas.Series.value_counts.html
            study_type_counts = excel_df["study type"].value_counts()

            # Set colors for every study type for a good overview
            # https://proclusacademy.com/blog/customize_matplotlib_piechart/#slice-colors
            study_type_colors = [
                "#1f77b4",  # blue
                "#ff7f0e",  # orange
                "#2ca02c",  # green
                "#9467bd",  # purple
            ]

            # Adjust the size of the plot so the picture is better usable later on
            # https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.figure.html
            plot.figure(figsize=(6, 5))

            # # Create the pie chart with percentages and white lines between the pieces
            # https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.pie.html
            wedges, texts, autotexts = plot.pie(
                study_type_counts,
                autopct="%1.1f%%",
                colors=study_type_colors,
                startangle=90,
                wedgeprops={"edgecolor": "white", "linewidth": 0.5},
            )

            # Set label positions manually for the study type "Review", so they are right next to their pieces,
            # by iterating over all labels by using .index to enumerate them
            # https://stackoverflow.com/a/43916835 (set_position())
            # https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.title.html
            # https://www.w3schools.com/python/pandas/ref_df_index.asp
            # https://matplotlib.org/stable/api/text_api.html#module-matplotlib.text
            for i, label in enumerate(study_type_counts.index):
                # Re-capitalize labels for the pie chart by defining them as titles
                label = label.title()
                # Adjusting the position of "Review" by using specific coordinates
                if label == "Review":
                    texts[i].set_position((-0.05, 1.05))
                else:
                    # Keep default position for other labels since they are fine on default
                    texts[i].set_position(texts[i].get_position())

                # Adding back the study type label text (since set_position overrides them)
                # https://www.tutorialspoint.com/how-to-add-title-to-subplots-in-matplotlib#:~:text=The%20Matplotlib%20set_text()%20function,in%20a%20subplot%20or%20plot.
                texts[i].set_text(label)

            # Draw the plot as circle and ensure equal aspect ratio
            # https://matplotlib.org/stable/gallery/subplots_axes_and_figures/axis_equal_demo.html
            plot.axis("equal")

            # Set the title and filename for this pie chart
            # https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.title.html#matplotlib-pyplot-title
            plot.title("Distribution of the study types out of all used studies")
            study_type_output_path = r"D:\Uni\Bachelorarbeit\Plots\Main pie chart with complete study type percentages.jpg"

            # Save the pie chart as a JPG file to use it in the thesis
            # https://www.geeksforgeeks.org/matplotlib-pyplot-savefig-in-python/
            # plot.savefig(study_type_output_path, format="jpg")

            # Optionally display the plot (for finetuning so adjusting is easier)
            # https://www.geeksforgeeks.org/matplotlib-pyplot-show-in-python/
            plot.show()

        # If "breakdown" is selected, create the drought quantification breakdown pie charts for each study type
        elif chart_type == "breakdown":
            # Group the data by "study type" and count the occurrences of "drought quantification keyword for plots"
            # https://pandas.pydata.org/docs/user_guide/10min.html#grouping
            # https://www.statology.org/pandas-unstack/
            study_type_breakdown_data = (
                excel_df.groupby("study type")[
                    "drought quantification keyword for plots"
                ]
                .value_counts()
                .unstack(fill_value=0)
            )

            # Display only the study types "experimental", "observational", and "modeling" in a specific order for pie charts
            desired_study_type_order = ["Experimental", "Observational", "Modeling"]

            # Filter and reorder the study types using .isin() to keep only the relevant types and .reindex() to match the desired order
            # https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.loc.html#pandas-dataframe-loc
            # https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.isin.html
            # https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.reindex.html
            final_breakdown_data = study_type_breakdown_data.loc[
                study_type_breakdown_data.index.isin(desired_study_type_order)
            ].reindex(desired_study_type_order)

            # Define the number of subplots based on the number of study types because we need one pie chart for each relevant, named study type
            # https://www.programiz.com/python-programming/methods/built-in/len
            # https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.subplots.html
            number_of_study_types = len(final_breakdown_data)
            fig, axes = plot.subplots(1, 3, figsize=(20, 8))

            # Flatten the axes for easier iteration and a faster plot creation
            # https://stackoverflow.com/questions/46862861/what-does-axes-flat-in-matplotlib-do
            axes = axes.flatten()

            # Iterate over the final dataframe that holds the wanted information to filter out zero values and assign the wanted colors
            # https://www.w3schools.com/python/pandas/ref_df_iterrows.asp
            for i, (study_type, row) in enumerate(final_breakdown_data.iterrows()):
                # Filter out redundant zero values in the rows (Given drought categories) so only the drought categories that are given for the study types are displayed
                row = row[row > 0]
                # Use consistent colors for each keyword, so it is not confusing (using the colors declared before in "drought_keywords_color_mapping"
                breakdown_colors = [
                    drought_keywords_color_mapping[label] for label in row.index
                ]

                # Display percentages inside the pieces and assign the labels and colors to the pie chart axes
                # Also add the "" back to the "Dry" label since it had to be removed for python rules before
                # https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.pie.html
                axes[i].pie(
                    row,
                    labels=[
                        f'"{label}"' if label == "Dry" else label for label in row.index
                    ],
                    autopct="%1.1f%%",
                    colors=breakdown_colors,
                )

                # Display a title for every single pie chart containing its study type
                # https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.set_title.html
                axes[i].set_title(f"{study_type}")

            # Set the main title for the entire figure (has to be done separately because every pie chart has its own title) as well as the file name
            # https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.title.html#matplotlib-pyplot-title
            # https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.suptitle.html
            fig.suptitle(
                "Breakdown of the given drought quantification for the relevant study types",
                fontsize=16,
            )
            breakdown_output_file_path = r"D:\Uni\Bachelorarbeit\Plots\NEW Breakdown pie charts for percentages of drought definitions for study types.jpg"

            # Ensure that the tight layout is used for a better visualisation (the single pie charts are too close to another if not used)
            # https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.tight_layout.html#matplotlib.pyplot.tight_layout
            plot.tight_layout()

            # Save the pie chart(s) as one JPG file to use it in the thesis
            # https://www.geeksforgeeks.org/matplotlib-pyplot-savefig-in-python/
            # plot.savefig(breakdown_output_file_path, format="jpg")

            # Optionally display the pie chart(s) (for finetuning so adjusting is easier)
            # https://www.geeksforgeeks.org/matplotlib-pyplot-show-in-python/
            plot.show()

    # Cases for all pie charts that need data from the shapefile with all re-analysed paper locations
    elif chart_type in ["SPEI category percentage", "Spheres SPEI"]:

        # Read the given shapefile for all pie chart cases using geopandas read_file() method and storing it as geodataframe
        # https://geopandas.org/en/stable/docs/user_guide/data_structures.html#geodataframe
        # https://geopandas.org/en/stable/docs/user_guide/io.html#reading-and-writing-files
        reanalysed_gdf = geopd.read_file(shape_or_excel_file_path)

        # Define the colors for SPEI drought categories, so they match in every plot (and with the QGIS map) from
        # https://spei.csic.es/map/maps.html
        # https://stackoverflow.com/questions/26139423/plot-different-color-for-different-categorical-levels
        spei_color_mapping = {
            "no drought (+1 < SPEI)": "#0000FF",  # Blue
            "near normal conditions (-1 < SPEI < +1)": "#ADD8E6",  # Light Blue
            "moderately dry (-1.5 < SPEI <= -1)": "#FFA500",  # Orange
            "severely dry (-2 < SPEI <= -1.5)": "#FF4500",  # Orange-Red
            "extremely dry (SPEI <= -2)": "#8B0000",  # Dark Red
        }

        # If "SPEI category percentage" is selected, create the SPEI drought category pie chart
        if chart_type == "SPEI category percentage":

            # Count the occurrences of each SPEI drought category to create the percentages
            # https://pandas.pydata.org/docs/reference/api/pandas.Series.value_counts.html
            spei_category_counts = reanalysed_gdf["Category"].value_counts()

            # Create a list of colors in the same order as the labels in spei_category_counts to use it for the pie chart
            spei_colors = [
                spei_color_mapping[label] for label in spei_category_counts.index
            ]

            # Adjust the size of the plot so the picture is better usable later and nothing gets cut off
            # https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.figure.html
            plot.figure(figsize=(14, 8))

            # Create the pie chart with black lines between pieces and percentages as texts
            # https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.pie.html
            wedges, category_texts, autotexts = plot.pie(
                spei_category_counts,
                autopct="%1.1f%%",
                colors=spei_colors,
                startangle=90,
                wedgeprops={"edgecolor": "black", "linewidth": 0.4},
            )

            # Change the color of the percentages to white for clearer visibility
            # https://stackoverflow.com/a/27899541 (set_color())
            for autotext in autotexts:
                autotext.set_color("white")

            # Set label position manually for the SPEI category ("no drought (+1 < SPEI)"), by iterating over all labels by using .index to enumerate them,
            # so it is right next to their piece and replace "<=" with "≤" if needed in the labels
            # https://www.w3schools.com/python/pandas/ref_df_index.asp
            # https://stackoverflow.com/a/43916835 (set_position())
            # https://docs.python.org/3/library/stdtypes.html#str.replace
            # https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.title.html
            for i, spei_label in enumerate(spei_category_counts.index):
                # Replace "<=" with "≤" in the labels (pie chart pieces descriptions)
                cleaned_spei_label = spei_label.replace("<=", "≤")

                # We only want to manually position the "no drought (+1 < SPEI)" label because it's not right on default
                if cleaned_spei_label == "no drought (+1 < SPEI)":
                    # Manually adjusting the position of "no drought (+1 < SPEI)" by using coordinates
                    category_texts[i].set_position((-0.1, 1.1))

                # Adding back the SPEI category label text (because set_position overrides them)
                # https://www.tutorialspoint.com/how-to-add-title-to-subplots-in-matplotlib#:~:text=The%20Matplotlib%20set_text()%20function,in%20a%20subplot%20or%20plot.
                category_texts[i].set_text(cleaned_spei_label)

            # Set the main title as well as the file name
            # https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.title.html#matplotlib-pyplot-title
            plot.title(
                "Distribution of the SPEI categories out of all re-analysed studies in percentage"
            )
            spei_category_output_file_path = r"D:\Uni\Bachelorarbeit\Plots\NEW Pie chart with complete SPEI drought category percentages and legend for total numbers.jpg"

            # Create and add a legend for the total numbers of SPEI categories for a better overview of the data
            # Create the labels out of the SPEI categories for the legend with counts so the total numbers are displayed
            # Also replace "<=" with "≤" in the legend labels for better looks
            # https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.items.html#pandas-dataframe-items
            # https://docs.python.org/3/library/stdtypes.html#str.replace
            spei_legend_labels = [
                f"{label.replace('<=', '≤')}: {count}"
                for label, count in spei_category_counts.items()
            ]
            # Now add the legend to the pie chart with the created SPEI category labels and place it in the center left outside the pie chart (with bbox_to_anchor)
            # https://matplotlib.org/stable/api/legend_api.html#module-matplotlib.legend
            plot.legend(
                wedges,
                spei_legend_labels,
                title="SPEI Categories (Count)",
                loc="center right",
                bbox_to_anchor=(1, 0, 0.4, 1),
            )

            # Ensure that the tight layout is used for a better visualisation and readability of the "no drought (+1 < SPEI)" percentage
            # https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.tight_layout.html#matplotlib.pyplot.tight_layout
            plot.tight_layout()

            # Save the pie chart as a JPG file to use it in the thesis
            # https://www.geeksforgeeks.org/matplotlib-pyplot-savefig-in-python/
            # plot.savefig(spei_category_output_file_path, format="jpg")

            # Optionally display the plot (for finetuning so adjusting is easier)
            # https://www.geeksforgeeks.org/matplotlib-pyplot-show-in-python/
            plot.show()

        # If "Spheres SPEI" is selected, create the Spheres SPEI pie chart
        elif chart_type == "Spheres SPEI":

            # Clean up the "sphere" values to be sure there are no duplicates due to blank spaces
            # https://pandas.pydata.org/docs/reference/api/pandas.Series.str.strip.html
            # https://pandas.pydata.org/docs/reference/api/pandas.Series.str.replace.html
            reanalysed_gdf["sphere"] = reanalysed_gdf["sphere"].str.strip()

            # Group the data by "sphere" and "Category" then count its occurrences with size()
            # Also create the pivot table to have drought_sphere as columns and fill missing with 0
            # https://pandas.pydata.org/docs/user_guide/10min.html#grouping
            # https://pandas.pydata.org/docs/reference/api/pandas.Series.str.strip.html
            # https://www.geeksforgeeks.org/list-size-method-in-java-with-examples/
            # https://www.statology.org/pandas-unstack/
            # https://note.nkmk.me/en/python-pandas-len-shape-size/#get-the-number-of-elements-dfsize
            sphere_spei_breakdown_data = (
                reanalysed_gdf.groupby(["sphere", reanalysed_gdf["Category"]])
                .size()
                .unstack(fill_value=0)
            )

            # Set the size of the figure and define the number of subplots based on the number of relevant drought spheres
            # manually because we need one pie chart for each sphere
            # https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.subplots.html
            fig, axes = plot.subplots(2, 2, figsize=(15, 7))

            # Iterate over the final dataframe that holds the wanted information to filter out zero values and assign the wanted colors
            # https://www.w3schools.com/python/pandas/ref_df_iterrows.asp
            for i, (spheres, row) in enumerate(sphere_spei_breakdown_data.iterrows()):
                # Filter out redundant zero values in the rows (Given drought categories) so only the drought categories that are given for the study types are displayed
                row = row[row > 0]

                # Create a list with the SPEI categories in the desired order for the segments inside the pie charts
                desired_spei_order = [
                    "no drought (+1 < SPEI)",
                    "near normal conditions (-1 < SPEI < +1)",
                    "moderately dry (-1.5 < SPEI <= -1)",
                    "severely dry (-2 < SPEI <= -1.5)",
                    "extremely dry (SPEI <= -2)",
                ]

                # Reindex the segments of the pie chart (SPEI categories) with the desired order list and drop NaN values
                # https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.reindex.html
                # https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.dropna.html
                row = row.reindex(desired_spei_order).dropna()

                # Use consistent colors for each keyword, so it is not confusing (using the colors declared before globally)
                breakdown_colors = [spei_color_mapping[label] for label in row.index]

                # Calculate the row and column for 2x2 layout because it can not be set in "plot.subplots" if not done
                # https://how2matplotlib.com/plt-subplots.html
                row_index = i // 2
                col_index = i % 2

                # Display percentages inside the pieces and assign the labels and colors to the pie chart pieces
                # Also replace "<=" with "≤" in the pie chart labels
                # https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.pie.html
                # https://docs.python.org/3/library/stdtypes.html#str.replace
                wedges, texts, autotexts = axes[row_index, col_index].pie(
                    row,
                    labels=row.index.str.replace("<=", "≤"),
                    autopct="%1.1f%%",
                    startangle=90,
                    colors=breakdown_colors,
                )

                # Change the color of the percentages to white for clearer visibility
                # https://stackoverflow.com/a/27899541 (set_color())
                for autotext in autotexts:
                    autotext.set_color("white")

                # Display a title for every single pie chart containing its sphere as title
                # https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.set_title.html
                axes[row_index, col_index].set_title(f"{spheres.title()}")

            # Set the main title for the entire figure (has to be done separately because every pie chart has its own title) as well as the file name
            # https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.suptitle.html
            fig.suptitle(
                "Breakdown of the given SPEI categories from the drought spheres",
                fontsize=16,
            )
            sphere_reanalysis_output_file_path = r"D:\Uni\Bachelorarbeit\Plots\NEW Breakdown pie charts for percentages of SPEI categories for the drought spheres from the re-analysed shapefile locations.jpg"

            # Ensure that the tight layout is used for a better visualisation (the single pie charts are too close to another if not used)
            # https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.tight_layout.html#matplotlib.pyplot.tight_layout
            plot.tight_layout()

            # Save the pie chart(s) as one JPG file to use it in the thesis
            # https://www.geeksforgeeks.org/matplotlib-pyplot-savefig-in-python/
            # plot.savefig(sphere_reanalysis_output_file_path, format="jpg")

            # Optionally display the pie chart(s) (for finetuning so adjusting is easier)
            # https://www.geeksforgeeks.org/matplotlib-pyplot-show-in-python/
            plot.show()

    # Cases for all pie charts that need data from the shapefile with all paper points
    elif chart_type in [
        "MODIS percentage",
        "MODIS drought sphere",
        "MODIS drought category",
        "Continent percentage"
    ]:

        # Read the given shapefile for all pie chart cases using geopandas read_file() method and storing it as geodataframe
        # https://geopandas.org/en/stable/docs/user_guide/data_structures.html#geodataframe
        # https://geopandas.org/en/stable/docs/user_guide/io.html#reading-and-writing-files
        complete_gdf = geopd.read_file(shape_or_excel_file_path)

        # If "MODIS drought category" is selected, create the drought quantification breakdown pie charts for each MODIS forest type
        if chart_type == "MODIS drought category":

            # Group the data by "forest" and clean "drouquanti" and then count its occurrences with size()
            # Remove quotes with replace() (because python gives an error for "dry" keyword if there are quotes)
            # Also create the pivot table to have drought_sphere as columns and fill missing with 0
            # https://pandas.pydata.org/docs/user_guide/10min.html#grouping
            # https://pandas.pydata.org/docs/reference/api/pandas.Series.str.replace.html
            # https://pandas.pydata.org/docs/reference/api/pandas.Series.str.strip.html
            # https://www.geeksforgeeks.org/list-size-method-in-java-with-examples/
            # https://www.statology.org/pandas-unstack/
            # https://note.nkmk.me/en/python-pandas-len-shape-size/#get-the-number-of-elements-dfsize
            forest_breakdown_data = (
                complete_gdf.groupby(
                    [
                        "forest",
                        complete_gdf["drouquanti"].str.strip().str.replace('"', ""),
                    ]
                )
                .size()
                .unstack(fill_value=0)
            )

            # Reorder the MODIS Categories based on https://developers.google.com/earth-engine/datasets/catalog/MODIS_061_MCD12Q1#bands "LC_Type1 Class Table"
            desired_forest_order = [
                "Evergreen Needleleaf Forest",
                "Evergreen Broadleaf Forest",
                "Deciduous Needleleaf Forest",
                "Deciduous Broadleaf Forest",
                "Mixed Forest",
                "Closed Shrubland",
                "Woody Savanna",
                "Other (Mangrove Forest, Open Shrubland, Savannas, Permanent Wetlands, ...)",
            ]

            # Filter and reorder the MODIS forest types using .isin() to keep only the relevant types and .reindex() to match the desired order
            # https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.loc.html#pandas-dataframe-loc
            # https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.isin.html
            # https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.reindex.html
            final_forest_breakdown_data = forest_breakdown_data.loc[
                forest_breakdown_data.index.isin(desired_forest_order)
            ].reindex(desired_forest_order)

            # Define consistent colors for each drought quantification keyword across all plots, globally defined because of multiple use cases
            # https://stackoverflow.com/questions/26139423/plot-different-color-for-different-categorical-levels
            drought_keywords_color_mapping = {
                "Dry": "#ff7f0e",  # Dark Orange
                "Differs from normal": "#ff4500",  # Orange-Red
                "Dry season": "#87CEEB",  # Sky Blue
                "Low soil moisture": "#00ced1",  # Dark Turquoise
                "Low water flow/depth": "#4682b4",  # Steel Blue
                "Plant water stress": "#32cd32",  # Lime Green
                "Reduced rainfall": "#adff2f",  # Green Yellow
                "Standardized Index": "#9370db",  # Medium Purple
            }

            # Set the size of the figure and define the number of subplots based on the number of relevant MODIS forest types
            # manually because we need one pie chart for each relevant, named MODIS forest type
            # https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.subplots.html
            fig, axes = plot.subplots(2, 4, figsize=(30, 10))

            # Flatten the axes for easier iteration and a faster plot creation
            # https://stackoverflow.com/questions/46862861/what-does-axes-flat-in-matplotlib-do
            axes = axes.flatten()

            # Iterate over the final dataframe that holds the wanted information to filter out zero values and assign the wanted colors
            # https://www.w3schools.com/python/pandas/ref_df_iterrows.asp
            for i, (forest, row) in enumerate(final_forest_breakdown_data.iterrows()):
                # Filter out redundant zero values in the rows (Given drought categories) so only the drought categories that are given for the study types are displayed
                row = row[row > 0]
                # Use consistent colors for each keyword, so it is not confusing (using the colors declared before globally
                breakdown_colors = [
                    drought_keywords_color_mapping[label] for label in row.index
                ]

                # Display percentages inside the pieces and assign the labels and colors to the pie chart pieces
                # Also add the "" back to the "Dry" label since it had to be removed for python rules before
                # https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.pie.html
                axes[i].pie(
                    row,
                    labels=[
                        f'"{label}"' if label == "Dry" else label for label in row.index
                    ],
                    autopct="%1.1f%%",
                    colors=breakdown_colors,
                )

                # Display a title for every single pie chart containing its MODIS forest type
                # https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.set_title.html
                axes[i].set_title(f"{forest}")

            # Set the main title for the entire figure (has to be done separately because every pie chart has its own title) aswell as the file name
            # https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.suptitle.html
            fig.suptitle(
                "Breakdown of the given drought quantification for all paper locations MODIS forest types",
                fontsize=16,
            )
            modis_drought_output_file_path = r"D:\Uni\Bachelorarbeit\Plots\NEW Breakdown pie charts for percentages of drought definitions for MODIS forest types from complete location shapefile.jpg"

            # Remove the last unused pie chart since we only have 7 relevant MODIS forest types but 2 rows and 4 columns = 8 pie charts
            # https://www.geeksforgeeks.org/matplotlib-figure-figure-delaxes-in-python/
            # fig.delaxes(axes[-1])

            # Ensure that the tight layout is used for a better visualisation (the single pie charts are too close to another if not used)
            # https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.tight_layout.html#matplotlib.pyplot.tight_layout
            plot.tight_layout()

            # Save the pie chart(s) as one JPG file to use it in the thesis
            # https://www.geeksforgeeks.org/matplotlib-pyplot-savefig-in-python/
            # plot.savefig(modis_drought_output_file_path, format="jpg")

            # Optionally display the pie chart(s) (for finetuning so adjusting is easier)
            # https://www.geeksforgeeks.org/matplotlib-pyplot-show-in-python/
            plot.show()

        # If "MODIS drought sphere" is selected, create the drought quantification breakdown pie charts for each MODIS forest type
        if chart_type == "MODIS drought sphere":

            # Group the data by "forest" and "sphere". then count its occurrences with size()
            # Also create the pivot table to have sphere as columns and fill missing with 0
            # https://pandas.pydata.org/docs/user_guide/10min.html#grouping
            # https://pandas.pydata.org/docs/reference/api/pandas.Series.str.strip.html
            # https://www.geeksforgeeks.org/list-size-method-in-java-with-examples/
            # https://www.statology.org/pandas-unstack/
            # https://note.nkmk.me/en/python-pandas-len-shape-size/#get-the-number-of-elements-dfsize
            forest_sphere_breakdown_data = (
                complete_gdf.groupby(["forest", complete_gdf["sphere"]])
                .size()
                .unstack(fill_value=0)
            )

            # Reorder the MODIS Categories based on https://developers.google.com/earth-engine/datasets/catalog/MODIS_061_MCD12Q1#bands "LC_Type1 Class Table"
            desired_forest_order = [
                "Evergreen Needleleaf Forest",
                "Evergreen Broadleaf Forest",
                "Deciduous Needleleaf Forest",
                "Deciduous Broadleaf Forest",
                "Mixed Forest",
                "Closed Shrubland",
                "Woody Savanna",
                "Other (Mangrove Forest, Open Shrubland, Savannas, Permanent Wetlands, ...)",
            ]

            # Filter and reorder the MODIS forest types using .isin() to keep only the relevant types and .reindex() to match the desired order
            # https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.loc.html#pandas-dataframe-loc
            # https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.isin.html
            # https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.reindex.html
            final_forest_sphere_breakdown_data = forest_sphere_breakdown_data.loc[
                forest_sphere_breakdown_data.index.isin(desired_forest_order)
            ].reindex(desired_forest_order)

            # Manually define the number of subplots based on the number of relevant MODIS forest types because we need one pie chart for each relevant, named MODIS forest type
            # Also toggle size of the figures so every percentage is clear readable
            # https://www.programiz.com/python-programming/methods/built-in/len
            # https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.subplots.html
            fig, axes = plot.subplots(2, 4, figsize=(20, 10))

            # Flatten the axes for easier iteration and a faster plot creation
            # https://stackoverflow.com/questions/46862861/what-does-axes-flat-in-matplotlib-do
            axes = axes.flatten()

            # Define consistent colors for each drought quantification keyword across all plots, globally defined because of muliple use cases
            # https://stackoverflow.com/questions/26139423/plot-different-color-for-different-categorical-levels
            sphere_color_mapping = {
                "soil": "#8B4513",  # brown
                "atmospheric": "#ADD8E6",  # light blue
                "hydrological": "#3232d1",  # dark blue
                "meteorological": "#808080",  # grey
            }

            # Iterate over the final dataframe that holds the wanted information to filter out zero values and assign the wanted colors
            # https://www.w3schools.com/python/pandas/ref_df_iterrows.asp
            for i, (drought_sphere, row) in enumerate(
                final_forest_sphere_breakdown_data.iterrows()
            ):
                # Filter out redundant zero values in the rows (Given drought categories) so only the drought categories that are given for the study types are displayed
                row = row[row > 0]
                # Now use the declared colors for the stacked bar plot, also use strip() to assure every class get taken withouth error
                sphere_breakdown_colors = [
                    sphere_color_mapping[label.strip()] for label in row.index
                ]

                # Display percentages inside the pieces and assign the labels and colors to the pie chart pieces
                # https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.pie.html
                axes[i].pie(
                    row,
                    labels=row.index,
                    autopct="%1.1f%%",
                    colors=sphere_breakdown_colors,
                )

                # Display a title for every single pie chart containing its MODIS forest type
                # https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.set_title.html
                axes[i].set_title(f"{drought_sphere.title()}")

            # Set the main title for the entire figure (has to be done separately because every pie chart has its own title) aswell as the file name
            # https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.suptitle.html
            fig.suptitle(
                "Breakdown of the given drought spheres for all MODIS forest types from all paper locations",
                fontsize=16,
            )
            modis_sphere_output_file_path = r"D:\Uni\Bachelorarbeit\Plots\Breakdown pie charts for percentages of drought spheres for MODIS forest types from all paper location.jpg"

            # Ensure that the tight layout is used for a better visualisation (the single pie charts are too close to another if not used)
            # https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.tight_layout.html#matplotlib.pyplot.tight_layout
            plot.tight_layout()

            # Save the pie chart(s) as one JPG file to use it in the thesis
            # https://www.geeksforgeeks.org/matplotlib-pyplot-savefig-in-python/
            #  plot.savefig(modis_sphere_output_file_path, format="jpg")

            # Optionally display the pie chart(s) (for finetuning so adjusting is easier)
            # https://www.geeksforgeeks.org/matplotlib-pyplot-show-in-python/
            plot.show()

        # If "MODIS percentage" is selected, this case is used to create the general MODIS forest type percentage pie chart
        if chart_type == "MODIS percentage":

            # Count the occurrences of each MODIS forest type to create the percentages
            # https://pandas.pydata.org/docs/reference/api/pandas.Series.value_counts.html
            modis_category_counts = complete_gdf["forest"].value_counts()

            # Change the label for "Other" category, so it is not too long (only for bar plots with MODIS involved)
            # https://pandas.pydata.org/docs/user_guide/basics.html#renaming-mapping-labels
            modis_category_counts.rename(
                index={
                    "Other (Mangrove Forest, Open Shrubland, Savannas, Permanent Wetlands, ...)": "Other"
                },
                inplace=True,
            )

            # Map the study types to their corresponding colors from https://developers.google.com/earth-engine/datasets/catalog/MODIS_061_MCD12Q1#bands "LC_Type1 Class Table"
            # https://stackoverflow.com/questions/26139423/plot-different-color-for-different-categorical-levels
            modis_color_mapping = {
                "Evergreen Needleleaf Forest": "#05450a",  # Dark Green
                "Evergreen Broadleaf Forest": "#086a10",  # Forest Green
                "Deciduous Needleleaf Forest": "#54a708",  # Lime Green
                "Deciduous Broadleaf Forest": "#78d203",  # Bright Lime
                "Mixed Forest": "#009900",  # Green
                "Closed Shrubland": "#c6b044",  # Goldenrod
                "Woody Savanna": "#dade48",  # Light Yellow-Green
                "Other": "#27ff87",  # Bright Mint Green
            }

            # Create a list of colors in the same order as the labels in modis_category_counts
            modis_colors = [
                modis_color_mapping[label] for label in modis_category_counts.index
            ]

            # Exploding the "Deciduous Needleleaf Forest" slice so the difference and the percentages are clearer
            # https://www.educative.io/answers/how-to-explode-a-pie-chart-using-matplotlib-in-python
            explode = [0, 0, 0, 0, 0, 0, 0, 0.2]

            # Adjust the size of the plot so the picture is better usable later on
            # https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.figure.html
            plot.figure(figsize=(10, 8))

            # Create the pie chart with percentages and white lines between the pieces
            # https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.pie.html
            wedges, texts, autotexts = plot.pie(
                modis_category_counts,
                autopct="%1.1f%%",
                colors=modis_colors,
                startangle=90,
                explode=explode,
                wedgeprops={"edgecolor": "white", "linewidth": 0.5},
            )

            # Set label positions manually for the MODIS forest types "Deciduous Needleleaf Forest", "Closed Shrubland" and "Other",
            # so they are right next to their pieces, by iterating over all labels by using .index to enumerate them
            # https://stackoverflow.com/a/43916835 (set_position())
            # https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.title.html
            # https://www.w3schools.com/python/pandas/ref_df_index.asp
            # https://stackoverflow.com/a/43916835 (set_position())
            # https://matplotlib.org/stable/api/text_api.html#module-matplotlib.text
            for i, label in enumerate(modis_category_counts.index):
                # Re-capitalize labels for the pie chart by defining them as titles
                label = label.title()
                # Adjusting the position of "Deciduous Needleleaf Forest" by using specific coordinates
                if label == "Deciduous Needleleaf Forest":
                    texts[i].set_position((-0.25, 1.24))
                # Adjusting the position of "Closed Shrubland" by using specific coordinates
                if label == "Closed Shrubland":
                    texts[i].set_position((0.07, 1.062))
                # Adjusting the position of "Other" by using specific coordinates
                if label == "Other":
                    texts[i].set_position((0.632, 0.87))
                else:
                    # Keep default position for other labels since they are fine on default
                    texts[i].set_position(texts[i].get_position())

                # Adding back the study type label text (since set_position overrides them)
                # https://www.tutorialspoint.com/how-to-add-title-to-subplots-in-matplotlib#:~:text=The%20Matplotlib%20set_text()%20function,in%20a%20subplot%20or%20plot.
                texts[i].set_text(label)

            # Draw the plot as circle and ensure equal aspect ratio
            # https://matplotlib.org/stable/gallery/subplots_axes_and_figures/axis_equal_demo.html
            plot.axis("equal")

            # Set the title and filename for this pie chart
            # https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.title.html#matplotlib-pyplot-title
            plot.title("Distribution of the MODIS forest types in percentages")
            study_type_output_path = r"D:\Uni\Bachelorarbeit\Plots\Pie chart with MODIS forest category percentages from the complete locations shapefile.jpg"

            # Save the pie chart as a JPG file to use it in the thesis
            # https://www.geeksforgeeks.org/matplotlib-pyplot-savefig-in-python/
            # plot.savefig(study_type_output_path, format="jpg")

            # Optionally display the plot (for finetuning so adjusting is easier)
            # https://www.geeksforgeeks.org/matplotlib-pyplot-show-in-python/
            plot.show()


        # If "Continent percentage" is selected, this case is used to create the general continent percentage pie chart
        if chart_type == "Continent percentage":
            # Count the occurrences of each continent to create the percentages
            # https://pandas.pydata.org/docs/reference/api/pandas.Series.value_counts.html
            continent_counts = complete_gdf["Continent"].value_counts()

            # Map the study types to their corresponding colors from https://developers.google.com/earth-engine/datasets/catalog/MODIS_061_MCD12Q1#bands "LC_Type1 Class Table"
            # https://stackoverflow.com/questions/26139423/plot-different-color-for-different-categorical-levels
            continent_color_mapping = {
                "Europe": "#0000FF",  # blue
                "Africa": "#808080",  # grey
                "Asia": "#FFFF00",  # yellow
                "Oceania": "#008000",  # green
                "US": "#ADD8E6",       # light blue
                "North America": "#FF0000",  # red
                "Latin and South America": "#FFA500"  # orange
            }

            # Create a list of colors in the same order as the labels in modis_category_counts
            continent_colors = [
                continent_color_mapping[label] for label in continent_counts.index
            ]

            # Adjust the size of the plot so the picture is better usable later on
            # https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.figure.html
            plot.figure(figsize=(8, 7))

            # Create the pie chart with percentages and white lines between the pieces
            # https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.pie.html
            wedges, texts, autotexts = plot.pie(
                continent_counts,
                autopct="%1.1f%%",
                colors=continent_colors,
                startangle=90,
                wedgeprops={"edgecolor": "black", "linewidth": 0.5},
            )


            # Set label positions manually for the  continent "North America" so it is right next to its segment in the pie chart
            # by iterating over all labels by using .index to enumerate them
            # https://stackoverflow.com/a/43916835 (set_position())
            # https://www.w3schools.com/python/pandas/ref_df_index.asp
            # https://stackoverflow.com/a/43916835 (set_position())
            # https://matplotlib.org/stable/api/text_api.html#module-matplotlib.text
            for i, label in enumerate(continent_counts.index):
                # Re-capitalize labels for the pie chart by defining them as titles
                label = label
                # Adjusting the position of "North America" by using specific coordinates
                if label == "North America":
                    texts[i].set_position((0.1, 1.05))
                else:
                    # Keep default position for other labels since they are fine on default
                    texts[i].set_position(texts[i].get_position())

                # Adding back the study type label text (since set_position overrides them)
                # https://www.tutorialspoint.com/how-to-add-title-to-subplots-in-matplotlib#:~:text=The%20Matplotlib%20set_text()%20function,in%20a%20subplot%20or%20plot.
                texts[i].set_text(label)

            # Set the title and filename for this pie chart
            # https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.title.html#matplotlib-pyplot-title
            plot.title("Distribution of the continents in percentages")
            continent_output_path = r"D:\Uni\Bachelorarbeit\Plots\Pie chart with continent percentages from the complete locations shapefile.jpg"

            # Save the pie chart as a JPG file to use it in the thesis
            # https://www.geeksforgeeks.org/matplotlib-pyplot-savefig-in-python/
            # plot.savefig(continent_output_path, format="jpg")

            # Optionally display the plot (for finetuning so adjusting is easier)
            # https://www.geeksforgeeks.org/matplotlib-pyplot-show-in-python/
            plot.show()

# DONE
# Generate the general continent percentages pie chart
# create_pie_chart(reanalysis_shapefile_path, "Continent percentage")

# DONE
# Generate the sphere SPEI category percentage pie chart
# create_pie_chart(reanalysis_shapefile_path, "Spheres SPEI")

# DONE
# Generate the Spheres drought category keywords percentage pie chart
# create_pie_chart(excel_file_path, "Spheres drought category")

# DONE
# Generate the MODIS forest type percentage pie chart
# create_pie_chart(all_studies_shapefile_path, "MODIS percentage")

# DONE
# Generate the SPEI category percentage pie chart
# create_pie_chart(reanalysis_shapefile_path, "SPEI category percentage")

# DONE
# Generate the general study type percentages pie chart
# create_pie_chart(excel_file_path, "study type")

# DONE
# Generate the study type breakdown of given drought quantification keyword pie chart
# create_pie_chart(excel_file_path, "breakdown")

# DONE
# Generate the MODIS breakdown of given drought quantification keyword pie chart
# create_pie_chart(all_studies_shapefile_path, "MODIS drought category")

# Done
# Generate the MODIS breakdown of drought spheres pie chart
# create_pie_chart(all_studies_shapefile_path, "MODIS drought sphere")

# Generate overview pie chart of drought spheres
# create_pie_chart(excel_file_path, "spheres")


def create_true_false_bar_chart(shape_or_excel_file_path, chart_type):
    """
    Generates a stacked bar chart visualizing either the correlation of drought category keywords with
    drought quantification or the correctness of drought quantification. The chart is generated based on
    the specified `chart_type`, using data from either a shapefile or an Excel file, and saved as a JPG image.
    The function is designed to combine (hatched) bar chart creation logic for different cases which all use the given
    drought categories from the papers and "True" or "False" values for the stacked bars.
    This allows for easy extension if more bar charts are needed in the future from the same shapefile or Excel data,
    without requiring the creation of additional functions.

    Args:
        shape_or_excel_file_path (str): The file path to the shapefile or Excel file to be analyzed.
                                        The path can be either a .shp or .xlsx file, and the data
                                        should contain columns for drought quantification and correctness.
        chart_type (str): Specifies the type of pie chart to generate.
                        Options are:
                            - "Drought quantified": Correlation of drought category keywords with quantification.
                            - "Drought correctness": Correctness of drought quantification based on SPEI categories.

    Returns:
        None: The function saves the generated bar chart as a JPG image.
    """
    # Maybe also implement cases in this one but not sure if there is another plot fitting needed

    if chart_type == "Drought quantified":
        # Load the Excel file and "relevantInfo" sheet where the data for the pie charts is stored
        # https://pandas.pydata.org/docs/reference/api/pandas.read_excel.html
        excel_df = pd.read_excel(shape_or_excel_file_path, sheet_name="relevantInfo")

        # Set the output path for this bar plot
        output_file_path = r"D:\Uni\Bachelorarbeit\Plots\Bar plot that shows the correlation between all given drought keywords and if drought was quantified in percent.jpg"

        # Grouping the data by "drought quantification keyword for plots" and "was drought quantified**"
        # to count their occurrences and the percentages later
        # https://pandas.pydata.org/docs/user_guide/10min.html#grouping
        # https://www.geeksforgeeks.org/list-size-method-in-java-with-examples/
        # https://www.statology.org/pandas-unstack/
        drought_quantification_counts = (
            excel_df.groupby(
                ["drought quantification keyword for plots", "was drought quantified**"]
            )
            .size()
            .unstack(fill_value=0)
        )

        # Calculate the percentage for each drought quantification keyword by dividing each value by the global total (sum of all counts)
        # https://www.w3schools.com/python/pandas/ref_df_sum.asp
        # https://www.w3schools.com/python/pandas/ref_df_div.asp
        drought_quantification_global_total = drought_quantification_counts.values.sum()
        drought_quantification_percentage = (
            drought_quantification_counts.div(drought_quantification_global_total) * 100
        )

        # Set the order as wanted for the X-Axis by creating a list that has all the keywords in the wanted order
        desired_drought_keyword_order = [
            '"Dry"',
            "Dry season",
            "Differs from normal",
            "Low soil moisture",
            "Low water flow/depth",
            "Reduced rainfall",
            "Standardized Index",
            "Plant water stress",
        ]

        # Applying the desired order to the data so it will be used for the X-Axis
        # https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.reindex.html
        sorted_drought_quantification_percentage = (
            drought_quantification_percentage.reindex(desired_drought_keyword_order)
        )

        # Change the "True" and "False" values from the Excel file to strings because they could not be used to set a desired order
        # https://stackoverflow.com/a/60553529 (astype("string"))
        sorted_drought_quantification_percentage.columns = (
            sorted_drought_quantification_percentage.columns.astype("string")
        )

        # Generate the plot with sorted categories and hardcoded colors, as well as the order for the bars
        # ("darkblue" on the bottom for "True", "red" on the top for "False")
        # https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.bar.html
        sorted_drought_quantification_percentage[["True", "False"]].plot(
            kind="bar",
            stacked=True,
            figsize=(10, 6),
            color=["darkblue", "red"],
            edgecolor="black",
        )

        # Counting the values for "True" and "False" to add them to the Legend
        # Again, the series values had to be converted to strings first
        # https://stackoverflow.com/a/60553529 (astype("string"))
        # https://www.w3schools.com/python/pandas/ref_df_sum.asp
        true_count = (
            drought_quantification_counts[True].sum()
            if "True" in drought_quantification_counts.columns.astype("string")
            else 0
        )
        false_count = (
            drought_quantification_counts[False].sum()
            if "False" in drought_quantification_counts.columns.astype("string")
            else 0
        )

        # Add the legend, so it gets clear what part of the bars is "True" and "False"
        # https://matplotlib.org/stable/api/legend_api.html#module-matplotlib.legend
        plot.legend(
            [
                f"Quantified (True): {true_count}",
                f"Not Quantified (False): {false_count}",
            ],
            title="Was drought quantified?",
            loc="upper right",
            alignment="left",
        )

        # Optionally set a title for this case for a better overview (not needed later in the thesis)
        title = (
            "Correlation between given drought keywords and if drought was quantified"
        )

        # Set the y-axis limit to 30% for a better overview
        # https://www.geeksforgeeks.org/matplotlib-pyplot-ylim-in-python/
        plot.ylim(0, 35)

    if chart_type == "Drought correctness":
        # Read the given shapefile geopandas read_file() method and storing it as geodataframe
        # https://geopandas.org/en/stable/docs/user_guide/data_structures.html#geodataframe
        # https://geopandas.org/en/stable/docs/user_guide/io.html#reading-and-writing-files
        complete_gdf = geopd.read_file(shape_or_excel_file_path)

        # Set the output path for this bar plot
        output_file_path = r"D:\Uni\Bachelorarbeit\Plots\Bar plot that shows the correctness of the given drought quantification keywords for all re-analyzed paper locations.jpg"

        # Set the title for this case
        title = "Bar plot to show the correctness of the given drought keywords"

        # Grouping the data by "dr_quanti" and "drouright" to count their occurrences and the percentages later
        # https://pandas.pydata.org/docs/user_guide/10min.html#grouping
        # https://www.geeksforgeeks.org/list-size-method-in-java-with-examples/
        # https://www.statology.org/pandas-unstack/
        drought_correctness_counts = (
            complete_gdf.groupby(["dr_quanti", "drouright"])
            .size()
            .unstack(fill_value=0)
        )

        # Calculate the percentage for each drought quantification keyword by dividing each value by the global total (sum of all counts)
        # https://www.w3schools.com/python/pandas/ref_df_sum.asp
        # https://www.w3schools.com/python/pandas/ref_df_div.asp
        global_total = drought_correctness_counts.values.sum()
        drought_correctness_counts_percentage = (
            drought_correctness_counts.div(global_total) * 100
        )

        # Calculate the sum of all rows (True & False for each drought quantification keyword) and store it in a "Total" column
        # This new "Total" column is then used for sorting the categories in descending order based on the total occurrences.
        # https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.sort_values.html
        drought_correctness_counts_percentage["Total"] = (
            drought_correctness_counts_percentage.sum(axis=1)
        )

        # Sort by the total percentage of (True & False) in descending order and then remove the "Total" column because it served its purpose
        # https://www.w3schools.com/python/pandas/ref_df_sort_values.asp
        # https://www.w3schools.com/python/pandas/ref_df_drop.asp
        sorted_category_counts_percentage = (
            drought_correctness_counts_percentage.sort_values(
                by="Total", ascending=False
            ).drop(columns=["Total"])
        )

        # Generate the plot with sorted categories and hardcoded colors
        # https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.bar.html
        sorted_category_counts_percentage[["True", "False"]].plot(
            kind="bar",
            stacked=True,
            figsize=(10, 6),
            color=["darkblue", "red"],
            edgecolor="black",
        )

        # Again, the series values had to be converted to strings first
        # https://www.w3schools.com/python/pandas/ref_df_sum.asp
        true_count = (
            drought_correctness_counts["True"].sum()
            if "True" in drought_correctness_counts.columns
            else 0
        )
        false_count = (
            drought_correctness_counts["False"].sum()
            if "False" in drought_correctness_counts.columns
            else 0
        )

        # Add the legend, so it gets clear what part of the bars is "True" and "False"
        # https://matplotlib.org/stable/api/legend_api.html#module-matplotlib.legend
        plot.legend(
            [
                f"There was a drought (True): {true_count}",
                f"There was no drought (False): {false_count}",
            ],
            title="Was there a drought according to SPEI?",
            loc="upper right",
            alignment="left",
        )

    if chart_type in ["Drought quantified", "Drought correctness"]:

        # For ALL cases so the two cases have to come back together here:

        # Customize the "False" bars with diagonal stripes by using .gca() to get the needed axis and its patches
        # https://www.geeksforgeeks.org/matplotlib-pyplot-gca-in-python/
        # https://stackoverflow.com/a/59586067 (set_hatch)
        # Use gca to get all axes and their patches with .patches
        bars = plot.gca().patches
        # Iterate over the bars
        for bar in bars:
            # Determines that only the red colored stacked bar gets diagonally striped
            if bar.get_facecolor() == (1.0, 0.0, 0.0, 1.0):
                bar.set_hatch("//")

        # Add X-axis title manually for both cases because it is the same
        # https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.xlabel.html#matplotlib.pyplot.xlabel
        plot.xlabel("Given drought category")

        # Add manual y-axis label manually for both cases because it is the same
        # https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.ylabel.html#matplotlib-pyplot-ylabel
        plot.ylabel("Percentage of all drought category keywords")

        # Optionally add the title from the cases
        # https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.title.html#matplotlib-pyplot-title
        plot.title(title)

        # Rotate x-axis labels for readability and better plot-text ratio
        # https://www.geeksforgeeks.org/matplotlib-pyplot-xticks-in-python/
        plot.xticks(rotation=45)

        # Ensure that the tight layout is used for a better visualisation
        # https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.tight_layout.html#matplotlib.pyplot.tight_layout
        plot.tight_layout()

        # Save the bar plot as a JPG file to use it in the thesis
        # https://www.geeksforgeeks.org/matplotlib-pyplot-savefig-in-python/
        # plot.savefig(output_file_path, format="jpg")

        # Optionally display the plot (for finetuning so adjusting is easier)
        # https://www.geeksforgeeks.org/matplotlib-pyplot-show-in-python/
        plot.show()


# DONE
# Generate the bar plot with correctness of the given drought quantification keywords for all re-analyzed paper locations
# create_true_false_bar_chart(reanalysis_shapefile_path, "Drought correctness")

# DONE
# Generate the bar plot that shows the correlation between all given drought keywords and if drought was quantified in percent
# create_true_false_bar_chart(excel_file_path, "Drought quantified")
