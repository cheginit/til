# Run Jupyter Lab as an Application

You can run Jupyter Lab as an applicaton using application mode of Chrome as follows:

```bash
jupyter lab --no-browser /dev/null 2>&1 & \
sleep 2 && \
google-chrome --app="$(jupyter lab list 2>&1 | tail -1 | awk -F '::' '{print $1}')"
```

Alternatively, you can add the following line to your Jupyter Lab config file
e.g., `~/.jupyter/jupyter_lab_config.py`:

```bash
c.LabApp.browser = 'google-chrome --app=%s'
```

Credits to [Christopher Roach](http://christopherroach.com/articles/jupyterlab-desktop-app/).
