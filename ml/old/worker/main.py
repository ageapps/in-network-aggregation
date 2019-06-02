from LinearRegressor import LinearRegressionUsingGD
import numpy as np

X = 2 * np.random.rand(100, 1)
Y = 4*X + np.random.randn(100, 1)

eta = 0.1
iterations = 100
print("Shape of input: ", X.shape)
print("Shape of output: ", Y.shape)
print("Iterations: ", iterations)


model = LinearRegressionUsingGD(eta=eta, n_iterations=iterations)

model.fit(X, Y)

model.plotCostAndData(True)
