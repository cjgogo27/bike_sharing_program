import numpy as np
import matplotlib.pyplot as plt
import math

def kolmogorov_forward_equation(mu,lam,capacity):
    s_min=0
    s_max=0
    t0 = 0.0
    tf = 180
    dt = 1/60
    total = 0
    Nt = int((tf-t0)/dt)

    for i in range(capacity):
        P0 = np.zeros((capacity))
        P0[i] = 1

        P = np.zeros((Nt+1, capacity))
        P[0] = P0
        total = rk4(P,capacity,t0,dt,Nt,mu,lam,'min')
        print("gi({},0,T) : {}".format(math.floor(i),total/(mu*Nt)))
        if total/(mu*Nt) >= 0.85 :
            s_min = i;
            break
    
    for i in reversed(range(capacity)):
        P0 = np.zeros((capacity))
        P0[i] = 1
        P = np.zeros((Nt+1, capacity))
        P[0] = P0
        total = rk4(P,capacity,t0,dt,Nt,mu,lam,'max')
        print("gi({},Ci,T) : {}".format(math.floor(i),total/(lam*Nt)))
        if total/(lam*Nt) >= 0.85 :
            s_max = i;
            break
        

    return (s_min,s_max)



# Define the discretized Kolmogorov forward equation
def kolmogorov_forward(P, t, capacity,mu,lam):
    dP = np.zeros_like(P)
    dP[0] = -lam*P[0] + mu*P[1]
    # dP[1] = mu*P[2] + lam*P[0] - lam*P[1] - mu*P[1] 
    # dP[2] = mu*P[3] + lam*P[1] - lam*P[2] - mu*P[2]
    for i in range(1,capacity):
        dP[i] = mu*P[i+1] + lam*P[i-1] - lam*P[i] - mu*P[i]
    dP[capacity] = lam*P[capacity-1] - mu*P[capacity]
    return dP

# Apply the fourth-order Runge-Kutta method
def rk4(P,capacity,t0,dt,Nt,mu,lam,type):
    for i in range(Nt):
        k1 = dt*kolmogorov_forward(P[i], t0 + i*dt,capacity-1,mu,lam)
        k2 = dt*kolmogorov_forward(P[i] + 0.5*k1, t0 + i*dt + 0.5*dt,capacity-1,mu,lam)
        k3 = dt*kolmogorov_forward(P[i] + 0.5*k2, t0 + i*dt + 0.5*dt,capacity-1,mu,lam)
        k4 = dt*kolmogorov_forward(P[i] + k3, t0 + i*dt + dt,capacity-1,mu,lam)
        P[i+1] = P[i] + (1/6)*(k1 + 2*k2 + 2*k3 + k4)

    result = np.zeros((Nt+1, capacity))
    total = 0
    if type == 'min':
        result = (1 - P[:,0])  
        for i in range(Nt):
            total+=result[i]*mu 
    else:
        result = (1 - P[:,capacity-1]) 
        for i in range(Nt):
            total+=result[i]*lam  
    return total



