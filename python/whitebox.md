# WhiteboxTools Wrapper

This is a Python wrapper for the command-line interface of
[WhiteboxTools](https://www.whiteboxgeo.com/manual/wbt_book/)
that downloads the binaries for the current platform and
runs the specified tool with the given arguments.

```python
import platform
import requests
import zipfile
import shutil
import tempfile
import stat
from pathlib import Path
import re
import subprocess


def _download_wbt(
    wbt_root: str | Path = "WBT",
    zip_path: str | Path | None = None,
    refresh_download: bool = False,
    verbose: bool = False,
) -> None:
    """Download the WhiteboxTools executable for the current platform."""
    base_url = "https://www.whiteboxgeo.com/WBT_{}/WhiteboxTools_{}.zip"

    system = platform.system()
    if system not in ("Windows", "Darwin", "Linux"):
        raise ValueError(f"Unsupported operating system: {system}")

    if system == "Windows":
        platform_suffix = "win_amd64"
    elif system == "Darwin":
        if platform.machine() == "arm64":
            platform_suffix = "darwin_m_series"
        else:
            platform_suffix = "darwin_amd64"
    elif system == "Linux":
        if "musl" in platform.libc_ver()[0].lower():
            platform_suffix = "linux_musl"
        else:
            platform_suffix = "linux_amd64"

    url = base_url.format(system, platform_suffix)
    wbt_root = Path(wbt_root)

    exe_name = (
        "whitebox_tools.exe" if platform.system() == "Windows" else "whitebox_tools"
    )
    if (wbt_root / exe_name).exists():
        shutil.rmtree(wbt_root)

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        zip_path = (
            temp_path / "whitebox_tools.zip" if zip_path is None else Path(zip_path)
        )
        zip_path.parent.mkdir(parents=True, exist_ok=True)
        if zip_path.suffix != ".zip":
            zip_path = zip_path.with_suffix(".zip")

        if not zip_path.exists() or refresh_download:
            zip_path.unlink(missing_ok=True)
            try:
                response = requests.get(url)
                response.raise_for_status()
                zip_path.write_bytes(response.content)
            except requests.exceptions.RequestException as e:
                raise RuntimeError(f"Failed to download WhiteboxTools: {e!s}") from e
        elif verbose:
            print(f"Using existing WhiteboxTools zip file: {zip_path}")

        try:
            with zipfile.ZipFile(zip_path, "r") as zip_ref:
                for file_info in zip_ref.infolist():
                    if "/WBT/" in file_info.filename:
                        extracted_path = Path(
                            *Path(file_info.filename).parts[
                                Path(file_info.filename).parts.index("WBT") + 1 :
                            ]
                        )
                        if extracted_path.parts:
                            source = zip_ref.extract(file_info, path=temp_dir)
                            dest = wbt_root / extracted_path
                            dest.parent.mkdir(parents=True, exist_ok=True)
                            shutil.move(source, dest)
        except zipfile.BadZipFile as e:
            raise RuntimeError("Downloaded file is not a valid zip file.") from e

    # Set executable permissions for non-Windows platforms
    if system != "Windows":
        for exec_name in ("whitebox_tools", "whitebox_runner"):
            exec_path = wbt_root / exec_name
            if exec_path.exists():
                exec_path.chmod(
                    exec_path.stat().st_mode
                    | stat.S_IXUSR
                    | stat.S_IXGRP
                    | stat.S_IXOTH
                )


def _get_wbt_version(exe_path: str | Path) -> str:
    """Get the version of WhiteboxTools."""
    try:
        result = subprocess.run(
            [str(exe_path), "--version"], capture_output=True, text=True
        )
        output = result.stdout.strip()
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Error running WhiteboxTools: {e!s}") from e
    match = re.search(r"WhiteboxTools v(\d+\.\d+\.\d+)", output)
    return match.group(1) if match else "unknown"


def whitebox_tools(
    tool_name: str,
    args: list[str] | tuple[str, ...],
    wbt_root: str | Path = "WBT",
    work_dir: str | Path = "",
    verbose: bool = False,
    compress_rasters: bool = False,
    zip_path: str | Path | None = None,
    refresh_download: bool = False,
) -> None:
    """Run a WhiteboxTools (not WhiteboxRunner) tool with specified arguments.

    Parameters
    ----------
    tool_name : str
        Name of the WhiteboxTools to run.
    args : list or tuple
        List of arguments for the tool.
    wbt_root : str or Path, optional
        Path to the root directory containing the Whitebox executables (default is "WBT").
    work_dir : str or Path, optional
        Working directory for the tool (default is current directory).
    verbose : bool, optional
        Whether to print verbose output (default is False).
    compress_rasters : bool, optional
        Whether to compress output rasters (default is False).
    zip_path : str or Path, optional
        Path to the zip file containing the WhiteboxTools executables (default is None).
        If None, the zip file will be downloaded to a temporary directory that gets
        deleted after the function finishes. Otherwise, the zip file will be saved to
        the specified path.
    refresh_download : bool, optional
        Whether to refresh the download if WhiteboxTools is found (default is False).

    Raises
    ------
    subprocess.CalledProcessError
        If the tool execution fails.
    Exception
        For any other unexpected errors.

    Notes
    -----
    This function will run the specified WhiteboxTools tool and handle its output.
    If verbose is True, all output will be printed.
    """
    wbt_root = Path(wbt_root)
    work_dir = Path(work_dir) if work_dir else Path.cwd()

    exe_name = (
        "whitebox_tools.exe" if platform.system() == "Windows" else "whitebox_tools"
    )
    exe_path = wbt_root / exe_name

    if not exe_path.exists() or refresh_download:
        _download_wbt(wbt_root, zip_path, refresh_download, verbose)

    command = [
        str(exe_path),
        f"--run={tool_name}",
        f"--wd={work_dir}",
        "-v" if verbose else "-v=false",
        f"--compress_rasters={'true' if compress_rasters else 'false'}",
    ]
    command.extend(args)

    if verbose:
        version = _get_wbt_version(exe_path)
        print(f"WhiteboxTools version: {version}")
        print(" ".join(map(str, command)))

    try:
        process = subprocess.run(command, check=True, text=True, capture_output=True)
        if verbose:
            print(process.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Error output: {e.stdout}")
        raise RuntimeError(f"Error running tool: {e}") from e
    except Exception as e:
        raise Exception(f"Unexpected error: {e}")
```

Some example usage:

```python
whitebox_tools("BreachDepressionsLeastCost", ["-i=dem.tif", "-o=dem_corr.tif"])
```
