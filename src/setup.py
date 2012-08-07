# Installation script

from distutils.core import setup, Extension

setup(
      name='neat-python',
      version='0.1',
      description='A NEAT (NeuroEvolution of Augmenting Topologies) implementation',
      packages=['src/neat', 'src/neat/iznn', 'src/neat/nn', 'src/neat/ctrnn', 'src/neat/ifnn'],
      ext_modules=[
               Extension('src/neat/iznn/iznn_cpp', ['src/neat/iznn/iznn.cpp'], extra_compile_args=['-Wno-write-strings']),
               Extension('src/neat/nn/ann', ['src/neat/nn/nn_cpp/ANN.cpp', 'src/neat/nn/nn_cpp/PyANN.cpp'], extra_compile_args=['-Wno-write-strings']),
               Extension('src/neat/ifnn/ifnn_cpp', ['src/neat/ifnn/ifnn.cpp'], extra_compile_args=['-Wno-write-strings']),],
)
