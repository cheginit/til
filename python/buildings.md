# Overture Buildings using DuckDB

[Overture Maps](https://overturemaps.org)
has a building footprints dataset that contains
"2.35B conflated building footprints from OSM, Esri Community Maps,
Microsoft ML Building Footprints, and Google Open Buildings".
We can subset their dataset efficiently with DuckDB using the
following function.

```python
import duckdb
from pathlib import Path

THEME_MAP = {
    "locality": "admins",
    "locality_area": "admins",
    "administrative_boundary": "admins",
    "building": "buildings",
    "building_part": "buildings",
    "place": "places",
    "segment": "transportation",
    "connector": "transportation",
    "infrastructure": "base",
    "land": "base",
    "land_use": "base",
    "water": "base",
}


def overture_buildings(
    bbox: tuple[float, float, float, float],
    overture_type: str,
    dst_parquet: str | Path,
) -> None:
    """Query a subset of Overture's buildings data and save it as a GeoParquet file.

    Parameters
    ----------
    bbox : tuple
        A tuple of floats representing the bounding box of the area of interest
        in the format (xmin, ymin, xmax, ymax) and 4326 coordinate reference system.
    overture_type : str
        The type of Overture data to query. Valid options are:

        - ``locality``
        - ``locality_area``
        - ``administrative_boundary``
        - ``building``
        - ``building_part``
        - ``place``
        - ``segment``
        - ``connector``
        - ``infrastructure``
        - ``land``
        - ``land_use``
        - ``water``

    dst_parquet : str or Path
        The path to the output GeoParquet file.
    """
    s3_region = "us-west-2"
    base_url = f"s3://overturemaps-{s3_region}/release"
    version = "2024-04-16-beta.0"
    if overture_type not in THEME_MAP:
        raise ValueError(f"Valid Overture types are: {list(THEME_MAP)}")
    theme = THEME_MAP[overture_type]
    remote_path = f"{base_url}/{version}/theme={theme}/type={overture_type}/*"

    conn = duckdb.connect()
    conn.execute("INSTALL httpfs;")
    conn.execute("INSTALL spatial;")
    conn.execute("LOAD httpfs;")
    conn.execute("LOAD spatial;")
    conn.execute(f"SET s3_region='{s3_region}';")

    read_parquet = f"read_parquet('{remote_path}', filename=true, hive_partitioning=1);"
    conn.execute(f"CREATE OR REPLACE VIEW data_view AS SELECT * FROM {read_parquet}")

    query = f"""
    SELECT
        data.*,
    FROM data_view AS data
    WHERE data.bbox.xmin <= {bbox[2]} AND data.bbox.xmax >= {bbox[0]}
    AND data.bbox.ymin <= {bbox[3]} AND data.bbox.ymax >= {bbox[1]}
    """

    file = str(Path(dst_parquet).resolve())
    conn.execute(f"COPY ({query}) TO '{file}' WITH (FORMAT PARQUET);")

    conn.close()


# Manhattan bbox
bbox_example = (-74.02169, 40.696423, -73.891338, 40.831263)
overture_buildings(bbox_example, "building", "nyc_buildings_subset.parquet")
```

You can read the GeoParquet file with GeoPandas using the following code snippet:

```python
import geopandas as gpd
import pandas as pd
import shapely.wkb


manhatten = pd.read_parquet("nyc_buildings_subset.parquet")
manhatten = gpd.GeoDataFrame(
    manhatten.drop(columns="geometry"),
    geometry=shapely.wkb.loads(manhatten["geometry"]),
    crs=4326,
)
```

Alternatively, you can use `pyarrow`:

```python
def _record_batch_reader(
    bbox: tuple[float, float, float, float]
) -> pa.RecordBatchReader:
    """Get a pyarrow RecordBatchReader for the desired bounding box and s3 path."""
    path = "overturemaps-us-west-2/release/2024-06-13-beta.1/theme=buildings/type=building/"
    xmin, ymin, xmax, ymax = bbox
    filter = (
        (pc.field("bbox", "xmin") < xmax)
        & (pc.field("bbox", "xmax") > xmin)
        & (pc.field("bbox", "ymin") < ymax)
        & (pc.field("bbox", "ymax") > ymin)
    )

    dataset = ds.dataset(
        path, filesystem=fs.S3FileSystem(anonymous=True, region="us-west-2")
    )
    batches = dataset.to_batches(filter=filter)
    non_empty_batches = (b for b in batches if b.num_rows > 0)

    geoarrow_schema = dataset.schema.set(
        dataset.schema.get_field_index("geometry"),
        dataset.schema.field("geometry").with_metadata(
            {b"ARROW:extension:name": b"geoarrow.wkb"}
        ),
    )
    return pa.RecordBatchReader.from_batches(geoarrow_schema, non_empty_batches)


def get_buildings(
    bbox: tuple[float, float, float, float], path_parquet: str | Path
) -> gpd.GeoDataFrame:
    """Retrieve building data from Overture Maps for a given bounding box.

    Notes
    -----
    This function is based on
    `overturemaps-py <https://github.com/OvertureMaps/overturemaps-py>`__.

    Parameters
    ----------
    bbox : tuple
        Bounding box coordinates (xmin, ymin, xmax, ymax)
    path_parquet : str or Path
        Path to save the output file

    Returns
    -------
    geopandas.GeoDataFrame
        GeoDataFrame containing the building data
    """
    path_parquet = Path(path_parquet)
    if path_parquet.suffix != ".parquet":
        msg = "The output file must be a GeoParquet file with the extension `.parquet`"
        raise ValueError(msg)

    reader = _record_batch_reader(bbox)
    with pq.ParquetWriter(path_parquet, reader.schema) as writer:
        for batch in reader:
            if batch.num_rows > 0:
                writer.write_batch(batch)

    return gpd.read_parquet(path_parquet)
```
