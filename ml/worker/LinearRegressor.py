import numpy as np
import matplotlib.pyplot as plt


class LinearRegressionUsingGD:
    """Linear Regression Using Gradient Descent.
    Parameters
    ----------
    eta : float
        Learning rate
    n_iterations : int
        No of passes over the training set
    Attributes
    ----------
    w_ : weights/ after fitting the model
    cost_ : total error of the model after each iteration
    """

    def __init__(self, eta=0.01, n_iterations=1000):
        self.eta = eta
        self.epochs = n_iterations

    def fit(self, x, y, batch_size=0):
        """Fit the training data
        Parameters
        ----------
        x : array-like, shape = [n_samples, n_features]
            Training samples
        y : array-like, shape = [n_samples, n_target_values]
            Target values
        Returns
        -------
        self : object
        """
        self.cost = []
        n_samples = x.shape[0]
        n_features = x.shape[1]
        n_out_classes = y.shape[1]

        if batch_size == 0:
            batch_size = n_samples

        print("Number of samples:", n_samples)
        print("Number of features:", n_features)
        print("Number of out classes:", n_out_classes)
        print("Epochs:", self.epochs)

        # stack bias into X and w
        self.w = np.random.randn(n_features + 1, n_out_classes)

        m = x.shape[0]

        self.x = x
        self.y = y
        print("W:", self.w.shape)
        print("X:", x.shape)

        for i in range(self.epochs):
            acc_cost = 0.0
            # batch training
            for b in range(0, x.shape[0], batch_size):
                x_i = x[b:b+batch_size]
                y_i = y[b:b+batch_size]

                y_pred = self.predict(x_i)
                dY = y_pred - y_i
                acc_cost += 1/(2 * m) * np.sum(np.square(dY))

                dLdw = self.get_gradient(i, x_i, dY)
                self.w -= (self.eta / m) * dLdw
            
            self.cost.append(acc_cost)
            if i % 10 == 0:
                print("Iter: {} Cost:{}".format(i, acc_cost))

        return self

    
    def get_gradient(self, i, dYdw, dY):
        """ Get gradient given dYdw=x and dY=(y_p-y)
        """
        x_b = np.c_[dYdw, np.ones((len(dYdw), 1))]
        return np.dot(x_b.T, dY)


    def predict(self, x):
        """ Predicts the value after the model has been trained.
        Parameters
        ----------
        x : array-like, shape = [n_samples, n_features]
            Test samples
        Returns
        -------
        Predicted value
        """
        x_b = np.c_[x, np.ones((len(x), 1))]
        return np.dot(x_b, self.w)

        """ Plots the cost
        """

    def plotCostAndData(self, s=False):
        X = self.x
        Y = self.y
        plotOutput = X.shape[1] == 1 and Y.shape[1] == 1
        if plotOutput:
            fig, ax = plt.subplots(1, 2, figsize=(20, 8))
            cost_ax = ax[0]
        else:
            fig, cost_ax = plt.subplots(1, 1, figsize=(10, 8))

        # Plot Cost
        cost_ax.set_ylabel('Cost')
        cost_ax.set_xlabel('Iterations')
        _ = cost_ax.plot(range(self.epochs), self.cost, 'b-')

        if plotOutput:
            print("Ploting")
            #X_b = np.c_[X,np.ones((len(X),1))]
            pred = self.predict(X)
            # Plot original data
            _ = ax[1].plot(X, Y, 'b.')
            # Plot regression line
            _ = ax[1].plot(X, pred, 'r-')
        if s:
            fig.savefig('figure.png')

