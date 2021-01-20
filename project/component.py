import networkx as nx
import pygame
import numpy as np
import math
import pygame_gui
import gc


def distance(A, B):
    return ((A[0]-B[0])**2+(A[1]-B[1])**2)**0.5


def between(target, bound1, bound2):
    # print(bound1, bound2)
    if bound1 > bound2:
        bound1 -= 6.28
        # target -= 6.28
    # print(bound1, target, bound2)
    if bound1 <= target <= (bound2+0.05):
        return True
    return False


class graph(nx.Graph):
    frames = []
    # colorList = dict()
    # nameList = dict()
    edgeInfoList = dict()
    edgeIdList = []
    # posList = dict()
    parasList = dict()
    nodeInfo = dict()
    nodeIdList = []
    nameIDList = dict()

    def set_frame_size(self, width, height):
        self.width = width
        self.height = height
        # surface = pygame.Surface(
        #     (self.width, self.height))
        # surface.fill((255, 255, 255))
        # self.frames.append(surface)

    def add_node_graph(self, label, number, color, pos):
        self.add_node(number)
        # self.colorList[number] = color
        # self.nameList[number] = label
        # self.posList[number] = pos
        self.nodeIdList.append(number)
        self.nodeInfo[number] = {'name': label, 'color': color, 'pos': pos}
        self.nameIDList[label] = number
        self.frames.append(self.draw())

    def add_edge_graph(self, edge, color, weight):
        self.add_edge(edge[0], edge[1])
        self.edgeIdList.append((edge[0], edge[1]))
        self.edgeInfoList[edge] = {"color": color, "weight": weight}
        self.frames.append(self.draw())

    def draw(self):
        nodeSize = 5
        frame = pygame.Surface((self.width, self.height))
        frame.fill((255, 255, 255))
        for e in self.edgeIdList:
            x1 = self.nodeInfo[e[0]]['pos'][0]
            y1 = self.nodeInfo[e[0]]['pos'][1]
            x2 = self.nodeInfo[e[1]]['pos'][0]
            y2 = self.nodeInfo[e[1]]['pos'][1]
            v = (x2-x1, y2-y1)
            vlen = (v[0]**2+v[1]**2)**0.5
            u = (v[0]/vlen, v[1]/vlen)
            d = (int(u[0]*nodeSize), int(u[1]*nodeSize))
            pygame.draw.line(frame, (0, 0, 0),
                             (x1+d[0], y1+d[1]), (x2-d[0], y2-d[1]), 1)
        for node in self.nodeIdList:
            # font = pygame.font.Font('freesansbold.ttf', 16)
            # text = font.render(str(node), True, (0, 0, 255), (255, 255, 255))
            # textRect = text.get_rect()
            # textRect.center = self.posList[node][0], self.posList[node][1]
            pygame.draw.circle(frame, self.nodeInfo[node]['color'],
                               (self.nodeInfo[node]['pos']), nodeSize)
            # frame.blit(text, textRect)
        return frame

    def del_node_graph(self, name):
        NodeId = self.nameIDList[name]
        self.nodeInfo.pop(NodeId, None)
        self.nodeIdList.remove(NodeId)

        for e in self.edgeIdList:
            if NodeId == e[0] or NodeId == e[1]:
                self.edgeIdList.remove(e)
                self.edgeInfoList.pop(e, None)
        self.frames.append(self.draw())

    def del_edge_graph(self, fromNode, toNode):
        for e in self.edgeInfoList:
            if (fromNode == e[0] and toNode == e[1]) or (fromNode == e[1] and toNode == e[0]):
                self.edgeIdList.remove(e)
                self.edgeInfoList.pop(e, None)
        self.frames.append(self.draw())

    def clear_frame_buffer(self):
        curFrame = self.frames[len(self.frames)-1]
        self.frames = [curFrame]

    def printf(self):
        print(self.nodes)
        print("Label is ", self.labelList)
        print("Color is ", self.colorList)
        print("edge", self.edgeInfoList)
        print(self.edges)


# def calcenter(hing_point, end_point, radius):
#     v = np.array((end_point[0] - hing_point[0], end_point[1] - hing_point[1]))
#     theta = np.radians(-60)
#     c, s = np.cos(theta), np.sin(theta)
#     rotateMatrix = np.array([[c, -s], [s, c]])
#     rv = rotateMatrix.dot(v)
#     print(rotateMatrix, v)
#     rvlen = (rv[0]**2+rv[1]**2)**0.5
#     center = (int(hing_point[0]+(rv[0]/rvlen)*radius),
#               int(hing_point[1]+(rv[1]/rvlen)*radius))
#     return center


class Curve():
    def __init__(self, hing_point, end_point, radius, startSurface):
        self.hing_point = hing_point
        self.end_point = end_point
        self.radius = radius
        self.startSurface = startSurface
        self.frameList = []
        self.hitNode = None

    def draw_curve(self, surface):
        center = self.calcenter(self.hing_point, self.end_point, self.radius)
        startAngle = self.calAngle(center, self.hing_point)
        endAngle = self.calAngle(center, self.end_point)
        pygame.draw.arc(surface, (0, 0, 0),
                        (center[0]-self.radius, center[1]-self.radius, 2*self.radius, 2*self.radius), endAngle, startAngle)  # surface 是還沒畫過曲線的frame

        # pygame.draw.circle(
        #     surface, (0, 0, 255), (center[0], center[1]), 1, 1)
        pygame.draw.circle(
            surface, (0, 255, 0), (self.hing_point[0], self.hing_point[1]), 1, 1)
        pygame.draw.circle(
            surface, (255, 0, 0), (self.end_point[0], self.end_point[1]), 1, 1)
        return surface

    def calAngle(self, center, target):
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

    def calcenter(self, hing_point, end_point, radius):
        v = np.array((end_point[0] - hing_point[0],
                      end_point[1] - hing_point[1]))
        theta = np.radians(60)
        c, s = np.cos(theta), np.sin(theta)
        rotateMatrix = np.array([[c, -s], [s, c]])
        rv = rotateMatrix.dot(v)
        rvlen = (rv[0]**2+rv[1]**2)**0.5
        center = (int(hing_point[0]+(rv[0]/rvlen)*radius),
                  int(hing_point[1]+(rv[1]/rvlen)*radius))
        return center

    def findNext(self, cur_neighbor, graph):
        initAngle = self.calAngle(self.hing_point, self.end_point)
        for theta in range(0, 360):
            tmp = theta
            surface = self.startSurface.copy()
            theta = theta/180*3.14
            end_point = (int(self.hing_point[0]+self.radius*math.cos(initAngle+theta)),
                         int(self.hing_point[1]-self.radius*math.sin(initAngle+theta)))
            self.end_point = end_point
            center = self.calcenter(
                self.hing_point, self.end_point, self.radius)
            hitNode = self.hit_node(center, cur_neighbor, graph)
            # if 100 <= tmp <= 120:
            #     print("tmp:", tmp, "end_point", self.end_point)
            if hitNode != None:
                self.frameList.append(self.draw_curve(surface))
                self.hitNode = hitNode
                # print("hit tmp:", tmp)
                return (self.hing_point, self.end_point, self.draw_curve(surface))
            self.frameList.append(self.draw_curve(surface))
        return (self.hing_point, self.end_point, self.draw_curve(surface))

    def hit_node(self, center, cur_neighbor, graph):
        delta = 3
        for nodeId in cur_neighbor:
            # if(self.hing_point == (449, 284) and graph.nodeInfo[nodeId]['pos'] == (399, 200) and math.fabs(distance(center, graph.nodeInfo[nodeId]['pos']) - self.radius) < 5):
            #     print(self.hing_point,
            #           graph.nodeInfo[nodeId]['pos'], "Inhit")
            #     print(
            #         math.fabs(distance(center, graph.nodeInfo[nodeId]['pos']) - self.radius))
            #     startAngle = self.calAngle(center, self.hing_point)
            #     endAngle = self.calAngle(center, self.end_point)
            #     nowAngle = self.calAngle(center, graph.nodeInfo[nodeId]['pos'])

            #     print("Start:", startAngle)
            #     print("endAngle", endAngle)
            #     print("nowAngle", nowAngle)
            # if self.hing_point == (420, 350):
            #     startAngle = self.calAngle(center, self.hing_point)
            #     endAngle = self.calAngle(center, self.end_point)
            #     nowAngle = self.calAngle(center, graph.nodeInfo[nodeId]['pos'])
            #     print("-------", nowAngle)
            # if 350 <= center[0] <= 435 and 310 <= center[1] <= 350:
            #     startAngle = self.calAngle(center, self.hing_point)
            #     endAngle = self.calAngle(center, self.end_point)
            #     nowAngle = self.calAngle(center, graph.nodeInfo[nodeId]['pos'])
            #     print("-------", nowAngle)
            #     print(
            #         math.fabs(distance(center, graph.nodeInfo[nodeId]['pos']) - self.radius))
            if math.fabs(distance(center, graph.nodeInfo[nodeId]['pos']) - self.radius) <= delta:
                startAngle = self.calAngle(center, self.hing_point)
                endAngle = self.calAngle(center, self.end_point)
                nowAngle = self.calAngle(center, graph.nodeInfo[nodeId]['pos'])
                # print("possiblehit")
                # print(center)
                if between(nowAngle, endAngle, startAngle):
                    # print("Hit d = ", distance(
                    #     center, graph.nodeInfo[nodeId]['pos']))
                    # print("Hit angle", startAngle, nowAngle, endAngle)
                    return nodeId
        return None

    def rotate(self, finalend, graph):
        # print("hing_point", self.hing_point, "end point", self.end_point)
        initAngle = self.calAngle(self.hing_point, self.end_point)
        count = 0
        for theta in range(0, 360):
            count += 1
            surface = self.startSurface.copy()
            theta = theta/180*3.14
            if self.end_point[0] == finalend[0] and self.end_point[1] == finalend[1]:
                start_point = (int(self.hing_point[0]+self.radius*math.cos(initAngle+theta)),
                               int(self.hing_point[1]-self.radius*math.sin(initAngle+theta)))
                self.end_point = start_point
                self.frameList.append(self.draw_curve(surface))
                break

            start_point = (int(self.hing_point[0]+self.radius*math.cos(initAngle+theta)),
                           int(self.hing_point[1]-self.radius*math.sin(initAngle+theta)))
            self.end_point = start_point
            self.frameList.append(self.draw_curve(surface))

            del(surface)
            gc.collect()
        # print("count", count)
        # print("Out rotate")
        return self.frameList
# def calAngle(center, target):
#     vectorA = (1, 0)
#     vectorB = (target[0]-center[0], target[1]-center[1])
#     Alen = (vectorA[0]**2+vectorA[1]**2)**0.5
#     Blen = (vectorB[0]**2+vectorB[1]**2)**0.5
#     AdotB = vectorA[0]*vectorB[0]+vectorA[1]*vectorB[1]
#     ctheta = AdotB/(Alen*Blen)
#     # return np.arccos(ctheta)
#     if(center[1]-target[1] >= 0):
#         return np.arccos(ctheta)

#     else:
#         return -np.arccos(ctheta)


# def draw_curve(hing_point, end_point, radius, surface):
#     center = calcenter(hing_point, end_point, radius)
#     startAngle = calAngle(center, hing_point)
#     endAngle = calAngle(center, end_point)
#     pygame.draw.arc(surface, (0, 0, 0),
#                     (center[0]-radius, center[1]-radius, 2*radius, 2*radius), startAngle, endAngle)  # surface 是還沒畫過曲線的frame

#     pygame.draw.circle(
#         surface, (0, 0, 255), (center[0], center[1]), 1, 1)
#     pygame.draw.circle(
#         surface, (0, 255, 0), (hing_point[0], hing_point[1]), 1, 1)
#     pygame.draw.circle(
#         surface, (255, 0, 0), (end_point[0], end_point[1]), 1, 1)
#     return surface


# def rotate(start_surface, hing_point, radius):
#     surface = start_surface.copy()
#     frameList = []
#     for theta in range(0, 360):
#         surface = start_surface.copy()
#         theta = theta/180*3.14
#         start_point = (int(hing_point[0]+radius*math.cos(theta)),
#                        int(hing_point[1]-radius*math.sin(theta)))
#         frameList.append(draw_curve(hing_point, start_point, radius, surface))
#     return frameList


class Window:
    def __init__(self, width, height, manager, title=""):
        self.width = width
        self.height = height
        self.manager = manager
        self.BtnList = []
        self.BtnDict = dict()
        self.InputList = dict()
        self.labelList = dict()
        self.panelList = dict()
        self.title = title
        self.window = self.create()
        self.window_survive = True

    def create(self):
        return pygame_gui.elements.ui_window.UIWindow(pygame.Rect((200, 200), (self.width, self.height)), manager=self.manager)

    def add_button(self, text, posx, posy, width, height, objid, parent):
        self.BtnList.append(pygame_gui.elements.UIButton(pygame.Rect(
            (posx, posy), (width, height)), text=text, manager=self.manager, container=parent, parent_element=parent, object_id=objid))
        self.BtnDict[objid] = self.BtnList[len(self.BtnList)-1]

    def add_label(self, text, posx, posy, width, height, objid, parent):
        self.labelList[objid] = (pygame_gui.elements.UILabel(pygame.Rect(
            (posx, posy), (width, height)), text=text, manager=self.manager, container=parent, parent_element=parent, object_id=objid))
        self.InputList[objid] = []

    def add_inputEntry(self, objid, posx, posy, width, height, parent):
        self.InputList[objid].append(pygame_gui.elements.ui_text_entry_line.UITextEntryLine(relative_rect=pygame.Rect(
            (posx, posy), (width, height)), manager=self.manager, container=parent, parent_element=parent, object_id=objid))

    def add_dropdownMenu(self, objid, posx, posy, width, height, optionList, default, parent):
        self.InputList[objid].append(
            pygame_gui.elements.ui_drop_down_menu.UIDropDownMenu(relative_rect=pygame.Rect(
                (posx, posy), (width, height)), options_list=optionList, manager=self.manager, container=parent, parent_element=parent, starting_option=default, object_id=objid))

    def add_panel(self, posx, posy, width, height, objid):
        self.panelList[objid] = (pygame_gui.elements.ui_panel.UIPanel(relative_rect=pygame.Rect(
            (posx, posy), (width, height)), starting_layer_height=1, manager=self.manager, container=self.window, parent_element=self.window))

    def update_label_txt(self, objid, text):
        self.labelList[objid].set_text(text)

    def kill(self):
        self.window.kill()


class AddNodeWindow(Window):
    xValue = None
    yValue = None
    NameValue = None
    ConfirmBtnId = 0
    CancelBtnId = 1
    PosXLabelId = 2
    PosYLabelId = 3
    NameLabelId = 4
    NodeId = 5
    EdgeId = 6
    WeightId = 7
    ToId = 8
    FromId = 9
    PosToId = 10
    PosFromId = 11
    Mode = 'Node'
    NameValue = None
    xValue = None
    yValue = None

    def create(self):
        self.type = 'Add Node'
        return pygame_gui.elements.ui_window.UIWindow(pygame.Rect(
            (200, 200), (self.width, self.height)), manager=self.manager)

    def addAllElement(self, G):
        self.window.set_display_title("Add node")
        self.add_panel(0, 50, 400, 275, self.NodeId)
        self.add_panel(0, 50, 400, 275, self.EdgeId)
        self.add_button("Node", 50, 20, 70, 20, self.NodeId,
                        self.window)
        self.add_button("Edge", 130, 20, 70, 20, self.EdgeId,
                        self.window)
        self.add_button("Confirm", 70, 220, 70, 50,
                        self.ConfirmBtnId, self.panelList[self.NodeId])
        self.add_button("Cancel", 160, 220, 70, 50,
                        self.CancelBtnId, self.panelList[self.NodeId])
        self.add_label("X   :", 50, 100, 40, 20,
                       self.PosXLabelId, self.panelList[self.NodeId])
        self.add_label("Y   :", 50, 160, 40, 20,
                       self.PosYLabelId, self.panelList[self.NodeId])
        self.add_label("Name:", 50, 50, 40, 20, self.NameLabelId,
                       self.panelList[self.NodeId])
        self.add_inputEntry(self.PosXLabelId, 100, 100, 70,
                            20, self.panelList[self.NodeId])
        self.add_inputEntry(self.PosYLabelId, 100, 160, 70,
                            20, self.panelList[self.NodeId])
        self.add_inputEntry(self.NameLabelId, 100, 50, 70,
                            20, self.panelList[self.NodeId])
        # ---------------------------------
        self.add_label("Weight:", 50, 50, 60, 20,
                       self.WeightId, self.panelList[self.EdgeId])
        self.add_label("To    :", 50, 100, 60, 20,
                       self.ToId, self.panelList[self.EdgeId])
        self.add_label("From  :", 50, 160, 60, 20, self.FromId,
                       self.panelList[self.EdgeId])
        self.add_inputEntry(self.WeightId, 120, 50, 70,
                            20, self.panelList[self.EdgeId])

        nodeName = []
        for i in G.nodeIdList:
            nodeName.append(G.nodeInfo[i]['name'])

        self.add_dropdownMenu(self.ToId, 120,
                              100, 90, 20, nodeName, "Default", self.panelList[self.EdgeId])

        self.add_label("Pos:({:d},{:d})".format(0, 0), 210, 100,
                       120, 20, self.PosToId, self.panelList[self.EdgeId])
        # self.labelList[self.PosToId].set_text("AAA")
        self.add_dropdownMenu(self.FromId, 120,
                              160, 90, 20, nodeName, "Default", self.panelList[self.EdgeId])
        self.add_label("Pos:({:d},{:d})".format(0, 0), 210, 160,
                       120, 20, self.PosFromId, self.panelList[self.EdgeId])
        self.add_button("Confirm", 70, 220, 70, 50,
                        self.ConfirmBtnId, self.panelList[self.EdgeId])
        self.add_button("Cancel", 160, 220, 70, 50,
                        self.CancelBtnId, self.panelList[self.EdgeId])
        self.BtnDict[self.NodeId].disable()
        self.panelList[self.EdgeId].hide()

    def handleEvent(self, event, G):
        # print("press", event.ui_element)
        # print(self.InputList[self.ToId])
        # print(event.user_type)
        if event.type == pygame.USEREVENT:
            if event.user_type == pygame_gui.UI_BUTTON_PRESSED and event.ui_element.text == 'Node':
                self.BtnDict[self.NodeId].disable()
                self.BtnDict[self.EdgeId].enable()
                self.panelList[self.EdgeId].hide()
                self.panelList[self.NodeId].show()
                self.Mode = 'Node'
            elif event.user_type == pygame_gui.UI_BUTTON_PRESSED and event.ui_element.text == 'Edge':
                self.BtnDict[self.EdgeId].disable()
                self.BtnDict[self.NodeId].enable()
                self.panelList[self.NodeId].hide()
                self.panelList[self.EdgeId].show()
                self.Mode = 'Edge'
            if event.user_type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED and event.ui_element == self.InputList[self.ToId][0]:
                # print("enter this")
                if self.Mode == "Edge":
                    # print("Drops")
                    name = event.text
                    self.ToName = name
                    number = G.nameIDList[self.ToName]
                    self.Tid = number
                    ToPos = G.nodeInfo[number]['pos']
                    # print(ToPos)
                    # print(self.labelList[self.PosToId].text)
                    self.labelList[self.PosToId].set_text(
                        "Pos:({:d},{:d})".format(ToPos[0], ToPos[1]))
                    # self.labelList[self.PosToId].set_text("HHH")
            if event.user_type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED and event.ui_element == self.InputList[self.FromId][0]:
                # print("enter this")
                if self.Mode == "Edge":
                    print("Drops")
                    name = event.text
                    self.FromName = name
                    number = G.nameIDList[self.FromName]
                    self.Fid = number
                    FromPos = G.nodeInfo[number]['pos']
                    # print(ToPos)
                    # print(self.labelList[self.PosToId].text)
                    self.labelList[self.PosFromId].set_text(
                        "Pos:({:d},{:d})".format(FromPos[0], FromPos[1]))
                    # self.labelList[self.PosToId].set_text("HHH")
            if event.user_type == pygame_gui.UI_BUTTON_PRESSED and event.ui_element.text == 'Confirm':
                if self.Mode == 'Node':
                    x = self.checkInput(self.InputList[self.PosXLabelId])
                    y = self.checkInput(self.InputList[self.PosYLabelId])
                    Name = self.checkName(self.InputList[self.NameLabelId])
                    if x == None or y == None or Name == None:
                        pass
                    else:
                        self.xValue = x
                        self.yValue = y
                        self.NameValue = Name
                        self.window_survive = False
                        self.kill()
                else:
                    weight = self.checkInput(self.InputList[self.WeightId])
                    To = self.labelList[self.PosToId].text
                    From = self.labelList[self.PosFromId].text
                    if weight == None or To == 'Default' or From == 'Default':
                        pass
                    else:
                        self.weightValue = weight
                        self.To = To

                        self.From = From
                        self.window_survive = False
                        self.kill()
            elif event.user_type == pygame_gui.UI_BUTTON_PRESSED and event.ui_element.text == 'Cancel':
                self.window_survive = False
                self.kill()

    def checkInput(self, inputList):
        if inputList[0].text == '':
            return None
        else:
            return int(inputList[0].text)

    def checkName(self, inputList):
        if inputList[0].text == '':
            return None
        else:
            return inputList[0].text


class SetPropertyWindow(Window):
    StartLabelId = 0
    DestinationLabelId = 1
    RadiusLabelId = 2
    MinSizeLabelId = 3
    StartPosLabelId = 4
    DestinationPosLabelId = 5
    ConfirmBtnId = 6
    CancelBtnId = 7

    def create(self):
        self.type = 'Set'
        return pygame_gui.elements.ui_window.UIWindow(pygame.Rect(
            (200, 200), (self.width, self.height)), manager=self.manager)

    def addAllElement(self, G):
        nodeName = []
        for i in G.nodeIdList:
            nodeName.append(G.nodeInfo[i]['name'])
        self.add_label("      Start", 50, 50, 90, 20,
                       self.StartLabelId, self.window)
        self.add_label("Destination", 50, 80, 90, 20,
                       self.DestinationLabelId, self.window)
        self.add_label("     Radius", 50, 110, 90, 20,
                       self.RadiusLabelId, self.window)
        self.add_label("   Min_size", 50, 140, 90, 20,
                       self.MinSizeLabelId, self.window)
        self.add_dropdownMenu(self.StartLabelId, 140, 50, 90,
                              20, nodeName, G.parasList['Start'], self.window)
        self.startName = G.parasList['Start']
        self.add_label("Pos:({:d},{:d})".format(G.parasList['StartPos'][0], G.parasList['StartPos'][1]), 240, 50,
                       120, 20, self.StartPosLabelId, self.window)
        self.startPos = G.parasList['StartPos']
        # self.add_label("( )", 310, 50, 50, 20)
        self.add_dropdownMenu(self.DestinationLabelId, 140,
                              80, 90, 20, nodeName, G.parasList['Destination'], self.window)
        self.destinationName = G.parasList['Destination']
        self.add_label("Pos:({:d},{:d})".format(G.parasList['DestinationPos'][0], G.parasList['DestinationPos'][1]), 240, 80,
                       120, 20, self.DestinationPosLabelId, self.window)
        self.destinationPos = G.parasList['DestinationPos']
        self.add_inputEntry(self.RadiusLabelId, 140, 110,
                            70, 20, self.window)
        self.InputList[self.RadiusLabelId][0].set_text(
            str(G.parasList['Radius']))
        self.Radius = G.parasList['Radius']
        self.add_inputEntry(self.MinSizeLabelId, 140, 140,
                            60, 20, self.window)
        self.InputList[self.MinSizeLabelId][0].set_text(
            str(G.parasList['MinSize']))
        self.MinSize = G.parasList['MinSize']
        self.add_button("Confirm", 100, 280, 70, 50,
                        self.ConfirmBtnId, self.window)
        self.add_button("Cancel", 220, 280, 70, 50,
                        self.CancelBtnId, self.window)

    def handleEvent(self, event, G):
        # print(event.user_type)
        if event.type == pygame.USEREVENT:

            if event.user_type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED and event.ui_element == self.InputList[self.StartLabelId][0]:
                name = event.text
                self.startName = name
                number = G.nameIDList[name]
                self.startPos = G.nodeInfo[number]['pos']
                self.labelList[self.StartPosLabelId].set_text(
                    "Pos:({:d},{:d})".format(self.startPos[0], self.startPos[1]))
            elif event.user_type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED and event.ui_element == self.InputList[self.DestinationLabelId][0]:
                name = event.text
                self.destinationName = name
                number = G.nameIDList[name]
                self.destinationPos = G.nodeInfo[number]['pos']
                self.labelList[self.DestinationPosLabelId].set_text(
                    "Pos:({:d},{:d})".format(self.destinationPos[0], self.destinationPos[1]))
            elif event.user_type == pygame_gui.UI_BUTTON_PRESSED and event.ui_element.text == 'Confirm':
                Radius = self.checkInput(self.InputList[self.RadiusLabelId])
                MinSize = self.checkInput(self.InputList[self.MinSizeLabelId])
                if Radius == None or MinSize == None:
                    pass
                else:
                    self.Radius = Radius
                    self.MinSize = MinSize
                    self.window_survive = False
                    self.kill()
            elif event.user_type == pygame_gui.UI_BUTTON_PRESSED and event.ui_element.text == 'Cancel':
                self.Radius = None
                self.MinSize = None
                self.window_survive = False
                self.kill()
        else:
            pass

    def checkInput(self, inputList):
        if inputList == []:
            return None
        else:
            return int(inputList[0].text)


class DelNodeWindow(Window):
    Mode = 'Node'
    NodeId = 0
    EdgeId = 1
    LabelNameId = 2
    ConfirmBtnId = 3
    CancelBtnId = 4
    LabelFromId = 5
    LabelToId = 6
    PosFromId = 7
    PosToId = 8
    NameValue = None

    def create(self):
        self.type = 'Del Node'
        return pygame_gui.elements.ui_window.UIWindow(pygame.Rect(
            (200, 200), (self.width, self.height)), manager=self.manager)

    def addAllElement(self, G):
        self.window.set_display_title("Delete node")
        self.add_panel(0, 50, 400, 275, self.NodeId)
        self.add_panel(0, 50, 400, 275, self.EdgeId)
        self.add_button("Node", 50, 20, 70, 20, self.NodeId,
                        self.window)
        self.add_button("Edge", 130, 20, 70, 20, self.EdgeId,
                        self.window)
        # ------------Node----------
        self.add_label("Name:", 50, 100, 40, 20,
                       self.LabelNameId, self.panelList[self.NodeId])
        self.add_inputEntry(self.LabelNameId, 100, 100, 100,
                            20, self.panelList[self.NodeId])

        self.add_button("Confirm", 70, 220, 70, 50,
                        self.ConfirmBtnId, self.panelList[self.NodeId])

        self.add_button("Cancel", 160, 220, 70, 50,
                        self.CancelBtnId, self.panelList[self.NodeId])
        # ------------Edge----------
        self.add_label("From:", 50, 50, 40, 20, self.LabelFromId,
                       self.panelList[self.EdgeId])
        self.add_label("To  :", 50, 90, 40, 20, self.LabelToId,
                       self.panelList[self.EdgeId])
        nodeName = []
        for i in G.nodeIdList:
            nodeName.append(G.nodeInfo[i]['name'])
        self.add_dropdownMenu(self.LabelFromId, 100, 50, 100,
                              20, nodeName, "Default", self.panelList[self.EdgeId])
        self.add_dropdownMenu(self.LabelToId, 100, 90, 100,
                              20, nodeName, "Default", self.panelList[self.EdgeId])

        self.add_label("Pos:({:d},{:d})".format(0, 0), 210, 50,
                       120, 20, self.PosFromId, self.panelList[self.EdgeId])

        self.add_label("Pos:({:d},{:d})".format(0, 0), 210, 90,
                       120, 20, self.PosToId, self.panelList[self.EdgeId])

        self.add_button("Confirm", 70, 220, 70, 50,
                        self.ConfirmBtnId, self.panelList[self.EdgeId])
        self.add_button("Cancel", 160, 220, 70, 50,
                        self.CancelBtnId, self.panelList[self.EdgeId])

        self.BtnDict[self.NodeId].disable()
        self.panelList[self.EdgeId].hide()

    def handleEvent(self, event, G):
        if event.type == pygame.USEREVENT:
            if event.user_type == pygame_gui.UI_BUTTON_PRESSED and event.ui_element.text == 'Node':
                self.BtnDict[self.NodeId].disable()
                self.BtnDict[self.EdgeId].enable()
                self.panelList[self.EdgeId].hide()
                self.panelList[self.NodeId].show()
                self.Mode = 'Node'
            elif event.user_type == pygame_gui.UI_BUTTON_PRESSED and event.ui_element.text == 'Edge':
                self.BtnDict[self.NodeId].enable()
                self.BtnDict[self.EdgeId].disable()
                self.panelList[self.EdgeId].show()
                self.panelList[self.NodeId].hide()
                self.Mode = 'Edge'
            if event.user_type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED and event.ui_element == self.InputList[self.LabelToId][0]:
                # print("enter this")
                if self.Mode == "Edge":
                    # print("Drops")
                    name = event.text
                    self.ToName = name
                    number = G.nameIDList[self.ToName]
                    ToPos = G.nodeInfo[number]['pos']
                    # print(ToPos)
                    # print(self.labelList[self.PosToId].text)
                    self.labelList[self.PosToId].set_text(
                        "Pos:({:d},{:d})".format(ToPos[0], ToPos[1]))
                    # self.labelList[self.PosToId].set_text("HHH")
            if event.user_type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED and event.ui_element == self.InputList[self.LabelFromId][0]:
                # print("enter this")
                if self.Mode == "Edge":
                    print("Drops")
                    name = event.text
                    self.FromName = name
                    number = G.nameIDList[self.FromName]
                    FromPos = G.nodeInfo[number]['pos']
                    # print(ToPos)
                    # print(self.labelList[self.PosToId].text)
                    self.labelList[self.PosFromId].set_text(
                        "Pos:({:d},{:d})".format(FromPos[0], FromPos[1]))
                    # self.labelList[self.PosToId].set_text("HHH")
            if event.user_type == pygame_gui.UI_BUTTON_PRESSED and event.ui_element.text == 'Confirm':
                if self.Mode == 'Node':
                    Name = self.checkName(self.InputList[self.LabelNameId])
                    if Name == None:
                        pass
                    else:
                        self.NameValue = Name
                        self.window_survive = False
                        self.kill()
                else:
                    To = self.labelList[self.PosToId].text
                    From = self.labelList[self.PosFromId].text
                    if To == 'Default' or From == 'Default':
                        pass
                    else:
                        self.To = To
                        self.From = From
                        self.window_survive = False
                        self.kill()
            elif event.user_type == pygame_gui.UI_BUTTON_PRESSED and event.ui_element.text == 'Cancel':
                self.window_survive = False
                self.kill()

    def checkInput(self, inputList):
        if inputList[0].text == '':
            return None
        else:
            return int(inputList[0].text)

    def checkName(self, inputList):
        if inputList[0].text == '':
            return None
        else:
            return inputList[0].text
