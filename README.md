--Monte Carlo Portfolio Simulator--

This project is a Python-based Monte Carlo simulator I built to explore how investments might perform under uncertainty. 
It comes with a simple Tkinter GUI that makes it easy to tweak inputs and see results without touching the code. 
The backend simulation logic is handled in a separate module (Simulation_Core.py), while the GUI (MonteCarlo_GUI.py) takes care of user input and visualization.

--What it does--

Lets you choose between different simulation types:

Retirement – add contributions or withdrawals and see the probability of running out of money.

Single Stock – model the growth of a single asset over time.

Multi-Asset – simulate a portfolio with multiple correlated assets.

Plots hundreds of simulation paths, an average growth line, and a confidence band (5th–95th percentile).

Provides hover tooltips for exact year and value.

In retirement mode, calculates the chance of portfolio depletion and the average year it happens.

--How it works--

The core uses NumPy to generate random returns (lognormal distributions for single-asset, multivariate for multiple assets).
The GUI uses Matplotlib embedded in Tkinter to plot results interactively.

--How to run it-- 

Make sure you have Python 3 with numpy, matplotlib, and mplcursors installed. Then just run:

python MonteCarlo_GUI.py

--Preview--

<img width="1917" height="1127" alt="MonteCarloSimulation" src="https://github.com/user-attachments/assets/c55668ae-f0e0-4b0d-834e-54b8c801b9e1" />

