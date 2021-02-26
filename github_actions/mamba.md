# Speed up Github Actions with `mamba`

[Mamba](https://github.com/mamba-org/mamba) is a reimplementation of the conda package manager
in C++. I use [setup-miniconda](https://github.com/conda-incubator/setup-miniconda)
workflow for creating Python environment in Github Actions. Recently, this workflow
added support for `mamba`. Here's how you can use it in combination with caching
to speedup your CI:

```yaml
on: [push, pull_request]

name: CI

jobs:
  test:
    name: python ${{ matrix.python-version }}, ${{ matrix.os }}
    runs-on: ${{ matrix.os }}
    defaults:
      run:
        shell: bash -l {0}
    strategy:
      matrix:
        python-version: [3.6, 3.7, 3.8, 3.9]
        os: [ubuntu-latest, macos-latest, windows-latest]
        exclude:
            - os: windows-latest
              python-version: 3.6

    steps:
      - name: Cancel Previous Runs
        uses: styfle/cancel-workflow-action@0.6.0
        with:
          access_token: ${{ github.token }}
      - uses: actions/checkout@master
      - name: Set environment variables
        run: |-
          echo "CONDA_ENV_FILE=ci/requirements/environment.yml" >> $GITHUB_ENV
          echo "PYTHON_VERSION=${{ matrix.python-version }}" >> $GITHUB_ENV
      - name: Cache conda
        uses: actions/cache@v2
        with:
          path: ~/conda_pkgs_dir
          key:
            ${{ runner.os }}-conda-py${{ matrix.python-version }}-${{
            hashFiles('ci/requirements/environment.yml') }}
      - name: Setup conda
        uses: conda-incubator/setup-miniconda@v2
        with:
          channels: conda-forge
          channel-priority: strict
          mamba-version: "*"
          activate-environment: hydrodata-tests
          auto-update-conda: false
          python-version: ${{ matrix.python-version }}
          use-only-tar-bz2: true
      - name: Install conda dependencies
        run: |-
          mamba env update -f $CONDA_ENV_FILE
```
