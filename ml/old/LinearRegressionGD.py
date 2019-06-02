
# coding: utf-8

# # Linear Regression with GD

# very usefull tutorial from https://towardsdatascience.com/step-by-step-tutorial-on-linear-regression-with-stochastic-gradient-descent-1d35b088a843

# In[311]:


import numpy as np
import matplotlib
matplotlib.use('TkAgg')

import matplotlib.pyplot as plt


# ## Data

# In[341]:

X = 2 * np.random.rand(100,1)
Y = 4 +3 * X+np.random.randn(100,1)


# ## Model 

# In[401]:


class Linear(object):
    
    def __init__(self, in_size, out_size):
        self.in_size = in_size
        self.out_size = out_size
        # Initial values of the weights
        self.w = np.random.randn(self.in_size+1, self.out_size)
        
    def forward(self,X):
        self.x = X
        # add the bias to the input
        self.x_b= np.c_[np.ones((len(X), 1)), X]
        return np.dot(self.x_b,self.w)
    
    def backward(self):
        return self.x_b


# ## Cost

# In[343]:


class LossMSE(object):
    
    def __init__(self):
        self.y_t = np.array([])
        self.y_p = np.array([])
        self.L = np.array([])

    def cost(self,predicted, target):
        self.y_t = target
        self.y_p = predicted
        self.L = 0.5*np.sum(np.square(self.y_t-self.y_p))
        return self.L
    
    def backward(self, input):
        dL = - np.dot(input,(self.y_t-self.y_p))
        return dL


# ## Training

# In[402]:


model = Linear(X.shape[1],1)
optim = LossMSE()
eta=0.01
iterations = 200


# In[403]:


def trainGD(model, X, Y):
    cost_history = np.zeros(iterations)
    for i in range(iterations):
        # forward pass, get prediction
        y_pred = model.forward(X)
        # calculate cost
        cost_history[i] = optim.cost(y_pred,Y)
        # update weights, backward prop
        model.w = model.w - (1/len(Y))*eta*optim.backward(model.backward().T)
        if i%10==0:
            print("Iter: {} Cost:{}".format(i,cost_history[i]))
    return cost_history
    


# In[394]:


def trainBatchGD(model, X, Y, batch_size=5):
    cost_history = []
    
    for i in range(iterations):
        cost = 0.0
        for b in range(0,X.shape[0],batch_size):            
            X_i = X[b:b+batch_size]
            Y_i = Y[b:b+batch_size]

            # forward pass, get prediction
            y_pred = model.forward(X_i)            
            # calculate cost
            cost += optim.cost(y_pred,Y_i)
            model.w = model.w - (1/len(Y_i))*eta*optim.backward(model.backward().T)
            
            
        cost_history.append(cost)
        if i%10==0:
           print("Iter: {} Cost:{}".format(i,cost))
             
    return cost_history
    


# In[405]:


# cost = trainGD(model,X,Y)
cost = trainBatchGD(model,X,Y, batch_size=10)


# In[407]:


fig,ax = plt.subplots(1,2, figsize=(20,8))

# Plot Cost
ax[0].set_ylabel('Cost')
ax[0].set_xlabel('Iterations')
_=ax[0].plot(range(iterations),cost,'b.')

#X_b = np.c_[X,np.ones((len(X),1))]
pred = model.forward(X)
# Plot original data
_ = ax[1].plot(X,Y,'b.')
# Plot regression line
_ = ax[1].plot(X,pred,'r-')

fig.savefig('myfilename.png')
