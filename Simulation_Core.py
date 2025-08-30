import numpy as np
from numpy.random import seed, normal, multivariate_normal

# random.seed(4)

def run_simulation(simulation_type, initial_investment, mean_return, volatility, years, simulations, assets, correlation, contribution):
    

    def draw_lognormal_returns(mu, sigma, size):
        """
        Generate lognormal gross return factors with expected mean return ~mu
        and volatility ~sigma.
        """
        mu_adj = np.log1p(mu) - 0.5 * sigma**2
        normal_draws = normal(mu_adj, sigma, size=size)
        return np.exp(normal_draws)

    if simulation_type == "single_stock":
        gross_returns = draw_lognormal_returns(mean_return, volatility, (simulations, years))
        portfolio = np.zeros((simulations, years+1))
        portfolio[:, 0] = initial_investment
        
        for t in range(1, years+1):
            portfolio[:, t] = portfolio[:, t-1] * gross_returns[:, t-1]

    elif simulation_type == "multi_asset":
        mean_vector = np.full(assets, mean_return)
        vol_vector = np.full(assets, volatility)
        
        corr_matrix = np.full((assets, assets), correlation)
        np.fill_diagonal(corr_matrix, 1.0)
        cov_matrix = np.outer(vol_vector, vol_vector) * corr_matrix
        
        gross_returns = np.zeros((simulations, years, assets))
        for t in range(years):
            normal_draws = multivariate_normal(
                np.log1p(mean_vector) - 0.5 * np.diag(cov_matrix),
                cov_matrix,
                size=simulations
            )
            gross_returns[:, t, :] = np.exp(normal_draws)
        
        weights = np.ones(assets) / assets
        portfolio = np.zeros((simulations, years+1))
        portfolio[:, 0] = initial_investment
        
        for t in range(1, years+1):
            weighted_returns = np.dot(gross_returns[:, t-1, :], weights)
            portfolio[:, t] = portfolio[:, t-1] * weighted_returns

    elif simulation_type == "retirement":
        gross_returns = draw_lognormal_returns(mean_return, volatility, (simulations, years))
        portfolio = np.zeros((simulations, years+1))
        portfolio[:, 0] = initial_investment
        
        for t in range(1, years+1):
            portfolio[:, t] = (portfolio[:, t-1] + contribution) * gross_returns[:, t-1]

    return portfolio
