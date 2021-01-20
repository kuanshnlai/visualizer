import sys
import pygame
import pygame_gui
from component import *
from routingGUI import *
from pygame.locals import *
import networkx as nx
import threading


def checkInput(inputEntry):
    return int(inputEntry.get_text())


def handleBtnEvent(event, BtnList):
    for b in BtnList:
        if event.ui_element == b:
            text = b.text
            b.disable()
        else:
            b.enable()
    return text


def handleControlEvent(event, BtnList):
    for b in BtnList:
        if event.ui_element == b:
            text = b.text
    return text


def handleSelectList(mode, optionList, selectionList):
    selectionList.set_item_list(optionList[mode])


def handleLayout(mode, panelDict, panelList):
    for p in panelList:
        if p in panelDict[mode]:
            p.show()
        else:
            p.hide()


def handleControlBtn(controlBtnList, allBtn):
    for b in allBtn:
        if b in controlBtnList:
            b.enable()
        else:
            b.disable()


def animation(graphRegion, surface, frameList, manager):
    for frame in frameList:
        surface.blit(frame, (0, 0))
        pygame.display.update()
        graphRegion.set_image(surface)
        pygame.time.wait(500)
        manager.update(1)
        manager.draw_ui(window_surface)
        pygame.display.update()


def CSanimation(graphRegion, surface, frameList, manager, cs, playMode):
    count = 0
    clock = pygame.time.Clock()
    time_delta = clock.tick(60)/1000
    rotate = 0
    for frame in frameList:
        # print(count)

        while playMode[0] == 'pause':
            manager.update(time_delta)
            manager.draw_ui(window_surface)
            if playMode[0] == 'play':
                print("change")
        if frameList[count] in cs.rotateFrameList:
            doRotateAnimation(graphRegion, surface,
                              frameList, manager, cs, frameList[count], count, playMode)
            rotate += 1

        if playMode[0] == 'previous':
            if count == 0:
                print("count = 0")
            else:
                count -= 1
                surface.blit(frameList[count], (0, 0))
                pygame.display.update()
                graphRegion.set_image(surface)
                pygame.time.delay(500)
                manager.update(time_delta)
                manager.draw_ui(window_surface)
                pygame.display.update()
                playMode[0] = 'pause'
        surface.blit(frameList[count], (0, 0))
        pygame.display.update()
        graphRegion.set_image(surface)
        pygame.time.delay(500)
        manager.update(time_delta)
        manager.draw_ui(window_surface)
        pygame.display.update()
        count += 1


# def doRotateAnimation(graphRegion, surface, frameList, manager, cs, frame, count):
#     # print("-----------rotate-------")
#     hing_point = cs.rotateFrameList[frame]['Start'][0]
#     end_point = cs.rotateFrameList[frame]['Start'][1]
#     endfinal = cs.rotateFrameList[frame]['Final'][1]
#     r = cs.rotateFrameList[frame]['R']
#     curve = Curve(hing_point, end_point, cs.radius, surface)
#     # print(hing_point, endfinal, end_point)
#     frames = curve.rotate(endfinal, cs.graph)
#     clock = pygame.time.Clock()
#     time_delta = clock.tick(60)/1000
#     for f in frames:
#         # print(count)
#         count += 1
#         surface.blit(f, (0, 0))
#         pygame.display.update()
#         graphRegion.set_image(surface)
#         manager.update(time_delta)
#         manager.draw_ui(window_surface)

#         # pygame.display.update()
#     return count

def doRotateAnimation(graphRegion, surface, frameList, manager, cs, frame, count, playMode):
    # print(cs.rotateFrameList[frame])
    for index in range(0, len(cs.rotateFrameList[frame]['Start'])):
        # print("I", index)
        hing_point = cs.rotateFrameList[frame]['Start'][index][0]
        end_point = cs.rotateFrameList[frame]['Start'][index][1]
        endfinal = cs.rotateFrameList[frame]['Final'][index][1]
        r = cs.rotateFrameList[frame]['R'][index]
        curve = Curve(hing_point, end_point, r, surface)
        frames = curve.rotate(endfinal, cs.graph)
        clock = pygame.time.Clock()
        time_delta = clock.tick(60)/1000
        for f in frames:
            # print(count)
            count += 1
            surface.blit(f, (0, 0))
            # pygame.display.update()
            if playMode[0] == 'previous':
                return
            while playMode[0] == 'pause':
                manager.update(time_delta)
                manager.draw_ui(window_surface)
                if playMode[0] == 'play':
                    print("change")
            graphRegion.set_image(surface)
            manager.update(time_delta)
            manager.draw_ui(window_surface)

            # pygame.display.update()
    return


def runAlgo(graph, width, height, graphRegion, surface, manager, playMode, finish):
    cs = AdaptiveCS(graph, width, height)
    cs.run()
    frameList = cs.frameList
    CSanimation(graphRegion, surface, frameList, manager, cs, playMode)
    finish[0] = True
    playMode[0] = 'init'
    print("finish")


width, height = 1530, 700
selectPanelWidth, selectPanelHeight = 210, height
controlPanelOffsetX, controlPanelOffsetY, controlPanelWidth, controlPanelHeight = 220, 50, 890, 80
graphPanelOffsetX, graphPanelOffsetY, graphPanelWidth, graphPanelHeight = 220, 80, 890, 620
arrayPanelOffsetX, arrayPanelOffsetY, arrayPanelWidth, arrayPanelHeight = 1120, 50, 400, 310
consoleOffsetX, consoleOffsetY, consoleWidth, consoleHeight = 1120, 360, 400, 310
commandLineOffsetX, commandLineOffsetY, commandLineWidth, commandLineHeight = 1120, 670, 400, 30

backgroundColor = (81, 98, 111)
menu = []
BtnList = []
allControlBtnList = []
optionList = {"Home": ["Manual", "Guide", "About"], "Routing": ["Adaptive CS", "CS", " Distance vector routing", "Link state routing"],
              "Algorithm": ["1", "2", "3", "4"]}
# Panel manager call handle panel to manage panel
panelDict = {"Home": [], "Routing": [], "Algorithm": []}
panelList = []
mode = "Home"
controlBtnStateList = {"NoMethod": [], "CSMethod": {"NoGraph": [], "Play": [], "Pause": [
]}, "OtherMethod": {"NoGraph": [], "Play": [], "Pause": []}}  # 各個演算法有哪些button
pygame.init()
pygame.font.init()


# G = nx.Graph()
# test = graph(G)
# test.set_frame_size(890, 620)
# test.add_node_graph("A", 1, (255, 0, 0), (430, 300))
# test.add_node_graph("B", 2, (0, 255, 0), (100, 550))
# test.add_edge_graph((1, 2), (255, 1, 255), 1)
# test.printf()
# finalFrame = test.frames[len(test.frames)-1]
# rotateFrameList = []
# rotateFrameList = rotate(finalFrame, (430, 300), 50)
window_surface = pygame.display.set_mode((width, height))
surf = pygame.Surface((890, 620))
pygame.display.set_caption("VISUALIZER")
manager = pygame_gui.UIManager((width, height))

# -----------Button--------------
HomeBtn = pygame_gui.elements.UIButton(relative_rect=pygame.Rect(
    (210, 0), (100, 50)), text="Home", manager=manager)
HomeBtn.disable()
routingBtn = pygame_gui.elements.UIButton(relative_rect=pygame.Rect(
    (320, 0), (100, 50)), text="Routing", manager=manager)

# AlgorithmBtn = pygame_gui.elements.UIButton(relative_rect=pygame.Rect(
#     (370, 0), (100, 50)), text="Algorithm", manager=manager)
# ----------Panel---------------
selectListPanel = pygame_gui.elements.ui_panel.UIPanel(
    relative_rect=pygame.Rect((0, 0), (selectPanelWidth, height)), manager=manager, starting_layer_height=1)
controlPanel = pygame_gui.elements.ui_panel.UIPanel(
    relative_rect=pygame.Rect((controlPanelOffsetX, controlPanelOffsetY), (controlPanelWidth, controlPanelHeight)), manager=manager, starting_layer_height=1)
graphPanel = pygame_gui.elements.ui_panel.UIPanel(relative_rect=pygame.Rect(
    (graphPanelOffsetX, graphPanelOffsetY), (graphPanelWidth, graphPanelHeight)), manager=manager, starting_layer_height=1)

arrayPanel = pygame_gui.elements.ui_panel.UIPanel(relative_rect=pygame.Rect(
    (arrayPanelOffsetX, arrayPanelOffsetY), (arrayPanelWidth, arrayPanelHeight)), manager=manager, starting_layer_height=1)
consolePanel = pygame_gui.elements.ui_panel.UIPanel(relative_rect=pygame.Rect(
    (consoleOffsetX, consoleOffsetY), (consoleWidth, consoleHeight)), manager=manager, starting_layer_height=1)
commandLinePanel = pygame_gui.elements.ui_panel.UIPanel(relative_rect=pygame.Rect(
    (commandLineOffsetX, commandLineOffsetY), (commandLineWidth, commandLineHeight)), manager=manager, starting_layer_height=1)
# ----------control BTN list-----------
playbutton = pygame_gui.elements.UIButton(relative_rect=pygame.Rect(
    (10, 0), (50, 30)), text="play", manager=manager, container=controlPanel, parent_element=controlPanel)
allControlBtnList.append(playbutton)
pausebutton = pygame_gui.elements.UIButton(relative_rect=pygame.Rect(
    (70, 0), (50, 30)), text="pause", manager=manager, container=controlPanel, parent_element=controlPanel)
allControlBtnList.append(pausebutton)
stopbutton = pygame_gui.elements.UIButton(relative_rect=pygame.Rect(
    (130, 0), (50, 30)), text="stop", manager=manager, container=controlPanel, parent_element=controlPanel)
allControlBtnList.append(stopbutton)

addnodebutton = pygame_gui.elements.UIButton(relative_rect=pygame.Rect(
    (190, 0), (70, 30)), text="Add Node", manager=manager, container=controlPanel, parent_element=controlPanel)
allControlBtnList.append(addnodebutton)

deletenodebutton = pygame_gui.elements.UIButton(relative_rect=pygame.Rect(
    (270, 0), (100, 30)), text="Delete Node", manager=manager, container=controlPanel, parent_element=controlPanel)
allControlBtnList.append(deletenodebutton)
previousbutton = pygame_gui.elements.UIButton(relative_rect=pygame.Rect(
    (380, 0), (70, 30)), text="previous", manager=manager, container=controlPanel, parent_element=controlPanel)
allControlBtnList.append(previousbutton)
nextbutton = pygame_gui.elements.UIButton(relative_rect=pygame.Rect(
    (460, 0), (50, 30)), text="next", manager=manager, container=controlPanel, parent_element=controlPanel)
allControlBtnList.append(nextbutton)

# addedgebutton = pygame_gui.elements.UIButton(relative_rect=pygame.Rect(
#     (380, 0), (70, 30)), text="Add Edge", manager=manager, container=controlPanel, parent_element=controlPanel)

# allControlBtnList.append(addedgebutton)

# deleteedgebutton = pygame_gui.elements.UIButton(relative_rect=pygame.Rect(
#     (460, 0), (100, 30)), text="Delete Edge", manager=manager, container=controlPanel, parent_element=controlPanel)

# allControlBtnList.append(deleteedgebutton)

speedtxtlabel = pygame_gui.elements.ui_label.UILabel(relative_rect=pygame.Rect(
    (650, 5), (50, 20)), manager=manager, parent_element=controlPanel, container=controlPanel, text="Speed:")
speedlabel = pygame_gui.elements.ui_label.UILabel(relative_rect=pygame.Rect(
    (700, 5), (30, 20)), manager=manager, parent_element=controlPanel, container=controlPanel, text="1.0")
speedaddbutton = pygame_gui.elements.UIButton(relative_rect=pygame.Rect(
    (740, 0), (20, 30)), text="+", manager=manager, container=controlPanel, parent_element=controlPanel)
speedminusbutton = pygame_gui.elements.UIButton(relative_rect=pygame.Rect(
    (760, 0), (20, 30)), text="-", manager=manager, container=controlPanel, parent_element=controlPanel)

allControlBtnList.append(speedaddbutton)
allControlBtnList.append(speedminusbutton)

setpropertybutton = pygame_gui.elements.UIButton(relative_rect=pygame.Rect(
    (570, 0), (60, 30)), text="Set", manager=manager, container=controlPanel, parent_element=controlPanel)
allControlBtnList.append(setpropertybutton)
# processbar = pygame_gui.elements.ui_screen_space_health_bar.UIScreenSpaceHealthBar(
#     relative_rect=pygame.Rect((600, 0), (150, 30)), container=controlPanel, parent_element=controlPanel, manager=manager,)
# ---------Label------------------
selectLabel = pygame_gui.elements.ui_label.UILabel(
    relative_rect=pygame.Rect((0, 0), (selectPanelWidth, 20)), manager=manager, parent_element=selectListPanel, container=selectListPanel, text="Selection")
graphLabel = pygame_gui.elements.ui_label.UILabel(relative_rect=pygame.Rect(
    (0, 0), (120, 20)), manager=manager, parent_element=graphPanel, container=graphPanel, text="Graph tracer")
arrayLabel = pygame_gui.elements.ui_label.UILabel(relative_rect=pygame.Rect(
    (0, 0), (120, 20)), manager=manager, parent_element=arrayPanel, container=arrayPanel, text="Array tracer")
consoleLabel = pygame_gui.elements.ui_label.UILabel(relative_rect=pygame.Rect(
    (0, 0), (80, 20)), manager=manager, parent_element=consolePanel, container=consolePanel, text="Console")
# --------console ----------------
consoleTextBox = pygame_gui.elements.UITextBox(html_text="", relative_rect=pygame.Rect(
    (0, 20), (consoleWidth, consoleHeight-20)), manager=manager, parent_element=controlPanel, container=consolePanel)
# --------command line------------
commandLineEntry = pygame_gui.elements.ui_text_entry_line.UITextEntryLine(relative_rect=pygame.Rect(
    (0, 0), (commandLineWidth, commandLineHeight)), manager=manager, container=commandLinePanel, parent_element=commandLinePanel)

g = pygame.Surface((graphPanelWidth, graphPanelHeight-30))
graphRegion = pygame_gui.elements.ui_image.UIImage(relative_rect=pygame.Rect(
    (0, 30), (graphPanelWidth, graphPanelHeight-30)), manager=manager, container=graphPanel, parent_element=graphPanel, image_surface=g)


# controlBtnStateList = {"NoMethod":[],"CSMeThod":{"NoGraph":[],"Play":[],"Pause":[]}}

controlBtnStateList["NoMethod"] = []
controlBtnStateList["CSMethod"]["NoGraph"] = [addnodebutton]
controlBtnStateList["CSMethod"]["Play"] = [
    pausebutton, stopbutton, speedaddbutton, speedminusbutton, previousbutton, nextbutton]
controlBtnStateList["CSMethod"]["Pause"] = [
    playbutton, addnodebutton, deletenodebutton, setpropertybutton]
controlBtnStateList["OtherMethod"]["NoGraph"] = [addnodebutton]
controlBtnStateList["OtherMethod"]["Play"] = [
    pausebutton, stopbutton, speedaddbutton, speedminusbutton]
controlBtnStateList["OtherMethod"]["Pause"] = [
    playbutton, addnodebutton, deletenodebutton, setpropertybutton]


controlPanel.hide()
graphPanel.hide()
arrayPanel.hide()
consolePanel.hide()
commandLinePanel.hide()
# ------select List
selectionList = pygame_gui.elements.ui_selection_list.UISelectionList(
    relative_rect=pygame.Rect((0, 20), (selectPanelWidth, height)), manager=manager, container=selectListPanel, item_list=optionList["Home"])


panelList.append(selectListPanel)
panelList.append(controlPanel)
panelList.append(graphPanel)
panelList.append(arrayPanel)
panelList.append(consolePanel)
panelList.append(commandLinePanel)

panelDict["Home"].append(selectListPanel)

panelDict["Routing"].append(selectListPanel)
panelDict["Routing"].append(controlPanel)
panelDict["Routing"].append(graphPanel)
panelDict["Routing"].append(arrayPanel)
panelDict["Routing"].append(consolePanel)
panelDict["Routing"].append(commandLinePanel)

panelDict["Algorithm"].append(selectListPanel)

BtnList.append(HomeBtn)
BtnList.append(routingBtn)
# BtnList.append(AlgorithmBtn)
background = pygame.Surface((width, height))

background.fill(backgroundColor)
colok = pygame.time.Clock()
pygame.display.update()
newWindowElement = dict()
newWindowSurvive = False
window = None
G = graph(nx.Graph())
G.set_frame_size(graphPanelWidth, graphPanelHeight)
NodeNum = 0
playMode = ['init']
finish = [True]
while True:
    time_delta = colok.tick(60)/1000
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.USEREVENT:
            if event.user_type == pygame_gui.UI_BUTTON_PRESSED and event.ui_element in BtnList:
                mode = handleBtnEvent(event, BtnList)
                handleSelectList(mode, optionList, selectionList)
            if event.user_type == pygame_gui.UI_BUTTON_PRESSED and event.ui_element in allControlBtnList:
                t = handleControlEvent(event, allControlBtnList)
                if t == 'Add Node':
                    window = AddNodeWindow(400, 400, manager)
                    window.addAllElement(G)
                    newWindowSurvive = True
                elif t == 'play':
                    # cs = CSRouting(G, graphPanelWidth, graphPanelHeight)
                    # cs.run()
                    # frameList = cs.frameList
                    # CSanimation(graphRegion, g, frameList, manager, cs)
                    playMode[0] = 'play'
                    if finish[0]:
                        finish[0] = False
                        th = threading.Thread(target=runAlgo, args=(
                            G, graphPanelWidth, graphPanelHeight, graphRegion, g, manager, playMode, finish))
                        th.start()
                    # cs = AdaptiveCS(G, graphPanelWidth, graphPanelHeight)
                    # cs.run()
                    # frameList = cs.frameList
                    # CSanimation(graphRegion, g, frameList, manager, cs)
                elif t == 'pause':
                    print("pause now")
                    playMode[0] = 'pause'
                elif t == 'stop':
                    pass
                elif t == 'next':
                    print("next")
                elif t == 'previous':
                    playMode[0] = 'previous'

                elif t == 'Delete Node':
                    window = DelNodeWindow(400, 400, manager)
                    window.addAllElement(G)
                    newWindowSurvive = True
                elif t == '+':
                    pass
                elif t == '-':
                    pass
                elif t == 'Set':
                    window = SetPropertyWindow(400, 400, manager)
                    window.addAllElement(G)
                    newWindowSurvive = True
            if newWindowSurvive and window.type == 'Add Node':
                # print("enter this")
                window.handleEvent(event, G)
                newWindowSurvive = window.window_survive
                if window.Mode == 'Node' and newWindowSurvive == False and (window.xValue != None and window.yValue != None):
                    # G.add_node_graph(window.NameValue, NodeNum, (0, 0, 255),
                    #                  (window.xValue, window.yValue))
                    # NodeNum += 1
                    # G.parasList['Destination'] = G.nodeInfo[len(
                    #     G.nodes)-1]['name']
                    # G.parasList['DestinationPos'] = G.nodeInfo[len(
                    #     G.nodes)-1]['pos']

                    # ===========test case========
                    # G.add_node_graph("A", 0, (0, 0, 255), (300, 200))
                    # G.add_node_graph("B", 1, (0, 0, 255), (399, 200))
                    # G.add_node_graph("C", 2, (0, 0, 255), (249, 284))
                    # G.add_node_graph("D", 3, (0, 0, 255), (449, 284))
                    # G.add_node_graph("E", 4, (0, 0, 255), (300, 368))
                    # G.add_node_graph("F", 5, (0, 0, 255), (399, 368))
                    # G.add_node_graph("G", 6, (0, 0, 255), (499, 480))
                    G.add_node_graph("S", 0, (0, 0, 255), (500, 500))
                    G.add_node_graph("V0", 1, (0, 0, 255), (490, 460))
                    G.add_node_graph("V1", 2, (0, 0, 255), (430, 450))
                    G.add_node_graph("V2", 3, (0, 0, 255), (380, 400))
                    G.add_node_graph("V3", 4, (0, 0, 255), (420, 350))
                    G.add_node_graph("V4", 5, (0, 0, 255), (435, 310))
                    G.add_node_graph("V5", 6, (0, 0, 255), (490, 280))
                    G.add_node_graph("V6", 7, (0, 0, 255), (464, 305))
                    G.add_node_graph("V7", 8, (0, 0, 255), (470, 330))
                    G.add_node_graph("V8", 9, (0, 0, 255), (520, 320))
                    G.add_node_graph("V9", 10, (0, 0, 255), (370, 300))
                    G.add_node_graph("D", 11, (0, 0, 255), (570, 400))
                    G.parasList['Destination'] = G.nodeInfo[len(
                        G.nodes)-1]['name']
                    G.parasList['DestinationPos'] = G.nodeInfo[len(
                        G.nodes)-1]['pos']
                if window.Mode == 'Edge' and newWindowSurvive == False and (window.To != None and window.From != None and window.weightValue != None):
                    # G.add_edge_graph((window.Tid, window.Fid),
                    #                  (0, 0, 0), window.weightValue)
                    # print(window.ToName, window.FromName, window.weightValue)
                    G.add_edge_graph((0, 1), (0, 0, 0), 1)
                    G.add_edge_graph((0, 2), (0, 0, 0), 1)
                    G.add_edge_graph((1, 2), (0, 0, 0), 1)
                    G.add_edge_graph((2, 10), (0, 0, 0), 1)
                    G.add_edge_graph((2, 3), (0, 0, 0), 1)
                    G.add_edge_graph((3, 4), (0, 0, 0), 1)
                    G.add_edge_graph((4, 5), (0, 0, 0), 1)
                    G.add_edge_graph((5, 6), (0, 0, 0), 1)
                    G.add_edge_graph((6, 7), (0, 0, 0), 1)
                    G.add_edge_graph((7, 8), (0, 0, 0), 1)
                    G.add_edge_graph((8, 9), (0, 0, 0), 1)
                    G.add_edge_graph((9, 11), (0, 0, 0), 1)
            if newWindowSurvive and window.type == 'Set':
                window.handleEvent(event, G)
                newWindowSurvive = window.window_survive
                if newWindowSurvive == False and (window.Radius != None and window.MinSize != None):
                    G.parasList['Start'] = window.startName
                    G.parasList['StartPos'] = window.startPos
                    G.parasList['Destination'] = window.destinationName
                    G.parasList['DestinationPos'] = window.destinationPos
                    G.parasList['MinSize'] = window.MinSize
                    G.parasList['Radius'] = window.Radius
            if newWindowSurvive and window.type == 'Del Node':
                window.handleEvent(event, G)
                newWindowSurvive = window.window_survive
                if window.Mode == 'Node' and newWindowSurvive == False and window.NameValue != None:
                    G.del_node_graph(window.NameValue)
                    print("del ", window.NameValue)

        handleLayout(mode, panelDict, panelList)
        manager.process_events(event)

        if mode == "Routing":
            method = selectionList.get_single_selection()
            if method == None:
                methodState = 'NoMethod'
                handleControlBtn(
                    controlBtnStateList[methodState], allControlBtnList)
            if method == 'Adaptive CS':
                methodState = 'CSMethod'
                if(len(G.nodes) >= 1 and playMode[0] != 'play'):
                    if playState == 'NoGraph':
                        G.parasList['Start'] = G.nodeInfo[0]['name']
                        G.parasList['Destination'] = G.nodeInfo[len(
                            G.nodes)-1]['name']
                        G.parasList['StartPos'] = G.nodeInfo[0]['pos']
                        G.parasList['DestinationPos'] = G.nodeInfo[len(
                            G.nodes)-1]['pos']
                        G.parasList['MinSize'] = 30
                        G.parasList['Radius'] = 100
                    playState = 'Pause'
                elif playMode[0] == 'play':
                    playState = 'Play'
                elif playMode[0] == 'pause':
                    playState = 'Pause'
                else:
                    playState = 'NoGraph'

                handleControlBtn(
                    controlBtnStateList[methodState][playState], allControlBtnList)

            elif mode == "Home":
                pass
            elif mode == "Algorithm":
                pass
    if G.frames == []:
        finalFrame = pygame.Surface((graphPanelWidth, graphPanelHeight))
        finalFrame.fill((255, 255, 255))
    else:
        finalFrame = G.frames[len(G.frames)-1]
    manager.update(time_delta)
    if playMode[0] != 'play' and playMode[0] != 'pause':
        g.blit(finalFrame, (0, 0))
        graphRegion.set_image(g)
        window_surface.blit(background, (0, 0))
        manager.draw_ui(window_surface)
    pygame.display.update()
