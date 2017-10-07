'''
Created on April 22, 2017

@author: Katherine
'''
import random
from genetic import make_zero_grid

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

#populate random grid with 1s OR 0s - ensure its feasible
def random_grid(list_grids):
    #track all grid solutions
    for grid in range (len(list_grids)):
        #track all caches in each solution grid
        for cache in range (len(list_grids[grid])):
            #cache size
            current_cache_size = data['cache_size']
            #track all videos in each cache in each grid
            for video in range (len(list_grids[grid][cache])):
                #find individual video size
                video_size = (data['video_size_desc'][video])
                #15% chance that 0 turns to 1 OR VISE VERSA
                if random.random()<=0.15:
                    if list_grids[grid][cache][video] == 0:
                        list_grids[grid][cache][video] = 1
                        #video takes up room in cache so remove video size from  available cache size
                        current_cache_size -= video_size
                        #check if cache size is completely consumed
                        if current_cache_size < 0:
                            list_grids[grid][cache][video] = 0
                            current_cache_size += video_size
                            #if cache is consumed with that video, try the next vid. If that vid is out of range, try first vid in list
                            try:
                                list_grids[grid][cache][video+1] = 1
                                current_cache_size -= data['video_size_desc'][video+1]
                                if current_cache_size < 0:
                                    list_grids[grid][cache][video+1] = 0
                                    current_cache_size += data['video_size_desc'][video+1]
                            except IndexError:
                                list_grids[grid][cache][0] = 1
                                current_cache_size -= data['video_size_desc'][0]
                                if current_cache_size < 0:
                                    list_grids[grid][cache][0] = 0
                                    current_cache_size += data['video_size_desc'][0]
                    else:
                        list_grids[grid][cache][video] = 0
                        current_cache_size += video_size
                else:
                    continue
    return list_grids
                
def fitness_of_grids(list_grids):
    #initialize best score and best grid starting at zero
    best_score = 0
    best_grid = 0
    for grid in list_grids:
        score = find_fitness(grid)
        #find fitness score of each grid and if it's the best one, save it
        if score > best_score:
            best_score = score
            best_grid = grid
    return best_score, best_grid

def randomize_grids():
    #start with fifty random grids
    zeros = []
    for i in range (0,50):
        start_grid = make_zero_grid()
        zeros.append(start_grid)
    random_solutions = random_grid(zeros)
    #after first checking fitness, then randomize random solutions and check that fitness
    #do this at least 3 times or until it isn't finding a much better solution - while loop
    #initialize best score and best grid starting at zero
    best_score = 0
    best_grid = 0
    loops = 0
    dead = False
    while dead is False or loops <=5:
        x = fitness_of_grids(random_solutions)
        if x[0] > best_score + 100:
            best_score = x[0]
            best_grid = x[1]
        else:
            dead = True
        loops += 1
        #randomize the first random grids and loop again with new grids
        random_solutions = random_grid(random_solutions)
    print('The best score found after randomization is: ', best_score)
    print('The grid that matches this score is: ', best_grid)
    return best_score, best_grid

randomize_grids()