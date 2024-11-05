# Overture Buildings using PyArrow

[Overture Maps](https://overturemaps.org)
has a building footprints dataset that contains
"2.35B conflated building footprints from OSM, Esri Community Maps,
Microsoft ML Building Footprints, and Google Open Buildings".
We can subset their dataset efficiently using `pyarrow`:

```python
from pathlib import Path

import pyarrow as pa
import pyarrow.compute as pc
import pyarrow.dataset as ds
import pyarrow.parquet as pq
from pyarrow import fs


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
        msg = "The output file must be a GeoParquet file with `.parquet` extension."
        raise ValueError(msg)

    if not isinstance(bbox, tuple | list) or len(bbox) != 4:
        msg = "The bounding box must be a tuple of four elements."
        raise ValueError

    s3_region = "us-west-2"
    version = "2024-10-23.0"
    src = f"overturemaps-{s3_region}/release/{version}/theme=buildings/type=building/"
    xmin, ymin, xmax, ymax = bbox
    filter = (
        (pc.field("bbox", "xmin") < xmax)
        & (pc.field("bbox", "xmax") > xmin)
        & (pc.field("bbox", "ymin") < ymax)
        & (pc.field("bbox", "ymax") > ymin)
    )

    dataset = ds.dataset(
        src, filesystem=fs.S3FileSystem(anonymous=True, region=s3_region)
    )
    batches = dataset.to_batches(filter=filter)
    non_empty_batches = (b for b in batches if b.num_rows > 0)

    geoarrow_schema = dataset.schema.set(
        dataset.schema.get_field_index("geometry"),
        dataset.schema.field("geometry").with_metadata(
            {b"ARROW:extension:name": b"geoarrow.wkb"}
        ),
    )
    reader = pa.RecordBatchReader.from_batches(geoarrow_schema, non_empty_batches)

    with pq.ParquetWriter(path_parquet, reader.schema) as writer:
        for batch in reader:
            if batch.num_rows > 0:
                writer.write_batch(batch)

    return gpd.read_parquet(path_parquet)
```

Note that you can set the `version` to the latest by checking Overture's [release notes](https://docs.overturemaps.org/release/latest/).
