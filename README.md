# IEXPLOT

## Creating a conda environment
	conda create --name iex_env python=3.8 ipykernel jupyterlab
	conda activate iex_env
	ipython kernel install --user --name=iex_env
	
## Installing iex plot
	git clone https://github.com/apsIEX/iexplot
	cd iexplot
	pip install .


## Running your first example

    cd iexplot/examples
    
## TO-DO

* `iexplot.readMDA` does not work if verbose=1
