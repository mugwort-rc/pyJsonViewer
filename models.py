# -*- coding: utf-8 -*-

from PyQt4 import QtCore

class Progress:
    def __init__(self, model, maximum):
        self.model = model
        self.maximum = maximum
        self.current = 0

    def __enter__(self):
        self.model.startProgress.emit(0, self.maximum)
        self.current = 0
        return self

    def __exit__(self, type, value, traceback):
        self.model.finishProgress.emit()
        return type is None

    def update(self, value):
        self.current = value
        self.model.updateProgress.emit(self.current)

    def increment(self, value):
        self.update(self.current + value)

class JsonTreeNode(object):

    ARRAY = 1
    OBJECT = 2
    VALUE = 3

    def __init__(self, type, selector, parent=None):
        super(JsonTreeNode, self).__init__()
        self.type = type
        self.selector = selector
        self.parent = parent
        self.child = None

    def __len__(self):
        return len(self.keys())

    @property
    def type(self):
        return self._type
    @type.setter
    def type(self, type):
        self._type = type

    @property
    def selector(self):
        return self._selector
    @selector.setter
    def selector(self, selector):
        self._selector = selector

    @property
    def parent(self):
        return self._parent
    @parent.setter
    def parent(self, parent):
        self._parent = parent

    @property
    def child(self):
        if self._child is None:
            temp = []
            data = self.data
            root = self.root()
            with Progress(root._model, len(self)) as progress:
                for key in self.keys():
                    temp.append(self.create(key, data[key], self))
                    progress.increment(1)
            self._child = temp
        return self._child
    @child.setter
    def child(self, child):
        self._child = child

    @property
    def data(self):
        if self.isRoot():
            return self._source
        else:
            return self.parent.data[self.selector]

    @property
    def path(self):
        if self.isRoot():
            return []
        else:
            path = self.parent.path()
            path.append(self.selector)
            return path

    def root(self):
        if self.isRoot():
            return self
        else:
            return self.parent.root()

    def isRoot(self):
        return self.parent is None

    def keys(self):
        data = self.data
        if isinstance(data, list):
            return range(len(data))
        elif isinstance(data, dict):
            return data.keys()
        else:
            return []

    def key(self):
        if self.selector is None:
            return '#root'
        elif isinstance(self.selector, int):
            return '[{}]'.format(self.selector)
        elif isinstance(self.selector, str) or isinstance(self.selector, unicode):
            return u'["{}"]'.format(self.selector)

    def value(self):
        data = self.data
        if data is None:
            return 'null'
        elif isinstance(data, str) or isinstance(data, unicode):
            return u'"{}"'.format(data)
        elif isinstance(data, int) or isinstance(data, float):
            return '{}'.format(data)
        elif isinstance(data, bool):
            return 'true' if data else 'false'
        elif isinstance(data, list):
            return 'array({})'.format(len(data))
        elif isinstance(data, dict):
            return 'object({})'.format(len(data))

    @classmethod
    def create_root(cls, model, doc):
        result = cls.create(None, doc, None)
        result._model = model
        result._source = doc
        return result

    @classmethod
    def create(cls, selector, data, parent):
        result = None
        if isinstance(data, list):
            result = cls.create_array(selector, parent)
        elif isinstance(data, dict):
            result = cls.create_object(selector, parent)
        else:
            result = cls.create_value(selector, parent)
        return result

    @classmethod
    def create_array(cls, selector, parent):
        return JsonTreeNode(type=cls.ARRAY, selector=selector, parent=parent)

    @classmethod
    def create_object(cls, selector, parent):
        return JsonTreeNode(type=cls.OBJECT, selector=selector, parent=parent)

    @classmethod
    def create_value(cls, selector, parent):
        return JsonTreeNode(type=cls.VALUE, selector=selector, parent=parent)

class JsonTreeModel(QtCore.QAbstractItemModel):

    startProgress = QtCore.pyqtSignal(int, int)
    updateProgress = QtCore.pyqtSignal(int)
    finishProgress = QtCore.pyqtSignal()

    def __init__(self, parent):
        super(JsonTreeModel, self).__init__(parent)
        self._json = None

    def setJsonDocument(self, json):
        self.beginResetModel()
        self.json = JsonTreeNode.create_root(self, json)
        self.endResetModel()

    def reset(self):
        self.beginResetModel()
        self.json = None
        self.endResetModel()

    def columnCount(self, parent=QtCore.QModelIndex()):
        return 2

    def rowCount(self, parent=QtCore.QModelIndex()):
        if self.json is None:
            return 0
        if not parent.isValid():
            return 1  # root
        node = parent.internalPointer()
        return len(node)

    def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):
        if role != QtCore.Qt.DisplayRole:
            return QtCore.QVariant()
        if orientation != QtCore.Qt.Horizontal:
            return QtCore.QVariant()
        if section == 0:
            return self.tr('Key')
        elif section == 1:
            return self.tr('Value')
        return QtCore.QVariant()

    def hasChildren(self, parent=QtCore.QModelIndex()):
        if not parent.isValid():
            return True
        node = parent.internalPointer()
        return len(node) > 0

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if self.json is None:
            return QtCore.QVariant()
        if not index.isValid():
            return QtCore.QVariant()
        if role != QtCore.Qt.DisplayRole:
            return QtCore.QVariant()
        node = index.internalPointer()
        if index.column() == 0:
            return node.key()
        elif index.column() == 1:
            return node.value()
        return QtCore.QVariant()

    def index(self, row, column, parent=QtCore.QModelIndex()):
        if not parent.isValid():
            return self.createIndex(row, column, self.json)
        node = parent.internalPointer()
        return self.createIndex(row, column, node.child[row])

    def parent(self, index):
        if not index.isValid():
            return QtCore.QModelIndex()
        node = index.internalPointer()
        if node.parent is None:
            return QtCore.QModelIndex()
        if node.parent.parent is None:
            return self.index(0, 0)
        return self.createIndex(node.parent.parent.child.index(node.parent), 0, node.parent)

    @property
    def json(self):
        return self._json
    @json.setter
    def json(self, json):
        self._json = json

