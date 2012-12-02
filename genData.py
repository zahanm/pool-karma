import random
#import networkx as nx
#import matplotlib.pyplot as plt

# generate random locations for people and goal state
def main():
    numPeople = 5
    numCars = 2
    width = 10
    height = 10

    #G=nx.Graph()
    nodes = []
    carNodes = random.sample(range(numPeople), numCars)
    with open("data.txt", "w") as out:
        out.write("{}\n".format(numPeople+1))
        for i in range(numPeople+1):
            x = random.randint(0, width)
            y = random.randint(0, height)

            l = x, y
            nodes.append(l)
            #G.add_nodes(i)
            
            if i==numPeople:
                out.write ("{} {}\n".format(x, y))
                break
            if (i in carNodes):
                out.write ("{} {} {}\n".format(x, y, 4))
            else:
                out.write ("{} {} {}\n".format(x, y, 0))
            


        for i in range(len(nodes)):
            for j in range(len(nodes)):
                if i < j:
                    dist_i_j = dist(nodes[i], nodes[j])
                    #G.add_edge(i, j, weight=dist_i_j)
                    out.write("{} {} {}\n".format(i, j, dist_i_j))


#nx.draw(G)

def dist(a,b):
    dist = ((a[0]-b[0])**2 + (a[1]-b[1])**2)**0.5
    return dist



if __name__ == '__main__':
  main()
