# Importing pandas for data manipulation and analysis and name it pd for simpler use
import pandas as pd

# Importing geopandas for working with geospatial data, including shapefiles
import geopandas as geopd

# Creates the plots from the data handled by (geo)pandas

import matplotlib.pyplot as plot

# Path to the shapefile containing the information needed for all plots depending on the re-analysis data
reanalysis_shapefile_path = r'D:\Uni\Bachelorarbeit\complete_paper_points\re-analysed paper points with forest\re-analysed_paper_points_with_forest.shp'

# Path to the excel file containing all data
excel_file_path = r'D:\Uni\Bachelorarbeit\2024Apr_Mana_Review_v2i - paper_coords_area_years_plotkeywords_speireanalysis_month_finished.xlsx'

def create_reanalysis_based_bar_chart(shapefile_path, chart_type):
    """
    Creates a bar chart based on the specified chart type, either 'MODIS', 'Drought', or 'SPEI category totals'.
    The function handles various types of bar charts, such as showing the correlation between MODIS classes and
    SPEI drought categories, the distribution of drought quantifications from studies, or the total distribution of
    SPEI drought categories.
    The function is designed to combine bar chart creation logic for different cases into a single method.
    This allows for easy extension if more bar charts are needed in the future from the same shapefile data,
    without requiring the creation of additional methods.

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

    # Define the category order for SPEI categories (applies to all chart types and thus globally defined before the cases)
    # https://pandas.pydata.org/docs/user_guide/10min.html#categoricals
    category_order = [
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
    if chart_type == 'MODIS':
        # Grouping the data by 'MODIS' and 'Category' to count occurrences for the MODIS chart
        # https://pandas.pydata.org/docs/user_guide/10min.html#grouping
        category_counts = gdf.groupby(['MODIS', 'Category']).size().unstack(fill_value=0)
        # X-axis text
        xaxisdescription = 'MODIS category'
        # Title of the plot
        title = 'Distribution of SPEI drought categories within each MODIS category'
        # Path where the plot is going to be saved
        output_file_path = r'D:\Uni\Bachelorarbeit\Plots\Bar chart for correlation MODIS classes and SPEI drought categories.jpg'

    # For SPEI drought category totals only as series
    if chart_type == 'SPEI category totals':
        # Count occurrences of each 'Category' (SPEI drought category) and reindex using the predefined category order
        # https://pandas.pydata.org/docs/user_guide/10min.html#categoricals
        category_counts = gdf['Category'].value_counts().reindex(category_order, fill_value=0)
        # X-axis text
        xaxisdescription = 'SPEI drought category'
        # Title of the plot
        title = 'Total number of occurrences for each SPEI drought category'
        # Path where the plot is going to be saved
        output_file_path = r'D:\Uni\Bachelorarbeit\Plots\Bar chart for SPEI drought category totals.jpg'

    if chart_type in ['Drought', 'MODIS', 'SPEI category totals']:
        # Change the label for 'Other' category, so it is not too long (only for 'MODIS')
        # https://pandas.pydata.org/docs/user_guide/basics.html#renaming-mapping-labels
        category_counts.rename(
            index={"Other (Mangrove Forest, Open Shrubland, Savannas, Permanent Wetlands, ...)": "Other"}, inplace=True)

        # Define the colors for SPEI drought categories, so they match in every plot and with the QGIS) map
        # https://stackoverflow.com/questions/26139423/plot-different-color-for-different-categorical-levels
        color_mapping = {
            'no drought (+1 < SPEI)': '#0000FF',
            'near normal conditions (-1 < SPEI < +1)': '#ADD8E6',
            'moderately dry (-1.5 < SPEI <= -1)': '#FFA500',
            'severely dry (-2 < SPEI <= -1.5)': '#FF4500',
            'extremely dry (SPEI <= -2)': '#8B0000'
        }

        # Reindex the DataFrame with the correct category order for all stacked bar plots
        # https://pandas.pydata.org/docs/user_guide/indexing.html#indexing-and-selecting-data
        if chart_type != 'SPEI category totals':
            existing_categories = [cat for cat in category_order if cat in category_counts.columns]
            category_counts = category_counts[existing_categories]

        # Sorting the created pivot table by total occurrences (sum of rows), from most to least in descending order for all stacked bar plots for the custom legend
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

        # Replace <= with ≤ in the legend labels for better looks
        # https://docs.python.org/3/library/stdtypes.html#str.replace
        legend_labels_with_counts = [label.replace('<=', '≤') for label in legend_labels_with_counts]

        # Sorting legend labels based on the counts numeric in descending order
        # https://docs.python.org/3/howto/sorting.html
        sorted_legend_labels_with_counts = sorted(legend_labels_with_counts, key=lambda x: int(x.split('[')[1][:-1]),
                                                  reverse=True)

        # Generate the plot with sorted categories and the customized colors
        # https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.bar.html
        category_counts_sorted.plot(kind='bar', stacked=(chart_type != 'SPEI category totals'), figsize=(12, 6),
                                    color=[color_mapping[cat] for cat in
                                           category_counts_sorted.index] if chart_type == 'SPEI category totals' else [
                                        color_mapping[cat] for cat in category_counts_sorted.columns])

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
            legend_handles = [plot.Rectangle((0, 0), 1, 1, color=color_mapping[cat]) for cat in
                              category_counts_sorted.index]
            plot.legend(legend_handles, sorted_legend_labels_with_counts, title="SPEI drought category",
                        loc='upper right')
        else:
            plot.legend(sorted_legend_labels_with_counts, title="SPEI drought category", loc='upper right')

        # Rotate x-axis labels for readability and better plot-text ratio and adjust them so they have '≤' instead of '<='
        # https://www.geeksforgeeks.org/matplotlib-pyplot-xticks-in-python/
        # https://docs.python.org/3/library/stdtypes.html#str.replace
        plot.xticks(ticks=range(len(category_counts_sorted.index)),  # Specify the positions of the ticks
                    labels=[label.replace('<=', '≤') for label in category_counts_sorted.index],  # Replace <= with ≤
                    rotation=45, ha='right')

        # Ensure that the tight layout is used for a better visualisation
        # https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.tight_layout.html#matplotlib.pyplot.tight_layout
        plot.tight_layout()

        # Save the plot as a JPG file to use it in the bachelor-thesis
        # https://www.geeksforgeeks.org/matplotlib-pyplot-savefig-in-python/
        #plot.savefig(output_file_path, format='jpg')

        # Optionally display the plot (for finetuning so adjusting is easier)
        # https://www.geeksforgeeks.org/matplotlib-pyplot-show-in-python/
        plot.show()

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

    # For the pie charts that need an Excel file
    if chart_type in ['study type', 'breakdown']:
        # Load the Excel file and "relevantInfo" sheet where the data for the pie charts is stored
        # https://pandas.pydata.org/docs/reference/api/pandas.read_excel.html
        df = pd.read_excel(excel_file_path, sheet_name='relevantInfo')

        # Normalize the 'study type' column to avoid duplicates due to capitalization or extra spaces to be on the safe side
        # https://pandas.pydata.org/docs/reference/api/pandas.Series.str.strip.html
        # https://pandas.pydata.org/docs/reference/api/pandas.Series.str.lower.html
        df['study type'] = df['study type'].str.strip().str.lower()

        # Clean up the 'drought quantification keyword for plots' to remove quotes and extra spaces
        # https://pandas.pydata.org/docs/reference/api/pandas.Series.str.replace.html
        df['drought quantification keyword for plots'] = df[
            'drought quantification keyword for plots'].str.strip().str.lower().str.replace('"', '')

        # If 'study type' is selected, create the general "study type" pie chart
        if chart_type == 'study type':
            # Clean and count the occurrences of each study type for percentages
            # https://pandas.pydata.org/docs/reference/api/pandas.Series.value_counts.html
            study_type_counts = df['study type'].value_counts()

            # Define colors for every study type for a good overview
            # https://proclusacademy.com/blog/customize_matplotlib_piechart/#slice-colors
            colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']

            # Exploding the "review" and "conceptual" slices so the difference and the percentages are clearer
            # https://www.educative.io/answers/how-to-explode-a-pie-chart-using-matplotlib-in-python
            explode = [0, 0, 0, 0.1, 0.2]

            # Adjusting the size of the plot so the picture is better usable
            # https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.figure.html
            plot.figure(figsize=(6, 5))

            # Create the pie chart without labels but with percentages
            # https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.pie.html
            wedges, texts, autotexts = plot.pie(study_type_counts, autopct='%1.1f%%', colors=colors, startangle=90,
                                                explode=explode)

            # Set label positions manually for the exploded study types, so they are right next to their pieces
            # https://stackoverflow.com/questions/43916834/matplotlib-dynamically-change-text-position
            for i, label in enumerate(study_type_counts.index):
                label = label.title()  # Capitalize labels for display
                if label == "Conceptual":
                    # Adjusting the position of "Conceptual" by using specific coordinates
                    texts[i].set_position((-0.1, 1.25))
                elif label == "Review":
                    # Adjusting the position of "Review" by using specific coordinates
                    texts[i].set_position((0.1, 1.15))
                else:
                    # Keep default position for other labels since they are fine on default
                    texts[i].set_position(texts[i].get_position())

                # Adding back the study type label text (since set_position overrides them)
                # https://www.tutorialspoint.com/how-to-add-title-to-subplots-in-matplotlib#:~:text=The%20Matplotlib%20set_text()%20function,in%20a%20subplot%20or%20plot.
                texts[i].set_text(label)

            # Draw the plot as circle and ensure equal aspect ratio
            # https://matplotlib.org/stable/gallery/subplots_axes_and_figures/axis_equal_demo.html
            plot.axis('equal')

            # Save the pie chart with its title as jpg to use it in the thesis
            # https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.title.html#matplotlib-pyplot-title
            plot.title("Distribution of the study types out of all used studies")
            output_file_path = r'D:\Uni\Bachelorarbeit\Plots\Main pie chart with complete study type percentages.jpg'

            # Ensure that the tight layout is used for a better visualisation
            # https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.tight_layout.html#matplotlib.pyplot.tight_layout
            plot.tight_layout()

            # Save the pie chart as a JPG file to use it in the thesis
            # https://www.geeksforgeeks.org/matplotlib-pyplot-savefig-in-python/
            # plt.savefig(output_file_path, format='jpg')

            # Optionally display the plot (for finetuning so adjusting is easier)
            # https://www.geeksforgeeks.org/matplotlib-pyplot-show-in-python/
            plot.show()

        # If 'breakdown' is selected, create the drought quantification breakdown pie charts for each study type
        elif chart_type == 'breakdown':
            # Group the data by 'study type' and count the occurrences of 'drought quantification keyword for plots'
            # https://pandas.pydata.org/docs/user_guide/10min.html#grouping
            grouped_data = df.groupby('study type')['drought quantification keyword for plots'].value_counts().unstack(
                fill_value=0)

            # Clean the data (handling duplicates of 'observational' type)
            # https://pandas.pydata.org/docs/user_guide/10min.html#grouping
            # https://www.programiz.com/python-programming/methods/built-in/sum
            cleaned_grouped_data = grouped_data.groupby(grouped_data.index).sum()

            # Define consistent colors for each drought quantification keyword across all charts
            # https://stackoverflow.com/questions/26139423/plot-different-color-for-different-categorical-levels
            color_mapping = {
                'dry': '#ff7f0e',
                'differs from normal': '#ff4500',
                'dry season': '#87CEEB',
                'low soil moisture': '#00ced1',
                'low water flow/depth': '#4682b4',
                'plant water stress': '#32cd32',
                'reduced rainfall': '#adff2f',
                'standardized index': '#9370db'
            }

            # Define the number of subplots based on the number of study types because we need one pie chart for each study type
            # https://www.programiz.com/python-programming/methods/built-in/len
            # https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.subplots.html
            num_study_types = len(cleaned_grouped_data)
            fig, axes = plot.subplots(2, 3, figsize=(19, 10))

            # Set the main title for the entire figure
            # https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.suptitle.html
            fig.suptitle('Breakdown of the given drought quantification for every study type', fontsize=16)

            # Flatten the axes for easy iteration
            # https://stackoverflow.com/questions/46862861/what-does-axes-flat-in-matplotlib-do
            axes = axes.flatten()

            # Create pie charts for each study type with consistent colors for a better overview
            for i, (study_type, row) in enumerate(cleaned_grouped_data.iterrows()):
                # Filter out redundant zero values
                row = row[row > 0]
                # Use consistent colors for each keyword so it is not confusing
                colors = [color_mapping[label] for label in row.index]

                # Display percentages inside the pieces
                # https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.pie.html
                axes[i].pie(row, labels=row.index, autopct='%1.1f%%', colors=colors)

                # Display drought quantification keywords as text for the pieces
                # https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.set_title.html
                axes[i].set_title(f'{study_type.title()} Breakdown')

            # Remove the unused subplot so we only have the five for the study types
            # https://www.geeksforgeeks.org/matplotlib-figure-figure-delaxes-in-python/
            for j in range(i + 1, len(axes)):
                fig.delaxes(axes[j])

            # Save the pie chart with its title as jpg to use it in the thesis
            # https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.title.html#matplotlib-pyplot-title
            plot.title("Breakdown of the given drought quantification for every study type")
            output_file_path = r'D:\Uni\Bachelorarbeit\Plots\Breakdown pie charts for percentages of drought definitions for study types.jpg'

            # Ensure that the tight layout is used for a better visualisation
            # https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.tight_layout.html#matplotlib.pyplot.tight_layout
            plot.tight_layout()

            # Save the pie chart(s) as one JPG file to use it in the thesis
            # https://www.geeksforgeeks.org/matplotlib-pyplot-savefig-in-python/
            # plt.savefig(output_file_path, format='jpg')

            # Optionally display the plot (for finetuning so adjusting is easier)
            # https://www.geeksforgeeks.org/matplotlib-pyplot-show-in-python/
            plot.show()

    # If 'SPEI category percentage' is selected, create the SPEI drought category pie chart
    elif chart_type == 'SPEI category percentage':

        # Reading the given shapefile using geopandas read_file() method and storing it as geodataframe
        # https://geopandas.org/en/stable/docs/user_guide/data_structures.html#geodataframe
        # https://geopandas.org/en/stable/docs/user_guide/io.html#reading-and-writing-files
        gdf = geopd.read_file(shape_or_excel_file_path)

        # Count the occurrences of each SPEI drought category for percentages
        # https://pandas.pydata.org/docs/reference/api/pandas.Series.value_counts.html
        spei_category_counts = gdf['Category'].value_counts()

        # Define specific colors for every SPEI drought category
        # https://proclusacademy.com/blog/customize_matplotlib_piechart/#slice-colors
        colors = ['#FF4500', '#8B0000', '#FFA500', '#ADD8E6', '#0000FF']

        # Exploding the "no drought (+1 < SPEI)" slice for a better direct overview
        # https://www.educative.io/answers/how-to-explode-a-pie-chart-using-matplotlib-in-python
        explode = [0, 0, 0, 0, 0.3]

        # Adjusting the size of the plot so the picture is better usable later
        # https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.figure.html
        plot.figure(figsize=(10, 9))

        # Create the pie chart with white lines between pieces and percentage texts
        # https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.pie.html
        wedges, texts, autotexts = plot.pie(spei_category_counts, autopct='%1.1f%%', colors=colors, startangle=90,
                                            explode=explode, wedgeprops={'edgecolor': 'black', 'linewidth': 0.5})

        # Change percentage text color to white
        # https://stackoverflow.com/questions/27898830/python-how-to-change-autopct-text-color-to-be-white-in-a-pie-chart
        for autotext in autotexts:
            autotext.set_color('white')

        # Draw the plot as circle and ensure equal aspect ratio
        # https://matplotlib.org/stable/gallery/subplots_axes_and_figures/axis_equal_demo.html
        plot.axis('equal')

        # Set label position manually for the exploded SPEI category ("no drought (+1 < SPEI)"), so it is right next to their pieces
        # https://stackoverflow.com/questions/43916834/matplotlib-dynamically-change-text-position
        for i, label in enumerate(spei_category_counts.index):
            texts[i].set_position(texts[i].get_position())
            if label == "no drought (+1 < SPEI)":
                # Adjusting the position of "Conceptual" by using specific coordinates
                texts[i].set_position((-0.15, 1.35))

            else:
                # Keep default position for other labels since they are fine on default
                texts[i].set_position(texts[i].get_position())

            # Adding back the SPEI category label text (since set_position overrides them)
            # https://www.tutorialspoint.com/how-to-add-title-to-subplots-in-matplotlib#:~:text=The%20Matplotlib%20set_text()%20function,in%20a%20subplot%20or%20plot.
            texts[i].set_text(label)

        # Save the pie chart with its title as jpg to use it in the thesis
        # https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.title.html#matplotlib-pyplot-title
        plot.title("Distribution of the SPEI categories out of all re-analysed studies sorted by severity")
        output_file_path = r'D:\Uni\Bachelorarbeit\Plots\Pie chart with complete SPEI drought category percentages sorted bv severity.jpg'

        # Ensure that the tight layout is used for a better visualisation
        # https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.tight_layout.html#matplotlib.pyplot.tight_layout
        plot.tight_layout()

        # Save the pie chart as a JPG file to use it in the thesis
        # https://www.geeksforgeeks.org/matplotlib-pyplot-savefig-in-python/
        #plot.savefig(output_file_path, format='jpg')

        # Optionally display the plot (for finetuning so adjusting is easier)
        # https://www.geeksforgeeks.org/matplotlib-pyplot-show-in-python/
        plot.show()


# Generate the SPEI drought categories bar chart
#create_reanalysis_based_bar_chart(reanalysis_shapefile_path, 'SPEI category totals')

# Generate the drought quantification keyword bar chart
#create_reanalysis_based_bar_chart(reanalysis_shapefile_path, 'Drought')

# Generate the MODIS category bar chart
#create_reanalysis_based_bar_chart(reanalysis_shapefile_path, 'MODIS')

# Generate the ´SPEI category pie chart
create_pie_chart(reanalysis_shapefile_path, 'SPEI category percentage')

# Generate the general study type pie chart
#create_pie_chart(excel_file_path, 'study type')

# Generate the study type breakdown of given drought quantifications pie chart
#create_pie_chart(excel_file_path, 'breakdown')  # For smaller breakdown pie charts