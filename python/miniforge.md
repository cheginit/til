# Install and setup `miniforge`

[`miniforge`](https://github.com/conda-forge/miniforge) is a minimal installer for Conda specific
to conda-forge. It is comparable to Miniconda, but with:

* `conda-forge` set as the default channel
* An emphasis on supporting various CPU architectures
* Optional support for PyPy in place of standard Python (aka "CPython")
* Optional support for Mamba in place of Conda

First, install `miniforge`:

```bash
wget https://github.com/conda-forge/miniforge/releases/latest/download/Mambaforge-Linux-x86_64.sh
chmod +x Mambaforge-Linux-x86_64.sh
APP_DIR="~/.local/apps"
bash Mambaforge-Linux-x86_64.sh -b -p ${APP_DIR}/mambaforge
rm -f Mambaforge-Linux-x86_64.sh
```

Next, add the following lines to your shell `rc` file (e.g., `~/.zshrc`):

```bash
APP_DIR="~/.local/apps"

mmf () {
    __conda_setup="$('${APP_DIR}/mambaforge/bin/conda' 'shell.zsh' 'hook' 2> /dev/null)"
    if [ $? -eq 0 ]
    then
        eval "$__conda_setup"
    else
        if [ -f "${APP_DIR}/mambaforge/etc/profile.d/conda.sh" ]
        then
            . "${APP_DIR}/mambaforge/etc/profile.d/conda.sh"
        else
            export PATH="${APP_DIR}/mambaforge/bin:$PATH"
        fi
    fi
    unset __conda_setup
}

cac () {
    current_env="$CONDA_DEFAULT_ENV"
    command -v conda >/dev/null 2>&1 || mmf
    [[ $current_env != "base" ]] && conda deactivate
    conda activate $1
}

jp () {
    cac $1 && \
    cd ~/repos && \
    jupyter lab
}

alias mbu="mamba update -c conda-forge --strict-channel-priority --all"
alias mbi="mamba install -c conda-forge --strict-channel-priority"
alias mbf="mamba env create -f"
```

Upon reloading your shell, you can use `mbu` for update all the installed packages in the
current environment. Moreover, `mbi` install the specified package in the current environemnt,
and `mbf` creates a new environment from the specified `.yml` file.

Next, we can activate any existing environment using `cac`, for example, if we can activate
`dev` environment by issuing `cac dev`. Additionally, you can run an instance of Jupyter Lab
from `~/repos` directory with `dev` environment by `jp dev`.
