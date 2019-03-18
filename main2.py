import sys
from PyQt4.QtCore import *
from PyQt4.QtGui import *
#from PyQt5.QtWidgets import *
import json
import uuid


#
# TODO fix the inversion between inputConnector and outputConnector 
# in serialisation
# 
data = [
            { "label":"constante" ,"nodes" :[ { "type": "void","output":[{"type": "int"}],"input": [] } ]},
            {"label":"operation" ,"nodes" : [{ "type": "add","output":[{"type":"void"}],"input":[{"type":"int"},{"type":"int"}] }] }
        ]

class WindowClass(QMainWindow):
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)
        self.view = ViewClass()
        self.setCentralWidget(self.view)
        self.nodesEditor = QNodesEditor(self)
        self.nodesEditor.install(self.view.s)

        self.toolBar = QToolBar(self)
        self.addToolBar(Qt.TopToolBarArea, self.toolBar)

        self.statusbar = QStatusBar(self)
        #self.statusbar.setObjectName(_fromUtf8("statusbar"))
        self.setStatusBar(self.statusbar)

        self.menubar = QMenuBar(self)
        self.setMenuBar(self.menubar)
        self.menu_file = QMenu(self.menubar)
        self.menu_file.setTitle('File')
        self.menubar.addAction(self.menu_file.menuAction())

        # exit action
        self.menu_action_exit = QAction(self)
        self.menu_action_exit.setText("Exit")
        self.menu_action_exit.triggered.connect(self.close)
        self.menubar.addAction(self.menu_action_exit)

        self.menu_file.addAction('New',self.actionNew)
        self.menu_file.addAction('Load',self.actionLoad)
        self.menu_file.addAction('Save',self.actionSave)
        self.menu_file.addAction('Save As',self.actionSaveAs)

    def actionNew(self):
        pass
    
    def actionLoad(self):
        self.nodesEditor.load()
    
    def actionSave(self):
        self.nodesEditor.save()
    
    def actionSaveAs(self):
        pass

class MenuAction(QAction):
    def __init__(self,label, parent=None):
        super(MenuAction, self).__init__(label, parent)

    def setTypeNode(self,typenode):
        self.typenode = typenode

    def typeNode(self):
        return self.typenode


class ViewClass(QGraphicsView):
    def __init__(self, parent=None):
        QGraphicsView.__init__(self, parent)

        self.menuaction = []

        self.setDragMode(QGraphicsView.RubberBandDrag)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.s = SceneClass()
        self.setScene(self.s)
        self.setRenderHint(QPainter.Antialiasing)

        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.viewContextMenu)
        self.initAction()


    def initAction(self):
        for typestr in data:
            #print(typestr)
            #self.action_addNode = QAction(u"Add Node %s " % ( data["data"][typestr]["type"] ), self)
            for nodesa in typestr["nodes"]:
                action = MenuAction(u"Add Node %s " % ( typestr["label"] ), self)
                action.setTypeNode(nodesa)
                #self.action_addNode = QAction(u"Add Node", self)
                action.triggered.connect(self.addNode)
                self.menuaction.append(action)

    def addNode(self):
        print(self.sender())
        return self.s.addNode(self.mapToScene(self.mapFromGlobal( self.menu.pos()) ),self.sender().typeNode())

    def viewContextMenu(self, p):

        self.menu = QMenu(self)
        for a in self.menuaction:
            self.menu.addAction(a)

        self.menu.exec_(self.mapToGlobal(p))



class QNodesEditor(QObject):
    def __init__(self, parent):
        super(QNodesEditor, self).__init__(parent)
        self.connection = None
        self.edgeCreated = None

    def install(self, scene):
        self.scene = scene
        self.scene.installEventFilter(self)

    def itemAt(self, position):
        items = self.scene.items(QRectF( position - QPointF(1,1) , QSizeF(3,3) ))

        for item in items:
            if isinstance( item,  Connector):
                return item

        return None

    def save(self):

        result = []
        for item in self.scene.items():
            if isinstance(item,Node):
                #print(item)
                result.append(item.serialize())
        #print(self.connection)
        #print(self.edgeCreated) 
        print(result)
        with open('data.json', 'w') as outfile:
            json.dump(result, outfile)

    def load(self):
        with open('data.json', 'r') as outfile:
            result = json.load(outfile)
            allnodeInput = {}
            allnodeOutput = {}
            for r in result:
                n = self.scene.addNode(QPointF(r["pos"]["x"],r["pos"]["y"]),r)
                for iconc in n.inputConnector:
                    allnodeInput[iconc.uuid] = iconc
                for oconc in n.outputConnector:
                    allnodeOutput[oconc.uuid] = oconc
                #print(n.outputConnector)
            print(allnodeInput)
            print(allnodeOutput)
            for r in result:
                # TODO inverse input and output Connector
                for iconn,oconn in r["connection"]:
                    #on = allnodeOutput[oconn]
                    allnodeInput[iconn].loadEdge(allnodeOutput[oconn])
                    #print("%s %s " % (iconn,oconn))


    def eventFilter(self, object, event):
        if event.type() == QEvent.GraphicsSceneMousePress:

            if event.button() == Qt.LeftButton:
                item = self.itemAt(event.scenePos())
                if item != None:
                    self.connection = item
                    self.edgeCreated = item.createEdge(event)

                    #item.setInputConnection(event.scenePos())
                    """
                    self.connection = QNEConnection(None)
                    self.scene.addItem(self.connection)

                    self.connection.setPort1(item)
                    self.connection.setPos1(item.scenePos())
                    self.connection.setPos2(event.scenePos())
                    self.connection.updatePath()
                    """

                    return super(QNodesEditor, self).eventFilter(object, event)

            elif event.button() == Qt.RightButton:
                item = self.itemAt(event.scenePos())
                if item != None:
                    print ( "Mouse Right %s " % ( item.type() ) )

                """
                if item and (item.type() == Connector.Type or item.type() == Node.Type):
                    if item.type() == QNEConnection.Type:
                        item.delete()
                    elif item.type() == QNEBlock.Type:
                        item.delete()
                """
                return super(QNodesEditor, self).eventFilter(object, event)


        elif event.type() == QEvent.GraphicsSceneMouseMove:
            pass
            #if self.connection:
            #    self.connection.setPos2(event.scenePos())
            #    self.connection.updatePath()
            #    return super(QNodesEditor, self).eventFilter(object, event)


        elif event.type() == QEvent.GraphicsSceneMouseRelease:
            #if self.connection and event.button() == Qt.LeftButton:
            item = self.itemAt(event.scenePos())

            if self.edgeCreated != None:
                if self.edgeCreated.isCompatible(item):
                    self.edgeCreated.target = item
                    self.edgeCreated = None
                else:
                    self.edgeCreated.source.removeEdge(self.edgeCreated)
                    self.scene.removeItem(self.edgeCreated)
                    self.edgeCreated = None

                """
                else:
                    if self.edgeCreated is not None:
                        self.edgeCreated.source.removeEdge(self.edgeCreated)
                        self.scene.removeItem(self.edgeCreated)
                        self.edgeCreated = None
                """

                """
                if item and item.type() == Connector.Type:
                    port1 = self.connection.port1()
                    port2 = item

                    if port1.block() != port2.block() and port1.isOutput() != port2.isOutput() and not port1.isConnected(port2):

                        self.connection.setPos2(port2.scenePos())
                        self.connection.setPort2(port2)
                        self.connection.updatePath()
                        self.connection = None

                        return True

                self.connection.delete()
                self.connection = None
                """
        return super(QNodesEditor, self).eventFilter(object, event)
                #return True

        #return super(QNodesEditor, self).eventFilter(object, event)


class SceneClass(QGraphicsScene):
    grid = 30

    def __init__(self, parent=None):
        QGraphicsScene.__init__(self, QRectF(-1000, -1000, 2000, 2000), parent)


    def drawBackground(self, painter, rect):
        painter.fillRect(rect, QColor(130, 130, 130))
        left = int(rect.left()) - int((rect.left()) % self.grid)
        top = int(rect.top()) - int((rect.top()) % self.grid)
        right = int(rect.right())
        bottom = int(rect.bottom())
        lines = []
        for x in range(left, right, self.grid):
            lines.append(QLineF(x, top, x, bottom))
        for y in range(top, bottom, self.grid):
            lines.append(QLineF(left, y, right, y))
        painter.setPen(QPen(QColor(50, 50, 50)))
        painter.drawLines(lines)

    def mouseDoubleClickEvent(self, event):
        # self.addNode(event.scenePos())
        QGraphicsScene.mouseMoveEvent(self, event)


    def mousePressEvent(self, event):
        if event.button() == Qt.RightButton:
            if len(self.selectedItems()) == 2:
                edge = Edge(self.selectedItems()[0], self.selectedItems()[1])
                self.addItem(edge)
        QGraphicsScene.mousePressEvent(self, event)

    def addNode(self,pos, typenode):
        print(typenode)
        if typenode["type"] =="int":
            node = NodeInt(typenode["type"],typenode["input"],typenode["output"])
        elif typenode["type"] =="add":
            node = NodeAdd(typenode["type"],typenode["input"],typenode["output"])
        else:
            node = Node(typenode["type"],typenode["input"],typenode["output"])

        self.addItem(node)
        node.setPos(pos)
        return node

"""
  Class Edge.
"""
"""
class Edge(QGraphicsLineItem):
    def __init__(self, source, dest, parent=None):
        QGraphicsLineItem.__init__(self, parent)
        self.source = source
        self.dest = dest
        self.source.addEdge(self)
        self.dest.addEdge(self)
        self.setPen(QPen(Qt.red, 1.75))
        self.adjust()

    def adjust(self):
        self.prepareGeometryChange()
        self.setLine(QLineF(self.dest.pos(), self.source.pos()))
"""



class Edge(QGraphicsPathItem):
    """A connection between two Knobs."""

    def __init__(self,  parent= None):
        QGraphicsPathItem.__init__(self,parent)

        self.lineColor = QColor(10, 10, 10)
        self.removalColor = Qt.red
        self.thickness = 1

        self.source = None
        self.target = None

        self.sourcePos = QPointF(0, 0)
        self.targetPos = QPointF(0, 0)

        self.curv1 = 0.6
        self.curv3 = 0.4

        self.curv2 = 0.2
        self.curv4 = 0.8

        self.setAcceptHoverEvents(True)


    def updatePath(self):
        """Adjust current shape based on Knobs and curvature settings."""
        if self.source:
            self.sourcePos = self.source.mapToScene(
                self.source.boundingRect().center())

        if self.target:
            self.targetPos = self.target.mapToScene(
                self.target.boundingRect().center())


        path = QPainterPath()
        path.moveTo(self.sourcePos)

        dx = self.targetPos.x() - self.sourcePos.x()
        dy = self.targetPos.y() - self.sourcePos.y()

        ctrl1 = QPointF(self.sourcePos.x() + dx * self.curv1,
                               self.sourcePos.y() + dy * self.curv2)
        ctrl2 = QPointF(self.sourcePos.x() + dx * self.curv3,
                               self.sourcePos.y() + dy * self.curv4)
        path.cubicTo(ctrl1, ctrl2, self.targetPos)
        self.setPath(path)

    def paint(self, painter, option, widget):
        """Paint Edge color depending on modifier key pressed or not."""

        self.setPen(QPen(self.lineColor, self.thickness))

        #self.setBrush(Qt.NoBrush)
        self.setZValue(-1)
        self.updatePath()
        super(Edge, self).paint(painter, option, widget)

    def isCompatible(self, connector):
        if connector is None:
            return False

        if self.source.isCompatible(connector):
            return True
        return False


class GraphLineEdit(QLineEdit):
    def __init__(self,connector,text, parent=None):
        super(GraphLineEdit,self).__init__(text,parent)
        self.connector = connector

"""
  Class Connector
"""
class Connector(QGraphicsEllipseItem):
    Type = QGraphicsItem.UserType +1

    def __init__(self,rect, parent=None):
        self.uuid = str(uuid.uuid4())
        self.mousehover = False
        self.parent = parent
        QGraphicsEllipseItem.__init__(self,rect, parent)
        #self.setFlags(QGraphicsItem.ItemIsSelectable)

        self.createSpecificGui()
        self.edges = []

        self.setAcceptHoverEvents(True)
        self.setZValue(2)
        self.value = None

    def paint(self, painter, option, widget):
        bbox = self.boundingRect()
        if self.mousehover:
            painter.setBrush(QBrush(QColor(255,255,0)))
        else:
            painter.setBrush(QBrush(QColor(130, 130, 130)))

        painter.drawEllipse(bbox)

        if len(self.edges) > 0:
            painter.setBrush(QBrush(QColor(255,0,0)))
            bbox2 = QRectF(bbox)
            # bbox2 -=  QMargins(5, 5, 5 ,5)
            painter.drawEllipse(bbox2)

    def hoverEnterEvent(self, event):
        """Change the Knob's rectangle color."""
        #print("hoverEnterEvent")
        self.mousehover = True
        self.update()

    def hoverLeaveEvent(self, event):
        """Change the Knob's rectangle color."""
        self.mousehover = False
        #print("hoverLeaveEvent")
        self.update()
        #super(Connector, self).hoverLeaveEvent(event)

    """
    def setInputConnection(self, scenePos):
        self.newEdge = Edge()
        self.newEdge.source = self
        #self.newEdge.targetPos = event.scenePos()
        self.newEdge.targetPos = scenePos
        self.newEdge.updatePath()

        scene = self.scene()
        if self.newEdge not in scene.items():
            scene.addItem(self.newEdge)
    """

    def loadEdge(self, target):
        self.newEdge = Edge()
        self.newEdge.source = self
        self.newEdge.target = target
        self.edges.append(self.newEdge)
        scene = self.scene()
        if self.newEdge not in scene.items():
            scene.addItem(self.newEdge)


    def createEdge(self, event):
        self.newEdge = Edge()
        self.newEdge.source = self
        self.newEdge.targetPos = event.scenePos()
        self.newEdge.updatePath()

        self.edges.append(self.newEdge)

        scene = self.scene()
        if self.newEdge not in scene.items():
            scene.addItem(self.newEdge)

        return self.newEdge

    def removeEdge(self,event):
        self.update()
        self.newEdge.source = None
        self.edges.pop()

    def setValue(self, value):
        for e in self.edges:
            if e.target is not None:
                e.target.setInputValue(value)

    def setInputValue(self, value):
        print(self.parent)
        self.value = value
        self.parent.execute()

    def mousePressEvent(self, event):
        pass
        # print("mousePressEvent")

    def mouseMoveEvent(self, event):
        if self.newEdge:
            #print("mouseMoveEvent dragging ")
            self.newEdge.targetPos = event.scenePos()
            self.newEdge.updatePath()

    def createSpecificGui(self):
        pass
    """
    def mouseReleaseEvent(self, event):
        print("mouseReleaseEvent")
    """

    def isCompatible(self, connector):
        return False


class ConnectorOutput(Connector):
    def isCompatible(self, connector):
        if isinstance(connector,ConnectorInput):
            return True
        return False

class ConnectorInput(Connector):
    def isCompatible(self, connector):
        if isinstance(connector,ConnectorOutput):
            return True
        return False


#class Node(QGraphicsRectItem):
class Node(QGraphicsObject):
    def __init__(self, label, inputc, outputc,parent=None):
 #       QGraphicsRectItem.__init__(self, rect, parent)
        QGraphicsObject.__init__(self, parent)

        #print(inputc)
        #print(outputc)
        self.isSelected = False

        self.label = label
        self.inputc = inputc
        self.outputc = outputc
        self.edges = []
        self.inputConnector = []
        self.outputConnector = []
        self.setZValue(1)
        self.setFlags(QGraphicsItem.ItemIsMovable |
                      QGraphicsItem.ItemIsSelectable |
                      QGraphicsItem.ItemSendsGeometryChanges)

        self.label = QGraphicsTextItem(self.getLabel(),self)
        self.createSpecificGui()
        self.createInputConnector()
        self.createOutputConnector()

    def getNbInput(self):
        return len(self.inputc)

    def getNbOutput(self):
        return len(self.outputc)

    def getLabel(self):
        return self.label

    def getType(self):
        return "int"

    def createSpecificGui(self):
        pass

    def createInputConnector(self):
        for n in range(self.getNbInput()):
            ic = ConnectorInput(QRectF(-10, 25*n+50, 20, 20),self)
            if "uid" in self.inputc[n]:
                ic.uuid = self.inputc[n]["uid"]
            else:
                self.inputc[n]["uid"] = ic.uuid

            self.inputConnector.append( ic )
            label = QGraphicsTextItem(("%d" % (n)),self)
            label.setPos(10,25*n+50)

    def createOutputConnector(self):
        for n in range(self.getNbOutput()):
            connector = ConnectorOutput(QRectF(90, 25*n+50, 20, 20),self)
            self.outputConnector.append(connector)
            if "uid" in self.outputc[n]:
                connector.uuid = self.outputc[n]["uid"]
            else:
                self.outputc[n]["uid"] = connector.uuid 


            if self.outputc[n]["type"]=="int":
                proxy = QGraphicsProxyWidget(self)
                widget = GraphLineEdit(connector,"")
                widget.textChanged.connect(self.valueChanged)
                widget.setMaximumWidth(80)
                proxy.setWidget(widget)
                br = proxy.boundingRect()
                proxy.setPos(90 - br.width() ,25*n+50)
            else:
                label = QGraphicsTextItem(("%d" % (n)),self)
                br = label.boundingRect()
                label.setPos(90 - br.width() ,25*n+50)


            """
            label = QGraphicsTextItem(("%d" % (n)),self)
            br = label.boundingRect()
            label.setPos(90 - br.width() ,25*n+50)
            """


    def boundingRect(self):
        nb = max(self.getNbInput(),self.getNbOutput())
        return QRectF( 0, 0, 100, nb*30 + 50)

    def paint(self, painter, option, widget):
        if self.isSelected:
            painter.setBrush(Qt.darkGray)
            painter.setPen(Qt.blue)
        else:
            painter.setBrush(Qt.lightGray)

        painter.drawRect( self.boundingRect() )

    def addEdge(self, edge):
        self.edges.append(edge)

    def itemChange(self, change, value):
        """
        if change == QGraphicsItem.ItemSelectedChange:
            self.isSelected = True
        else:
            self.isSelected = False
        """

        if change == QGraphicsItem.ItemPositionHasChanged:
            for edge in self.edges:
                edge.adjust()

        return QGraphicsItem.itemChange(self, change, value)

    def mousePressEvent(self, event):
        self.isSelected = True
        #self.child
        self.update()
        QGraphicsItem.mousePressEvent(self, event)

    def mouseReleaseEvent(self, event):
        self.isSelected = False
        self.update()
        QGraphicsItem.mouseReleaseEvent(self, event)

    def setValue(self,value):
        print(value)
        self.execute()

    def execute(self):
        pass

    def valueChanged(self,text):
        self.sender().connector.setValue(text)
        # for connect in self.outputConnector:
        #    connect.setValue(text)

    def serialize(self):
        print("SERIALIZE ")
            
        result = {}
        result["type"] = self.getType()
        result["input"] = self.inputc # self.getinput()
        result["output"] = self.outputc # self.getoutput()
        result["pos"] = {}
        result["pos"]["x"] =self.scenePos().x()
        result["pos"]["y"] =self.scenePos().y()
        #result['inputuuid'] = []
        #result['outputuuid'] = []
        """ 
        for ic in self.inputConnector:
            result['inputuuid'].append(ic.uuid)
        for oc in self.outputConnector:
            result['outputuuid'].append(oc.uuid)
        """
        """
        for output in self.outputConnector:
            for edge in output.edges:
                result("%s %s " % (edge.source.uuid, edge.target.uuid)) 
        """
        result["connection"] = []
        for output in self.outputConnector:
            for edge in output.edges:
                result["connection"].append((edge.target.uuid, edge.source.uuid))        
        return result

class NodeAdd(Node):

    def createSpecificGui(self):
        proxy = QGraphicsProxyWidget(self)
        self.widget = QLabel("    ")
        proxy.setWidget(self.widget)
        proxy.setPos(10,30)

    def execute(self):
        if self.inputConnector[0].value is not None and self.inputConnector[1].value is not None:
            computeValue = (int(self.inputConnector[0].value) + int(self.inputConnector[1].value))
            self.widget.setText("%d" % computeValue)
            for outc in self.outputConnector:
                outc.setValue(computeValue)

    def getType(self):
        return "add"


class NodeInt(Node):
    def createSpecificGui(self):
        proxy = QGraphicsProxyWidget(self)
        widget = QLineEdit("")
        widget.textChanged.connect(self.valueChanged)
        widget.setMaximumWidth(80)
        proxy.setWidget(widget)
        proxy.setPos(10,30)

    def getType(self):
        return "NodeInt"

    def valueChanged(self,text):
        for connect in self.outputConnector:
            connect.setValue(text)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    wd = WindowClass()
    wd.show()
    sys.exit(app.exec_())