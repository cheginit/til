# Connect to a remote JupyterLab server

Here are the steps for connecting to a remote Jupyter server on a cluster. Note that you need
to work with two terminals; One for running the remote server, and another for connecting to
the remote Jupyter server.

1. Open up the first terminal on your local machine and create a public SSH key
(change `your_email_address` with your own email address):

    ```bash
    EMAIL="your_email_address" && \
    ssh-keygen -t rsa -b 4096 -C "$EMAIL" -q -N "" -f ${HOME}/.ssh/id_rsa && \
    eval $(ssh-agent -s) && \
    ssh-add ~/.ssh/id_rsa
    ```

2. Add this key to the cluster (replace `your_cluster_id` and `cluster_url` with yours.
You will be prompted to enter your password after issuing these commands):

    ```bash
    USER_ID="your_cluster_id" && \
    CLUSTER="cluster_url" && \
    ssh-copy-id "${USER_ID}@${CLUSTER}"
    ```

3. SSH to the cluster:

    ```bash
    ssh -l "${USER_ID}" "${CLUSTER}"
    ```

4. Now, we need to add some lines to `~/.bash_profile` to running a Jupyter server:

    ```bash
    cat << 'EOF' >> ~/.bash_profile

    jlremote () {
        echo $(hostname) > ~/.jupyternode.txt
        XDG_RUNTIME_DIR= jupyter lab --no-browser --port=${1:-9753} --ip="$(hostname)"
    }

    EOF
    ```

5. Disconnect from the cluster by hitting `Ctrl+D`, then reconnect:

    ```bash
    ssh -l "${USER_ID}" "${CLUSTER}"
    ```

6. Request for an interactive session on the cluster, for example:

    ```bash
    srun --gpus=1 --mem=8GB -p gpu -t 01:00:00 --pty /bin/bash -l
    ```

7. After you got connected to a compute node, run a Jupyter server by simply running the
function that we defined earlier:

    ```bash
    jlremote
    ```

8. Make note of the token and leave this terminal open. You should see something like this:

    ```bash
    [USER_ID@compute-0-11 ~]$ jlremote
    [I 21:36:08.564 LabApp] JupyterLab extension loaded from jupyterlab
    [I 21:36:08.564 LabApp] JupyterLab application directory is lab
    [I 21:36:08.567 LabApp] Serving notebooks from local directory: /home/USER_ID
    [I 21:36:08.567 LabApp] The Jupyter Notebook is running at:
    [I 21:36:08.567 LabApp] http://compute-node.local:9753/?token=A_LONG_SEQUENCE_OF_CHARCTERS
    [I 21:36:08.567 LabApp] or http://127.0.0.1:9753/?token=THE_SAME_TOKEN_IS_SHOWN_HERE
    ```

9. Open up a second terminal on your local machine, and add a function for connecting to a
remote Jupyter server. Note that depending on your system setup you might need to change
`~/.bashrc`. First, check if you're using `bash` or `zsh` by running `echo $SHELL`. If the
output put is`zsh` then replace `~/.bashrc` with `~/.zshrc`. If the output is `bash` then
you can leave it as is unless you're using MacOSX which is that case you should replace
`~/.bashrc` with `~/.bash_profile`. Also replace `your_cluster_id` and `cluster_url` with
yours):

    ```bash
    cat << 'EOF' >> ~/.bashrc

    jllocal () {
        PORT=${1:-9753}
        USER_ID="your_cluster_id"
        HOST_URL="cluster_url"
        JUPY_NODE=$(ssh ${USER_ID}@${HOST_URL} 'tail -1 ~/.jupyternode.txt')
        JUPY_NODE=${JUPY_NODE//[$'\t\r\n ']}
        CMD="ssh -CNL ${PORT}:${JUPY_NODE}:${PORT} ${USER_ID}@${HOST_URL}"
        command -v open > /dev/null 2>&1 && OPEN=open
        command -v xdg-open > /dev/null 2>&1 && OPEN=xdg-open
        eval "$CMD" & \
        sleep 2 && eval "$OPEN http://localhost:$PORT"
    }

    EOF
    ```

10. Now close this terminal and open a new one to apply the changes. Then you can connect to the
Jupyter server by simply issuing the function that we just created:

    ```bash
    jllocal
    ```

11. This command opens a new tab in your browser. You might need to enter the remote server
token that you copied earlier.

You don't have to repeat these steps every time. Now that we created these helper functions,
there are only two steps:

1. Open the first terminal and type:

    ```bash
    ssh -l your_id cluster_ulr
    srun --gpus=1 --mem=8GB -p gpu -t 01:00:00 --pty /bin/bash -l
    jlremote
    ```

2. Open the second terminal and type:

    ```bash
    jllocal
    ```

Credits to [Ben Lindsay](https://benjlindsay.com/posts/running-jupyter-lab-remotely).
