import sys
from fetchdata import fetchdata
from datetime import datetime
from service_level import service_level
from draw import draw

class Agent:
    def __init__(self,start_date,end_date,start_time,end_time,area):
        self.start_date = int(start_date)
        self.end_date = int(end_date)
        self.start_time = datetime.strptime(start_time, '%H:%M:%S').time()
        self.end_time = datetime.strptime(end_time,"%H:%M:%S").time()
        self.targetarea=area.split(",")
        self.station_num = 0
        self.station_num=fetchdata(self.start_date,self.end_date,self.start_time,self.end_time,self.targetarea)

    def service_level_requirement(self):
        service_level(self.station_num)
        draw()

if __name__=='__main__':
    argc = len(sys.argv)

    agent = Agent(sys.argv[1],sys.argv[2],sys.argv[3],sys.argv[4],sys.argv[5])
    print(agent.station_num)
    if argc == 7:
        if sys.argv[6] == 'service':
            agent.service_level_requirement()  


             


    
    