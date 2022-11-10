def parseMatrixRows(matrix, indexes):
    index = {}
    for i in indexes:
        index.update({indexes.index(i): i})
    newMatrix = matrix.reset_index(drop=True).rename(index=index)
    return newMatrix


def parseMatrixColumns(matrix, i):
    matrix.columns = i
    return matrix


def parseMatrixIndexes(matrix, i):
    x = parseMatrixColumns(matrix, i)
    return parseMatrixRows(x, i)
