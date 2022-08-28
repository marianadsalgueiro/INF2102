# Busc@PUC

## FLASK

All commands must be executed in the command line or anaconda command line (windows). All commands should be executed inside the project folder unless stated otherwise.

# Environment 

## Create 
```
conda create --name buscapuc python
```
## Activate

### Linux
```
source activate 
```

### Windows
```
activate quempuc
```

## Install packages (after activating the environment)

```
pip install -r requirements.txt
```

# Configuring development environment variables

## Linux

```
export FLASK_APP=run.py
export FLASK_CONFIG=development
```

## Windows

```
SET FLASK_APP=run.py
SET FLASK_CONFIG=development
SET AGRAPH_HOST=localhost
SET AGRAPH_PORT=(inserirAquiAPortaDoAllegro)
SET AGRAPH_USER=(inserirAquiOUserDoAllegro)
SET AGRAPH_PASSWORD=(inserirAquiOPasswordDoAllegro)
```

# Run in development

```
flask run
```