"""Plotting referendum results in pandas.

In short, we want to make beautiful map to report results of a referendum. In
some way, we would like to depict results with something similar to the maps
that you can find here:
https://github.com/x-datascience-datacamp/datacamp-assignment-pandas/blob/main/example_map.png

To do that, you will load the data as pandas.DataFrame, merge the info and
aggregate them by regions and finally plot them on a map using `geopandas`.
"""
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt


def load_data():
    """Load data from the CSV files referundum/regions/departments."""
    referendum = pd.read_csv("data/referendum.csv", sep=";")
    regions = pd.read_csv("data/regions.csv", sep=",")
    departments = pd.read_csv("data/departments.csv", sep=",")

    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """

    reg = regions[["code", "name"]]
    reg.rename(columns={"code": "code_reg", "name": "name_reg"}, inplace=True)
    dep = departments[["region_code", "code", "name"]]
    dep.rename(
        columns={
            "region_code": "code_reg",
            "code": "code_dep",
            "name": "name_dep",
        },
        inplace=True,
    )

    merged = pd.merge(reg, dep, on="code_reg", how="left")

    return merged


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """

    dfreg = regions_and_departments[
        regions_and_departments["code_reg"].str.isdigit()
    ]
    dfreg = dfreg[~dfreg["code_reg"].isin(["01", "02", "03", "04", "06"])]
    dfreg.rename(columns={"code_dep": "Department code"}, inplace=True)

    dfref = referendum
    dfref = dfref[dfref["Department code"].str.isdigit()]

    merged = pd.merge(dfref, dfreg, on="Department code", how="left")
    merged["code_dep"] = merged["Department code"]
    print(merged.shape)

    return merged


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """

    grouped = referendum_and_areas.groupby("name_reg").sum()
    grouped.rename(
        columns={
            "registered": "Registered",
            "abstentions": "Abstentions",
            "null": "Null",
            "choice_a": "Choice A",
            "choice_b": "Choice B",
        },
        inplace=True,
    )
    grouped = grouped[
        ["Registered", "Abstentions", "Null", "Choice A", "Choice B"]
    ]

    return grouped


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """

    geo = gpd.read_file("data/regions.geojson")
    geo = geo[~geo["code"].isin(["01", "02", "03", "04", "06", "94"])]
    geo.rename(columns={"nom": "name_reg"}, inplace=True)

    merged = pd.merge(geo, referendum_result_by_regions, on="name_reg")

    merged["ratio"] = merged["Choice A"] / merged["Registered"]
    merged.plot(column="ratio")

    return merged


if __name__ == "__main__":

    referendum, df_reg, df_dep = load_data()
    regions_and_departments = merge_regions_and_departments(df_reg, df_dep)
    referendum_and_areas = merge_referendum_and_areas(
        referendum, regions_and_departments
    )
    referendum_results = compute_referendum_result_by_regions(
        referendum_and_areas
    )
    print(referendum_results)

    plot_referendum_map(referendum_results)
    plt.show()
