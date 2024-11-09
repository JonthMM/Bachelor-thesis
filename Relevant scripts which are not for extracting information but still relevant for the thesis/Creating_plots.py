# Importing pandas for data manipulation and analysis and giving it the alias pd for further usage
import pandas as pd

# Importing geopandas for working with geospatial data, including shapefiles and giving it the alias geopd for further usage
import geopandas as geopd

# Creates the plots from the data handled by (geo)pandas by using matplotlib.pyplot and giving it the alias plot for further usage
import matplotlib.pyplot as plot

# Add the patches module from matplotlib for a better representation of the legends and giving it the alias mpatches for further usage
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

    # Read the given shapefile for all pie chart cases using geopandas read_file() method and storing it as a geodataframe
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
        # Grouping the data by "MODIS" and "drouquanti" to count occurrences of the drought quantifications
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
        output_file_path = r"D:\Uni\Bachelorarbeit\Plots\Aktuell\Re-worked data\NEW Bar chart for correlation between MODIS classes and given drought quantification keywords from complete paper points shapefile.jpg"

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
            "Dry season": "#adff2f",  # Green Yellow
            "Low soil moisture": "#b47d49",  # Brown
            "Low water flow/depth": "#4682b4",  # Steel Blue
            "Plant water stress": "#32cd32",  # Lime Green
            "Reduced rainfall": "#87CEEB",  # Sky Blue
            "Standardized Index": "#a245a8",  # Purple
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

        # Add titles and axis labels that were defined before depending on automatically from the titels
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
            sorted_legend_labels_with_counts,
            title="Drought Keyword",
            loc="upper right",
            frameon=False,
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
                            - "Drought keyword SPEI": Correlates SPEI drought categories with drought quantification keywords.
                            - "MODIS SPEI": Correlates SPEI drought categories with MODIS forest types.
                            - "Continent SPEI": Correlates SPEI drought categories with the continent of locations.
    Returns:
        None: The function saves the generated bar chart as a JPG image.
    """

    # Reading the given shapefile using geopandas read_file() method and storing it as geodataframe
    # https://geopandas.org/en/stable/docs/user_guide/data_structures.html#geodataframe
    # https://geopandas.org/en/stable/docs/user_guide/io.html#reading-and-writing-files
    gdf = geopd.read_file(shapefile_path)

    # For Study types and SPEI drought categories
    if chart_type == "Study type SPEI Bar":
        # Grouping the data by "studytype" and "Category" to count occurrences for the drought chart
        # https://pandas.pydata.org/docs/user_guide/10min.html#grouping
        # https://www.statology.org/pandas-unstack/
        # https://note.nkmk.me/en/python-pandas-len-shape-size/#get-the-number-of-elements-dfsize
        category_counts = (
            gdf.groupby(["studytype", "Category"]).size().unstack(fill_value=0)
        )
        # X-axis text
        xaxisdescription = "Study type"
        # Title of the plot
        title = "Distribution of SPEI drought categories in correlation with the used study types of the re-analysed paper locations"
        # Path where the plot is going to be saved
        output_file_path = r"D:\Uni\Bachelorarbeit\Plots\Aktuell\re-analysis\No frame on legend\NEW Bar chart for correlation of SPEI drought category and the used study types of the re-analysed paper locations in percent.jpg"


    # For continents and SPEI drought categories
    if chart_type == "Continent SPEI":
        # Grouping the data by "Continent" and "Category" to count occurrences for the drought chart
        # https://pandas.pydata.org/docs/user_guide/10min.html#grouping
        # https://www.statology.org/pandas-unstack/
        # https://note.nkmk.me/en/python-pandas-len-shape-size/#get-the-number-of-elements-dfsize
        category_counts = (
            gdf.groupby(["Continent", "Category"]).size().unstack(fill_value=0)
        )
        # X-axis text
        xaxisdescription = "Global region"
        # Title of the plot
        title = "Distribution of SPEI drought categories in correlation with the continents of the re-analysed paper locations"
        # Path where the plot is going to be saved
        output_file_path = r"D:\Uni\Bachelorarbeit\Plots\Aktuell\re-analysis\No frame on legend\NEW Bar chart for correlation of SPEI drought category and the continents of the re-analysed paper locations in percent.jpg"

    # For the given drought quantification keywords from the studies and SPEI drought categories
    if chart_type == "Drought keyword SPEI":
        # Grouping the data by "drouquanti" and "Category" to count occurrences for the drought chart
        # https://pandas.pydata.org/docs/user_guide/10min.html#grouping
        # https://www.statology.org/pandas-unstack/
        # https://note.nkmk.me/en/python-pandas-len-shape-size/#get-the-number-of-elements-dfsize
        category_counts = (
            gdf.groupby(["drouquanti", "Category"]).size().unstack(fill_value=0)
        )
        # X-axis text
        xaxisdescription = "Given drought category"
        # Title of the plot
        title = "Distribution of SPEI drought categories in correlation with the given drought quantification keywords from the studies"
        # Path where the plot is going to be saved
        output_file_path = r"D:\Uni\Bachelorarbeit\Plots\Aktuell\new data\NEW Bar chart for correlation of SPEI drought category and the given drought quantifications of the studies  in percent.jpg"

    # For MODIS forest types and SPEI drought categories
    if chart_type == "MODIS SPEI":
        # Grouping the data by "forest" and "Category" to count occurrences for the MODIS chart
        # https://pandas.pydata.org/docs/user_guide/10min.html#grouping
        # https://www.statology.org/pandas-unstack/
        # https://note.nkmk.me/en/python-pandas-len-shape-size/#get-the-number-of-elements-dfsize
        category_counts = (
            gdf.groupby(["forest", "Category"]).size().unstack(fill_value=0)
        )
        # X-axis text
        xaxisdescription = "Forest type"
        # Title of the plot
        title = "Distribution of SPEI drought categories within each MODIS category"
        # Path where the plot is going to be saved
        output_file_path = r"D:\Uni\Bachelorarbeit\Plots\Aktuell\re-analysis\No frame on legend\NEW Bar chart for correlation MODIS classes and SPEI drought categories in percent.jpg"

    # For all cases that somehow use "Category" (The SPEI categories)
    if chart_type in ["Drought keyword SPEI", "MODIS SPEI", "Continent SPEI", "Study type SPEI Bar"]:
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
            "no drought (+1 < SPEI)",
        ]

        # Reindex the columns of my "category_counts_sorted" DataFrame with the created list
        # https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.reindex.html
        category_counts_sorted = category_counts_sorted.reindex(
            columns=spei_desired_order
        )

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
            for category, label in zip(
                sorted_spei_categories, sorted_legend_labels_with_counts
            )
        ]

        # Place the sorted legend with counts inside the plot on the upper right
        # https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.legend.html
        plot.legend(
            handles=legend_handles,
            title="SPEI drought category",
            loc="upper right",
            frameon=False,
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

        # Adjust the Y-Axis manually by a fixed array
        # https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.yticks.html#matplotlib-pyplot-yticks
        # For the two cases that only need 0-35
        if chart_type in ["MODIS SPEI", "Continent SPEI"]:
            plot.yticks(
                [0, 2.5, 5, 7.5, 10, 12.5, 15, 17.5, 20, 22.5, 25, 27.5, 30, 32.5, 35]
            )
        # For the other case that needs 0-40
        elif chart_type in ["Drought keyword SPEI"]:
            plot.yticks(
                [
                    0,
                    2.5,
                    5,
                    7.5,
                    10,
                    12.5,
                    15,
                    17.5,
                    20,
                    22.5,
                    25,
                    27.5,
                    30,
                    32.5,
                    35,
                    37.5,
                    40,
                ]
            )

        # For the study types since Observational has way more then the other
        elif chart_type in ["Study type SPEI Bar"]:
            plot.yticks(
                [
                    0,
                    2.5,
                    5,
                    7.5,
                    10,
                    12.5,
                    15,
                    17.5,
                    20,
                    50,
                    43,
                    70,
                    76
                ]
            )


        # Ensure that the tight layout is used for a better visualisation
        # https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.tight_layout.html#matplotlib.pyplot.tight_layout
        plot.tight_layout()

        # Save the plot as a JPG file to use it in the bachelor-thesis
        # https://www.geeksforgeeks.org/matplotlib-pyplot-savefig-in-python/
        plot.savefig(output_file_path, format="jpg")

        # Optionally display the plot (for finetuning so adjusting is easier)
        # https://www.geeksforgeeks.org/matplotlib-pyplot-show-in-python/
        plot.show()


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
                            - "drought keywords percentage excel": Distribution of drought keywords from Excel.
                            - "drought keywords percentage": Distribution of drought keywords from re-analysed paper points.
                            - "study type": Distribution of study types from Excel.
                            - "study type drought category excel": Breakdown of drought quantification keywords by study type from Excel.
                            - "study type drought category": Breakdown of drought quantification keywords by study type from re-analysed paper locations.
                            - "study type SPEI": Breakdown of SPEI categories for each study type.
                            - "MODIS drought category all": Breakdown of drought categories for MODIS forest types from all locations.
                            - "MODIS drought category": Breakdown of drought categories for MODIS forest types from re-analysed locations.
                            - "MODIS percentage all": Percentage distribution of MODIS forest types from all locations.
                            - "MODIS percentage": Percentage distribution of MODIS forest types from re-analysis locations.
                            - "MODIS drought sphere": Drought sphere categories for MODIS forest types.
                            - "Spheres drought category excel": Drought quantification breakdown for each sphere from Excel.
                            - "Spheres drought category": Drought quantification breakdown for each sphere from re-analysed paper locations.
                            - "spheres": Percentage overview of drought spheres.
                            - "Spheres SPEI": Breakdown of SPEI categories for each sphere.
                            - "Continent percentage all": Percentage distribution by continent from all locations.
                            - "Continent drought category all": Drought quantification breakdown for each continent from all locations.
                            - "Continent drought category": Drought quantification breakdown for each continent re-analysis locations.
                            - "Continent SPEI": Breakdown of SPEI categories for each continent.
                            - "SPEI category percentage": Percentage of re-analysed study locations by SPEI category.
                            - "Quantified correctness": Correctness of whether drought was quantified or not.
                            - "Quantification drought keywords": Contribution of drought keywords for quantified or not.

    Returns:
        None: The function saves the generated pie chart(s) as a JPG image.
    """

    # Cases for the pie charts that need data from the Excel file
    if chart_type in [
        "study type",
        "study type drought category excel",
        "MODIS drought sphere",
        "spheres",
        "Spheres drought category excel",
        "drought keywords percentage excel",
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
            "Dry season": "#adff2f",  # Green Yellow
            "Low soil moisture": "#b47d49",  # Brown
            "Low water flow/depth": "#4682b4",  # Steel Blue
            "Plant water stress": "#32cd32",  # Lime Green
            "Reduced rainfall": "#87CEEB",  #  Sky Blue
            "Standardized Index": "#a245a8",  # Purple
        }

        # If "drought keywords percentage excel" is selected, create the general drought keywords pie chart from the Excel
        if chart_type == "drought keywords percentage excel":
            # Count the occurrences of each drought keyword and clean them to create the percentages, then count its occurrences with size()
            # Remove quotes with replace() (because python gives an error for "dry" keyword if there are quotes)
            # https://pandas.pydata.org/docs/reference/api/pandas.Series.str.replace.html
            # https://pandas.pydata.org/docs/reference/api/pandas.Series.str.strip.html
            # https://pandas.pydata.org/docs/reference/api/pandas.Series.value_counts.html
            drought_keywords_counts = (
                excel_df["drought quantification keyword for plots"]
                .str.strip()
                .str.replace('"', "")
                .value_counts()
            )

            # Create a list of colors in the same order as the labels in spei_category_counts to use it for the pie chart
            drought_keywords_colors = [
                drought_keywords_color_mapping[label]
                for label in drought_keywords_counts.index
            ]

            # Adjust the size of the plot so the picture is better usable later and nothing gets cut off
            # https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.figure.html
            plot.figure(figsize=(11, 7))

            # Create the pie chart with black lines between pieces and percentages as texts
            # https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.pie.html
            wedges, category_texts, autotexts = plot.pie(
                drought_keywords_counts,
                autopct="%1.1f%%",
                colors=drought_keywords_colors,
                wedgeprops={"edgecolor": "black", "linewidth": 0.4},
            )

            # Change the color of the percentages to white for clearer visibility
            # https://stackoverflow.com/a/27899541 (set_color())
            for autotext in autotexts:
                autotext.set_color("black")

            # Manage the labels for the segments by iterating over the dataframe "drought_keywords_counts"
            # https://www.w3schools.com/python/pandas/ref_df_index.asp
            # https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.title.html
            for i, keyword_label in enumerate(drought_keywords_counts.index):

                # Add back the "" for the "Dry" drought keyword since it had to be removed earlier for python rules
                if keyword_label == "Dry":
                    keyword_label = '"Dry"'

                # Add the drought keyword label texts automatically from the drought_keywords_counts dataframe
                # https://www.tutorialspoint.com/how-to-add-title-to-subplots-in-matplotlib#:~:text=The%20Matplotlib%20set_text()%20function,in%20a%20subplot%20or%20plot.
                category_texts[i].set_text(keyword_label)

            # Set the main title as well as the file name
            # https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.title.html#matplotlib-pyplot-title
            plot.title("Distribution of the drought keywords out of all studies")
            drought_keywords_output_file_path = r"D:\Uni\Bachelorarbeit\Plots\Aktuell\new data\NEW Pie chart with drought keywords percentages and legend for total numbers from excel updated.jpg"

            # Create and add a legend for the total numbers of drought keywords for a better overview of the data
            # Create the labels out of the SPEI categories for the legend with counts so the total numbers are displayed
            # Also add back the "" for the "Dry" drought keyword since it had to be removed earlier for python rules
            # https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.items.html#pandas-dataframe-items
            # https://docs.python.org/3/library/stdtypes.html#str.replace
            keywords_legend_labels = [
                f'"{label}": {count}' if label == "Dry" else f"{label}: {count}"
                for label, count in drought_keywords_counts.items()
            ]

            # Now add the legend to the pie chart with the drought keyword labels and place it in the upper right outside the pie chart (with bbox_to_anchor)
            # https://matplotlib.org/stable/api/legend_api.html#module-matplotlib.legend
            plot.legend(
                wedges,
                keywords_legend_labels,
                title="Drought categories: 168 total",
                loc="center right",
                bbox_to_anchor=(1, 0.15, 0.4, 1),
                frameon=False,
            )

            # Ensure that the tight layout is used for a better visualisation and readability
            # https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.tight_layout.html#matplotlib.pyplot.tight_layout
            plot.tight_layout()

            # Save the pie chart as a JPG file to use it in the thesis
            # https://www.geeksforgeeks.org/matplotlib-pyplot-savefig-in-python/
            plot.savefig(drought_keywords_output_file_path, format="jpg")

            # Optionally display the plot (for finetuning so adjusting is easier)
            # https://www.geeksforgeeks.org/matplotlib-pyplot-show-in-python/
            plot.show()

        # If "Spheres drought category excel" is selected, create the drought quantification breakdown pie charts for each drought sphere
        if chart_type == "Spheres drought category excel":

            # Group the data by "drought_sphere" and clean the drought quantification keywords and then count its occurrences with size()
            # Remove quotes with replace() (because python gives an error for "dry" keyword if there are quotes)
            # Also create the pivot table to have "drought_sphere" as columns and fill missing with 0
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
                # No "startangle=90" because the percentages overlap if used
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
                "Breakdown of the given drought quantification for the drought spheres",
                fontsize=16,
            )
            sphere_category_output_file_path = r"D:\Uni\Bachelorarbeit\Plots\Aktuell\new data\NEW Breakdown pie charts for percentages of drought definitions for the drought spheres from the Excel file.jpg"

            # Ensure that the tight layout is used for a better visualisation (the single pie charts are too close to another if not used)
            # https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.tight_layout.html#matplotlib.pyplot.tight_layout
            plot.tight_layout()

            # Save the pie chart(s) as one JPG file to use it in the thesis
            # https://www.geeksforgeeks.org/matplotlib-pyplot-savefig-in-python/
            plot.savefig(sphere_category_output_file_path, format="jpg")

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
            study_type_output_path = r"D:\Uni\Bachelorarbeit\Plots\Aktuell\Re-worked data\NEW main pie chart with complete drought sphere percentages.jpg"

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

        # If "study type drought category excel" is selected, create the drought quantification breakdown pie charts for each study type
        elif chart_type == "study type drought category excel":
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
            breakdown_output_file_path = r"D:\Uni\Bachelorarbeit\Plots\Aktuell\new data\NEW Breakdown pie charts for percentages of drought definitions for study types.jpg"

            # Ensure that the tight layout is used for a better visualisation (the single pie charts are too close to another if not used)
            # https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.tight_layout.html#matplotlib.pyplot.tight_layout
            plot.tight_layout()

            # Save the pie chart(s) as one JPG file to use it in the thesis
            # https://www.geeksforgeeks.org/matplotlib-pyplot-savefig-in-python/
            plot.savefig(breakdown_output_file_path, format="jpg")

            # Optionally display the pie chart(s) (for finetuning so adjusting is easier)
            # https://www.geeksforgeeks.org/matplotlib-pyplot-show-in-python/
            plot.show()

    # Cases for all pie charts that need data from the shapefile with all re-analysed paper locations
    elif chart_type in [
        "SPEI category percentage",
        "Spheres SPEI",
        "Spheres drought category",
        "study type SPEI",
        "study type drought category",
        "MODIS percentage",
        "MODIS drought category",
        "Continent percentage",
        "Continent drought category",
        "drought keywords percentage",
        "Quantified correctness",
        "Quantification drought keywords",
    ]:

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

        # Define consistent colors for each drought quantification keyword across all plots, globally defined because of multiple use cases
        # https://stackoverflow.com/questions/26139423/plot-different-color-for-different-categorical-levels
        drought_keywords_color_mapping = {
            "Dry": "#ff7f0e",  # Dark Orange
            "Differs from normal": "#ff4500",  # Orange-Red
            "Dry season": "#adff2f",  # Green Yellow
            "Low soil moisture": "#b47d49",  # Brown
            "Low water flow/depth": "#4682b4",  # Steel Blue
            "Plant water stress": "#32cd32",  # Lime Green
            "Reduced rainfall": "#87CEEB",  # Sky Blue
            "Standardized Index": "#a245a8",  # Purple
        }

        # If "Quantification drought keywords" is selected, create the drought keywords distribution pie charts for if drought was quantified or not from the re-analysed paper points
        if chart_type == "Quantification drought keywords":
            # Group the data by "wasdrquant" and "drouright" then count its occurrences with size()
            # Also create the pivot table to have "wasdrquant" as columns and fill missing values with 0
            # https://pandas.pydata.org/docs/user_guide/10min.html#grouping
            # https://pandas.pydata.org/docs/reference/api/pandas.Series.str.strip.html
            # https://www.geeksforgeeks.org/list-size-method-in-java-with-examples/
            # https://www.statology.org/pandas-unstack/
            # https://note.nkmk.me/en/python-pandas-len-shape-size/#get-the-number-of-elements-dfsize
            quant_drought_keywords_counts = (
                reanalysed_gdf.groupby(["wasdrquant", reanalysed_gdf["Category"]])
                .size()
                .unstack(fill_value=0)
            )
            # Set the output path for this drought category per quantification pie chart
            quant_drought_keywords_output_file_path = (
                r"D:\Uni\Bachelorarbeit\Plots\Aktuell\new data\Quantified_drought_keywords_pie_chart.jpg"
            )

            # Set the size of the figure and define the number of subplots
            # manually because we need one pie chart for each drought quantification category
            # https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.subplots.html
            fig, axes = plot.subplots(1, 2, figsize=(19, 7))

            # Flatten the axes for easier iteration and a faster plot creation
            # https://stackoverflow.com/questions/46862861/what-does-axes-flat-in-matplotlib-do
            axes = axes.flatten()

            # Create a list for the desired order of the spei categories inside the pie chars
            # https://pandas.pydata.org/docs/user_guide/indexing.html#indexing-and-selecting-data
            spei_desired_order = [
                "extremely dry (SPEI <= -2)",
                "severely dry (-2 < SPEI <= -1.5)",
                "moderately dry (-1.5 < SPEI <= -1)",
                "near normal conditions (-1 < SPEI < +1)",
                "no drought (+1 < SPEI)",
            ]

            # Iterate over the final dataframe that holds the wanted information to filter out zero values and assign the wanted colors
            # In this case everything has to be done in the for-loop because we need to add the legends separately for every pie chart, not one for all
            # https://www.w3schools.com/python/pandas/ref_df_iterrows.asp
            for i, wasdrquant_value in enumerate(quant_drought_keywords_counts.index):

                # Get the counts for the drought keywords per drought quantification category and filter out any zero values.
                # https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.loc.html#pandas-dataframe-loc
                counts = quant_drought_keywords_counts.loc[wasdrquant_value]

                # Reorder the counts be the desires SPEI category defined above
                # https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.reindex.html
                counts = counts.reindex(spei_desired_order)

                # Filter out redundant zero values in the retrieved counts (drought quantifications) with a simple comparison
                counts = counts[counts > 0]

                # Calculate and get the total numbers of "wasdrquant" for the title of the legend(s)
                # https://www.w3schools.com/python/ref_func_sum.asp
                total_count = counts.sum()

                # Create a list of colors in the same order as the labels in spei_category_counts to use it for the pie chart
                spei_colors = [spei_color_mapping[label] for label in counts.index]

                # Display percentages inside the pieces and assign the labels and colors to the pie chart pieces
                # Also replace "<=" with "≤" in the pie chart segment labels
                # https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.pie.html
                # https://docs.python.org/3/library/stdtypes.html#str.replace
                wedges, texts, autotexts = axes[i].pie(
                    counts,
                    labels=counts.index.str.replace("<=", "≤"),
                    autopct="%1.1f%%",
                    startangle=90,
                    colors=spei_colors,
                )

                # Change the color of the percentages to white for clearer visibility
                # https://stackoverflow.com/a/27899541 (set_color())
                for autotext in autotexts:
                    autotext.set_color("white")

                # Display a title for every single pie chart containing its drought quantification status
                # https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.set_title.html
                status = "Yes" if wasdrquant_value == "True" else "No"
                axes[i].set_title(f"Drought quantified: {status}")

                # Create the labels for the legends out of the segment labels and add a count for each category
                # https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.items.html#pandas-dataframe-items
                legend_labels = [
                    f'{label.replace("<=", "≤")}: {count}'
                    for label, count in counts.items()
                ]

                # Now add a legend to each pie chart separately on the upper right of the pie charts and
                # place it below the pie charts using "loc" and "bbox_to_anchor"
                # https://matplotlib.org/stable/api/legend_api.html#module-matplotlib.legend
                axes[i].legend(
                    legend_labels,
                    title=f'Total count of "Drought quantified: {status}" studies: {total_count}',
                    loc="upper center",
                    frameon=False,
                    bbox_to_anchor=(0.5, 0.1),
                )

            # Set the main title for the entire figure (has to be done separately because every pie chart has its own title) as well as the file name
            # https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.suptitle.html
            fig.suptitle(
                "Distribution of drought findings for quantified vs not quantified",
                fontsize=16,
            )

            # Ensure that the tight layout is used for a better visualisation (the single pie charts are too close to another if not used)
            # https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.tight_layout.html#matplotlib.pyplot.tight_layout
            plot.tight_layout()

            # Save the pie chart(s) as one JPG file to use it in the thesis
            # https://www.geeksforgeeks.org/matplotlib-pyplot-savefig-in-python/
            plot.savefig(quant_drought_keywords_output_file_path, format="jpg")

            # Optionally display the pie chart(s) (for finetuning so adjusting is easier)
            # https://www.geeksforgeeks.org/matplotlib-pyplot-show-in-python/
            plot.show()

        # If "Quantified correctness" is selected, create the correctness pie charts for if drought was quantified or not from the re-analysed paper points
        if chart_type == "Quantified correctness":

            # Group the data by "wasdrquant" and "drouright" then count its occurrences with size()
            # Also create the pivot table to have "wasdrquant" as columns and fill missing with 0
            # https://pandas.pydata.org/docs/user_guide/10min.html#grouping
            # https://pandas.pydata.org/docs/reference/api/pandas.Series.str.strip.html
            # https://www.geeksforgeeks.org/list-size-method-in-java-with-examples/
            # https://www.statology.org/pandas-unstack/
            # https://note.nkmk.me/en/python-pandas-len-shape-size/#get-the-number-of-elements-dfsize
            quant_correctness_counts = (
                reanalysed_gdf.groupby(["wasdrquant", reanalysed_gdf["drouright"]])
                .size()
                .unstack(fill_value=0)
            )
            # Set the output path for this quantification correctness pie chart
            quant_correctness_output_file_path = (
                r"D:\Uni\Bachelorarbeit\Plots\Aktuell\new data\Quantified_correctness_pie_chart.jpg"
            )

            # Set the size of the figure and define the number of subplots
            # manually because we need one pie chart for each drought quantification category
            # https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.subplots.html
            fig, axes = plot.subplots(1, 2, figsize=(15, 7))

            # Hard code the colors as a list to be used for the pie chart segments in this order ("red" for "False", "darkblue" for "True")
            correctness_colors = ["red", "darkblue"]

            # Flatten the axes for easier iteration and a faster plot creation
            # https://stackoverflow.com/questions/46862861/what-does-axes-flat-in-matplotlib-do
            axes = axes.flatten()

            # Iterate over the final dataframe that holds the wanted information to filter out zero values and assign the wanted colors
            # In this case everything has to be done in the for-loop because we need to add the legends seperately for every pie chart, not one for all
            # https://www.w3schools.com/python/pandas/ref_df_iterrows.asp
            for i, wasdrquant_value in enumerate(quant_correctness_counts.index):

                # Get the counts for the drought quantifications and filter out any zero values.
                # https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.loc.html#pandas-dataframe-loc
                counts = quant_correctness_counts.loc[wasdrquant_value]
                # Filter out redundant zero values in the retrieved counts (drought quantifications)
                counts = counts[counts > 0]

                # Calculate and get the total numbers of "wasdrquant" for the title of the legend(s)
                # https://www.w3schools.com/python/ref_func_sum.asp
                total_count = counts.sum()

                # Display percentages inside the pieces, assign the labels and colors to the pie chart pieces and set the startangle to 90°
                # https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.pie.html
                wedges, texts, autotexts = axes[i].pie(
                    counts,
                    labels=[
                        f"Correct (True)" if idx == "True" else "Incorrect (False)"
                        for idx in counts.index
                    ],
                    autopct="%1.1f%%",
                    colors=correctness_colors,
                    startangle=90,
                    wedgeprops={"edgecolor": "black", "linewidth": 0.5},
                )

                # Change the color of the percentages to white for clearer visibility
                # https://stackoverflow.com/a/27899541 (set_color())
                for autotext in autotexts:
                    autotext.set_color("white")

                # Display a title for every single pie chart containing its drought quantification status
                # https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.set_title.html
                status = "Yes" if wasdrquant_value == "True" else "No"
                axes[i].set_title(f"Drought quantified: {status}")

                # Get the counts for "True" and "False" values from "drouright", if they do not exist they get set to 0
                # https://www.w3schools.com/python/ref_dictionary_get.asp
                true_count = counts.get("True", 0)
                false_count = counts.get("False", 0)

                # Set the legend entries manually with all its attributes colors and hatches (using mpatches.Patch()), so they match the segments
                # https://matplotlib.org/stable/api/_as_gen/matplotlib.patches.Patch.html#matplotlib-patches-patch
                # https://stackoverflow.com/a/37296137
                true_patch = mpatches.Patch(
                    color="darkblue", label=f"Correct (True): {true_count}"
                )
                false_patch = mpatches.Patch(
                    color="red", label=f"Incorrect (False): {false_count}"
                )

                # Now add a legend each pie charts separately on the upper right of the pie charts
                # https://matplotlib.org/stable/api/legend_api.html#module-matplotlib.legend
                axes[i].legend(
                    handles=[true_patch, false_patch],
                    title=f"Classification of drought correctness: {total_count}",
                    loc="upper right",
                    frameon=False,
                )

            # Set the main title for the entire figure (has to be done separately because every pie chart has its own title) as well as the file name
            # https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.suptitle.html
            fig.suptitle(
                "Correctness of drought findings for quantified vs not quantified",
                fontsize=16,
            )

            # Ensure that the tight layout is used for a better visualisation (the single pie charts are too close to another if not used)
            # https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.tight_layout.html#matplotlib.pyplot.tight_layout
            plot.tight_layout()

            # Save the pie chart(s) as one JPG file to use it in the thesis
            # https://www.geeksforgeeks.org/matplotlib-pyplot-savefig-in-python/
            plot.savefig(quant_correctness_output_file_path, format="jpg")

            # Optionally display the pie chart(s) (for finetuning so adjusting is easier)
            # https://www.geeksforgeeks.org/matplotlib-pyplot-show-in-python/
            plot.show()

        # If "MODIS drought category" is selected, create the drought quantification breakdown pie charts for each MODIS forest class from the re-analysed paper points
        if chart_type == "MODIS drought category":
            # Group the data by "forest" and clean "drouquanti" and then count its occurrences with size()
            # Remove quotes with replace() (because python gives an error for "dry" keyword if there are quotes)
            # Also create the pivot table to have forest as columns and fill missing with 0
            # https://pandas.pydata.org/docs/user_guide/10min.html#grouping
            # https://pandas.pydata.org/docs/reference/api/pandas.Series.str.replace.html
            # https://pandas.pydata.org/docs/reference/api/pandas.Series.str.strip.html
            # https://www.geeksforgeeks.org/list-size-method-in-java-with-examples/
            # https://www.statology.org/pandas-unstack/
            # https://note.nkmk.me/en/python-pandas-len-shape-size/#get-the-number-of-elements-dfsize
            forest_breakdown_data = (
                reanalysed_gdf.groupby(
                    [
                        "forest",
                        reanalysed_gdf["drouquanti"].str.strip().str.replace('"', ""),
                    ]
                )
                .size()
                .unstack(fill_value=0)
            )

            # Reorder the MODIS Categories based on https://developers.google.com/earth-engine/datasets/catalog/MODIS_061_MCD12Q1#bands "LC_Type1 Class Table"
            # (No "Deciduous Needleleaf Forest" because there are no locations that have this MODIS forest type)
            desired_forest_order = [
                "Evergreen Needleleaf Forest",
                "Evergreen Broadleaf Forest",
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
                    startangle=120,
                )

                # Display a title for every single pie chart containing its MODIS forest type
                # https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.set_title.html
                axes[i].set_title(f"{forest}")

            # Set the main title for the entire figure (has to be done separately because every pie chart has its own title) as well as the file name
            # https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.suptitle.html
            fig.suptitle(
                "Breakdown of the given drought quantification for the re-analysed paper locations MODIS forest types",
                fontsize=16,
            )
            modis_drought_output_file_path = r"D:\Uni\Bachelorarbeit\Plots\Aktuell\new data\NEW DATA Breakdown pie charts for percentages of drought definitions for MODIS forest types from re-analysed shapefile.jpg"

            # Remove the last unused pie chart since we only have 7 relevant MODIS forest types but 2 rows and 4 columns = 8 pie charts
            # https://www.geeksforgeeks.org/matplotlib-figure-figure-delaxes-in-python/
            fig.delaxes(axes[-1])

            # Ensure that the tight layout is used for a better visualisation (the single pie charts are too close to another if not used)
            # https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.tight_layout.html#matplotlib.pyplot.tight_layout
            plot.tight_layout()

            # Save the pie chart(s) as one JPG file to use it in the thesis
            # https://www.geeksforgeeks.org/matplotlib-pyplot-savefig-in-python/
            plot.savefig(modis_drought_output_file_path, format="jpg")

            # Optionally display the pie chart(s) (for finetuning so adjusting is easier)
            # https://www.geeksforgeeks.org/matplotlib-pyplot-show-in-python/
            plot.show()

        # If "study type drought category" is selected, create the drought quantification breakdown pie charts for each study type from the re-analysed paper points
        if chart_type == "study type drought category":
            # Group the data by "study type" and clean the drought quantification keywords and then count its occurrences with size()
            # Remove quotes with replace() (because python gives an error for "dry" keyword if there are quotes)
            # Also create the pivot table to have "studytype" as columns and fill missing with 0
            # https://pandas.pydata.org/docs/user_guide/10min.html#grouping
            # https://pandas.pydata.org/docs/reference/api/pandas.Series.str.replace.html
            # https://pandas.pydata.org/docs/reference/api/pandas.Series.str.strip.html
            # https://www.geeksforgeeks.org/list-size-method-in-java-with-examples/
            # https://www.statology.org/pandas-unstack/
            # https://note.nkmk.me/en/python-pandas-len-shape-size/#get-the-number-of-elements-dfsize
            study_type_breakdown_data = (
                reanalysed_gdf.groupby(
                    [
                        "studytype",
                        reanalysed_gdf["drouquanti"].str.strip().str.replace('"', ""),
                    ]
                )
                .size()
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

                # Explode the "Plant water stress" segment in the "Observational" pie chart for bettere readability of the percentages
                # https://www.educative.io/answers/how-to-explode-a-pie-chart-using-matplotlib-in-python
                explode = [
                    0.1 if i == 1 and label == "Plant water stress" else 0
                    for label in row.index
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
                    explode=explode,
                    startangle=110,
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
            breakdown_output_file_path = r"D:\Uni\Bachelorarbeit\Plots\Aktuell\new data\NEW DATA Breakdown pie charts for percentages of drought definitions for study types for the re-analysed paper locations.jpg"

            # Ensure that the tight layout is used for a better visualisation (the single pie charts are too close to another if not used)
            # https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.tight_layout.html#matplotlib.pyplot.tight_layout
            plot.tight_layout()

            # Save the pie chart(s) as one JPG file to use it in the thesis
            # https://www.geeksforgeeks.org/matplotlib-pyplot-savefig-in-python/
            plot.savefig(breakdown_output_file_path, format="jpg")

            # Optionally display the pie chart(s) (for finetuning so adjusting is easier)
            # https://www.geeksforgeeks.org/matplotlib-pyplot-show-in-python/
            plot.show()

        # If "Spheres drought category" is selected, create the drought quantification breakdown pie charts for each drought sphere from the re-analysed paper points
        if chart_type == "Spheres drought category":
            # Group the data by "drought_sphere" and clean the drought quantification keywords and then count its occurrences with size()
            # Remove quotes with replace() (because python gives an error for "dry" keyword if there are quotes)
            # Also create the pivot table to have "sphere" as columns and fill missing with 0
            # https://pandas.pydata.org/docs/user_guide/10min.html#grouping
            # https://pandas.pydata.org/docs/reference/api/pandas.Series.str.replace.html
            # https://pandas.pydata.org/docs/reference/api/pandas.Series.str.strip.html
            # https://www.geeksforgeeks.org/list-size-method-in-java-with-examples/
            # https://www.statology.org/pandas-unstack/
            # https://note.nkmk.me/en/python-pandas-len-shape-size/#get-the-number-of-elements-dfsize
            spheres_breakdown_data = (
                reanalysed_gdf.groupby(
                    [
                        "sphere",
                        reanalysed_gdf["drouquanti"].str.strip().str.replace('"', ""),
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
                # No "startangle=90" because the percentages overlap if used
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

            # Set the main title for the entire figure (has to be done separately because every pie chart has its own title) as well as the file name
            # https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.suptitle.html
            fig.suptitle(
                "Breakdown of the given drought quantification of the drought spheres",
                fontsize=16,
            )
            sphere_category_output_file_path = r"D:\Uni\Bachelorarbeit\Plots\Aktuell\new data\NEW Breakdown pie charts for percentages of drought definitions for the drought spheres from the re-analysis paper points.jpg"

            # Ensure that the tight layout is used for a better visualisation (the single pie charts are too close to another if not used)
            # https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.tight_layout.html#matplotlib.pyplot.tight_layout
            plot.tight_layout()

            # Save the pie chart(s) as one JPG file to use it in the thesis
            # https://www.geeksforgeeks.org/matplotlib-pyplot-savefig-in-python/
            plot.savefig(sphere_category_output_file_path, format="jpg")

            # Optionally display the pie chart(s) (for finetuning so adjusting is easier)
            # https://www.geeksforgeeks.org/matplotlib-pyplot-show-in-python/
            plot.show()

        # If "Continent drought category" is selected, this case is used to create the drought quantification breakdown pie charts for each continent for the re-analysed locations
        if chart_type == "Continent drought category":
            # Group the data by "Continent" and clean "drouquanti" and then count its occurrences with size()
            # Remove quotes with replace() (because python gives an error for "dry" keyword if there are quotes)
            # Also create the pivot table to have "Continent" as columns and fill missing with 0
            # https://pandas.pydata.org/docs/user_guide/10min.html#grouping
            # https://pandas.pydata.org/docs/reference/api/pandas.Series.str.replace.html
            # https://pandas.pydata.org/docs/reference/api/pandas.Series.str.strip.html
            # https://www.geeksforgeeks.org/list-size-method-in-java-with-examples/
            # https://www.statology.org/pandas-unstack/
            # https://note.nkmk.me/en/python-pandas-len-shape-size/#get-the-number-of-elements-dfsize
            continent_breakdown_data = (
                reanalysed_gdf.groupby(
                    [
                        "Continent",
                        reanalysed_gdf["drouquanti"].str.strip().str.replace('"', ""),
                    ]
                )
                .size()
                .unstack(fill_value=0)
            )

            # Set the size of the figure and define the number of subplots based on the number of continents
            # https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.subplots.html
            fig, axes = plot.subplots(2, 4, figsize=(30, 10))

            # Flatten the axes for easier iteration and a faster plot creation
            # https://stackoverflow.com/questions/46862861/what-does-axes-flat-in-matplotlib-do
            axes = axes.flatten()

            # Iterate over the final dataframe that holds the wanted information to filter out zero values and assign the wanted colors
            # https://www.w3schools.com/python/pandas/ref_df_iterrows.asp
            for i, (continent, row) in enumerate(continent_breakdown_data.iterrows()):
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
                    startangle=90,
                )

                # Display a title for every single pie chart containing the continents
                # https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.set_title.html
                axes[i].set_title(f"{continent}")

            # Set the main title for the entire figure (has to be done separately because every pie chart has its own title) as well as the file name
            # https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.suptitle.html
            fig.suptitle(
                "Breakdown of the given drought quantification for the re-analysed paper locations continents",
                fontsize=16,
            )
            continent_drought_output_file_path = r"D:\Uni\Bachelorarbeit\Plots\Aktuell\new data\NEW Breakdown pie charts for percentages of drought definitions for all continents from re-analysed location shapefile.jpg"

            # Remove the last unused pie chart since we only have 7 continents but 2 rows and 4 columns = 8 pie charts
            # https://www.geeksforgeeks.org/matplotlib-figure-figure-delaxes-in-python/
            fig.delaxes(axes[-1])

            # Ensure that the tight layout is used for a better visualisation (the single pie charts are too close to another if not used)
            # https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.tight_layout.html#matplotlib.pyplot.tight_layout
            plot.tight_layout()

            # Save the pie chart(s) as one JPG file to use it in the thesis
            # https://www.geeksforgeeks.org/matplotlib-pyplot-savefig-in-python/
            plot.savefig(continent_drought_output_file_path, format="jpg")

            # Optionally display the pie chart(s) (for finetuning so adjusting is easier)
            # https://www.geeksforgeeks.org/matplotlib-pyplot-show-in-python/
            plot.show()

        # If "Continent percentage" is selected, this case is used to create the general continent percentage pie chart
        if chart_type == "Continent percentage":
            # Count the occurrences of each continent to create the percentages
            # https://pandas.pydata.org/docs/reference/api/pandas.Series.value_counts.html
            continent_counts = reanalysed_gdf["Continent"].value_counts()

            # Map the study types to their corresponding colors from https://developers.google.com/earth-engine/datasets/catalog/MODIS_061_MCD12Q1#bands "LC_Type1 Class Table"
            # https://stackoverflow.com/questions/26139423/plot-different-color-for-different-categorical-levels
            continent_color_mapping = {
                "Europe": "#0000FF",  # blue
                "Africa": "#808080",  # grey
                "Asia": "#FFFF00",  # yellow
                "Oceania": "#008000",  # green
                "US": "#ADD8E6",  # light blue
                "North America": "#FF0000",  # red
                "Latin and South America": "#FFA500",  # orange
            }

            # Create a list of colors in the same order as the labels in modis_category_counts
            continent_colors = [
                continent_color_mapping[label] for label in continent_counts.index
            ]

            # Adjust the size of the plot so the picture is better usable later on
            # https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.figure.html
            plot.figure(figsize=(8, 7))

            # Create the pie chart with percentages and black lines between the pieces
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
            continent_output_path = r"D:\Uni\Bachelorarbeit\Plots\Pie chart with continent percentages from the re-analysed paper locations shapefile.jpg"

            # Save the pie chart as a JPG file to use it in the thesis
            # https://www.geeksforgeeks.org/matplotlib-pyplot-savefig-in-python/
            # plot.savefig(continent_output_path, format="jpg")

            # Optionally display the plot (for finetuning so adjusting is easier)
            # https://www.geeksforgeeks.org/matplotlib-pyplot-show-in-python/
            plot.show()

        # If "MODIS percentage" is selected, this case is used to create the general MODIS forest type percentage pie chart for the re-analyzed locations
        if chart_type == "MODIS percentage":

            # Count the occurrences of each MODIS forest type to create the percentages
            # https://pandas.pydata.org/docs/reference/api/pandas.Series.value_counts.html
            modis_category_counts = reanalysed_gdf["forest"].value_counts()

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
            explode = [0, 0, 0, 0, 0, 0, 0.2]

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
                # Adjusting the position of "Closed Shrubland" by using specific coordinates
                if label == "Closed Shrubland":
                    texts[i].set_position((-0.1, 1.258))
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
            plot.title(
                "Distribution of the MODIS forest types in percentages for re-analysed paper locations"
            )
            study_type_output_path = r"D:\Uni\Bachelorarbeit\Plots\Pie chart with MODIS forest category percentages from the re-analysis locations shapefile.jpg"

            # Save the pie chart as a JPG file to use it in the thesis
            # https://www.geeksforgeeks.org/matplotlib-pyplot-savefig-in-python/
            # plot.savefig(study_type_output_path, format="jpg")

            # Optionally display the plot (for finetuning so adjusting is easier)
            # https://www.geeksforgeeks.org/matplotlib-pyplot-show-in-python/
            plot.show()

        # If "drought keywords percentage" is selected, create the general drought keywords pie chart
        if chart_type == "drought keywords percentage":

            # Count the occurrences of each drought keyword to create the percentages and clean "drouquanti", then count its occurrences with size()
            # Remove quotes with replace() (because python gives an error for "dry" keyword if there are quotes)
            # https://pandas.pydata.org/docs/reference/api/pandas.Series.str.replace.html
            # https://pandas.pydata.org/docs/reference/api/pandas.Series.str.strip.html
            # https://pandas.pydata.org/docs/reference/api/pandas.Series.value_counts.html
            drought_keywords_counts = (
                reanalysed_gdf["drouquanti"]
                .str.strip()
                .str.replace('"', "")
                .value_counts()
            )

            # Create a list of colors in the same order as the labels in spei_category_counts to use it for the pie chart
            drought_keywords_colors = [
                drought_keywords_color_mapping[label]
                for label in drought_keywords_counts.index
            ]

            # Adjust the size of the plot so the picture is better usable later and nothing gets cut off
            # https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.figure.html
            plot.figure(figsize=(10, 7))

            # Create the pie chart with black lines between pieces and percentages as texts
            # https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.pie.html
            wedges, category_texts, autotexts = plot.pie(
                drought_keywords_counts,
                autopct="%1.1f%%",
                colors=drought_keywords_colors,
                wedgeprops={"edgecolor": "black", "linewidth": 0.4},
            )

            # Change the color of the percentages to white for clearer visibility
            # https://stackoverflow.com/a/27899541 (set_color())
            for autotext in autotexts:
                autotext.set_color("white")

            # Manage the labels for the segments by iterating over the dataframe "drought_keywords_counts"
            # https://www.w3schools.com/python/pandas/ref_df_index.asp
            # https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.title.html
            for i, keyword_label in enumerate(drought_keywords_counts.index):

                # Add back the "" for the "Dry" drought keyword since it had to be removed earlier for python rules
                if keyword_label == "Dry":
                    keyword_label = '"Dry"'

                # Add the drought keyword label texts automatically from the drought_keywords_counts dataframe
                # https://www.tutorialspoint.com/how-to-add-title-to-subplots-in-matplotlib#:~:text=The%20Matplotlib%20set_text()%20function,in%20a%20subplot%20or%20plot.
                category_texts[i].set_text(keyword_label)

            # Set the main title as well as the file name
            # https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.title.html#matplotlib-pyplot-title
            plot.title(
                "Distribution of the drought keywords out of all re-analysed studies in percentage"
            )
            drought_keywords_output_file_path = r"D:\Uni\Bachelorarbeit\Plots\Aktuell\new data\Re-worked data\NEW Pie chart with drought keywords percentages and legend for total numbers from re-analysed paper location.jpg"

            # Create and add a legend for the total numbers of drought keywords for a better overview of the data
            # Create the labels out of the SPEI categories for the legend with counts so the total numbers are displayed
            # Also add back the "" for the "Dry" drought keyword since it had to be removed earlier for python rules
            # https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.items.html#pandas-dataframe-items
            # https://docs.python.org/3/library/stdtypes.html#str.replace
            keywords_legend_labels = [
                f'"{label}": {count}' if label == "Dry" else f"{label}: {count}"
                for label, count in drought_keywords_counts.items()
            ]

            # Now add the legend to the pie chart with the drought keyword labels and place it in the upper right outside the pie chart (with bbox_to_anchor)
            # https://matplotlib.org/stable/api/legend_api.html#module-matplotlib.legend
            plot.legend(
                wedges,
                keywords_legend_labels,
                title="Drought keywords (Count)",
                loc="upper right",
                bbox_to_anchor=(0.9, 0, 0.4, 1),
                frameon=False,
            )

            # Ensure that the tight layout is used for a better visualisation and readability
            # https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.tight_layout.html#matplotlib.pyplot.tight_layout
            plot.tight_layout()

            # Save the pie chart as a JPG file to use it in the thesis
            # https://www.geeksforgeeks.org/matplotlib-pyplot-savefig-in-python/
            # plot.savefig(drought_keywords_output_file_path, format="jpg")

            # Optionally display the plot (for finetuning so adjusting is easier)
            # https://www.geeksforgeeks.org/matplotlib-pyplot-show-in-python/
            plot.show()

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
                frameon=False,
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
            # Also create the pivot table to have "sphere" as columns and fill missing with 0
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
            sphere_reanalysis_output_file_path = r"D:\Uni\Bachelorarbeit\Plots\Aktuell\Re-worked data\NEW Breakdown pie charts for percentages of SPEI categories for the drought spheres from the re-analysed shapefile locations.jpg"

            # Ensure that the tight layout is used for a better visualisation (the single pie charts are too close to another if not used)
            # https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.tight_layout.html#matplotlib.pyplot.tight_layout
            plot.tight_layout()

            # Save the pie chart(s) as one JPG file to use it in the thesis
            # https://www.geeksforgeeks.org/matplotlib-pyplot-savefig-in-python/
            # plot.savefig(sphere_reanalysis_output_file_path, format="jpg")

            # Optionally display the pie chart(s) (for finetuning so adjusting is easier)
            # https://www.geeksforgeeks.org/matplotlib-pyplot-show-in-python/
            plot.show()

        elif chart_type == "study type SPEI":
            # Group the data by "studytype" and "Category" then count its occurrences with size()
            # Also create the pivot table to have "studytype" as columns and fill missing with 0
            # https://pandas.pydata.org/docs/user_guide/10min.html#grouping
            # https://pandas.pydata.org/docs/reference/api/pandas.Series.str.strip.html
            # https://www.geeksforgeeks.org/list-size-method-in-java-with-examples/
            # https://www.statology.org/pandas-unstack/
            # https://note.nkmk.me/en/python-pandas-len-shape-size/#get-the-number-of-elements-dfsize
            study_type_spei_data = (
                reanalysed_gdf.groupby(["studytype", reanalysed_gdf["Category"]])
                .size()
                .unstack(fill_value=0)
            )

            # Display only the study types "experimental", "observational", and "modeling" in the given order as pie charts
            desired_study_type_order = ["Experimental", "Observational", "Modeling"]

            # Filter and reorder the study types using .isin() to keep only the relevant types and .reindex() to match the desired order
            # https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.loc.html#pandas-dataframe-loc
            # https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.isin.html
            # https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.reindex.html
            final_breakdown_data = study_type_spei_data.loc[
                study_type_spei_data.index.isin(desired_study_type_order)
            ].reindex(desired_study_type_order)

            # Define the number of subplots based on the number of study types because we need one pie chart for each relevant, named study type
            # https://www.programiz.com/python-programming/methods/built-in/len
            # https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.subplots.html
            number_of_study_types = len(final_breakdown_data)
            fig, axes = plot.subplots(1, 3, figsize=(27, 8))

            # Iterate over the final dataframe that holds the wanted information and the given order to filter out zero values and assign the wanted colors
            # https://www.w3schools.com/python/pandas/ref_df_iterrows.asp
            for i, (studytype, row) in enumerate(final_breakdown_data.iterrows()):
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

                # Display percentages inside the pieces and assign the labels and colors to the pie chart pieces
                # Also replace "<=" with "≤" in the pie chart labels
                # https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.pie.html
                # https://docs.python.org/3/library/stdtypes.html#str.replace
                wedges, texts, autotexts = axes[i].pie(
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

                # Display a title for every single pie chart containing its study type as title
                # https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.set_title.html
                axes[i].set_title(f"{studytype.title()}")

            # Set the main title for the entire figure (has to be done separately because every pie chart has its own title) as well as the file name
            # https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.suptitle.html
            fig.suptitle(
                "Breakdown of the given SPEI categories from the study types",
                fontsize=16,
            )
            sphere_reanalysis_output_file_path = r"D:\Uni\Bachelorarbeit\Plots\Aktuell\re-analysis\BIGGER NEW Breakdown pie charts for percentages of SPEI categories for the study types of the papers from the re-analysed shapefile locations.jpg"

            # Ensure that the tight layout is used for a better visualisation (the single pie charts are too close to another if not used)
            # https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.tight_layout.html#matplotlib.pyplot.tight_layout
            plot.tight_layout()

            # Save the pie chart(s) as one JPG file to use it in the thesis
            # https://www.geeksforgeeks.org/matplotlib-pyplot-savefig-in-python/
            plot.savefig(sphere_reanalysis_output_file_path, format="jpg")

            # Optionally display the pie chart(s) (for finetuning so adjusting is easier)
            # https://www.geeksforgeeks.org/matplotlib-pyplot-show-in-python/
            plot.show()

    # Cases for all pie charts that need data from the shapefile with all paper points
    elif chart_type in [
        "MODIS percentage all",
        "MODIS drought sphere",
        "MODIS drought category all",
        "Continent percentage all",
        "Continent drought category all",
    ]:

        # Read the given shapefile for all pie chart cases using geopandas read_file() method and storing it as geodataframe
        # https://geopandas.org/en/stable/docs/user_guide/data_structures.html#geodataframe
        # https://geopandas.org/en/stable/docs/user_guide/io.html#reading-and-writing-files
        complete_gdf = geopd.read_file(shape_or_excel_file_path)

        # Define consistent colors for each drought quantification keyword across all plots, globally defined because of multiple use cases
        # https://stackoverflow.com/questions/26139423/plot-different-color-for-different-categorical-levels
        drought_keywords_color_mapping = {
            "Dry": "#ff7f0e",  # Dark Orange
            "Differs from normal": "#ff4500",  # Orange-Red
            "Dry season": "#adff2f",  # Green Yellow
            "Low soil moisture": "#b47d49",  # Brown
            "Low water flow/depth": "#4682b4",  # Steel Blue
            "Plant water stress": "#32cd32",  # Lime Green
            "Reduced rainfall": "#87CEEB",  # Sky Blue
            "Standardized Index": "#a245a8",  # Purple
        }

        # If "MODIS drought category all" is selected, create the drought quantification breakdown pie charts for each MODIS forest type
        if chart_type == "MODIS drought category all":

            # Group the data by "forest" and clean "drouquanti" and then count its occurrences with size()
            # Remove quotes with replace() (because python gives an error for "dry" keyword if there are quotes)
            # Also create the pivot table to have "forest" as columns and fill missing with 0
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
                # No "startangle=90" because the percentages overlap if used
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

            # Set the main title for the entire figure (has to be done separately because every pie chart has its own title) as well as the file name
            # https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.suptitle.html
            fig.suptitle(
                "Breakdown of the given drought quantification for all paper locations MODIS forest types",
                fontsize=16,
            )
            modis_drought_output_file_path = r"D:\Uni\Bachelorarbeit\Plots\Aktuell\new data\NEW Breakdown pie charts for percentages of drought definitions for MODIS forest types from complete location shapefile.jpg"

            # Ensure that the tight layout is used for a better visualisation (the single pie charts are too close to another if not used)
            # https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.tight_layout.html#matplotlib.pyplot.tight_layout
            plot.tight_layout()

            # Save the pie chart(s) as one JPG file to use it in the thesis
            # https://www.geeksforgeeks.org/matplotlib-pyplot-savefig-in-python/
            plot.savefig(modis_drought_output_file_path, format="jpg")

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

            # Define consistent colors for each drought quantification keyword across all plots, globally defined because of multiple use cases
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

            # Set the main title for the entire figure (has to be done separately because every pie chart has its own title) as well as the file name
            # https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.suptitle.html
            fig.suptitle(
                "Breakdown of the given drought spheres for all MODIS forest types from all paper locations",
                fontsize=16,
            )
            modis_sphere_output_file_path = r"D:\Uni\Bachelorarbeit\Plots\Aktuell\Re-worked data\Breakdown pie charts for percentages of drought spheres for MODIS forest types from all paper location.jpg"

            # Ensure that the tight layout is used for a better visualisation (the single pie charts are too close to another if not used)
            # https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.tight_layout.html#matplotlib.pyplot.tight_layout
            plot.tight_layout()

            # Save the pie chart(s) as one JPG file to use it in the thesis
            # https://www.geeksforgeeks.org/matplotlib-pyplot-savefig-in-python/
            # plot.savefig(modis_sphere_output_file_path, format="jpg")

            # Optionally display the pie chart(s) (for finetuning so adjusting is easier)
            # https://www.geeksforgeeks.org/matplotlib-pyplot-show-in-python/
            plot.show()

        # If "MODIS percentage all" is selected, this case is used to create the general MODIS forest type percentage pie chart
        if chart_type == "MODIS percentage all":

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

        # If "Continent percentage all" is selected, this case is used to create the general continent percentage pie chart
        if chart_type == "Continent percentage all":
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
                "US": "#ADD8E6",  # light blue
                "North America": "#FF0000",  # red
                "Latin and South America": "#FFA500",  # orange
            }

            # Create a list of colors in the same order as the labels in modis_category_counts
            continent_colors = [
                continent_color_mapping[label] for label in continent_counts.index
            ]

            # Exploding the "Africa" slice so the difference and the percentages are clearer
            # https://www.educative.io/answers/how-to-explode-a-pie-chart-using-matplotlib-in-python
            explode = [0, 0, 0, 0, 0, 0, 0.2]

            # Adjust the size of the plot so the picture is better usable later on
            # https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.figure.html
            plot.figure(figsize=(9, 7))

            # Create the pie chart with percentages and black lines between the pieces
            # https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.pie.html
            wedges, texts, autotexts = plot.pie(
                continent_counts,
                autopct="%1.1f%%",
                colors=continent_colors,
                startangle=90,
                explode=explode,
                wedgeprops={"edgecolor": "black", "linewidth": 0.5},
            )

            # Set label positions manually for the  continents "Africa" and "North America" so they are right next to its segment in the pie chart
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
                    texts[i].set_position((-0.635, -0.944))
                # Adjusting the position of "Africa" by using specific coordinates
                if label == "Africa":
                    texts[i].set_position((0, 1.245))
                else:
                    # Keep default position for other labels since they are fine on default
                    texts[i].set_position(texts[i].get_position())

                # Adding back the study type label text (since set_position overrides them)
                # https://www.tutorialspoint.com/how-to-add-title-to-subplots-in-matplotlib#:~:text=The%20Matplotlib%20set_text()%20function,in%20a%20subplot%20or%20plot.
                texts[i].set_text(label)

            # Set the title and filename for this pie chart
            # https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.title.html#matplotlib-pyplot-title
            # plot.title("Distribution of the continents in percentages")
            continent_output_path = r"D:\Uni\Bachelorarbeit\Plots\Pie chart with continent percentages from the complete locations shapefile from all paper location.jpg"

            # Save the pie chart as a JPG file to use it in the thesis
            # https://www.geeksforgeeks.org/matplotlib-pyplot-savefig-in-python/
            # plot.savefig(continent_output_path, format="jpg")

            # Optionally display the plot (for finetuning so adjusting is easier)
            # https://www.geeksforgeeks.org/matplotlib-pyplot-show-in-python/
            plot.show()

        # If "Continent drought category all" is selected, create the drought quantification breakdown pie charts for each continent
        if chart_type == "Continent drought category all":

            # Group the data by "Continent" and clean "drouquanti" and then count its occurrences with size()
            # Remove quotes with replace() (because python gives an error for "dry" keyword if there are quotes)
            # Also create the pivot table to have drought_sphere as columns and fill missing with 0
            # https://pandas.pydata.org/docs/user_guide/10min.html#grouping
            # https://pandas.pydata.org/docs/reference/api/pandas.Series.str.replace.html
            # https://pandas.pydata.org/docs/reference/api/pandas.Series.str.strip.html
            # https://www.geeksforgeeks.org/list-size-method-in-java-with-examples/
            # https://www.statology.org/pandas-unstack/
            # https://note.nkmk.me/en/python-pandas-len-shape-size/#get-the-number-of-elements-dfsize
            continent_breakdown_data = (
                complete_gdf.groupby(
                    [
                        "Continent",
                        complete_gdf["drouquanti"].str.strip().str.replace('"', ""),
                    ]
                )
                .size()
                .unstack(fill_value=0)
            )

            # Set the size of the figure and define the number of subplots based on the number of continents
            # https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.subplots.html
            fig, axes = plot.subplots(2, 4, figsize=(30, 10))

            # Flatten the axes for easier iteration and a faster plot creation
            # https://stackoverflow.com/questions/46862861/what-does-axes-flat-in-matplotlib-do
            axes = axes.flatten()

            # Iterate over the final dataframe that holds the wanted information to filter out zero values and assign the wanted colors
            # https://www.w3schools.com/python/pandas/ref_df_iterrows.asp
            for i, (continent, row) in enumerate(continent_breakdown_data.iterrows()):
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
                    startangle=90,
                )

                # Display a title for every single pie chart containing the continents
                # https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.set_title.html
                axes[i].set_title(f"{continent}")

            # Set the main title for the entire figure (has to be done separately because every pie chart has its own title) as well as the file name
            # https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.suptitle.html
            fig.suptitle(
                "Breakdown of the given drought quantification for all paper locations continents",
                fontsize=16,
            )
            continent_drought_output_file_path = r"D:\Uni\Bachelorarbeit\Plots\Aktuell\new data\NEW Breakdown pie charts for percentages of drought definitions for all continents from complete location shapefile.jpg"

            # Remove the last unused pie chart since we only have 7 continents but 2 rows and 4 columns = 8 pie charts
            # https://www.geeksforgeeks.org/matplotlib-figure-figure-delaxes-in-python/
            fig.delaxes(axes[-1])

            # Ensure that the tight layout is used for a better visualisation (the single pie charts are too close to another if not used)
            # https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.tight_layout.html#matplotlib.pyplot.tight_layout
            plot.tight_layout()

            # Save the pie chart(s) as one JPG file to use it in the thesis
            # https://www.geeksforgeeks.org/matplotlib-pyplot-savefig-in-python/
            plot.savefig(continent_drought_output_file_path, format="jpg")

            # Optionally display the pie chart(s) (for finetuning so adjusting is easier)
            # https://www.geeksforgeeks.org/matplotlib-pyplot-show-in-python/
            plot.show()


# CONTINENT:
# DONE
# Generate the general continent percentages pie chart from all studies
create_pie_chart(all_studies_shapefile_path, "Continent percentage all")

# DONE
# Generate the general continent percentages pie chart from re-analysis locations
# create_pie_chart(reanalysis_shapefile_path, "Continent percentage")

# DONE
# Generate the continent drought category keywords percentage pie chart from all paper locations since one paper can have multiple continents
# create_pie_chart(all_studies_shapefile_path, "Continent drought category all")

# DONE
# Generate the continent drought category keywords percentage pie chart from the re-analysed paper locations
# create_pie_chart(reanalysis_shapefile_path, "Continent drought category")

# DONE
# Generate the Continent SPEI bar chart
# create_reanalysis_based_bar_chart(reanalysis_shapefile_path, "Continent SPEI")

# -------------------------------------------------------------------------------------
# SPHERES:

# Generate overview pie chart of drought spheres
# create_pie_chart(excel_file_path, "spheres")

# DONE
# Generate the Spheres drought category keywords percentage pie chart from the Excel file since every paper can have only one sphere
# create_pie_chart(excel_file_path, "Spheres drought category excel")

# DONE
# Generate the Spheres drought category keywords percentage pie chart from re-analysed paper locations
# create_pie_chart(reanalysis_shapefile_path, "Spheres drought category")

# DONE
# Generate the sphere SPEI category percentage pie chart
# create_pie_chart(reanalysis_shapefile_path, "Spheres SPEI")

# -------------------------------------------------------------------------------------
# MODIS:

# DONE
# Generate the MODIS forest type percentage pie chart for all study locations
# create_pie_chart(all_studies_shapefile_path, "MODIS percentage all")

# DONE
# Generate the MODIS forest type percentage pie chart for re-analysis location
# create_pie_chart(reanalysis_shapefile_path, "MODIS percentage")

# DONE
# Generate the MODIS breakdown of given drought quantification keyword pie chart from all paper locations since one paper can have multiple MODIS forest types
# create_pie_chart(all_studies_shapefile_path, "MODIS drought category all")

# DONE
# Generate the MODIS breakdown of given drought quantification keyword pie chart for the re-analysed paper locations
# create_pie_chart(reanalysis_shapefile_path, "MODIS drought category")

# DONE
# Generate the MODIS SPEI category bar chart
# create_reanalysis_based_bar_chart(reanalysis_shapefile_path, "MODIS SPEI")

# DONE
# Generate the MODIS breakdown of drought spheres pie chart
# create_pie_chart(all_studies_shapefile_path, "MODIS drought sphere")

# -------------------------------------------------------------------------------------
# STUDY TYPE:

# DONE
# Generate the general study type percentages pie chart
# create_pie_chart(excel_file_path, "study type")

# DONE
# Generate the study type breakdown of given drought quantification keyword pie chart from Excel since every paper only has one study type
# create_pie_chart(excel_file_path, "study type drought category excel")

# DONE
# Generate the study type breakdown of given drought quantification keyword pie chart from the re-analysed paper locations
# create_pie_chart(reanalysis_shapefile_path, "study type drought category")

# DONE
# Generate the study type SPEI breakdown pie chart
# create_pie_chart(reanalysis_shapefile_path, "study type SPEI")

# -------------------------------------------------------------------------------------
# SPEI:

# DONE
# Generate the SPEI category percentage pie chart
# create_pie_chart(reanalysis_shapefile_path, "SPEI category percentage")

# DONE
# Generate the study type SPEI category bar chart
# create_reanalysis_based_bar_chart(reanalysis_shapefile_path, "Study type SPEI Bar")

# DONE
# Generate the drought quantification keyword SPEI bar chart
# create_reanalysis_based_bar_chart(reanalysis_shapefile_path, "Drought keyword SPEI")

# DONE
# Generate the drought keywords percentage pie chart from the re-analysed paper locations
# create_pie_chart(reanalysis_shapefile_path, "drought keywords percentage")

# DONE
# Plot that shows the contribution of drought keywords for quantified or not.
# create_pie_chart(reanalysis_shapefile_path, "Quantification drought keywords")

# -------------------------------------------------------------------------------------
# General:

# DONE
# Generate the drought keywords percentage pie chart from the Excel file to show the general paper contribution
# create_pie_chart(excel_file_path, "drought keywords percentage excel")


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
    # For the case that shows the correlation between all given drought keywords and if drought was quantified in percent
    if chart_type == "Drought quantified":
        # Load the Excel file and "relevantInfo" sheet where the data for the pie charts is stored
        # https://pandas.pydata.org/docs/reference/api/pandas.read_excel.html
        reanalysed_gdf = geopd.read_file(shape_or_excel_file_path)

        # Set the output path for this bar plot
        output_file_path = r"D:\Uni\Bachelorarbeit\Plots\Aktuell\new data\Bar plot that shows the correlation between all given drought keywords and if drought was quantified in percent.jpg"

        # Grouping the data by "drought quantification keyword for plots" and "was drought quantified**"
        # to count their occurrences and the percentages later
        # https://pandas.pydata.org/docs/user_guide/10min.html#grouping
        # https://www.geeksforgeeks.org/list-size-method-in-java-with-examples/
        # https://www.statology.org/pandas-unstack/
        drought_quantification_counts = (
            reanalysed_gdf.groupby(["drouquanti", "wasdrquant"])
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
            "Plant water stress",
            "Standardized Index",
        ]

        # Calculate the percentage for each drought quantification keyword by dividing each value by the global total (sum of all counts)
        # https://www.w3schools.com/python/pandas/ref_df_sum.asp
        # https://www.w3schools.com/python/pandas/ref_df_div.asp
        global_total = drought_quantification_counts.values.sum()
        drought_quantification_counts_percentage = (
            drought_quantification_counts.div(global_total) * 100
        )

        # Calculate the sum of all rows (True & False for each drought quantification keyword) and store it in a "Total" column
        # This new "Total" column is then used for sorting the categories in descending order based on the total occurrences.
        # https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.sort_values.html
        drought_quantification_counts_percentage["Total"] = (
            drought_quantification_counts_percentage.sum(axis=1)
        )

        # Applying the desired order to the data. so the X-Axis is ordered from "worst" to "best" keyword from left to right
        # https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.reindex.html
        sorted_category_counts_percentage = (
            drought_quantification_counts_percentage.reindex(
                desired_drought_keyword_order
            )
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

        # Calculate the total number of occurrences where "wasdrquant" is "True" and "False"
        # https://www.w3schools.com/python/pandas/ref_df_sum.asp
        true_count = (
            drought_quantification_counts["True"].sum()
            if "True" in drought_quantification_counts.columns
            else 0
        )
        false_count = (
            drought_quantification_counts["False"].sum()
            if "False" in drought_quantification_counts.columns
            else 0
        )

        # Set the legend entries manually with all its attributes colors and hatches (using mpatches.Patch()), so they match the bars
        # https://matplotlib.org/stable/api/_as_gen/matplotlib.patches.Patch.html#matplotlib-patches-patch
        # https://stackoverflow.com/a/37296137
        true_patch = mpatches.Patch(color="darkblue", label=f"Yes: {true_count}")
        false_patch = mpatches.Patch(
            facecolor="red", edgecolor="black", label=f"No: {false_count}", hatch="////"
        )

        # Add the legend, so it gets clear what part of the bars is "True" and "False"
        # https://matplotlib.org/stable/api/legend_api.html#module-matplotlib.legend
        plot.legend(
            handles=[true_patch, false_patch],
            title="Was drought quantified?",
            loc="upper right",
            alignment="left",
            frameon=False,
        )

        # Optionally set a title for this case for a better overview (not needed later in the thesis)
        title = (
            "Correlation between given drought keywords and if drought was quantified"
        )

        # Set the y-axis limit to 30% for a better overview
        # https://www.geeksforgeeks.org/matplotlib-pyplot-ylim-in-python/
        plot.ylim(0, 40)

    # For the case with correctness of the given drought quantification keywords for all re-analyzed paper locations
    if chart_type == "Drought correctness":
        # Read the given shapefile geopandas read_file() method and storing it as geodataframe
        # https://geopandas.org/en/stable/docs/user_guide/data_structures.html#geodataframe
        # https://geopandas.org/en/stable/docs/user_guide/io.html#reading-and-writing-files
        reanalysed_gdf = geopd.read_file(shape_or_excel_file_path)

        # Set the output path for this bar plot
        output_file_path = r"D:\Uni\Bachelorarbeit\Plots\Aktuell\new data\Bar plot that shows the correctness of the given drought quantification keywords for all re-analyzed paper locations.jpg"

        # Set the title for this case
        title = "Bar plot to show the correctness of the given drought keywords"

        # Grouping the data by "drouquanti" and "drouright" to count their occurrences and the percentages later
        # https://pandas.pydata.org/docs/user_guide/10min.html#grouping
        # https://www.geeksforgeeks.org/list-size-method-in-java-with-examples/
        # https://www.statology.org/pandas-unstack/
        drought_correctness_counts = (
            reanalysed_gdf.groupby(["drouquanti", "drouright"])
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

        # Calculate the total number of occurrences where "wasdrquant" is "True" and "False"
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

        # Set the legend entries manually with all its attributes colors and hatches (using mpatches.Patch()), so they match the bars
        # https://matplotlib.org/stable/api/_as_gen/matplotlib.patches.Patch.html#matplotlib-patches-patch
        # https://stackoverflow.com/a/37296137
        true_patch = mpatches.Patch(color="darkblue", label=f"Yes: {true_count}")
        false_patch = mpatches.Patch(
            facecolor="red", edgecolor="black", label=f"No: {false_count}", hatch="////"
        )

        # Add the legend, so it gets clear what part of the bars is "True" and "False"
        # https://matplotlib.org/stable/api/legend_api.html#module-matplotlib.legend
        plot.legend(
            handles=[true_patch, false_patch],
            title="Was there a drought according to SPEI?",
            loc="upper right",
            alignment="left",
            frameon=False,
        )

    # Bringing the two cases back here together, so everything below does not have to be hard-coded for each case separately
    if chart_type in ["Drought quantified", "Drought correctness"]:

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
        plot.savefig(output_file_path, format="jpg")

        # Optionally display the plot (for finetuning so adjusting is easier)
        # https://www.geeksforgeeks.org/matplotlib-pyplot-show-in-python/
        plot.show()


# -------------------------------------------------------------------------------------
# TRUE OR FALSE:

# DONE
# Plot that shows drought correctness for quantified or not, no matter the category.
# create_pie_chart(reanalysis_shapefile_path, "Quantified correctness")

# DONE
# Generate the bar plot with correctness of the given drought quantification keywords for all re-analyzed paper locations
# create_true_false_bar_chart(reanalysis_shapefile_path, "Drought correctness")

# DONE
# Generate the bar plot that shows the correlation between all given drought keywords and if drought was quantified in percent
# create_true_false_bar_chart(reanalysis_shapefile_path, "Drought quantified")
