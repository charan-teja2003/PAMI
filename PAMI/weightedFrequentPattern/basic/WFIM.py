# WFMiner is one of the fundamental algorithm to discover weighted frequent patterns in a transactional database.
# It stores the database in compressed fp-tree decreasing the memory usage and extracts the
# patterns from tree.It employs downward closure property to  reduce the search space effectively.
#
# **Importing this algorithm into a python program**
#
#             from PAMI.weightFrequentPattern.basic import basic as alg
#
#             iFile = 'sampleDB.txt'
#
#             minSup = 10  # can also be specified between 0 and 1
#
#             obj = alg.basic(iFile, wFile, minSup, minWeight)
#
#             obj.mine()
#
#             frequentPatterns = obj.getPatterns()
#
#             print("Total number of Frequent Patterns:", len(frequentPatterns))
#
#             obj.savePatterns(oFile)
#
#             Df = obj.getPatternsAsDataFrame()
#
#             memUSS = obj.getMemoryUSS()
#
#             print("Total Memory in USS:", memUSS)
#
#             memRSS = obj.getMemoryRSS()
#
#             print("Total Memory in RSS", memRSS)
#
#             run = obj.getRuntime()
#
#             print("Total ExecutionTime in seconds:", run)
#

__copyright__ = """
 Copyright (C)  2021 Rage Uday Kiran

     This program is free software: you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation, either version 3 of the License, or
     (at your option) any later version.

     This program is distributed in the hope that it will be useful,
     but WITHOUT ANY WARRANTY; without even the implied warranty of
     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
     GNU General Public License for more details.

     You should have received a copy of the GNU General Public License
     along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

from PAMI.weightedFrequentPattern.basic import abstract as _fp
from typing import List, Dict, Tuple, Union, Generator
import pandas as pd
from deprecated import deprecated


_minSup = str()
_minWeight = int()
_miniWeight = int()
_maxWeight = int()
_weights = {}
_fp._sys.setrecursionlimit(20000)


class _Node:
    """
    A class used to represent the node of frequentPatternTree

    :Attributes:

        itemId: int
            storing item of a node

        counter: int
            To maintain the support of node

        parent: node
            To maintain the parent of node

        children: list
            To maintain the children of node

    :Methods:

        addChild(node)
            Updates the nodes children list and parent for the given node
    """

    def __init__(self, item: str, children: list) -> None:
        self.itemId = item
        self.counter = 1
        self.parent = None
        self.children = children

    def addChild(self, node: '_Node') -> None:
        """
        Retrieving the child from the tree

        :param node: Children node
        :type node: _Node
        :return: Updates the children nodes and parent nodes
        """
        self.children[node.itemId] = node
        node.parent = self


class _Tree:
    """
    A class used to represent the frequentPatternGrowth tree structure

    :Attributes:

        root : Node
            The first node of the tree set to Null.

        summaries : dictionary
            Stores the nodes itemId which shares same itemId

        info : dictionary
            frequency of items in the transactions

    :Methods:

        addTransaction(transaction, freq)
            adding items of  transactions into the tree as nodes and freq is the count of nodes
        getFinalConditionalPatterns(node)
            getting the conditional patterns from fp-tree for a node
        getConditionalPatterns(patterns, frequencies)
            sort the patterns by removing the items with lower minSup
        generatePatterns(prefix)
            generating the patterns from fp-tree
    """

    def __init__(self) -> None:
        self.root = _Node(None, {})
        self.summaries = {}
        self.info = {}

    def addTransaction(self, transaction: List[str], count: int) -> None:
        """
        Adding transaction into tree

        :param transaction: it represents the one transaction in database
        :type transaction: list
        :param count: frequency of item
        :type count: int
        :return: None
        """
        # This method takes transaction as input and returns the tree
        currentNode = self.root
        for i in range(len(transaction)):
            if transaction[i] not in currentNode.children:
                newNode = _Node(transaction[i], {})
                newNode.freq = count
                currentNode.addChild(newNode)
                if transaction[i] in self.summaries:
                    self.summaries[transaction[i]].append(newNode)
                else:
                    self.summaries[transaction[i]] = [newNode]
                currentNode = newNode
            else:
                currentNode = currentNode.children[transaction[i]]
                currentNode.freq += count

    def getFinalConditionalPatterns(self, alpha: str) -> Tuple[List[List[str]], List[int], Dict[str, int]]:
        """
        Generates the conditional patterns for a node

        :param alpha: node to generate conditional patterns
        :return: returns conditional patterns, frequency of each item in conditional patterns
        """
        finalPatterns = []
        finalFreq = []
        for i in self.summaries[alpha]:
            set1 = i.freq
            set2 = []
            while i.parent.itemId is not None:
                set2.append(i.parent.itemId)
                i = i.parent
            if len(set2) > 0:
                set2.reverse()
                finalPatterns.append(set2)
                finalFreq.append(set1)
        finalPatterns, finalFreq, info = self.getConditionalTransactions(finalPatterns, finalFreq)
        return finalPatterns, finalFreq, info

    @staticmethod
    def getConditionalTransactions(ConditionalPatterns: List[List[str]], conditionalFreq: List[int]) -> Tuple[List[List[str]], List[int], Dict[str, int]]:
        """
        To calculate the frequency of items in conditional patterns and sorting the patterns

        :param ConditionalPatterns: paths of a node
        :param conditionalFreq: frequency of each item in the path
        :return: conditional patterns and frequency of each item in transactions
        """
        global _minSup, _miniWeight
        pat = []
        freq = []
        data1 = {}
        for i in range(len(ConditionalPatterns)):
            for j in ConditionalPatterns[i]:
                if j in data1:
                    data1[j] += conditionalFreq[i]
                else:
                    data1[j] = conditionalFreq[i]
        up_dict = {k: v for k, v in data1.items() if v >= _minSup and v * _miniWeight > _minSup}
        count = 0
        for p in ConditionalPatterns:
            p1 = [v for v in p if v in up_dict]
            trans = sorted(p1, key=lambda x: (up_dict.get(x), -x), reverse=True)
            if len(trans) > 0:
                pat.append(trans)
                freq.append(conditionalFreq[count])
            count += 1
        return pat, freq, up_dict

    def generatePatterns(self, prefix: List[str]) -> Generator[Tuple[List[str], int], None, None]:
        """
        To generate the frequent patterns

        :param prefix: an empty list
        :return: Frequent patterns that are extracted from fp-tree
        """
        global _miniWeight, _maxWeight, _minWeight, _minSup
        for i in sorted(self.summaries, key=lambda x: (self.info.get(x), -x)):
            pattern = prefix[:]
            pattern.append(i)
            yield pattern, self.info[i]
            patterns, freq, info = self.getFinalConditionalPatterns(i)
            conditionalTree = _Tree()
            conditionalTree.info = info.copy()
            for pat in range(len(patterns)):
                conditionalTree.addTransaction(patterns[pat], freq[pat])
            if len(patterns) > 0:
                for q in conditionalTree.generatePatterns(pattern):
                    yield q


class WFIM(_fp._weightedFrequentPatterns):
    """
    About this algorithm
    ====================

    :Description: * WFMiner is one of the fundamental algorithm to discover weighted frequent patterns in a transactional database.
                  * It stores the database in compressed fp-tree decreasing the memory usage and extracts the patterns from tree.It employs employs downward closure property to  reduce the search space effectively.

    :Reference:  U. Yun and J. J. Leggett, “Wfim: weighted frequent itemset mining with a weight range and a minimum weight,”
           In:   Proceedings of the 2005 SIAM International Conference on Data Mining. SIAM, 2005, pp. 636–640.
                 https://epubs.siam.org/doi/pdf/10.1137/1.9781611972757.76

    :param  iFile: str :
                   Name of the Input file to mine complete set of weighted Frequent Patterns.
    :param  oFile: str :
                   Name of the output file to store complete set of weighted Frequent Patterns.
    :param  minSup: str or int or float:
                   minimum support thresholds were tuned to find the appropriate ranges in the limited memory
    :param  sep: str :
                   This variable is used to distinguish items from one another in a transaction. The default seperator is tab space. However, the users can override their default separator.


    :Attributes :

        iFile : file
            Input file name or path of the input file

        minSup: float or int or str
            The user can specify minSup either in count or proportion of database size.
            If the program detects the data type of minSup is integer, then it treats minSup is expressed in count.
            Otherwise, it will be treated as float.
            Example: minSup=10 will be treated as integer, while minSup=10.0 will be treated as float

        minWeight: float or int or str
            The user can specify minWeight either in count or proportion of database size.
            If the program detects the data type of minWeight is integer, then it treats minWeight is expressed in count.
            Otherwise, it will be treated as float.
            Example: minWeight=10 will be treated as integer, while minWeight=10.0 will be treated as float

        sep : str
            This variable is used to distinguish items from one another in a transaction. The default separator is tab space or \t.
            However, the users can override their default separator.

        oFile : file
            Name of the output file or the path of the output file

        startTime:float
            To record the start time of the mining process

        endTime:float
            To record the completion time of the mining process

        memoryUSS : float
            To store the total amount of USS memory consumed by the program

        memoryRSS : float
            To store the total amount of RSS memory consumed by the program

        Database : list
            To store the transactions of a database in list

        mapSupport : Dictionary
            To maintain the information of item and their frequency

        lno : int
            it represents the total no of transactions

        tree : class
            it represents the Tree class

        finalPatterns : dict
            it represents to store the patterns

    :Methods :

        mine()
            Mining process will start from here
        getPatterns()
            Complete set of patterns will be retrieved with this function
        save(oFile)
            Complete set of frequent patterns will be loaded in to a output file
        getPatternsAsDataFrame()
            Complete set of frequent patterns will be loaded in to a dataframe
        getMemoryUSS()
            Total amount of USS memory consumed by the mining process will be retrieved from this function
        getMemoryRSS()
            Total amount of RSS memory consumed by the mining process will be retrieved from this function
        getRuntime()
            Total amount of runtime taken by the mining process will be retrieved from this function
        creatingItemSets()
            Scans the dataset or dataframes and stores in list format
        frequentOneItem()
            Extracts the one-frequent patterns from transactions

    Execution methods
    =================


    **Terminal command**


    .. code-block:: console

       Format:

       (.venv) $ python3 basic.py <inputFile> <weightFile> <outputFile> <minSup> <minWeight>

       Example Usage:

       (.venv) $ python3 basic.py sampleDB.txt weightSample.txt patterns.txt 10.0 3.4

    .. note:: minSup and maxPer will be considered in support count or frequency


    **Calling from a python program**

    .. code-block:: python

            from PAMI.weightFrequentPattern.basic import basic as alg

            iFile = 'sampleDB.txt'

            minSup = 10  # can also be specified between 0 and 1

            obj = alg.basic(iFile, wFile, minSup, minWeight)

            obj.mine()

            frequentPatterns = obj.getPatterns()

            print("Total number of Frequent Patterns:", len(frequentPatterns))

            obj.savePatterns(oFile)

            Df = obj.getPatternsAsDataFrame()

            memUSS = obj.getmemoryUSS()

            print("Total Memory in USS:", memUSS)

            memRSS = obj.getMemoryRSS()

            print("Total Memory in RSS", memRSS)

            run = obj.getRuntime()

            print("Total ExecutionTime in seconds:", run)

    Credits
    =======


             The complete program was written by P.Likhitha  under the supervision of Professor Rage Uday Kiran.
    """

    __startTime = float()
    __endTime = float()
    _minSup = str()
    __finalPatterns = {}
    _iFile = " "
    _oFile = " "
    _sep = " "
    __memoryUSS = float()
    __memoryRSS = float()
    __Database = []
    __mapSupport = {}
    __lno = 0
    __tree = _Tree()
    __rank = {}
    __rankDup = {}

    def __init__(self, iFile: str, wFile: str, minSup: str, minWeight: int, sep: str='\t') -> None:
        super().__init__(iFile, wFile, minSup, minWeight, sep)

    def __creatingItemSets(self) -> None:
        """
        Storing the complete transactions of the database/input file in a database variable

        :return: None
        """
        self.__Database = []
        if isinstance(self._iFile, _fp._pd.DataFrame):
            if self._iFile.empty:
                print("its empty..")
            i = self._iFile.columns.values.tolist()
            if 'Transactions' in i:
                self.__Database = self._iFile['Transactions'].tolist()

            # print(self.Database)
        if isinstance(self._iFile, str):
            if _fp._validators.url(self._iFile):
                data = _fp._urlopen(self._iFile)
                for line in data:
                    line.strip()
                    line = line.decode("utf-8")
                    temp = [i.rstrip() for i in line.split(self._sep)]
                    temp = [x for x in temp if x]
                    self.__Database.append(temp)
            else:
                try:
                    with open(self._iFile, 'r', encoding='utf-8') as f:
                        for line in f:
                            line.strip()
                            temp = [i.rstrip() for i in line.split(self._sep)]
                            temp = [x for x in temp if x]
                            # print(len(temp))
                            self.__Database.append(temp)
                except IOError:
                    print("File Not Found")
                    quit()

    def _scanningWeights(self) -> None:
        """
        Storing the weights of the variables in input file in a weights variable

        :return: None
        """
        global _weights
        _weights = {}
        if isinstance(self._wFile, _fp._pd.DataFrame):
            items, weights = [], []
            if self._wFile.empty:
                print("its empty..")
            i = self._wFile.columns.values.tolist()
            if 'items' in i:
                items = self._wFile['items'].tolist()
            if 'weights' in i:
                weights = self._wFile['weights'].tolist()
            for i in range(len(weights)):
                _weights[items[i]] = weights[i]

            # print(self.Database)
        if isinstance(self._wFile, str):
            if _fp._validators.url(self._wFile):
                data = _fp._urlopen(self._wFile)
                for line in data:
                    line.strip()
                    line = line.decode("utf-8")
                    temp = [i.rstrip() for i in line.split(self._sep)]
                    temp = [x for x in temp if x]
                    _weights[temp[0]] = temp[1]
            else:
                try:
                    with open(self._wFile, 'r', encoding='utf-8') as f:
                        for line in f:
                            line.strip()
                            temp = [i.rstrip() for i in line.split(self._sep)]
                            temp = [x for x in temp if x]
                            s = int(float(temp[1]))
                            _weights[temp[0]] = s
                except IOError:
                    print("File Not Found")
                    quit()

    def __convert(self, value: Union[int, float, str]) -> Union[int, float]:
        """
        To convert the type of user specified minSup value.

        :param value: user specified minSup value
        :return: converted type
        """
        if type(value) is int:
            value = int(value)
        if type(value) is float:
            value = (len(self.__Database) * value)
        if type(value) is str:
            if '.' in value:
                value = float(value)
                value = (len(self.__Database) * value)
            else:
                value = int(value)
        return value

    def __frequentOneItem(self) -> List[str]:
        """
        Generating One frequent items sets

        :return: list
        """
        global _maxWeight
        self.__mapSupport = {}
        for tr in self.__Database:
            for i in range(0, len(tr)):
                if tr[i] not in self.__mapSupport:
                    self.__mapSupport[tr[i]] = 1
                else:
                    self.__mapSupport[tr[i]] += 1
        self.__mapSupport = {k: v for k, v in self.__mapSupport.items() if v >= self._minSup and v * _maxWeight > self._minSup}
        genList = [k for k, v in sorted(self.__mapSupport.items(), key=lambda x: x[1], reverse=True)]
        self.__rank = dict([(index, item) for (item, index) in enumerate(genList)])
        return genList

    def __updateTransactions(self, itemSet: List[str]) -> List[List[int]]:
        """
        Updates the items in transactions with rank of items according to their support

        :Example: oneLength = {'a':7, 'b': 5, 'c':'4', 'd':3}
                    rank = {'a':0, 'b':1, 'c':2, 'd':3}

        :param itemSet: list of one-frequent items
        :return: list
        """
        list1 = []
        for tr in self.__Database:
            list2 = []
            for i in range(len(tr)):
                if tr[i] in itemSet:
                    list2.append(self.__rank[tr[i]])
            if len(list2) >= 1:
                list2.sort()
                list1.append(list2)
        return list1

    @staticmethod
    def __buildTree(transactions: List[List[int]], info: Dict[int, int]) -> '_Tree':
        """
        Builds the tree with updated transactions

        :param transactions: updated transactions
        :param info: support details of each item in transactions.
        :return: Transactions compressed in fp-tree
        """
        rootNode = _Tree()
        rootNode.info = info.copy()
        for i in range(len(transactions)):
            rootNode.addTransaction(transactions[i], 1)
        return rootNode

    def __savePeriodic(self, itemSet: List[int]) -> str:
        """
        The duplication items and their ranks

        :param itemSet: frequent itemSet that generated
        :return: patterns with original item names.
        """
        temp = str()
        for i in itemSet:
            temp = temp + self.__rankDup[i] + "\t"
        return temp

    @deprecated(
        "It is recommended to use 'mine()' instead of 'mine()' for mining process. Starting from January 2025, 'mine()' will be completely terminated.")
    def startMine(self) -> None:
        """
        main program to start the operation

        :return: None
        """
        self.mine()

    def mine(self) -> None:
        """
        main program to start the operation

        :return: None
        """
        global _minSup, _minWeight, _miniWeight, _maxWeight, _weights
        self.__startTime = _fp._time.time()
        if self._iFile is None:
            raise Exception("Please enter the file path or file name:")
        if self._minSup is None:
            raise Exception("Please enter the Minimum Support")
        self.__creatingItemSets()
        self._scanningWeights()
        _weights = {k: v for k, v in _weights.items() if v >= _minWeight}
        _maxWeight = max([s for s in _weights.values()])
        _miniWeight = min([s for s in _weights.values()])
        self._minSup = self.__convert(self._minSup)
        _minSup = self._minSup
        itemSet = self.__frequentOneItem()
        updatedTransactions = self.__updateTransactions(itemSet)
        for x, y in self.__rank.items():
            self.__rankDup[y] = x
        info = {self.__rank[k]: v for k, v in self.__mapSupport.items()}
        __Tree = self.__buildTree(updatedTransactions, info)
        patterns = __Tree.generatePatterns([])
        self.__finalPatterns = {}
        for k in patterns:
            s = self.__savePeriodic(k[0])
            self.__finalPatterns[str(s)] = k[1]
        print("Weighted Frequent patterns were generated successfully using basic algorithm")
        self.__endTime = _fp._time.time()
        self.__memoryUSS = float()
        self.__memoryRSS = float()
        process = _fp._psutil.Process(_fp._os.getpid())
        self.__memoryUSS = process.memory_full_info().uss
        self.__memoryRSS = process.memory_info().rss


    def getMemoryUSS(self) -> float:
        """

        Total amount of USS memory consumed by the mining process will be retrieved from this function

        :return: returning USS memory consumed by the mining process
        :rtype: float
        """

        return self.__memoryUSS

    def getMemoryRSS(self) -> float:
        """

        Total amount of RSS memory consumed by the mining process will be retrieved from this function.

        :return: returning RSS memory consumed by the mining process
        :rtype: float
        """

        return self.__memoryRSS

    def getRuntime(self) -> float:
        """

        Calculating the total amount of runtime taken by the mining process.

        :return: returning total amount of runtime taken by the mining process
        :rtype: float
        """

        return self.__endTime - self.__startTime

    def getPatternsAsDataFrame(self) -> pd.DataFrame:
        """

        Storing final frequent patterns in a dataframe.

        :return: returning frequent patterns in a dataframe
        :rtype: pd.DataFrame
        """

        dataframe = {}
        data = []
        for a, b in self.__finalPatterns.items():
            data.append([a.replace('\t', ' '), b])
            dataframe = _fp._pd.DataFrame(data, columns=['Patterns', 'Support'])
        return dataframe

    def save(self, outFile: str) -> None:
        """

        Complete set of frequent patterns will be loaded in to an output file.

        :param outFile: name of the output file
        :type outFile: csv file
        :return: None
        """
        self._oFile = outFile
        writer = open(self._oFile, 'w+')
        for x, y in self.__finalPatterns.items():
            s1 = x.strip() + ":" + str(y)
            writer.write("%s \n" % s1)

    def getPatterns(self) -> Dict[str, int]:
        """

        Function to send the set of frequent patterns after completion of the mining process.

        :return: returning frequent patterns
        :rtype: dict
        """
        return self.__finalPatterns

    def printResults(self) -> None:
        """
        This function is used to print the results
        """
        print("Total number of  Weighted Frequent Patterns:", len(self.getPatterns()))
        print("Total Memory in USS:", self.getMemoryUSS())
        print("Total Memory in RSS", self.getMemoryRSS())
        print("Total ExecutionTime in ms:",  self.getRuntime())

        


if __name__ == "__main__":
    _ap = str()
    if len(_fp._sys.argv) == 6 or len(_fp._sys.argv) == 7:
        if len(_fp._sys.argv) == 7:
            _ap = WFIM(_fp._sys.argv[1], _fp._sys.argv[3], _fp._sys.argv[4], _fp._sys.argv[5], _fp._sys.argv[6])
        if len(_fp._sys.argv) == 6:
            _ap = WFIM(_fp._sys.argv[1], _fp._sys.argv[3], _fp._sys.argv[4], _fp._sys.argv[5])
        _ap.mine()
        _ap.mine()
        print("Total number of Weighted Frequent Patterns:", len(_ap.getPatterns()))
        _ap.save(_fp._sys.argv[2])
        print("Total Memory in USS:",  _ap.getMemoryUSS())
        print("Total Memory in RSS", _ap.getMemoryRSS())
        print("Total ExecutionTime in ms:", _ap.getRuntime())
    else:
        print("Error! The number of input parameters do not match the total number of parameters provided")
