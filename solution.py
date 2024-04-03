import json
import math

#Class truck which we use to keep track of each Truck's individual stats
class Truck:
    def __init__(self):
        self.totalDist = 0
        self.dist = []
        self.city = 1
        self.packages = []
        self.size = 0
        self.deliveries = []

#Parse distance json file and store into dist variable
file = open('./json/distance.json',mode='r')
data = file.read() # read all lines at once
file.close() # close the file
dist = json.loads(data)

#Parse input json file and store into input variable
file = open('./json/input.json',mode='r')
data = file.read() # read all lines at once
file.close() # close the file
input = json.loads(data)

# list declarations used for management of truck paths and distaces
#   deliveries - List of cities that only recieve delieveries
#   cities - list of all cities including warehouses
#   warehourses - list of warehouse cities
#   days - list of working days
deliveries = ['Tilbury', 'Mississauga', 'Cornwall', 'London', 'Windsor', 'Niagara_Falls', 'Barrie', 'Kingston', 'Huntsville', 'North_Bay']
cities = ['Tilbury', 'Mississauga', 'Cornwall', 'London', 'Windsor', 'Niagara_Falls', 'Barrie', 'Kingston', 'Huntsville', 'North_Bay', "Goderich", "Toronto", "Picton"]
warehouses = ["Goderich", "Toronto", "Picton"]
days =  ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]

# Trucks list to store all trucks objects
#dailyDeliverables dictionary used to determine the total packages that need to be delievered on that day
trucks = []
dailyDeliverables = {"Monday": 0,"Tuesday": 0,"Wednesday": 0,"Thursday": 0,"Friday": 0,"Saturday": 0,"Sunday": 0}

# init dailyDeliverables by parsing through input data
for a in days:
    for b in deliveries:
        dailyDeliverables[a] += input[b][a]

# declare and init the number of trucks desired 
numTrucks = 20
for a in range(numTrucks):
    t = Truck()
    trucks.append(t)

# Additional output list and dictionary to format output into json
output = {"Total_cost": 0}
dict = {}

#The big loop that accounts for everything happening in a week
for day in days:
    curr = 0    #current location tracker (from 0-12 for all cities)

    #Distribute each package that needs to be delivered that day evenly among all trucks
    for b in range(dailyDeliverables[day]):
        while input[cities[curr]][day] == 0: #loop through the cities until one that has packages to be delivered to is found
            curr += 1
        trucks[b % numTrucks].packages.append(curr)
        trucks[b % numTrucks].size += 1
        
        input[cities[curr]][day] -= 1 #decrement the remaining packages to be distrubuted after it has been placed in a truck
    
    

    for count, a in enumerate(trucks):
        for b in a.packages:
            dict[count] = {b: a.packages.count(b)}
        a.packages = list(set(a.packages))


    #for each truck do the following:
    for count, a in enumerate(trucks): 
        d = 0
        
        #calculate the closest warehouse to the current truck's position 
        mini = 2000   
        for i in range(3):
            if dist[cities[a.city]][cities[10+i]] == "n/a": #if at warehouse stay there
                w_house = 10+i
                break
            d_initial = a.packages[0] if len(a.packages) > 0 else -1
            start_dist = dist[cities[a.city]][cities[10+i]] 
            if d_initial != -1:                                            #if truck has a delivery the next day take that into account when calculating 
                start_dist += dist[cities[10+i]][cities[d_initial]]        # which warehouse to go to
            if (start_dist < mini):
                w_house = 10+i
                mini = start_dist
        
  
        if dist[cities[a.city]][cities[w_house]] == "n/a": #if at a warehouse do not travel to it
            a.totalDist += 0                               #else go to nearest warehouse
        else:                                                       
            a.totalDist += dist[cities[a.city]][cities[w_house]] 
            d += dist[cities[a.city]][cities[w_house]]
            a.city = w_house
        removal = []
        for b in a.packages:                                    #for each package calculate if the next delovery will take too long
            if d + dist[cities[a.city]][cities[b]] > 1400:      #if so wait for next day to do 
                a.dist.append(d)
                d = 0
                continue
            d += dist[cities[a.city]][cities[b]]
            a.totalDist += dist[cities[a.city]][cities[b]]
            startQ = 0
            for c in dict[count]:
                startQ += dict[count][c]
            a.deliveries.append({"day": day,"startD": cities[a.city], "endD": cities[b], "dist": dist[cities[a.city]][cities[b]], "del_type": "drop_off", "startQ": startQ, "endQ": startQ - dict[count][b]})
            dict[count][b] = 0
            a.city = b
            removal.append(b)
        for b in removal:
            a.packages.remove(b)
        
        a.dist.append(d)

counter = 1
delC = 1

#Loop to collect and format all data into json
for t in trucks:                
    i = "Truck_" + str(counter)
    time = t.totalDist/100
    output[i] = {"Total_cost": format(300 + 0.68*t.totalDist + min(time,60)*20+max(time-60, 0)*30, ".2f")}
    for count, day in enumerate(days):
        output[i][day] = {"Total_time_driving": t.dist[count]/100,"Total_distance": t.dist[count],"Total_cost": format(0.68*t.dist[count] + min(t.dist[count]/100, 60)*20+max(t.dist[count]/100-60, 0)*30, ".2f")}
    for day in days:
        delC = 1
        currTime = 60*6
        sumTime = 0
        for a in t.deliveries:
            if a["day"] == day:
                if a["dist"] < 100:#in between 6 and 7
                    sumTime = (a["dist"]/100)*60
                elif a["dist"] > 100 and a["dist"] < 240: #in between 7-9
                    sumTime = 60+((a["dist"]-100)/70)*60
                elif a["dist"] < 940:
                    sumTime = ((a["dist"]-140)/100)*60+120#in 9 and 4:00
                elif a["dist"] > 940 and a["dist"] < 1080:
                    sumTime = ((a["dist"]-1080)*60)/70+10*60
                else:
                    sumTime = ((a["dist"]-1240)*60)/70
                output[i][day]["Delivery_" + str(delC)] ={
                    "Start_time":currTime,
                    "End_time":currTime + sumTime,
                    "Start_destination": a["startD"],
                    "End_destination": a["endD"],
                    "Distance": a["dist"],
                    "Delivery_type": a["del_type"],
                    "Start_quantity": a["startQ"],
                    "End_quantity": a["endQ"]}
                delC += 1
                currTime += sumTime
        

    counter += 1

json_object = json.dumps(output, indent=4)

        # Writing to sample.json
with open("./json/output.json", "w") as outfile:
    outfile.write(json_object)
    

dictionary = {

}

counter=0
for i in trucks:

    counter+=1
