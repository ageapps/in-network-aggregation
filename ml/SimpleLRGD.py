# coding: utf-8

# # Linear Regression with GD

# very usefull tutorial from https://towardsdatascience.com/step-by-step-tutorial-on-linear-regression-with-stochastic-gradient-descent-1d35b088a843

# In[2]:


import numpy as np
import matplotlib.pyplot as plt


# ## Model

# In[3]:


class Linear(object):

    def __init__(self, in_size, out_size, bias=True):
        self.in_size = in_size
        self.out_size = out_size
        # Initial values of the weights
        self.x = np.array([])
        self.x_b = np.array([])
        self.bias = bias
        if self.bias:
            self.in_size += 1
        self.w = np.random.randn(self.in_size, self.out_size)
        print("W ", self.w.shape)

    def update(self, params):
        self.w = params[0]

    def forward(self, X):
        self.x = X
        if self.bias:
            self.x_b = np.c_[X, np.ones((len(X), 1))]
        else:
            self.x_b = X
        
        # print("X_b ", self.x_b.shape)
        #print("Shape of w ", self.w.shape)
        return np.dot(self.x_b, self.w)

    def backward(self):
        return self.x_b

    def params(self):
        return [self.w]


# ## Cost

# In[5]:


class LossMSE(object):

    def __init__(self):
        self.y_t = np.array([])
        self.y_p = np.array([])
        self.L = np.array([])
        self.m = 0

    def cost(self, predicted, target):
        self.m = target.shape[1]
        self.y_t = target
        self.y_p = predicted
        self.L = (1/(2*self.m))*np.sum(np.square(self.y_p-self.y_t))
        return self.L

    def backward(self, input):
        dY = (1/self.m)*(self.y_p-self.y_t)
        dLdw = np.dot(input.T,dY)
        # print("Shape of dLdw: ", dLdw.shape)
        return [dLdw]


# ## Training


# In[311]:

def trainGD(model, X, Y):
    cost_history = np.zeros(iterations)
    #X_b = np.c_[X,np.ones((len(X),1))]
    X_b = X
    for i in range(iterations):
        # forward pass, get prediction
        y_pred = model.forward(X_b)
        # calculate cost
        cost_history[i] = optim.cost(y_pred, Y)
        # update weights, backward prop
        params = model.params()
        backwards = optim.backward(model.backward())
        updates = []
        for y in range(len(params)):
            param = params[y]
            backward = backwards[y]
            new = param - eta*backward
            updates.append(new)

        model.update(updates)
        if i % 10 == 0:
            print("Iter: {} Cost:{}".format(i, cost_history[i]))
    return cost_history


# In[297]:


def trainBatchGD(model, X, Y, batch_size=5):
    cost_history = []

    for i in range(iterations):
        cost = 0.0
        for b in range(0, X.shape[0], batch_size):
            X_i = X[b:b+batch_size]
            Y_i = Y[b:b+batch_size]

            # forward pass, get prediction
            y_pred = model.forward(X_i)
            # calculate cost
            cost += optim.cost(y_pred, Y_i)

            # update weights, backward prop
            params = model.params()
            backwards = optim.backward(model.backward())
            updates = []
            for y in range(len(params)):
                param = params[y]
                backward = backwards[y]
                new = param - eta*backward
                updates.append(new)

            model.update(updates)

        cost_history.append(cost)
        if i % 10 == 0:
            print("Iter: {} Cost:{}".format(i, cost))

    return cost_history



# In[314]:


def plotCostAndData(cost_b,X,Y,model):
    plotOutput = X.shape[1] == 1 and Y.shape[1] == 1
    if plotOutput:
        fig, ax = plt.subplots(1, 2, figsize=(20, 8))
        cost_ax = ax[0]

    else:
        fig, cost_ax = plt.subplots(1, 1, figsize=(20, 8))

    # Plot Cost
    cost_ax.set_ylabel('Cost')
    cost_ax.set_xlabel('Iterations')
    _ = cost_ax.plot(range(iterations), cost_b, 'b.')

    if plotOutput:
        #X_b = np.c_[X,np.ones((len(X),1))]
        pred = model.forward(X)
        # Plot original data
        _ = ax[1].plot(X, Y, 'b.')
        # Plot regression line
        _ = ax[1].plot(X, pred, 'r-')
    
    fig.savefig('myfilename.png')


# In[6]:


X = 2 * np.random.rand(100, 2)
Y = 4 + 3 * X+np.random.randn(100, 1)

# In[297]:

optim = LossMSE()
eta = 0.001
iterations = 100
print("Shape of input: ", X.shape)
print("Shape of output: ", Y.shape)
print("Iterations: ", iterations)


model = Linear(X.shape[1], Y.shape[1], bias=True)
cost = trainGD(model, X, Y)
# cost_b = trainBatchGD(model, X, Y)

plotCostAndData(cost,X,Y,model)



#%%
