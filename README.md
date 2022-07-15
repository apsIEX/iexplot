# IEXPLOT

## Installing iex plot


	conda create --name iex_env python=3.8 ipykernel jupyterlab
	conda activate iex_env

    git clone https://github.com/apsIEX/iexplot
    cd iexplot
    pip install .

## Installing image tool 

    git clone https://github.com/kgord831/PyImageTool
    cd iexplot
    pip install .

## Running your first example

    cd iexplot/examples
    
## TO-DO

* `iexplot.readMDA` does not work if verbose=1