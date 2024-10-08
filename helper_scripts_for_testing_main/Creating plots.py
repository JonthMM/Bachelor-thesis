# Importing pandas for data manipulation and analysis and name it pd for simpler use
import pandas as pd

# Importing geopandas for working with geospatial data, including shapefiles
import geopandas as geopd

# Creates the plots from the data handled by (geo)pandas

import matplotlib.pyplot as plot

# Path to the shapefile containing the information needed for all plots depending on the re-analysis data
reanalysis_shapefile_path = r'D:\Uni\Bachelorarbeit\complete_paper_points\re-analysed paper points with forest\re-analysed_paper_points_with_forest.shp'

all_studies_shapefile_path = r'D:\Uni\Bachelorarbeit\complete_paper_points\complete_paper_points_with_forest.shp'

# Path to the Excel file containing all data
excel_file_path = r'D:\Uni\Bachelorarbeit\2024Apr_Mana_Review_v2i - paper_coords_area_years_plotkeywords_speireanalysis_month_finished.xlsx'

# Probably not needed since a pie chart looks way better and has a better overview for this type of analysis
def create_drought_keywords_bar_chart(excel_file_path, chart_type):
    """
        Creates a bar chart based on the specified chart type, currently only 'MODIS drought keyword'.
        This function is used for bar charts with the given drought quantification keywords from the papers
        The function is designed to combine bar chart creation logic for different cases which all have
        "drought quantification keyword for plots" as stacked bars into a single method.
        This allows for easy extension if more bar charts are needed in the future from the same shapefile data,
        without requiring the creation of additional methods.

        Args:
            excel_file_path (str): The path to the shapefile containing the data.
            chart_type (str): The type of bar chart to generate.

        Returns:
            None: The function generates and displays the requested bar chart.
        """

    # Reading the given shapefile using geopandas read_file() method and storing it as geodataframe
    # https://geopandas.org/en/stable/docs/user_guide/data_structures.html#geodataframe
    # https://geopandas.org/en/stable/docs/user_guide/io.html#reading-and-writing-files
    excel_df = pd.read_excel(excel_file_path, sheet_name='relevantInfo')

    # Clean up the 'drought quantification keyword for plots' to remove quotes (because python gives an error for "dry" if there are quotes) and extra spaces
    # https://pandas.pydata.org/docs/reference/api/pandas.Series.str.replace.html
    excel_df['drought quantification keyword for plots'] = excel_df[
        'drought quantification keyword for plots'].str.strip().str.lower().str.replace('"', '')

    # For MODIS categories and SPEI drought categories
    if chart_type == 'MODIS drought keyword':
            # Grouping the data by 'MODIS' and 'dr_quanti' to count occurrences of the drought quantifications
            # https://pandas.pydata.org/docs/user_guide/10min.html#grouping
            drought_keywords_counts = excel_df.groupby(['MODIS_forest_type', 'drought quantification keyword for plots']).size().unstack(fill_value=0)
            # X-axis text
            xaxisdescription = 'Forest type'
            # Title of the plot
            title = 'Distribution of given drought quantification keywords within each MODIS category'
            # Path where the plot is going to be saved
            output_file_path = r'D:\Uni\Bachelorarbeit\Plots\Bar chart for correlation between MODIS classes and given drought quantification keywords from excel.jpg'

    if chart_type in ['MODIS drought keyword']:
            # Change the label for 'Other' category, so it is not too long (only for bar plots with MODIS involved)
            # https://pandas.pydata.org/docs/user_guide/basics.html#renaming-mapping-labels
            drought_keywords_counts.rename(
                index={"Other (Mangrove Forest, Open Shrubland, Savannas, Permanent Wetlands, ...)": "Other"},
                inplace=True)

            # Sorting the created pivot table by total occurrences (sum of rows), from most to least in descending order for all stacked bar plots for the custom legend
            # https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.loc.html#pandas-dataframe-loc
            # https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.sort_values.html
            drought_keywords_counts_sorted = drought_keywords_counts.loc[
            drought_keywords_counts.sum(axis=1).sort_values(ascending=False).index]

            # Sorting the columns by total occurrences (sum of columns) for legend and data
            # https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.sort_values.html
            drought_keywords_sums = drought_keywords_counts_sorted.sum(axis=0)
            drought_keywords_counts_sorted = drought_keywords_counts_sorted[drought_keywords_sums.sort_values(ascending=False).index]

            # Custom legend labels with counts included for clearer overview
            # https://www.geeksforgeeks.org/matplotlib-pyplot-legend-in-python/
            legend_labels_with_counts = [f"{category} [{count}]" for category, count in
                                             zip(drought_keywords_sums.index, drought_keywords_sums.values)]

            # Sorting legend labels based on the counts numeric in descending order
            # https://docs.python.org/3/howto/sorting.html
            sorted_legend_labels_with_counts = sorted(legend_labels_with_counts,
                                                      key=lambda x: int(x.split('[')[1][:-1]),
                                                      reverse=True)

            # Define consistent colors for each drought quantification keyword across all charts
            # https://stackoverflow.com/questions/26139423/plot-different-color-for-different-categorical-levels
            drought_keywords_color_mapping = {
                'dry': '#ff7f0e',                   # Dark Orange
                'differs from normal': '#ff4500',   # Orange-Red
                'dry season': '#87CEEB',            # Sky Blue
                'low soil moisture': '#00ced1',     # Dark Turquoise
                'low water flow/depth': '#4682b4',  # Steel Blue
                'plant water stress': '#32cd32',    # Lime Green
                'reduced rainfall': '#adff2f',      # Green Yellow
                'standardized index': '#9370db'     # Medium Purple
            }

            # Generate the plot with sorted categories and the customized colors
            # https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.bar.html
            drought_keywords_counts_sorted.plot(kind='bar', stacked=True, figsize=(12, 6),
                                        color=[drought_keywords_color_mapping[cat] for cat in drought_keywords_counts_sorted.columns])

            # Add titles and axis labels that were defined before depending automatically from the titels
            # https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.title.html#matplotlib-pyplot-title
            # https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.xlabel.html#matplotlib.pyplot.xlabel
            plot.title(title)
            plot.xlabel(xaxisdescription)

            # Add manual y-axis label for all studies
            # https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.ylabel.html#matplotlib-pyplot-ylabel
            plot.ylabel('Number of occurrences')

            # Place the sorted legend with counts inside the plot on the upper right
            # https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.legend.html
            plot.legend(sorted_legend_labels_with_counts, title="Drought Keyword", loc='upper right')

            # Rotate x-axis labels for readability and better plot-text ratio
            # https://www.geeksforgeeks.org/matplotlib-pyplot-xticks-in-python/
            plot.xticks(ticks=range(len(drought_keywords_counts_sorted.index)), labels=drought_keywords_counts_sorted.index, rotation=45,
                        ha='right')

            # Ensure that the tight layout is used for a better visualisation
            # https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.tight_layout.html#matplotlib.pyplot.tight_layout
            plot.tight_layout()

            # Save the plot as a JPG file to use it in the bachelor-thesis
            # https://www.geeksforgeeks.org/matplotlib-pyplot-savefig-in-python/
            # plot.savefig(output_file_path, format='jpg')

            # Optionally display the plot (for finetuning so adjusting is easier)
            # https://www.geeksforgeeks.org/matplotlib-pyplot-show-in-python/
            plot.show()

# Generate the MODIS and given drought category keyword bar chart
# create_drought_keywords_bar_chart(excel_file_path, 'MODIS drought keyword')

def create_reanalysis_based_bar_chart(shapefile_path, chart_type):
    """
    Creates a bar chart based on the specified chart type, either 'MODIS', 'Drought', or 'SPEI category totals'.
    The function is designed to combine bar chart creation logic for different cases which all use the SPEI drought category
    from the re-analysis into a single method.
    This allows for easy extension if more bar charts are needed in the future from the same shapefile data,
    without requiring the creation of additional methods.
    Only for re-analysis data!

    Args:
        shapefile_path (str): The path to the shapefile containing the data.
        chart_type (str): The type of bar chart to generate.

    Returns:
        None: The function generates and displays the requested bar chart.
    """

    # Reading the given shapefile using geopandas read_file() method and storing it as geodataframe
    # https://geopandas.org/en/stable/docs/user_guide/data_structures.html#geodataframe
    # https://geopandas.org/en/stable/docs/user_guide/io.html#reading-and-writing-files
    gdf = geopd.read_file(shapefile_path)

    # Define the category order for SPEI categories (applies to most of the chart types and thus globally defined before the cases)
    # https://pandas.pydata.org/docs/user_guide/10min.html#categoricals
    spei_category_order = [
        "extremely dry (SPEI <= -2)",
        "severely dry (-2 < SPEI <= -1.5)",
        "moderately dry (-1.5 < SPEI <= -1)",
        "near normal conditions (-1 < SPEI < +1)",
        "no drought (+1 < SPEI)"
    ]

    # For the given drought quantification keywords from the studies and SPEI drought categories
    if chart_type == 'Drought':
        # Grouping the data by 'dr_quanti' and 'Category' to count occurrences for the drought chart
        # https://pandas.pydata.org/docs/user_guide/10min.html#grouping
        category_counts = gdf.groupby(['dr_quanti', 'Category']).size().unstack(fill_value=0)
        # X-axis text
        xaxisdescription = 'Given drought category'
        # Title of the plot
        title = 'Distribution of SPEI drought categories in correlation with the given drought quantifications from the studies'
        # Path where the plot is going to be saved
        output_file_path = r'D:\Uni\Bachelorarbeit\Plots\Bar chart for correlation of SPEI drought category and the given drought quantifications of the studies.jpg'

    # For MODIS categories and SPEI drought categories
    if chart_type == 'MODIS SPEI':
        # Grouping the data by 'MODIS' and 'Category' to count occurrences for the MODIS chart
        # https://pandas.pydata.org/docs/user_guide/10min.html#grouping
        category_counts = gdf.groupby(['MODIS', 'Category']).size().unstack(fill_value=0)
        # X-axis text
        xaxisdescription = 'Forest type'
        # Title of the plot
        title = 'Distribution of SPEI drought categories within each MODIS category'
        # Path where the plot is going to be saved
        output_file_path = r'D:\Uni\Bachelorarbeit\Plots\Bar chart for correlation MODIS classes and SPEI drought categories.jpg'

    # For SPEI drought category totals only as series
    if chart_type == 'SPEI category totals':
        # Count occurrences of each 'Category' (SPEI drought category) and reindex using the predefined category order
        # https://pandas.pydata.org/docs/user_guide/10min.html#categoricals
        category_counts = gdf['Category'].value_counts().reindex(spei_category_order, fill_value=0)
        # X-axis text
        xaxisdescription = 'SPEI drought category'
        # Title of the plot
        title = 'Total number of occurrences for each SPEI drought category sorted by severity'
        # Path where the plot is going to be saved
        output_file_path = r'D:\Uni\Bachelorarbeit\Plots\Bar chart for SPEI drought category totals sorted by severity.jpg'

    # For all cases that somehow use "Category" (The SPEI categories)
    if chart_type in ['Drought', 'MODIS SPEI', 'SPEI category totals']:
        # Change the label for 'Other' category, so it is not too long (only for bar plots with MODIS involved)
        # https://pandas.pydata.org/docs/user_guide/basics.html#renaming-mapping-labels
        category_counts.rename(
            index={"Other (Mangrove Forest, Open Shrubland, Savannas, Permanent Wetlands, ...)": "Other"}, inplace=True)

        # Define the colors for SPEI drought categories, so they match in every plot (and with the QGIS map)
        # https://stackoverflow.com/questions/26139423/plot-different-color-for-different-categorical-levels
        spei_color_mapping = {
            'no drought (+1 < SPEI)': '#0000FF',                    # Blue
            'near normal conditions (-1 < SPEI < +1)': '#ADD8E6',   # Light Blue
            'moderately dry (-1.5 < SPEI <= -1)': '#FFA500',        # Orange
            'severely dry (-2 < SPEI <= -1.5)': '#FF4500',          # Orange-Red
            'extremely dry (SPEI <= -2)': '#8B0000'                 # Dark Red
        }

        # Reindex the DataFrame with the correct category order for all stacked bar plots
        # https://pandas.pydata.org/docs/user_guide/indexing.html#indexing-and-selecting-data
        if chart_type != 'SPEI category totals':
            existing_categories = [cat for cat in spei_category_order if cat in category_counts.columns]
            category_counts = category_counts[existing_categories]

        # Sorting the created pivot table by total occurrences (sum of rows), from most to least in descending order for all stacked bar plots
        # https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.loc.html#pandas-dataframe-loc
        # https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.sort_values.html
        if chart_type != 'SPEI category totals':
            category_counts_sorted = category_counts.loc[
                category_counts.sum(axis=1).sort_values(ascending=False).index]

            # Sorting the columns by total occurrences (sum of columns) for legend and data
            # https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.sort_values.html
            category_sums = category_counts_sorted.sum(axis=0)
            category_counts_sorted = category_counts_sorted[category_sums.sort_values(ascending=False).index]

            # Custom legend labels with counts included for clearer overview
            # https://www.geeksforgeeks.org/matplotlib-pyplot-legend-in-python/
            legend_labels_with_counts = [f"{category} [{count}]" for category, count in
                                         zip(category_sums.index, category_sums.values)]

        # Creating legend labels with count for non-stacked (series) bar plots (SPEI category totals)
        # https://pandas.pydata.org/docs/reference/api/pandas.Series.items.html#pandas-series-items
        else:
            category_counts_sorted = category_counts
            category_sums = category_counts
            legend_labels_with_counts = [f"{category} [{count}]" for category, count in category_counts.items()]

        # Replace '<='with '≤' in the legend labels for better looks
        # https://docs.python.org/3/library/stdtypes.html#str.replace
        legend_labels_with_counts = [label.replace('<=', '≤') for label in legend_labels_with_counts]

        # Sorting legend labels based on the counts numeric in descending order
        # https://docs.python.org/3/howto/sorting.html
        sorted_legend_labels_with_counts = sorted(legend_labels_with_counts, key=lambda x: int(x.split('[')[1][:-1]),
                                                  reverse=True)

        # Generate the plot with sorted categories and the customized colors
        # https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.bar.html
        category_counts_sorted.plot(kind='bar', stacked=(chart_type != 'SPEI category totals'), figsize=(12, 6),
                                    color=[spei_color_mapping[cat] for cat in
                                           category_counts_sorted.index] if chart_type == 'SPEI category totals' else [
                                        spei_color_mapping[cat] for cat in category_counts_sorted.columns])

        # Add titles and axis labels that were defined before depending automatically from the titels
        # https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.title.html#matplotlib-pyplot-title
        # https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.xlabel.html#matplotlib.pyplot.xlabel
        plot.title(title)
        plot.xlabel(xaxisdescription)

        # Add manual y-axis label for all studies
        # https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.ylabel.html#matplotlib-pyplot-ylabel
        plot.ylabel('Number of re-analysed studies')

        # Place the sorted legend with counts inside the plot on the upper right
        # https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.legend.html
        if chart_type == 'SPEI category totals':
            # Adding a custom legend for non-stacked bar charts (SPEI category totals)
            legend_handles = [plot.Rectangle((0, 0), 1, 1, color=spei_color_mapping[cat]) for cat in
                              category_counts_sorted.index]
            plot.legend(legend_handles, sorted_legend_labels_with_counts, title="SPEI drought category",
                        loc='upper right')
        # Adding a custom legend for all other stacked bar charts
        else:
            plot.legend(sorted_legend_labels_with_counts, title="SPEI drought category", loc='upper right')

        # Rotate x-axis labels for readability and better plot-text ratio and replace '<=' with '≤'
        # https://www.geeksforgeeks.org/matplotlib-pyplot-xticks-in-python/
        # https://docs.python.org/3/library/stdtypes.html#str.replace
        plot.xticks(ticks=range(len(category_counts_sorted.index)),  # Specify the positions of the ticks
                    labels=[label.replace('<=', '≤') for label in category_counts_sorted.index],
                    rotation=45, ha='right')

        # Ensure that the tight layout is used for a better visualisation
        # https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.tight_layout.html#matplotlib.pyplot.tight_layout
        plot.tight_layout()

        # Save the plot as a JPG file to use it in the bachelor-thesis
        # https://www.geeksforgeeks.org/matplotlib-pyplot-savefig-in-python/
        # plot.savefig(output_file_path, format='jpg')

        # Optionally display the plot (for finetuning so adjusting is easier)
        # https://www.geeksforgeeks.org/matplotlib-pyplot-show-in-python/
        plot.show()

# Generate the SPEI drought categories bar chart
# create_reanalysis_based_bar_chart(reanalysis_shapefile_path, 'SPEI category totals')

# Generate the drought quantification keyword bar chart
# create_reanalysis_based_bar_chart(reanalysis_shapefile_path, 'Drought')

# Generate the MODIS SPEI category bar chart
# create_reanalysis_based_bar_chart(reanalysis_shapefile_path, 'MODIS SPEI')

def create_pie_chart(shape_or_excel_file_path, chart_type):
    """
    Creates a pie chart based on the specified chart_type, either using data from an Excel file or a shapefile.
    The method is designed to combine the pie chart creation logic into a single function, allowing for easy
    extension. If additional pie charts are needed in the future from the same Excel- or shapefile, more cases can be
    added without creating new methods.

    Args:
        shape_or_excel_file_path (str): The path to either the Excel file or the shapefile.
        chart_type (str): Determines the type of pie chart to generate.

    Returns:
        None: The function generates and displays the requested pie chart(s).
    """

    # Cases for the pie charts that need data from the Excel file
    if chart_type in ['study type', 'breakdown', 'MODIS drought category', 'MODIS drought sphere']:
        # Load the Excel file and "relevantInfo" sheet where the data for the pie charts is stored
        # https://pandas.pydata.org/docs/reference/api/pandas.read_excel.html
        excel_df = pd.read_excel(excel_file_path, sheet_name='relevantInfo')

        # Clean up the 'study type' column to avoid duplicates due to capitalization or extra spaces and make the filtering for the breakdown pie charts easier
        # https://pandas.pydata.org/docs/reference/api/pandas.Series.str.strip.html
        # https://pandas.pydata.org/docs/reference/api/pandas.Series.str.lower.html
        excel_df['study type'] = excel_df['study type'].str.strip().str.lower()

        # Clean up the 'drought quantification keyword for plots' and remove quotes (because python gives an error for "dry" if there are quotes) and extra spaces
        # https://pandas.pydata.org/docs/reference/api/pandas.Series.str.strip.html
        # https://pandas.pydata.org/docs/reference/api/pandas.Series.str.lower.html
        # https://pandas.pydata.org/docs/reference/api/pandas.Series.str.replace.html
        excel_df['drought quantification keyword for plots'] = excel_df[
            'drought quantification keyword for plots'].str.strip().str.lower().str.replace('"', '')

        # Define consistent colors for each drought quantification keyword across all plots, globally defined because of multiple use cases
        # https://stackoverflow.com/questions/26139423/plot-different-color-for-different-categorical-levels
        drought_keywords_color_mapping = {
            'dry': '#ff7f0e',                   # Dark Orange
            'differs from normal': '#ff4500',   # Orange-Red
            'dry season': '#87CEEB',            # Sky Blue
            'low soil moisture': '#00ced1',     # Dark Turquoise
            'low water flow/depth': '#4682b4',  # Steel Blue
            'plant water stress': '#32cd32',    # Lime Green
            'reduced rainfall': '#adff2f',      # Green Yellow
            'standardized index': '#9370db'     # Medium Purple
        }

        # If 'study type' is selected, this case is used to create general "study type" pie chart
        if chart_type == 'study type':
            # Clean and count the occurrences of each study type to create the percentages
            # https://pandas.pydata.org/docs/reference/api/pandas.Series.value_counts.html
            study_type_counts = excel_df['study type'].value_counts()

            # Set colors for every study type for a good overview
            # https://proclusacademy.com/blog/customize_matplotlib_piechart/#slice-colors
            colors = ['#1f77b4', # blue
                      '#ff7f0e', # orange
                      '#2ca02c', # green
                      '#9467bd'  # purple
                      ]

            # Adjust the size of the plot so the picture is better usable later on
            # https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.figure.html
            plot.figure(figsize=(6, 5))

            # Create the pie chart without labels but with percentages
            # https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.pie.html
            wedges, texts, autotexts = plot.pie(study_type_counts, autopct='%1.1f%%', colors=colors, startangle=90,
                                                wedgeprops = {'edgecolor': 'white', 'linewidth': 0.5})

            # Set label positions manually for the study type "Review", so they are right next to their pieces
            # https://stackoverflow.com/questions/43916834/matplotlib-dynamically-change-text-position
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
            plot.axis('equal')

            # Set the title and filename for this pie chart
            # https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.title.html#matplotlib-pyplot-title
            plot.title("Distribution of the study types out of all used studies")
            study_type_output_path = r'D:\Uni\Bachelorarbeit\Plots\Main pie chart with complete study type percentages.jpg'

            # Save the pie chart as a JPG file to use it in the thesis
            # https://www.geeksforgeeks.org/matplotlib-pyplot-savefig-in-python/
            #plot.savefig(study_type_output_path, format='jpg')

            # Optionally display the plot (for finetuning so adjusting is easier)
            # https://www.geeksforgeeks.org/matplotlib-pyplot-show-in-python/
            plot.show()

        # If 'breakdown' is selected, create the drought quantification breakdown pie charts for each study type
        elif chart_type == 'breakdown':
            # Group the data by 'study type' and count the occurrences of 'drought quantification keyword for plots'
            # https://pandas.pydata.org/docs/user_guide/10min.html#grouping
            study_type_breakdown_data = excel_df.groupby('study type')['drought quantification keyword for plots'].value_counts().unstack(
                fill_value=0)

            # Display only the study types 'experimental', 'observational', and 'modeling' in a specific order for pie charts
            desired_study_type_order = ['experimental', 'observational', 'modeling']

            # Filter and reorder the study types using .isin() to keep only the relevant types and .reindex() to match the desired order
            # https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.loc.html#pandas-dataframe-loc
            # https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.isin.html
            # https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.reindex.html
            final_breakdown_data = study_type_breakdown_data.loc[
                study_type_breakdown_data.index.isin(desired_study_type_order)].reindex(desired_study_type_order)

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
                # Use consistent colors for each keyword, so it is not confusing (using the colors declared before in 'drought_keywords_color_mapping'
                breakdown_colors = [drought_keywords_color_mapping[label] for label in row.index]

                # Display percentages inside the pieces and assign the labels and colors to the pie chart axes
                # https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.pie.html
                axes[i].pie(row, labels=row.index, autopct='%1.1f%%', colors=breakdown_colors)

                # Display a title for every single pie chart containing its study type
                # https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.set_title.html
                axes[i].set_title(f'{study_type.title()}')

            # Set the main title for the entire figure (has to be done separately because every pie chart has its own title) aswell as the file name
            # https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.title.html#matplotlib-pyplot-title
            # https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.suptitle.html
            fig.suptitle('Breakdown of the given drought quantification for the relevant study types', fontsize=16)
            breakdown_output_file_path = r'D:\Uni\Bachelorarbeit\Plots\Breakdown pie charts for percentages of drought definitions for study types.jpg'

            # Ensure that the tight layout is used for a better visualisation (the single pie charts are too close to another if not used)
            # https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.tight_layout.html#matplotlib.pyplot.tight_layout
            plot.tight_layout()

            # Save the pie chart(s) as one JPG file to use it in the thesis
            # https://www.geeksforgeeks.org/matplotlib-pyplot-savefig-in-python/
            # plot.savefig(breakdown_output_file_path, format='jpg')

            # Optionally display the pie chart(s) (for finetuning so adjusting is easier)
            # https://www.geeksforgeeks.org/matplotlib-pyplot-show-in-python/
            plot.show()

        # MAYBE DATA SOURCE HAS TO BE CHANGED DEPENDING ON ANSWER (Currently Excel)
        # If 'MODIS drought category' is selected, create the drought quantification breakdown pie charts for each MODIS forest type
        elif chart_type == 'MODIS drought category':
            # Group the data by 'MODIS_forest_type' and count the occurrences of 'drought quantification keyword for plots'
            # https://pandas.pydata.org/docs/user_guide/10min.html#grouping
            forest_breakdown_data = excel_df.groupby('MODIS_forest_type')['drought quantification keyword for plots'].value_counts().unstack(
                fill_value=0)

            # Reorder the MODIS Categories based on https://developers.google.com/earth-engine/datasets/catalog/MODIS_061_MCD12Q1#bands "LC_Type1 Class Table"
            desired_forest_order = ['Evergreen Needleleaf Forest', 'Evergreen Broadleaf Forest',
                                    'Deciduous Broadleaf Forest', 'Mixed Forest', 'Closed Shrubland', 'Woody Savanna', 'Other (Mangrove Forest, Open Shrubland, Savannas, Permanent Wetlands, ...)']

            # Filter and reorder the MODIS forest types using .isin() to keep only the relevant types and .reindex() to match the desired order
            # https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.loc.html#pandas-dataframe-loc
            # https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.isin.html
            # https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.reindex.html
            final_forest_breakdown_data = forest_breakdown_data.loc[
                forest_breakdown_data.index.isin(desired_forest_order)].reindex(desired_forest_order)

            # Set the size of the figure and define the number of subplots based on the number of relevant MODIS forest types
            # manually because we need one pie chart for each relevant, named MODIS forest type
            # https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.subplots.html
            fig, axes = plot.subplots(2, 4, figsize=(30, 10))

            # Flatten the axes for easier iteration and a faster plot creation
            # https://stackoverflow.com/questions/46862861/what-does-axes-flat-in-matplotlib-do
            axes = axes.flatten()

            # Iterate over the final dataframe that holds the wanted information to filter out zero values and assign the wanted colors
            # https://www.w3schools.com/python/pandas/ref_df_iterrows.asp
            for i, (MODIS_forest_type, row) in enumerate(final_forest_breakdown_data.iterrows()):
                # Filter out redundant zero values in the rows (Given drought categories) so only the drought categories that are given for the study types are displayed
                row = row[row > 0]
                # Use consistent colors for each keyword, so it is not confusing (using the colors declared before globally
                breakdown_colors = [drought_keywords_color_mapping[label] for label in row.index]

                # Display percentages inside the pieces and assign the labels and colors to the pie chart pieces
                # https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.pie.html
                axes[i].pie(row, labels=row.index, autopct='%1.1f%%', colors=breakdown_colors)

                # Display a title for every single pie chart containing its MODIS forest type
                # https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.set_title.html
                axes[i].set_title(f'{MODIS_forest_type.title()}')

            # Set the main title for the entire figure (has to be done separately because every pie chart has its own title) aswell as the file name
            # https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.title.html#matplotlib-pyplot-title
            # https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.suptitle.html
            fig.suptitle('Breakdown of the given drought quantification for the relevant MODIS forest types', fontsize=16)
            breakdown_output_file_path = r'D:\Uni\Bachelorarbeit\Plots\Breakdown pie charts for percentages of drought definitions for MODIS forest types from excel.jpg'

            # Remove the last unused pie chart since we only have 7 relevant MODIS forest types but 2 rows and 4 columns = 8 pie charts
            # https://www.geeksforgeeks.org/matplotlib-figure-figure-delaxes-in-python/
            fig.delaxes(axes[-1])

            # Ensure that the tight layout is used for a better visualisation (the single pie charts are too close to another if not used)
            # https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.tight_layout.html#matplotlib.pyplot.tight_layout
            plot.tight_layout()

            # Save the pie chart(s) as one JPG file to use it in the thesis
            # https://www.geeksforgeeks.org/matplotlib-pyplot-savefig-in-python/
            # plot.savefig(breakdown_output_file_path, format='jpg')

            # Optionally display the pie chart(s) (for finetuning so adjusting is easier)
            # https://www.geeksforgeeks.org/matplotlib-pyplot-show-in-python/
            plot.show()

        # NEED TO EDIT THE EXCEL FILE FIRST BEFORE SAVING THE FINAL PIE CHART
        # If 'MODIS drought sphere' is selected, create the drought quantification breakdown pie charts for each MODIS forest type
        elif chart_type == 'MODIS drought sphere':

            # Group the data by 'MODIS_forest_type' and clean 'drought_sphere' and then count its occurrences with size()
            # https://pandas.pydata.org/docs/user_guide/10min.html#grouping
            # https://pandas.pydata.org/docs/reference/api/pandas.Series.str.strip.html
            # https://pandas.pydata.org/docs/reference/api/pandas.Series.str.lower.html
            # https://www.geeksforgeeks.org/list-size-method-in-java-with-examples/
            forest_sphere_breakdown_data = (
                excel_df.groupby(['MODIS_forest_type', excel_df['drought_sphere'].str.strip().str.lower()])
                .size()  # Count occurrences of each drought sphere within each forest type
                .unstack(fill_value=0)  # Pivot to have drought_sphere as columns and fill missing with 0
            )

            # Reorder the MODIS Categories based on https://developers.google.com/earth-engine/datasets/catalog/MODIS_061_MCD12Q1#bands "LC_Type1 Class Table"
            desired_forest_order = ['Evergreen Needleleaf Forest', 'Evergreen Broadleaf Forest',
                                    'Deciduous Broadleaf Forest', 'Mixed Forest', 'Closed Shrubland', 'Woody Savanna',
                                    'Other (Mangrove Forest, Open Shrubland, Savannas, Permanent Wetlands, ...)']

            # Filter and reorder the MODIS forest types using .isin() to keep only the relevant types and .reindex() to match the desired order
            # https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.loc.html#pandas-dataframe-loc
            # https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.isin.html
            # https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.reindex.html
            final_forest_sphere_breakdown_data = forest_sphere_breakdown_data.loc[
                forest_sphere_breakdown_data.index.isin(desired_forest_order)].reindex(desired_forest_order)

            # Manually define the number of subplots based on the number of relevant MODIS forest types because we need one pie chart for each relevant, named MODIS forest type
            # Also toggle size of the figures so every percentage is clear readable
            # https://www.programiz.com/python-programming/methods/built-in/len
            # https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.subplots.html
            fig, axes = plot.subplots(2, 4, figsize=(20, 20))

            # Flatten the axes for easier iteration and a faster plot creation
            # https://stackoverflow.com/questions/46862861/what-does-axes-flat-in-matplotlib-do
            axes = axes.flatten()

            # Define consistent colors for each drought quantification keyword across all plots, globally defined because of muliple use cases
            # https://stackoverflow.com/questions/26139423/plot-different-color-for-different-categorical-levels
            sphere_color_mapping = {
                'soil': '#8B4513',              # brown
                'atmospheric': '#ADD8E6',       # light blue
                'hydrological': '#3232d1',      # dark blue
                'meteorological': '#808080'     # grey
            }

            # Iterate over the final dataframe that holds the wanted information to filter out zero values and assign the wanted colors
            # https://www.w3schools.com/python/pandas/ref_df_iterrows.asp
            for i, (drought_sphere, row) in enumerate(final_forest_sphere_breakdown_data.iterrows()):
                # Filter out redundant zero values in the rows (Given drought categories) so only the drought categories that are given for the study types are displayed
                row = row[row > 0]
                # Now use the declared colors for the stacked bar plot, also use strip() to assure every class get taken withouth error
                sphere_breakdown_colors = [sphere_color_mapping[label.strip()] for label in row.index]

                # Display percentages inside the pieces and assign the labels and colors to the pie chart pieces
                # https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.pie.html
                axes[i].pie(row, labels=row.index, autopct='%1.1f%%', colors=sphere_breakdown_colors)

                # Display a title for every single pie chart containing its MODIS forest type
                # https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.set_title.html
                axes[i].set_title(f'{drought_sphere.title()}')

            # Set the main title for the entire figure (has to be done separately because every pie chart has its own title) aswell as the file name
            # https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.title.html#matplotlib-pyplot-title
            # https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.suptitle.html
            fig.suptitle('Breakdown of the given drought spheres for the relevant MODIS forest types',
                         fontsize=16)
            breakdown_output_file_path = r'D:\Uni\Bachelorarbeit\Plots\Breakdown pie charts for percentages of drought spheres for MODIS forest types from excel.jpg'

            # Remove the last unused pie chart since we only have 7 relevant MODIS forest types but 2 rows and 4 columns = 8 pie charts
            # https://www.geeksforgeeks.org/matplotlib-figure-figure-delaxes-in-python/
            fig.delaxes(axes[-1])

            # Ensure that the tight layout is used for a better visualisation (the single pie charts are too close to another if not used)
            # https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.tight_layout.html#matplotlib.pyplot.tight_layout
            plot.tight_layout()

            # Save the pie chart(s) as one JPG file to use it in the thesis
            # https://www.geeksforgeeks.org/matplotlib-pyplot-savefig-in-python/
            # plot.savefig(breakdown_output_file_path, format='jpg')

            # Optionally display the pie chart(s) (for finetuning so adjusting is easier)
            # https://www.geeksforgeeks.org/matplotlib-pyplot-show-in-python/
            plot.show()

    # If 'SPEI category percentage' is selected, create the SPEI drought category pie chart
    elif chart_type == 'SPEI category percentage':

        # Reading the given shapefile using geopandas read_file() method and storing it as geodataframe
        # https://geopandas.org/en/stable/docs/user_guide/data_structures.html#geodataframe
        # https://geopandas.org/en/stable/docs/user_guide/io.html#reading-and-writing-files
        spei_gdf = geopd.read_file(shape_or_excel_file_path)

        # Count the occurrences of each SPEI drought category to create the percentages
        # https://pandas.pydata.org/docs/reference/api/pandas.Series.value_counts.html
        spei_category_counts = spei_gdf['Category'].value_counts()

        # Define specific colors for every SPEI drought category so they are consistent in every plot
        # https://proclusacademy.com/blog/customize_matplotlib_piechart/#slice-colors
        spei_colors = ['#FF4500', '#8B0000', '#FFA500', '#ADD8E6', '#0000FF']

        # Adjust the size of the plot so the picture is better usable later and nothing gets cut off
        # https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.figure.html
        plot.figure(figsize=(11, 8))

        # Create the pie chart with black lines between pieces and percentages as texts
        # https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.pie.html
        wedges, category_texts, autotexts = plot.pie(spei_category_counts, autopct='%1.1f%%', colors=spei_colors, startangle=90,
                                            wedgeprops={'edgecolor': 'black', 'linewidth': 0.4})

        # Set label position manually for the SPEI category ('no drought (+1 < SPEI)'), so it is right next to their piece and replace '<=' with '≤' if needed in the labels
        # https://stackoverflow.com/questions/43916834/matplotlib-dynamically-change-text-position
        # https://docs.python.org/3/library/stdtypes.html#str.replace
        for i, spei_label in enumerate(spei_category_counts.index):
            # Replace '<=' with '≤' in the labels (pie chart pieces descriptions)
            cleaned_spei_label = spei_label.replace('<=', '≤')

            # We only want to manually position the 'no drought (+1 < SPEI)' label because it's not right on default
            if cleaned_spei_label == "no drought (+1 < SPEI)":
                # Manually adjusting the position of 'no drought (+1 < SPEI)' by using coordinates
                category_texts[i].set_position((-0.1, 1.1))

            # Adding back the SPEI category label text (because set_position overrides them)
            # https://www.tutorialspoint.com/how-to-add-title-to-subplots-in-matplotlib#:~:text=The%20Matplotlib%20set_text()%20function,in%20a%20subplot%20or%20plot.
            category_texts[i].set_text(cleaned_spei_label)

        # Set the main title as well as the file name
        # https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.title.html#matplotlib-pyplot-title
        plot.title("Distribution of the SPEI categories out of all re-analysed studies in percentage")
        spei_category_output_file_path = r'D:\Uni\Bachelorarbeit\Plots\Pie chart with complete SPEI drought category percentages.jpg'

        # Ensure that the tight layout is used for a better visualisation and readability of the 'no drought (+1 < SPEI)' percentage
        # https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.tight_layout.html#matplotlib.pyplot.tight_layout
        plot.tight_layout()

        # Save the pie chart as a JPG file to use it in the thesis
        # https://www.geeksforgeeks.org/matplotlib-pyplot-savefig-in-python/
        # plot.savefig(spei_category_output_file_path, format='jpg')

        # Optionally display the plot (for finetuning so adjusting is easier)
        # https://www.geeksforgeeks.org/matplotlib-pyplot-show-in-python/
        plot.show()

# Generate the ´SPEI category pie chart
# create_pie_chart(reanalysis_shapefile_path, 'SPEI category percentage')

# Generate the general study type pie chart
# create_pie_chart(excel_file_path, 'study type')

# Generate the study type breakdown of given drought quantifications pie chart
# create_pie_chart(excel_file_path, 'breakdown')

# Generate the MODIS breakdown of given drought quantifications pie chart
# create_pie_chart(excel_file_path, 'MODIS drought category')

# Generate the MODIS breakdown of drought spheres pie chart
create_pie_chart(excel_file_path, 'MODIS drought sphere')