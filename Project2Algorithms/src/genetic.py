'''
Created on Apr 13, 2017

@author: Katherine
'''
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
   
def make_zero_grid():
    #make grid of videos and first initialize them to zero
    number_vids = data['number_of_videos']
    caches = data['number_of_caches']
    global zero_grid
    #make grid of zeros
    zero_grid = [ [0]*number_vids for i in range(caches) ]
    return zero_grid

#populate random grid with 1s - ensure its feasible
def random_grid(parents):
    #track all grid solutions
    for grid in range (len(parents)):
        #track all caches in each solution grid
        for cache in range (len(parents[grid])):
            #cache size
            current_cache_size = data['cache_size']
            #track all videos in each cache in each grid
            for video in range (len(parents[grid][cache])):
                #find individual video size
                video_size = (data['video_size_desc'][video])
                #15% chance that 0 turns to 1
                if random.random()<=0.15:
                    parents[grid][cache][video] = 1
                    #video takes up room in cache so remove video size from  available cache size
                    current_cache_size -= video_size
                    #check if cache size is completely consumed
                    if current_cache_size < 0:
                        parents[grid][cache][video] = 0
                        current_cache_size += video_size
                        #if cache is consumed with that video, try the next vid. If that vid is out of range, try first vid in list
                        try:
                            parents[grid][cache][video+1] = 1
                            current_cache_size -= data['video_size_desc'][video+1]
                            if current_cache_size < 0:
                                parents[grid][cache][video+1] = 0
                                current_cache_size += data['video_size_desc'][video+1]
                        except IndexError:
                            parents[grid][cache][0] = 1
                            current_cache_size -= data['video_size_desc'][0]
                            if current_cache_size < 0:
                                parents[grid][cache][0] = 0
                                current_cache_size += data['video_size_desc'][0]
                    else:
                        continue
    return parents

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
                
def make_starter_pop():
    #start with two grids of zeros
    x = make_zero_grid()
    y = make_zero_grid()
    parents = []
    parents.append(x)
    parents.append(y)
    #add random grids to population until 10 grids in population
    population =[]
    x = 0
    while x <=5:
        new_grids = random_grid(parents)
        population.append(new_grids[0])
        population.append(new_grids[1])
        x+=1
    return population
         
             
def find_best_fitness_orig():
    population = make_starter_pop()
    #find fitness of each grid in pop and select the best fitness and best grid
    best_score = 0
    best_grid = []
    for grid in range(len(population)):
        x = find_fitness(population[grid])
        if best_score < x:
            best_score = x
            best_grid = population[grid]
    return population,best_score,best_grid

#function to make children grids
def make_children(pop,best_score,best_grid):
    num_caches = data["number_of_caches"]
    best_score = best_score
    best_grid = best_grid
    #need to decide what cache to take from parents to make children - needs to be random. Cannot be zero or all.
    cache_swap = random.randint(1, num_caches-1)
    for grid in range (len(pop)):
        for cache in range(0,(cache_swap+1)):
            #account for if it is the last grid in the list (will give index error)
            #if that happens, swap with first grid in list
            try:
                pop[grid][cache] = pop[grid+1][cache]
            except IndexError:
                pop[grid][cache] = pop[0][cache]
            #find fitness of new grid and replace old best score if better
            fitness = find_fitness(pop[grid])
            if fitness > best_score:
                best_score = fitness
                best_grid = pop[grid]
    pop.append(best_grid)
    return pop, best_score, best_grid
        
            
def genetics_at_work():
    x = find_best_fitness_orig()
    pop = x[0]           
    best_score = x[1]
    best_grid = x[2]
    #will establish a clamp of sorts to ensure that the program doesn't make children infinitely
    dead_end = False
    #ensure it goes around incoorporating the children to the population at least 5 times
    counter = 0 
    while dead_end is False or counter<=5:
        #make the children grids
        children = make_children(pop, best_score, best_grid)
        new_best_score = children[1]
        counter += 1
        #add child to population
        pop = children[0]
        #ensure new scores are at least 10 better than last - if not, is not much gain and will stop running program
        if new_best_score <= (best_score + 10):
            dead_end = True 
            #otherwise, add child to population and calculate with it as a parent
        else:
            best_score = new_best_score
            best_grid = children[2]
    print('after genetics, best score is: ', best_score)
    return best_score

genetics_at_work()