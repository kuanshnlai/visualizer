from component import *
import math
import random
from pygame.locals import *
import pygame
scale = 100
therhold = math.log(10)/2
para = 4

red = (255, 0, 0)
golden = (255, 242, 4)
green = (0, 255, 0)
pink = (255, 128, 192)
blue = (0, 0, 255)


def distance(A, B):
    return ((A[0]-B[0])**2+(A[1]-B[1])**2)**0.5


def calAngle(center, target):
    vectorA = (1, 0)
    vectorB = (target[0]-center[0], target[1]-center[1])
    Alen = (vectorA[0]**2+vectorA[1]**2)**0.5
    Blen = (vectorB[0]**2+vectorB[1]**2)**0.5
    AdotB = vectorA[0]*vectorB[0]+vectorA[1]*vectorB[1]
    ctheta = AdotB/(Alen*Blen)
    # return np.arccos(ctheta)
    if(center[1]-target[1] >= 0):
        return np.arccos(ctheta)

    else:
        return -np.arccos(ctheta)+6.28


class FindPathAlgorithm:
    def __init__(self, graph, width, height):
        self.frameList = []
        self.width = width
        self.height = height
        self.graph = graph
        self.radius = self.graph.parasList['Radius']
        self.startName = graph.parasList['Start']
        self.curName = graph.parasList['Start']
        self.destName = graph.parasList['Destination']
        self.startID = graph.nameIDList[self.startName]
        self.curID = graph.nameIDList[self.curName]
        self.destID = graph.nameIDList[self.destName]
        self.neighborTable = self.generateNeighbor(
            self.graph, self.graph.parasList['Radius'])
        self.curNeighbor = self.get_curNeighbor()
        self.MinSize = self.graph.parasList['MinSize']
        self.update()  # reset color redraw frame and append to list

    # def generateNeighbor(self, graph, radius):
    #     neighborTable = dict()
    #     for Node in graph.nodeInfo:
    #         neighborTable[Node] = []
    #     for A in graph.nodeInfo:
    #         for B in graph.nodeInfo:
    #             if A == B:
    #                 continue
    #             if distance(graph.nodeInfo[A]['pos'], graph.nodeInfo[B]['pos'])/scale <= radius:
    #                 par = random.uniform(0, 1)
    #                 while par == 1:
    #                     par = random.uniform(0, 1)
    #                 power = -1 * \
    #                     (math.log(
    #                         1-par))/(distance(graph.nodeInfo[A]['pos'], graph.nodeInfo[B]['pos'])/scale)**para
    #                 print(power)
    #                 if power >= therhold:
    #                     graph.add_edge_graph((A, B), (0, 0, 0), 1)
    #                     neighborTable[A].append(B)
    #                     neighborTable[B].append(A)
    #     return neighborTable

    # def generateNeighbor(self, graph, radius):
    #     neighborTable = dict()
    #     for Node in graph.nodeInfo:
    #         neighborTable[Node] = []
    #     for A in graph.nodeInfo:
    #         for B in graph.nodeInfo:
    #             if A == B or (B in neighborTable[A] and A in neighborTable[B]):
    #                 continue
    #             if distance(graph.nodeInfo[A]['pos'], graph.nodeInfo[B]['pos']) <= radius:
    #                 graph.add_edge_graph((A, B), (0, 0, 0), 1)
    #                 neighborTable[A].append(B)
    #                 neighborTable[B].append(A)
    #     return neighborTable
    def generateNeighbor(self, graph, radius):
        neighborTable = dict()
        for Node in graph.nodeInfo:
            neighborTable[Node] = []
        print(graph.edgeIdList)
        for A in graph.nodeInfo:
            for B in graph.nodeInfo:
                if A == B or (B in neighborTable[A] and A in neighborTable[B]):
                    continue
                if (A, B) in graph.edgeIdList:
                    neighborTable[A].append(B)
                    neighborTable[B].append(A)
        return neighborTable

    def get_curNeighbor(self):
        curNeighbor = []
        for nodeId in self.neighborTable[self.curID]:
            curNeighbor.append(nodeId)
        return curNeighbor

    def update(self):
        # color start: golden destination: green cur: red cur_neighbor: pink default = blue
        # priority start > cur > destination > cur_neighbor > default
        for nodeId in self.graph.nodeInfo:
            self.graph.nodeInfo[nodeId]['color'] = blue
        for nodeId in self.curNeighbor:
            self.graph.nodeInfo[nodeId]['color'] = pink
        self.graph.nodeInfo[self.destID]['color'] = green
        self.graph.nodeInfo[self.curID]['color'] = red
        self.graph.nodeInfo[self.startID]['color'] = golden

        self.frameList.append(self.graph.draw())


class CSRouting(FindPathAlgorithm):

    def get_nextnode(self):
        curDistance = distance(
            self.graph.nodeInfo[self.curID]['pos'], self.graph.nodeInfo[self.destID]['pos'])
        minDistance = curDistance
        nextNodeId = None
        for nodeId in self.neighborTable[self.curID]:
            if distance(self.graph.nodeInfo[nodeId]['pos'], self.graph.nodeInfo[self.destID]['pos']) < minDistance:
                nextNodeId = nodeId
        return nextNodeId

    def run(self):
        hopCount = 15
        self.rotateFrameList = dict()
        while self.curID != self.destID and hopCount > 0:
            nextNodeId = self.get_nextnode()
            if nextNodeId != None:  # greedy part
                self.curID = nextNodeId
                self.curNeighbor = self.get_curNeighbor()
                self.update()
                hopCount -= 1
            else:  # Recovery part
                stuckDis = distance(
                    self.graph.nodeInfo[self.curID]['pos'], self.graph.nodeInfo[self.destID]['pos'])
                self.stuckNodeID = self.curID
                self.preID = self.curID
                # -----------------------CS------------------------------
                while hopCount > 0 and distance(self.graph.nodeInfo[self.curID]['pos'], self.graph.nodeInfo[self.destID]['pos']) >= stuckDis:
                    # longNeighbor = self.get_longest_neighbor()
                    # if longNeighbor == None:
                    #     print("stuckFFF")
                    #     hopCount = 0
                    #     break
                    end_point = self.chooseSp(self.stuckNodeID, self.preID)
                    curFrame = self.frameList[len(self.frameList)-1]
                    # curFrameId = len(self.frameList)-1
                    curve = Curve(
                        self.graph.nodeInfo[self.curID]['pos'], end_point, self.radius, curFrame)
                    # print("cur", self.graph.nodeInfo[self.curID]['pos'])
                    # print("long", self.graph.nodeInfo[longNeighbor]['pos'])
                    finalFrame = curve.findNext(self.curNeighbor, self.graph)
                    self.rotateFrameList[curFrame] = {'Start': (
                        self.graph.nodeInfo[self.curID]['pos'], end_point, curFrame), 'Final': finalFrame}
                    nextNodeId = curve.hitNode

                    if nextNodeId != None:
                        self.preID = self.curID
                        self.curID = nextNodeId
                        self.curNeighbor = self.get_curNeighbor()
                        self.update()
                        hopCount -= 1
                    else:
                        print("stuck")
                        hopCount = 0
                        break
                # ---------------------Check------------------------------
        # print(self.frameList)
        # print(self.rotateFrameList)
        if hopCount > 0:
            print("find it")
        else:
            print("Noooo")
        # print("Find it")

    # def get_longest_neighbor(self):
    #     longDistance = 0
    #     longNeighbor = None
    #     for nodeId in self.curNeighbor:
    #         nowDistance = distance(
    #             self.graph.nodeInfo[nodeId]['pos'], self.graph.nodeInfo[self.curID]['pos'])
    #         if nowDistance > longDistance:
    #             longDistance = nowDistance
    #             longNeighbor = nodeId
    #     return longNeighbor

    def chooseSp(self, stuckNodeID, pre):
        if self.curID == stuckNodeID:
            v = (self.graph.nodeInfo[self.destID]['pos'][0]-self.graph.nodeInfo[self.curID]['pos'][0],
                 self.graph.nodeInfo[self.destID]['pos'][1]-self.graph.nodeInfo[self.curID]['pos'][1])
            vlen = (v[0]**2+v[1]**2)**0.5
            sp = (int(self.graph.nodeInfo[self.curID]['pos'][0]+v[0]/vlen*self.radius), int(
                self.graph.nodeInfo[self.curID]['pos'][1]+v[1]/vlen*self.radius))
            return sp
        else:
            nowPoint = self.graph.nodeInfo[self.curID]['pos']
            prePoint = self.graph.nodeInfo[self.preID]['pos']
            pointList = self.intersection(self.preID)
            # angle1 = calAngle(nowPoint, pointList[0])
            # angle2 = calAngle(nowPoint, pointList[1])
            u = (prePoint[0]-nowPoint[0], prePoint[1]-nowPoint[1])
            v1 = (pointList[0][0]-nowPoint[0], pointList[0][1]-nowPoint[1])
            v2 = (pointList[1][0]-nowPoint[0], pointList[1][1]-nowPoint[1])
            ulen = (u[0]**2+u[1]**2)**0.5
            v1len = (v1[0]**2+v1[1]**2)**0.5
            v2len = (v2[0]**2+v2[1]**2)**0.5
            c1 = (u[0]*v1[0]+u[1]*v1[1])/(ulen*v1len)
            c2 = (u[0]*v2[0]+u[1]*v2[1])/(ulen*v2len)
            if c1 >= 0:
                return pointList[0]
            else:
                return pointList[1]

    def intersection(self, otherID):
        nowPoint = self.graph.nodeInfo[self.curID]['pos']
        prePoint = self.graph.nodeInfo[otherID]['pos']

        delta = 10E-4
        x1 = nowPoint[0]
        y1 = nowPoint[1]
        x2 = prePoint[0]
        y2 = prePoint[1]
        r = self.radius
        a = 2*r*(x1-x2)
        b = 2*r*(y1-y2)
        c = -(x1-x2)**2-(y1-y2)**2

        p = a**2+b**2
        q = -2*a*c
        s = c**2-b**2
        if p == 0:
            p = delta
        c1 = (-q+(q**2-4*p*s)**0.5)/(2*p)  # cos theta
        c2 = (-q-(q**2-4*p*s)**0.5)/(2*p)
        s1 = (1-c1**2)**0.5
        s2 = (1-c2**2)**0.5

        p1 = self.calPos(c1, s1)
        p2 = self.calPos(c1, -s1)
        p3 = self.calPos(c2, s2)
        p4 = self.calPos(c2, -s2)
        realPoint = self.check([p1, p2, p3, p4])
        # print("real", realPoint)
        return realPoint

    def calPos(self, cos, sin):  # given cos and sin and cur point determine the point's pos
        nowPoint = self.graph.nodeInfo[self.curID]['pos']
        newPoint = ((nowPoint[0]+self.radius*cos),
                    (nowPoint[1]-self.radius*sin))
        return newPoint

    def check(self, pointList):
        nowPoint = self.graph.nodeInfo[self.curID]['pos']
        prePoint = self.graph.nodeInfo[self.preID]['pos']
        delta = 0.1
        realPoint = []
        for p in pointList:
            if math.fabs(distance(p, nowPoint)-self.radius) <= delta and math.fabs(distance(p, prePoint)-self.radius) <= delta:
                realPoint.append((int(p[0]), int(p[1])))
        return realPoint


class AdaptiveCS(CSRouting):
    preID = None

    def run(self):
        hopCount = 20
        print(self.neighborTable)
        self.rotateFrameList = dict()
        while self.curID != self.destID and hopCount >= 0:
            hopCount -= 1
            nextNode = self.get_nextnode()
            if nextNode != None:
                self.preID = self.curID
                self.curID = nextNode
                self.curNeighbor = self.get_curNeighbor()
                self.update()
                print("GF")
                # print(self.frameList)
            else:
                self.preID = self.curID
                stuckNodeID = self.curID
                # while cannot satisfy GF condition
                while distance(self.graph.nodeInfo[self.curID]['pos'], self.graph.nodeInfo[self.destID]['pos']) >= distance(self.graph.nodeInfo[self.preID]['pos'], self.graph.nodeInfo[self.destID]['pos']):
                    print("curID", self.curID, "curDis", distance(
                        self.graph.nodeInfo[self.curID]['pos'], self.graph.nodeInfo[self.destID]['pos']))
                    print("stuckID", self.preID, "stuckDis", distance(
                        self.graph.nodeInfo[self.preID]['pos'], self.graph.nodeInfo[self.destID]['pos']))
                    if hopCount <= 0:
                        return
                    hopCount -= 1
                    print("Call att", self.curID)

                    Ni = self.getNeighbor(self.curID)
                    tmp = self.curID
                    self.curID = self.aTT(
                        Ni, self.curID, self.preID, stuckNodeID)
                    self.preID = tmp
                    self.curNeighbor = self.get_curNeighbor()
                    if self.curID == None:
                        print("Stuck")
                        return
                    self.update()
        # print("RRRRRR", self.rotateFrameList)
        return

    def eSW(self, Ni, Vi, Vj, Vk, curFrame):
        '''
        Vi cur point
        Vj pre point
        Vk next point candidate
        '''
        # print("eSW")
        count = 0
        r = distance(self.graph.nodeInfo[Vi]['pos'],
                     self.graph.nodeInfo[Vk]['pos'])
        hitNode = Vk
        newR = r
        curve = Curve(
            self.graph.nodeInfo[Vi]['pos'], self.graph.nodeInfo[Vk]['pos'], newR, curFrame)
        initAngle = curve.calAngle(
            self.graph.nodeInfo[Vi]['pos'], self.graph.nodeInfo[Vk]['pos'])
        for theta in range(0, 360):
            count += 1
            rad = theta/180*3.14
            parameter = math.exp(-rad*math.sqrt(3))
            newR = r*parameter
            end_point = (int(self.graph.nodeInfo[Vi]['pos'][0]+newR*math.cos(
                initAngle+rad)), int(self.graph.nodeInfo[Vi]['pos'][1]-newR*math.sin(initAngle+rad)))
            curve = Curve(
                self.graph.nodeInfo[Vi]['pos'], end_point, newR, curFrame)
            center = curve.calcenter(
                curve.hing_point, curve.end_point, newR)
            for nodeID in Ni:
                if math.fabs(distance(center, graph.nodeInfo[nodeID]['pos']) - curve.radius) <= 3.0:
                    startAngle = curve.calAngle(center, curve.hing_point)
                    endAngle = curve.calAngle(center, curve.end_point)
                    nowAngle = curve.calAngle(
                        center, graph.nodeInfo[nodeID]['pos'])
                    if between(nowAngle, endAngle, startAngle):
                        hitNode = nodeID
                        break

            if hitNode != Vk:
                print("return", hitNode)
                return hitNode
            self.rotateFrameList[curFrame]['Start'].append(
                (curve.hing_point, curve.end_point, curFrame))
            self.rotateFrameList[curFrame]['Final'].append(
                (curve.hing_point, curve.end_point, curFrame))
            self.rotateFrameList[curFrame]['R'].append(newR)
            if newR <= self.MinSize:
                # print(count)
                break
        return hitNode

    def aTT(self, Ni, Vi, Vj, stuckNodeID):
        '''
        Ni now point neighbor
        Vi now point
        Vj previous point
        '''
        # print("aTT")
        self.update()
        neighborInfo = self.get_longest_neighbor(Vi, Ni)
        maxLen = neighborInfo[0]
        Vk = neighborInfo[1]
        r = math.ceil(max(maxLen, self.MinSize))

        end_point = self.chooseSp(stuckNodeID, Vj)

        curFrame = self.frameList[len(self.frameList)-1]
        curve = Curve(self.graph.nodeInfo[Vi]
                      ['pos'], end_point, r, curFrame)
        Frame = curve.findNext(Ni, self.graph)

        self.rotateFrameList[curFrame] = {'Start': [(
            self.graph.nodeInfo[Vi]['pos'], end_point, curFrame)], 'Final': [Frame], 'R': [r]}
        nextNode = curve.hitNode
        # print(Ni)
        # print("Hit", nextNode)
        while nextNode != None:
            if r <= self.MinSize:
                return nextNode
            elif r > self.MinSize and nextNode != Vk:
                # print("case1")
                # print("Case1 hit node = ", nextNode)
                # print("rotateFrame before", self.rotateFrameList[curFrame])
                Vk = nextNode
                r = math.ceil(max(distance(
                    self.graph.nodeInfo[self.curID]['pos'], self.graph.nodeInfo[Vk]['pos']), self.MinSize))
                # print("r = ", r)
                curve = Curve(
                    self.graph.nodeInfo[self.curID]['pos'], end_point, r, curFrame)
                Frame = curve.findNext(Ni, self.graph)
                self.rotateFrameList[curFrame]['Start'].append(
                    (self.graph.nodeInfo[self.curID]['pos'], end_point, curFrame))
                self.rotateFrameList[curFrame]['Final'].append(Frame)
                self.rotateFrameList[curFrame]['R'].append(r)
                nextNode = curve.hitNode
            elif r > self.MinSize and nextNode == Vk:
                # print("case2")
                Vn = self.eSW(Ni, Vi, Vj, Vk, curFrame)
                print("back to main")
                # print("Vk", Vk)
                # print("Vn", Vn)
                # print(self.rotateFrameList[curFrame])
                if Vn == Vk:
                    return Vn
                else:
                    nextNode = Vn
                    # r = max(distance(
                    #     self.graph.nodeInfo[self.curID]['pos'], self.graph.nodeInfo[Vn]['pos']), self.MinSize)
                    # curve = Curve(
                    #     self.graph.nodeInfo[self.curID]['pos'], end_point, r, curFrame)
                    # Frame = curve.findNext(Ni, self.graph)
                    # self.rotateFrameList[curFrame]['Start'].append(
                    #     (self.graph.nodeInfo[self.curID]['pos'], end_point, curFrame))
                    # self.rotateFrameList[curFrame]['Final'].append(Frame)
                    # self.rotateFrameList[curFrame]['R'].append(r)
        return None

    def getNeighbor(self, nodeID):
        neighbor = []
        for n in self.neighborTable[nodeID]:
            neighbor.append(n)
        return neighbor

    def get_longest_neighbor(self, vi, Ni):  # return (distance,nodeID)
        nowPoint = self.graph.nodeInfo[vi]['pos']
        maxLen = 0
        maxNeighbor = None
        for n in Ni:
            neighbor = self.graph.nodeInfo[n]['pos']
            if distance(nowPoint, neighbor) > maxLen:
                maxLen = distance(nowPoint, neighbor)
                maxNeighbor = n

        return (maxLen, maxNeighbor)

    def intersection(self, otherID):
        nowPoint = self.graph.nodeInfo[self.curID]['pos']
        prePoint = self.graph.nodeInfo[otherID]['pos']

        delta = 10E-4
        x1 = nowPoint[0]
        y1 = nowPoint[1]
        x2 = prePoint[0]
        y2 = prePoint[1]
        r = max(self.MinSize, distance(nowPoint, prePoint))
        a = 2*r*(x1-x2)
        b = 2*r*(y1-y2)
        c = -(x1-x2)**2-(y1-y2)**2

        p = a**2+b**2
        q = -2*a*c
        s = c**2-b**2
        if p == 0:
            p = delta
        c1 = (-q+(q**2-4*p*s)**0.5)/(2*p)  # cos theta
        c2 = (-q-(q**2-4*p*s)**0.5)/(2*p)
        s1 = (1-c1**2)**0.5
        s2 = (1-c2**2)**0.5

        p1 = self.calPos(c1, s1, r)
        p2 = self.calPos(c1, -s1, r)
        p3 = self.calPos(c2, s2, r)
        p4 = self.calPos(c2, -s2, r)
        realPoint = self.check([p1, p2, p3, p4], r)
        # print("real", realPoint)
        return realPoint

    def calPos(self, cos, sin, radius):  # given cos and sin and cur point determine the point's pos
        nowPoint = self.graph.nodeInfo[self.curID]['pos']
        newPoint = ((nowPoint[0]+radius*cos),
                    (nowPoint[1]-radius*sin))
        return newPoint

    def check(self, pointList, radius):
        nowPoint = self.graph.nodeInfo[self.curID]['pos']
        prePoint = self.graph.nodeInfo[self.preID]['pos']
        delta = 0.1
        realPoint = []
        for p in pointList:
            if math.fabs(distance(p, nowPoint)-radius) <= delta and math.fabs(distance(p, prePoint)-radius) <= delta:
                realPoint.append((int(p[0]), int(p[1])))
        return realPoint

    def chooseSp(self, stuckNodeID, pre):
        if self.curID == stuckNodeID or pre == None:
            v = (self.graph.nodeInfo[self.destID]['pos'][0]-self.graph.nodeInfo[self.curID]['pos'][0],
                 self.graph.nodeInfo[self.destID]['pos'][1]-self.graph.nodeInfo[self.curID]['pos'][1])
            vlen = (v[0]**2+v[1]**2)**0.5
            sp = (int(self.graph.nodeInfo[self.curID]['pos'][0]+v[0]/vlen*self.radius), int(
                self.graph.nodeInfo[self.curID]['pos'][1]+v[1]/vlen*self.radius))
            return sp
        else:
            nowPoint = self.graph.nodeInfo[self.curID]['pos']
            prePoint = self.graph.nodeInfo[self.preID]['pos']
            pointList = self.intersection(self.preID)
            # angle1 = calAngle(nowPoint, pointList[0])
            # angle2 = calAngle(nowPoint, pointList[1])
            u = (prePoint[0]-nowPoint[0], prePoint[1]-nowPoint[1])
            v1 = (pointList[0][0]-nowPoint[0], pointList[0][1]-nowPoint[1])
            v2 = (pointList[1][0]-nowPoint[0], pointList[1][1]-nowPoint[1])
            ulen = (u[0]**2+u[1]**2)**0.5
            v1len = (v1[0]**2+v1[1]**2)**0.5
            v2len = (v2[0]**2+v2[1]**2)**0.5
            c1 = (u[0]*v1[0]+u[1]*v1[1])/(ulen*v1len)
            c2 = (u[0]*v2[0]+u[1]*v2[1])/(ulen*v2len)
            if c1 >= 0:
                return pointList[0]
            else:
                return pointList[1]
