import pandas as pd
import numpy as np
from haversine import haversine,Unit
from mip import Model, xsum, minimize, BINARY,INTEGER,ConstrList,maximize
import matplotlib.pyplot as plt


vehicle_num = 2
truck_capacity = 14

df = pd.read_csv('data/service_level_result.csv').drop(columns=["Unnamed: 0"]).astype(int)
station = pd.read_csv('data/station_info.csv')


df.drop(df[(df["smin"]==0)&(df["smax"]==0)].index,inplace=True)
df.reset_index(inplace=True,drop=True)

s_plus = np.zeros(len(df))
s_minus = np.zeros(len(df))
spluslist = list(df["smin"]-df["start"])
sminuslist = list(df["start"]-df["smax"])

for i in range(len(df)):
    s_plus[i] = max(spluslist[i],0)
    s_minus[i] = max(sminuslist[i],0)

insufficent = (df["start"]<df["smin"]) | (df["start"]>df["smax"])
time_interval = insufficent

start = list(df["start"])
smin = list(df["smin"])
smax = list(df["smax"])


# initial inventory
q = np.zeros((vehicle_num))
# truck capacity
Qv = truck_capacity

station = station[station['id'].isin(list(df['id']))]

station.reset_index(inplace=True,drop=True)


S = set(df.index)
N = S.copy()
N.add(-1)

distance_matrix = np.zeros((len(S),len(S)))

for row in range(len(S)):
    for col in range(row,len(S)):
        if row == col:
            distance_matrix[row][col]=0
        else:
            coords_1 = (station.loc[row]["lat"],station.loc[row]["lng"])
            coords_2 = (station.loc[col]["lat"],station.loc[col]["lng"])
            distance_matrix[row][col] = haversine(coords_1,coords_2)*1000
            distance_matrix[col][row] = haversine(coords_1,coords_2)*1000

d_minus = 357
d_plus = 357



model = Model()

h = [model.add_var(var_type= INTEGER)for v in range(vehicle_num)]
z = [[model.add_var(var_type= BINARY) for i in range(len(S))] for v in range(vehicle_num)] 

total=0


    
for i in df[insufficent].index:
    model += xsum(z[v][i] for v in range(vehicle_num)) == 1

for i in df[~insufficent].index:
    model += xsum(z[v][i] for v in range(vehicle_num)) <= 1

for v in range(vehicle_num):
    model += (q[v]+xsum(start[i]*z[v][i] for i in range(len(S))) >= xsum(smin[i]*z[v][i] for i in range(len(S))))
    model += (-(Qv-q[v])+xsum(start[i]*z[v][i] for i in range(len(S))) <= xsum(smax[i]*z[v][i] for i in range(len(S))))
    
for v in range(vehicle_num):
    for i in range(len(S)):
        model += h[v] >= xsum(distance_matrix[i][j] * (z[v][i]+z[v][j]-1) for j in range(len(S)))+xsum((d_plus*s_plus[j]+d_minus*s_minus[j])*z[v][j] for j in range(len(S)))
        model += h[v] >= xsum(distance_matrix[i][j] * (z[v][i]+z[v][j]-1) for j in range(len(S)))+xsum((d_plus*s_plus[j]+d_minus*s_plus[j])*z[v][j] for j in range(len(S)))-d_minus*q[v]
        model += h[v] >= xsum(distance_matrix[i][j] * (z[v][i]+z[v][j]-1) for j in range(len(S)))+xsum((d_plus*s_minus[j]+d_minus*s_minus[j])*z[v][j] for j in range(len(S)))-d_plus*(Qv-q[v])

H = maximize(h[0])+maximize(h[1])

model.objective = minimize(H)

model.optimize()




vehicle1_cluster=[]
vehicle2_cluster=[]

for i in range(len(S)):
    if z[0][i].x==1:
        vehicle1_cluster.append(i)
    if z[1][i].x==1:
        vehicle2_cluster.append(i)

variable_values = [v.x for v in model.vars]

    # Iterate over the variable values and print the index and corresponding value
for i, value in enumerate(variable_values):
    print("Variable index:", i, "Value:", value)
vehicle1_cluster_df = station.loc[vehicle1_cluster]

vehicle1_cluster_df.drop_duplicates(inplace = True)

vehicle2_cluster_df = station.loc[vehicle2_cluster]
vehicle2_cluster_df.drop_duplicates(inplace = True)


fig, (ax1, ax2) = plt.subplots(1, 2)

ax1.scatter(x=vehicle1_cluster_df['lng'], y=vehicle1_cluster_df['lat'])
ax1.scatter(x=vehicle2_cluster_df['lng'], y=vehicle2_cluster_df['lat'])


result = np.load("data/np_save.npy")   

check = result[0][0][0][0]
check2 = result[1][0][0][0]
#np shape(vehicle num, time interval, drop & pickup, arc)
for i in range(len(result[0])):
    if result[0][i][0][0]!=0 and result[0][i][0][1]!=0:
        check = np.concatenate((check,result[0][i][0][1]),axis=None)
    if result[1][i][0][0]!=0 and result[1][i][0][1]!=0:
        check2 = np.concatenate((check2,result[1][i][0][1]),axis=None)



vehicle1_noncluster_df = station.loc[check]
vehicle1_noncluster_df.drop_duplicates(inplace = True)
vehicel1_station_condition = df.loc[vehicle1_cluster]

vehicle2_noncluster_df = station.loc[check2]
vehicle2_noncluster_df.drop_duplicates(inplace = True)
vehicel2_station_condition = df.loc[vehicle1_cluster]


vehicle1_cluster_df.reset_index(inplace=True,drop=True)
vehicel1_station_condition.reset_index(inplace=True,drop=True)
print(vehicle1_cluster_df)
print(vehicel1_station_condition)


time_interval = len(vehicle1_cluster_df)
vehicle_num=1
q = np.zeros(1)
    # truck capacity
Qv = truck_capacity

S = set(vehicle1_cluster_df.index)
N = S.copy()
N.add(-1)

distance_matrix = np.zeros((len(S),len(N)))

for row in range(len(S)):
    for col in range(row,len(N)):
        if row == col:
            distance_matrix[row][col]=0
        else:
            if col == len(N)-1:
                distance_matrix[row][col] = 0
            else:
                coords_1 = (vehicle1_cluster_df.loc[row]["lat"],vehicle1_cluster_df.loc[row]["lng"])
                coords_2 = (vehicle1_cluster_df.loc[col]["lat"],vehicle1_cluster_df.loc[col]["lng"])
                distance_matrix[row][col] = haversine(coords_1,coords_2)*1000
                distance_matrix[col][row] = haversine(coords_1,coords_2)*1000

model = Model()
h =0
x = [[[[model.add_var(var_type = BINARY) for i in range(len(S))]for j in range(len(N))]for t in range(time_interval)]for v in range(vehicle_num)]
y_plus = [[[model.add_var(var_type = INTEGER) for i in range(len(S))]for t in range(time_interval)]for v in range(vehicle_num)]
y_minus = [[[model.add_var(var_type = INTEGER) for i in range(len(S))]for t in range(time_interval)]for v in range(vehicle_num)]

for v in range(vehicle_num):
    h += (xsum(distance_matrix[i][j]*x[v][t][i][j] for i in range(len(S)) for j in range(len(S)) for t in range(time_interval))
        +xsum(d_minus*y_minus[v][t][i] for i in range(len(S)) for t in range(time_interval))
        +xsum(d_plus*y_plus[v][t][i] for i in range(len(S)) for t in range(time_interval)))

model.objective = minimize(h)
    #model constraint

for i in range(len(S)):
    model += (xsum(y_plus[v][t][i]-y_minus[v][t][i] for t in range(time_interval) for v in range(vehicle_num))+vehicel1_station_condition.loc[i]["start"])>= vehicel1_station_condition.loc[i]["smin"]
    model += (xsum(y_plus[v][t][i]-y_minus[v][t][i] for t in range(time_interval) for v in range(vehicle_num))+vehicel1_station_condition.loc[i]["start"])<= vehicel1_station_condition.loc[i]["smax"]

for v in range(vehicle_num):
    model += xsum(x[v][0][j][i] for i in range(len(S)) for j in range(len(N))) <=1

for i in range(len(S)):
    for t in range(1,time_interval):
        for v in range(vehicle_num):
            model += xsum(x[v][t][j][i] for j in range(len(N))) <= xsum(x[v][t-1][i][j] for j in range(len(S)))

model += xsum(x[v][t][i][i] for i in range(len(S)) for t in range(time_interval) for v in range(vehicle_num)) == 0  

for v in range(vehicle_num):
    for t in range(time_interval):
        for i in range(len(S)):        
            model += (xsum(x[v][t][j][i] for j in range(len(N)))*Qv) >= y_minus[v][t][i]
            model += (xsum(x[v][t][i][j] for j in range(len(S)))*Qv) >= y_plus[v][t][i]

for i in range(len(S)):
    model += xsum(y_minus[v][t][i] for t in range(time_interval) for v in range(vehicle_num)) <= vehicel1_station_condition.loc[i]["start"]
    model += xsum(y_plus[v][t][i] for t in range(time_interval) for v in range(vehicle_num)) <= vehicel1_station_condition.loc[i]["capacity"] - vehicel1_station_condition.loc[i]["start"]

for v in range(vehicle_num):
    for g in range(time_interval):
        model += (xsum(y_minus[v][t][i] - y_plus[v][t][i]for i in range(len(S)) for t in range(g+1)) + q[v])>=0
        model += (xsum(y_minus[v][t][i] - y_plus[v][t][i]for i in range(len(S)) for t in range(g+1)) + q[v])<=Qv


model.optimize()



for t in range(time_interval):
    for i in range(len(S)):
        for j in range(len(S)):
            if x[0][t][j][i].x!= False:
                print("vehicle_num : {} time_interval : {} arc i{} to j{}".format(0,t,i,j))
                if(y_plus[0][t][i].x!=0):
                    print("vehicle_num : {} time_interval : {} station : {} drop_off : {}".format(0,t,i,y_plus[0][t][i].x))
                    #vehicle drop off amount at time interval t and station i
                if(y_minus[0][t][i].x!=0):
                    print("vehicle_num : {} time_interval : {} station : {} pick_up : {}".format(0,t,i,y_minus[0][t][i].x))
                if(y_plus[0][t][j].x!=0):
                    print("vehicle_num : {} time_interval : {} station : {} drop_off : {}".format(0,t,j,y_plus[0][t][j].x))
                    #vehicle drop off amount at time interval t and station i
                if(y_minus[v][t][j].x!=0):
                    print("vehicle_num : {} time_interval : {} station : {} pick_up : {}".format(0,t,j,y_minus[0][t][j].x))

ax2.scatter(x=vehicle1_noncluster_df['lng'], y=vehicle1_noncluster_df['lat'])
ax2.scatter(x=vehicle2_noncluster_df['lng'], y=vehicle2_noncluster_df['lat'])

ax2.set_xticks([])
ax2.set_yticks([])
ax1.set_xticks([])
ax1.set_yticks([])

ax1.set_title('cluster')
ax1.set_xlabel("longitude")
ax1.set_ylabel("latitude")

ax2.set_title('non cluster')
ax2.set_xlabel("longitude")
ax2.set_ylabel("latitude")

plt.tight_layout()
plt.show()
