# BrewER Reproduction on Chameleon Trovi

## Repository Version (Pinned)
This artifact is pinned to commit `e33ee84`

## Overview
This repository contains the artifact for the Chameleon Trovi project, including the code and instructions for replicating experiments using a remote Chameleon compute node. Its primary purpose is to:

Demonstrate how our Trovi method works on Chameleon infrastructure.

Show how to connect and run code on a remote high-performance instance.

Provide an example notebook and scripts for practical usage.

Note: Running the provided Jupyter notebook directly through Chameleon’s UI is not recommended, as the interactive UI has limited memory and slower performance. Instead, we connect from a local machine to a remote Chameleon server via SSH, and run the notebook remotely.

### Repository Structure
```text
trovi_BrewER/
│── BrewER_reproduction.ipynb     # Notebook showing the experiment
│── my_key.pem                    # Your SSH private key for authentication
│── README.md                    # This documentation
│── silent_eval.py               # Utility script for model evaluation
```
* **BrewER_reproduction.ipynb**: The main notebook that loads data/models and runs the Trovi pipeline.
* **my_key.pem**: Your SSH private key file (not included by default; you must create it).
* **silent_eval.py**: A helper script used by the notebook for evaluations.


## Jupyter Notebook Overview
The core of this repository is the `BrewER_reproduction.ipynb` notebook.

It is structured into the following sections:

1. **Environment Setup**  
   Installs dependencies and configures paths on the remote machine.

2. **Chameleon Server Connection**  
   Establishes secure SSH-based access using your private key and prepares the remote execution environment.

3. **Data Loading & Preprocessing**  
   Loads the datasets and models required by the BrewER pipeline.

4. **Trovi Method Execution**  
   Runs the Trovi-based training and evaluation workflow and benchmarks results.

5. **Evaluation and Output**  
   Executes evaluation code and generates logs and plots.

6. **Remote Cleanup and Teardown**  
   Stops any running Jupyter servers or background processes on the remote instance and explains how to properly exit the SSH session and terminate the compute instance to avoid unnecessary resource usage.


> **Important**: You won’t start the notebook via Chameleon’s internal Jupyter interface or your local machine. Instead, you'll connect to the remote instance using SSH + your key, then start the notebook server on the remote machine.

## Remote Execution Workflow
Chameleon’s interactive notebook environment has limits on memory, CPU, and GPU availability, thus running heavy experiments there may fail. Instead, we:
1. SSH into a powerful instance
2. Launch Jupyter inside the instance
3. Connect the remote server notebook to our local browser

This approach ensures better performance and full control.

### SSH Key Pair Requirement
To securely connect your local machine to a Chameleon compute instance, you must generate an **SSH key pair**:
1. In the Chameleon dashboard, go to the `Key Pairs` tab under `Compute` tab.
2. Click `Create Key Pair`. 

![panel](start_panel.png)

3. Enter a name and choose `SSH Key` as the key type. In the notebook code, we default to using the key pair named “my_key”. You can also name your key my_key for convenience, otherwise you will need to update the key name in the code to match your chosen name.

![create key](create.png)

4. Click `Create KeyPair`

5. A `private key` file will be shown once, save it immediately! In the repository, you save the private key as `my_key.pem`.

![private key](private_key.png)

> Important:
> * The dashboard only shows the private key once. If you lose it, Chameleon cannot recover it.
> * In our code, when we prepare to connect to a remote Chameleon instance, we explicitly select and attach the public SSH key (identified by the key-pair name, e.g., `my_key`) to the target compute instance. This step installs the public key on the remote machine and registers it in the instance’s authorized SSH keys. 
> * This explicit key attachment ensures that the remote instance will accept SSH connections associated with the selected key pair.
> * The private key remains on your local machine or Jupyter interface (stored as `my_key.pem`) and is used by the SSH client to authenticate against the remote instance.
> * Always keep your private key safe, never share it.


This SSH tunnel allows:
* Launching Jupyter Notebook remotely
* Transferring data
* Running experiments without manual login

Check the **Key Pair** section in the [Documentation](https://chameleoncloud.readthedocs.io/en/latest/getting-started/) for more details. 


### SSH connection

Here is an example ssh command that restrict key permissions and connect us securely to the remote machine. 

```bash
chmod 600 my_key.pem

ssh -i my_key.pem your_username@remote_ip_address

```

In the notebook, we do the same via Python code so that everything is automated.
