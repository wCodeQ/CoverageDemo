#!/usr/bin/python
import re
import sys
import argparse

class DiffLineInfo:
    def __init__(self, startSubLine, subCount, startAddLine, addCount):
        self.startSubLine = startSubLine
        self.subCount = subCount
        self.startAddLine = startAddLine
        self.addCount = addCount

class DiffData:
    def __init__(self):
        self.infoFileName = ''
        self.diffLineInfoList = []


def main(args):
    # 解析diff文件
    diffDataList = parseDiffFile(args.diff)
    
    for diffData in diffDataList:
        print(diffData.infoFileName)
        for diffLineInfo in diffData.diffLineInfoList:
            print(diffLineInfo.__dict__)
    
    # 解析老info
    infoLineDataDic = parseOldInfo(args.source)

    print('处理前info行号信息')
    for fileName,infoLineDataList in infoLineDataDic.items():
        print(fileName)
        for infoLineData in infoLineDataList:
            print(infoLineData.__dict__)
    
    # 转换老info行号信息
    for diffData in diffDataList:
        newInfoLineData = transformOldInfoLineData(diffData, infoLineDataDic[diffData.infoFileName])
        infoLineDataDic[diffData.infoFileName] = newInfoLineData

    print('处理后info行号信息')
    for fileName,infoLineDataList in infoLineDataDic.items():
        print(fileName)
        for infoLineData in infoLineDataList:
            print(infoLineData.__dict__)

def getDiffContent(diffFilePath: str):
    with open(diffFilePath, 'r') as f:
        return f.readlines()

def parseDiffFile(diffFilePath: str):
    diffDataList: [DiffData] = []   # 存储文件diffData
    diffLines = getDiffContent(diffFilePath)
    diffLines.append('end of file')

    isDiffBlockStart = False     # 记录文件diff块的是否开始
    diffBlockEndLine = 0         # 记录判断diff块结束的行号
    diffBlockEndWithSubLine = True   # 标记判断diff块结束使用减的行号
    isNewDiff = False       # 记录需要统计的diff的是否开始
    startSubLine = 0
    subCount = 0
    startAddLine = 0
    addCount = 0

    diffData: DiffData
    for line in diffLines:
        if re.search('diff (.*)', line, re.M):
            #新文件
            fileNameIndex = line.rfind('/') + 1
            fileName = line[fileNameIndex: len(line) - 1]
            diffData = DiffData()
            diffData.infoFileName = fileName
            diffDataList.append(diffData)
            continue

        if (startAddLine,startSubLine)[diffBlockEndWithSubLine] >= diffBlockEndLine:
            isDiffBlockStart = False

        searchObj = re.search('@@(.*)@@', line, re.M)
        if searchObj:
            isDiffBlockStart = True
            # 寻找开始行号
            searchContents = searchObj.group().split(' ')
            subContent = searchContents[1]
            subLineAndCount = subContent.split(',')
            startSubLine = abs(int(subLineAndCount[0]))
            subCount = 0

            addContent = searchContents[2]
            addLineAndCount = addContent.split(',')
            startAddLine = abs(int(addLineAndCount[0]))
            addCount = 0

            if int(subLineAndCount[1]) > int(addLineAndCount[1]):
                diffBlockEndLine = startSubLine + int(subLineAndCount[1])
                diffBlockEndWithSubLine = True
            else:
                diffBlockEndLine = startAddLine + int(addLineAndCount[1])
                diffBlockEndWithSubLine = False
        else:
            if isDiffBlockStart:
                searchDiffObj = re.search('(\-|\+)(.*)', line, re.M)
                if searchDiffObj:
                    isNewDiff = True
                    if searchDiffObj.group().startswith('-'):
                        subCount += 1
                    else:
                        addCount += 1
                else:
                    if isNewDiff:
                        # 存储diff信息
                        diffData.diffLineInfoList.append(DiffLineInfo(startSubLine, subCount, startAddLine, addCount))
                        startSubLine += subCount + 1
                        startAddLine += addCount + 1
                        subCount = 0
                        addCount = 0
                        isNewDiff = False
                    else:
                        startSubLine += 1
                        startAddLine += 1
            else:
                startSubLine = 0
                subCount = 0
                startAddLine = 0
                addCount = 0
    
    return diffDataList



class InfoLineData:
    def __init__(self, lineNo, exeCount, funName = ''):
        self.lineNo = lineNo
        self.exeCount = exeCount
        self.funName = funName
        
def parseOldInfo(oldInfoPath: str):
    infoLineDataDic = {}
    infoLineDataList: [InfoLineData]
    fnTempDict: {}     # 存储函数和行号关系
    fileName: str
    with open(oldInfoPath, 'r') as f:
        for line in f.readlines():
            if line.startswith('SF:'):
                 # 开始新文件
                fileNameIndex = line.rfind('/') + 1
                fileName = line[fileNameIndex: len(line) - 1]
                infoLineDataList = []
                fnTempDict = {}
            elif line.startswith('DA:'):
                lineContent = line[3:]
                keyValues = lineContent.split(',')
                infoLineDataList.append(InfoLineData(int(keyValues[0]), int(keyValues[1])))
            elif line.startswith('FN:'):
                lineContent = line[3:]
                keyValues = lineContent.split(',')
                fnTempDict[keyValues[1]] = int(keyValues[0])
            elif line.startswith('FNDA:'):
                lineContent = line[5:]
                keyValues = lineContent.split(',')
                fnKey = keyValues[1]
                fnValue = keyValues[0]
                infoLineDataList.append(InfoLineData(fnTempDict[fnKey], int(fnValue), fnKey))
            elif line == 'end_of_record\n':
                # 文件结束
                sortedInfoLineDataList = sorted(infoLineDataList, key=lambda s: s.lineNo, reverse = True)
                infoLineDataDic[fileName] = sortedInfoLineDataList
    return infoLineDataDic

def transformOldInfoLineData(diffData: DiffData, infoLineDataList: [InfoLineData]):
    newInfoLineDataList = infoLineDataList
    # 匹配diff结果，修改info行号
    diffData.diffLineInfoList.reverse()
    for diffLineInfo in diffData.diffLineInfoList:
        # 先删除需要删除的行
        if diffLineInfo.subCount > 0:
            startRemoveLine = diffLineInfo.startSubLine
            endRemoveLine = startRemoveLine + diffLineInfo.subCount
            removeLineList = range(startRemoveLine, endRemoveLine)
            newInfoLineDataList = list(filter(lambda x: x.lineNo not in removeLineList, infoLineDataList))
        # 修改行号
        diffLineNo = diffLineInfo.addCount - diffLineInfo.subCount
        for infoLineData in newInfoLineDataList:
            if infoLineData.lineNo >= diffLineInfo.startSubLine:
                infoLineData.lineNo += diffLineNo
    return newInfoLineDataList
        
        
if __name__ == '__main__':
    parse = argparse.ArgumentParser()
    parse.add_argument('-d', '--diff', type=str, help='Diff file path')
    parse.add_argument('-s', '--source', type=str, help='Source file path')
    parse.add_argument('-o', '--output', type=str, help='Output file path')
    args = parse.parse_args()
    main(args)
