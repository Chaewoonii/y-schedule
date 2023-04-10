import os

import pandas as pd


class MyUtill:
    def __init__(self):
        pass

    def getFileNames(self, path, fList):
        cover = []
        for f in fList:
            li = os.listdir(path+'/'+f)
            cover.append(li)

        return cover

    def printLi(self, li):
        for idx, c in enumerate(li):
            print(f'{idx+1}. {c}')

    def getPath(self, path):
        print('숫자를 입력하세요.(예:1)')
        li = os.listdir(path)
        self.printLi(li)
        userInput = int(input(''))
        fileName = li[userInput - 1]
        path = f'{path}/{fileName}'

        return path

    def getPath_FName(self, path):
        print('숫자를 입력하세요.(예:1)')
        li = os.listdir(path)
        self.printLi(li)
        userInput = int(input(''))
        fileName = li[userInput - 1]
        path = f'{path}/{fileName}'

        return path, fileName

    def mkdir(self,path,folderName):
        if os.path.isdir(path) == False:
            os.mkdir(f'{path}/{folderName}')

    #컬럼이름 변경

    #_x, _y삭제 함수
    def delXY(self, df):
        col = df.columns.to_list()

        for c in col:
            if c.endswith('_x') or c.endswith('_y'):
                df = df.rename(columns={c:c[:-2]})
            '''elif c.endswith('_new'):
                df = df.rename(columns={c:c[:-6]})'''

        return df

    def changeDfType(self, df):
        for i in df.columns:
            if df[i].dtype != 'object':
                df[i] = df.astype({i : 'object'}).dtypes

        return df

    def getPath_FileName(self, path):
        print('[MyUtill] getPath_FileName init!!!')
        path = path.split('/')
        fileName = path.pop(-1)
        path = '/'.join(path)
        return path, fileName



if __name__ == '__main__':
    '''path = 'C:/chaeun/talk_files/유성구 GIS 데이터 현행화'
    path1 = 'C:/chaeun/talk_files/유성구 GIS 데이터 현행화/기존데이터/건축과/'
    path2 = 'C:/chaeun/talk_files/유성구 GIS 데이터 현행화/새로받은 데이터/건축과/'
    fileName1 = '건축과_단독주택현황.csv'
    fileName2 = '건축과_단독주택.csv'
    mu = MyUtill()
    # cd = CheckData(path)
    try:
        df1 = pd.read_csv(f'{path1 + fileName1}', encoding='cp949', engine='python')
    except:
        df1 = pd.read_csv(f'{path1 + fileName1}', encoding='utf-8-sig', engine='python')

    try:
        df2 = pd.read_csv(f'{path2 + fileName2}', encoding='cp949', engine='python')
    except:
        df2 = pd.read_csv(f'{path2 + fileName2}', encoding='utf-8-sig', engine='python')

    date = df2['사용승인일'].to_list()

    date = mu.setDate(date)

    print(date)
    df2['date'] = date

    print(df2)'''



