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


def overture_buildings(
    bbox: tuple[float, float, float, float],
    dst_parquet: str | Path,
) -> None:
    """Query a subset of Overture's buildings data and save it as a GeoParquet file.

    Parameters
    ----------
    bbox : tuple
        A tuple of floats representing the bounding box of the area of interest
        in the format (minX, minY, maxX, maxY) and 4326 coordinate reference system.
    dst_parquet : str or Path
        The path to the output GeoParquet file.
    """
    s3_region = "us-west-2"
    base_url = f"s3://overturemaps-{s3_region}/release"
    version = "2024-01-17-alpha.0"
    remote_path = f"{base_url}/{version}/theme=buildings/type=*/*"

    conn = duckdb.connect()
    conn.execute("INSTALL httpfs;")
    conn.execute("INSTALL spatial;")
    conn.execute("LOAD httpfs;")
    conn.execute("LOAD spatial;")
    conn.execute(f"SET s3_region='{s3_region}';")

    read_parquet = f"read_parquet('{remote_path}', filename=true, hive_partitioning=1);"
    conn.execute(f"CREATE VIEW buildings_view AS SELECT * FROM {read_parquet}")

    query = f"""
    SELECT
        buildings.id,
        ST_GeomFromWKB(buildings.geometry) as geometry
    FROM buildings_view AS buildings
    WHERE buildings.bbox.minX <= {bbox[2]} AND buildings.bbox.maxX >= {bbox[0]}
      AND buildings.bbox.minY <= {bbox[3]} AND buildings.bbox.maxY >= {bbox[1]}
    """

    file = str(Path(dst_parquet).resolve())
    conn.execute(f"COPY ({query}) TO '{file}' WITH (FORMAT PARQUET);")

    conn.close()


# New York City bbox
bbox_example = (-74.25909, 40.477399, -73.700181, 40.916178)
overture_buildings(bbox_example, "nyc_buildings_subset.parquet")
```
