# About
This is a POC project for idea: ["English to Bengali phonetic transformation keyboard using Deep Learning" by Tusher]


# Dependencies
- This program uses NVidia Graphics Driver 384 or above &  CUDA 9.0 or above. ** Must export CUDA to PATH
- TensorFlow 1.12.0 or above

# Setting Up

- Ensure to export following symbols to local machine as well as remote machine (~/.bashrc file):
	'''
	export LC_ALL=en_US.UTF-8
	export LANG=en_US.UTF-8
	'''
	** Remember to run "source ~/.bashrc" after updating .bashrc file 
Recommended setup procedure-
- Install Anaconda first https://www.anaconda.com/
- Anaconda should create a virtual environment, something like this - https://virtualenv.pypa.io/en/latest/
- On that environment, install tensorflow CPU version - https://www.tensorflow.org/install/
- Open jupyter notebook from commandline in "Neural_Keyboard" directory - https://jupyter.org/
- A link in browser will open. This will be the default browser. Chrome is recommended. Firefox also works. But please, avoid IE
- The webpage will show a heirarchical file system. From there you can open "PCVersionTests.ipynb". That file contains everything

# Current Abstract work plan(Priority wise)
- Integrate the existing model with a web framework so that we can make REST calls to it(Flask or django)
- Build an android keyboard so that it can communicate with it
- Enrich Dataset
- Enhance the model for better accuracy

# Contact
If you are interested & want to contribute to the project in any form, please contact:
kowsertusher@gmail.com

