
Installing iex plot
if you want to run in a new environment you can set it up by doing the following:
	conda create --name iex_env python=3.7
	conda activate iex_env
	python -m ipykernel install --user --name=iex_env

Note: if you want to use jupyterlab you may need to install it 
	#jupyter-lab
		pip install jupyterlab

install the latest version on GitHub
	python -m pip install -e git+https://github.com/apsIEX/iexplot#egg=iexplot 

Installing image tool 
install the latest version on GitHub
	python -m pip install -e git+https://github.com/kgord831/PyImageTool#egg=PyImageTool

Running jupiter
	cd path/to/your/working_directory (where you want to save the notebooks)
	jupyter-lab 
