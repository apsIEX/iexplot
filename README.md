# IEXPLOT

## Creating a conda environment (optional)
	conda create --name iex_env python=3.8 ipykernel jupyterlab
	conda activate iex_env
	ipython kernel install --user --name=iex_env
	
## Installing iexplot 
### directly from git

	install git+https://github.com/apsIEX/iexplot.git

### so that you can edit and submit changes to the repo
	git clone https://github.com/apsIEX/iexplot
	cd iexplot
	pip install .


## Running your first example

    cd iexplot/examples
    
## TO-DO

* `iexplot.readMDA` does not work if verbose=1
