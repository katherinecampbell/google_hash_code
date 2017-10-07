import numpy as np
from copy import deepcopy
import random

def read_google(filename):
    data = dict()
    with open(filename, "r") as fin:

        system_desc = next(fin)
        number_of_videos, number_of_endpoints, number_of_requests, number_of_caches, cache_size= system_desc.split(" ")
        number_of_videos = int(number_of_videos)
        number_of_endpoints = int(number_of_endpoints)
        number_of_requests = int(number_of_requests)
        number_of_caches = int(number_of_caches)
        cache_size = int(cache_size)
        video_ed_request = dict()
        video_size_desc = next(fin).strip().split(" ")
        for i in range(len(video_size_desc)):
            video_size_desc[i] = int(video_size_desc[i])
        ed_cache_list = []

        ### CACHE SECTION

        ep_to_cache_latency = [] 

        ep_to_dc_latency = [] 
        for i in range(number_of_endpoints):
            ep_to_dc_latency.append([])
            ep_to_cache_latency.append([])

            dc_latency, number_of_cache_i = next(fin).strip().split(" ")
            dc_latency = int(dc_latency)
            number_of_cache_i = int(number_of_cache_i)

            ep_to_dc_latency[i] = dc_latency

            for j in range(number_of_caches):
                ep_to_cache_latency[i].append(ep_to_dc_latency[i])

            cache_list = []
            for j in range(number_of_cache_i):
                cache_id, latency = next(fin).strip().split(" ")
                cache_id = int(cache_id)
                cache_list.append(cache_id)
                latency = int(latency)
                ep_to_cache_latency[i][cache_id] = latency

            ed_cache_list.append(cache_list)

        ### REQUEST SECTION
        for i in range(number_of_requests):
            video_id, ed_id, requests = next(fin).strip().split(" ")
            video_ed_request[(video_id,ed_id)] = requests


    data["number_of_videos"] = number_of_videos
    data["number_of_endpoints"] = number_of_endpoints
    data["number_of_requests"] = number_of_requests
    data["number_of_caches"] = number_of_caches
    data["cache_size"] = cache_size
    data["video_size_desc"] = video_size_desc
    data["ep_to_dc_latency"] = ep_to_dc_latency
    data["ep_to_cache_latency"] = ep_to_cache_latency
    data["ed_cache_list"] = ed_cache_list
    data["video_ed_request"] = video_ed_request

    return data





data = read_google("input/test.txt")
# print(data["number_of_requests"])
# sum1 = 0
# for i in data["video_ed_request"]:
#     sum1 += int(data["video_ed_request"][i])
# print("number of individual requests=", sum1, " which is different from the number of request descriptions ", data["number_of_requests"])

def check_grid(grid):
    #add up the elements or videos in each array to ensure that the cache amount doesn't overflow
    caches = data['number_of_caches']
    cache_size = data['cache_size']
    for i in range (0,caches):
        memory =[]
        for j in range (0,data['number_of_videos']):
            if grid[i][j] == 1:
                memory.append(data['video_size_desc'][j])   
                total = sum(memory)
                if total > cache_size:
                    return -1
    return 0
   
    
def make_grid():
    #make grid of videos and first initialize them to zero
    number_vids = data['number_of_videos']
    caches = data['number_of_caches']
    global grid
    #make grid of zeros
    grid = [ [0]*number_vids for i in range(caches) ]
    return(grid)
             
def find_fitness(grid):
    #iterate through video_ed_request dictionary
    requests= 0
    gains = 0
    for key, value in data['video_ed_request'].items():
        fileID = int(key[0])
        endpoint = int( key[1])
        caches =[]
        #check to see if video is even IN a cache
        cache_check = False
        for i in  range (len(grid)):
            if grid[i][fileID]==1:
                caches.append(i)
                cache_check = True
        num_requests = int(value)
        requests += num_requests
        dc_latency = data['ep_to_dc_latency'][endpoint]
        #now match endpoint with dc_latency index
        if cache_check:
            latency_ep_to_c =data["ep_to_cache_latency"][endpoint][caches[0]]
        else:
            latency_ep_to_c = dc_latency
        #if video is in more than one cache, find best (least) latency
        for i in caches:
            if data["ep_to_cache_latency"][endpoint][i] < latency_ep_to_c:
                latency_ep_to_c = data["ep_to_cache_latency"][endpoint][i]
        difference =  dc_latency - latency_ep_to_c
        gains += difference * num_requests
    fitness_score = (gains/requests)*1000 #because milliseconds
    return fitness_score

def hill_climb_new_grid(grid):
    #store the scores
    pos_solution_scores = []
    #store the location
    solution_coords =[]
    #copy grid with deep copy. 
    test_grid = deepcopy(grid)
    #change zeros to ones
    for i in range (0,len(test_grid)):
        for j in range(0,len(test_grid[0])):
            if test_grid[i][j] == 1:
                test_grid[i][j]=0
            else:
                test_grid[i][j]=1
            #check grid feasibility
            if check_grid(test_grid)!= -1:
                pos_solution_scores.append(find_fitness(test_grid))
                test_grid = deepcopy(grid)
                solution_coords.append((i,j))
            else:
                pos_solution_scores.append(0)
                test_grid = deepcopy(grid)
                solution_coords.append((i,j))
    best_score = max(pos_solution_scores)
    score_index = pos_solution_scores.index(best_score)
    best_score_location = (solution_coords[score_index])
#extract the coordinates to use and change the number at this coordinate
#print new grid with this coordinate 
    x= best_score_location[0]
    y = best_score_location[1]
    if test_grid[x][y]==0:
        test_grid[x][y]=1
    else:
        test_grid[x][y]=0
    return best_score, test_grid,x,y
    
def climb_the_hills(grid, score,x,y):
    #number of times I hill climb depends on the size of the grid
    #so must find size of the grid
    number_vids = data['number_of_videos']
    caches = data['number_of_caches']
    total_bits = number_vids * caches
    #want to test 1/3 of the grid
    #got to index the returns
    num_tests = round(total_bits/3)
    best_score = score
    best_grid = grid
    loops = 0
    dead_end = False
    #allow the function to continue searching if it continues to find improved solutions
    while loops<= num_tests or dead_end is False:
        considered_solution = hill_climb_new_grid(best_grid)
        new_score = considered_solution[0]
        #check if required loops have been exceeded 
        if loops > num_tests:
            #make array of scores
            #record scores and grids
            #check that new scores are significantly better than older ones
            #if this is the case, save scores and continue looping
            if new_score > (best_score + 1000):
                best_score = new_score
                best_grid = considered_solution[1] 
            #if not the case, dead_end
            else:
                dead_end = True
        else:
            if new_score > best_score:
                best_score = new_score
                best_grid = considered_solution[1]
        loops += 1       
    return(best_score,best_grid) 

def hill_climb_find_solution():
    start_grid = make_grid()
    output = hill_climb_new_grid(start_grid)
    improved_grid = output[1]
    score = output[0]
    x=output[2]
    y=output[3]
    final_results = climb_the_hills(improved_grid, score,x,y)
    best_solution = final_results[0]
    best_grid = final_results[1]
    print('The best grid found by hill-climbing was: ',best_grid)
    print('The best score found by hill-climbing was: ', best_solution)
    return best_grid, best_solution

hill_climb_find_solution()        