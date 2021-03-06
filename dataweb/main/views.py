from cProfile import label
import mimetypes
import os
import time
from django.shortcuts import render
from django.http import HttpResponse
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import random
import csv
from django.shortcuts import render
from django.http import HttpResponse
import datetime
from django.core.files.storage import FileSystemStorage
from django.http import FileResponse
from sklearn.model_selection import train_test_split

from django.shortcuts import render
from plotly.offline import plot
import plotly.express as px
import plotly.graph_objects as go

# from .SqlQuery import SqlQuery

# Include the `fusioncharts.py` file which has required functions to embed the charts in html page
# from .fusioncharts import FusionCharts

# 초기값 설정
global sel_val
global inputfile
global selected_category_name
global selected_category_no
global selected_index
global selected_add_category
global selected_one_category
global df
global nodata
sel_val = 0.7
nodata = "파일을 선택해주세요   ---->"

# 초기화시켜줄 메소드
def reset():
    global sel_val
    global inputfile
    global selected_category_name
    global selected_category_no
    global selected_index
    global selected_add_category
    global selected_one_category
    global df
    global nodata
    sel_val = 0.7                       # 기본 초기값
    inputfile = None                    # 입력한 첨부파일
    selected_category_name = None       # 선택한 카테고리명
    selected_category_no = None         # 선택한 카테고리 번호
    selected_index = None               # 선택한 컬럼
    selected_add_category = None        # 예상 범주와 함께 보여줄 변수
    selected_one_category = None        # 선택한 컬럼 정보 및 꺾은선 그래프로 보여주기 위한 변수
    df = None
    nodata = "파일을 선택해주세요   ---->"

def firstSetting(req, data):
    global df
    global nodata
    # ip 가져오기
    ip = get_client_ip(req)
    data['ip'] = ip
    # ip 주소 .을 _로 바꾸기
    under_ip = str(ip).replace('.', '_')
    # 파일명
    filename = f"./temp/{ip}.csv"
    # csv 첨부파일 경로 지정
    path = f"temp/{ip}.csv"
    # path = "temp/58.238.38.231.csv"

    return ip, under_ip, filename, path

def dataButton(req, filename, data, path):   
    # 시간 측정
    start = time.time()
    global df
    global nodata
    # 초기화 버튼
    try:
        if 'clearAll' in req.POST:
            reset()
            # 만약 해당 경로에 같은 이름의 파일이 있는 경우 삭제
            if os.path.isfile(filename):
                os.remove(filename)
            
            return 0

    except:
        print("초기화 실패")
        return 0

    print("초기화 버튼 처리 시간 : ", time.time() - start)    
    
    # 사용자로부터 첨부파일 받아오기 
    try:
        # 첨부 파일 가져오기
        if 'inputfile' in req.FILES:
            inputfile = req.FILES['inputfile']

            # temp폴더에 IP주소명으로 첨부파일 저장하기
            fs = FileSystemStorage()

            # 만약 해당 경로에 같은 이름의 파일이 있는 경우 삭제
            if os.path.isfile(filename):
                os.remove(filename)

            # 파일 저장
            fs.save(filename, inputfile)

            # 이전에 입력한 항목 초기화
            reset()

            df = makedf(data, path)

            nodata = ""

            print("데이터프레임 처리 시간 : ", time.time() - start)    
            return 1

    except:
        # input data가 없으면 초기화하고 내용 없이 return
        print("첨부파일 받는 중 error 발생")
        reset()
        return 0

def makedf(data, path):
    # 받은 csv파일로 데이터프레임 만들기
    try:
        # 지정한 경로에 있는 csv 파일을 읽어오기
        df = pd.read_csv(path)
        return df

    except:
        print("데이터 프레임 만드는 중 error 발생")
        reset()
        return None

def index(req):
    # 시간 측정
    start = time.time()

    # 값 불러와 사용
    global sel_val
    global inputfile
    global selected_category_name
    global selected_category_no
    global selected_index
    global selected_add_category
    global selected_one_category
    global df
    global nodata

    # 리턴할 값 모음
    data = {}  

    # 초기 설정
    ip, under_ip, filename, path = firstSetting(req, data)
    print("초기 설정 이후 시간 : ", time.time() - start)

    # 초기화 버튼, 첨부파일 받아오기, 데이터프레임 만들기
    btnResult = dataButton(req, filename, data, path)
    print("데이터프레임 생성 이후 시간 : ", time.time() - start)
    data['nodata'] = nodata
    if btnResult == 0:
        return render(req, 'index.html', data)

    # df = makedf(data, path)

    try:
        data['rownum'] = str(len(df)) + "개"
        data['columnnum'] = str(len(df.columns)) + "개"

        size = os.path.getsize(path)
        data['filesize'] = str(round(size/(1024*1024), 2)) + "mb"

        return render(req, 'index.html', data)
    except:
        print("index 처리 중 error 발생")
        return render(req, 'index.html', data)

def category(req):
    # 시간 측정
    start = time.time()

    # 값 불러와 사용
    global sel_val
    global inputfile
    global selected_category_name
    global selected_category_no
    global selected_index
    global selected_add_category
    global selected_one_category
    global df

    # 리턴할 값 모음
    data = {}  

    # 초기 설정
    ip, under_ip, filename, path = firstSetting(req, data)

    # 초기화 버튼, 첨부파일 받아오기, 데이터프레임 만들기
    btnResult = dataButton(req, filename, data, path)
    data['nodata'] = nodata
    if btnResult == 0:
        return render(req, 'category.html', data)

    # df = makedf(data, path)
    

    # 전체 데이터프레임의 Null값을 0으로
    try:
        nz = None
        if 'sel_null_zero' in req.POST:
            nz = req.POST.get('sel_null_zero')
        if nz == 'sel_null_zero':
            df = df.fillna(0)
            # 만약 해당 경로에 같은 이름의 파일이 있는 경우 삭제
            if os.path.isfile(filename):
                os.remove(filename)
            print("기존 csv 삭제 후 시간 : ", time.time() - start)
            # 0으로 만든 데이터프레임 저장 (시간 오래걸림)
            df.to_csv(filename, index=None)
            print("새로 csv 저장 후 시간 : ", time.time() - start)
            # 데이터프레임을 새 데이터프레임으로 덮어씌우기
            df = pd.read_csv(path)
    except:
        print("전체 null 값 0 만드는 중 실패")

    print("데이터프레임 전체 null 시간 : ", time.time() - start)

    # 범주 생성
    try:    
        # 문자열일 경우 or
        # 유일하지 않고, 값을 가지고 있는게 1 이상이고 값 종류는 5개 이하인 것
        objectName = []
        # objeect type이 아닌 것들을 담을 리스트
        nonObjectName = []
        dt = df.dtypes
        for d in range(len(dt)):
            if dt[d] == object:
                objectName.append(dt.index[d])
            else:
                nonObjectName.append(dt.index[d])
                vc = df.iloc[:,d].value_counts()
                if vc.count() > 1 and vc.sort_values().values[0] > 1 and len(vc) <= 5:
                    objectName.append(dt.index[d])                 

        # 범주에 해당되는 값의 범주 이름을 리스트형으로 전달
        data['category'] = objectName    
    except:
        print("범주 생성 중 error 발생")       

    print("범주 생성 시간 : ", time.time() - start)    

    # 추가 변수 생성
    try:
        addValidation = list(set(objectName + nonObjectName))
        data['category_add'] = sorted(addValidation)
    except:
        print("추가 변수 생성 중 error 발생")

    print("추가 변수 생성 시간 : ", time.time() - start)

    # 선택한 범주 변수로 저장
    try:
        # selected_category의 이름을 가진 버튼이 선택된 경우 (범주)
        if 'selected_category' in req.POST:          
            # 버튼으로 선택한 것들을 받아오기
            selected_category_name = req.POST.get('selected_category')  
        # 버튼 선택한 기록이 있는 경우
        if selected_category_name != None:
            data['selected_category_name'] = selected_category_name 
    except:
        print("선택한 범주 데이터를 가져오는 중 error 발생")

    # 선택한 추가 범주 변수로 저장
    try:
        # selected_index의 이름을 가진 버튼이 선택된 경우 (컬럼)
        if 'selected_add_category' in req.POST:          
            # 버튼으로 선택한 것들을 받아오기
            selected_add_category = req.POST.get('selected_add_category')
        # 선택된 추가 컬럼이 있었거나 있는 경우
        if selected_add_category != None:
            data['selected_add_category_name'] = selected_add_category 
    except:
        print("선택한 추가 변수 데이터를 가져오는 중 error 발생")

    print("모든 변수 얻는 시간 : ", time.time() - start)

    # 선택한 범주 Data Type / Empty Cells / Unique Value 
    try:
        # 버튼 선택한 기록이 있는 경우
        if selected_category_name != None:
            # 타입 확인
            selVariableType = str(df[selected_category_name].dtype)
            # null 개수 확인
            selVariableNull = df[selected_category_name].isnull().sum()
            # unique 개수
            selVariableDistinctCount = len(df[selected_category_name].unique())
            # unique 리스트
            try:
                selVariableDistinctList = sorted(df[selected_category_name].unique())
            except:
                selVariableDistinctList = list(df[selected_category_name].unique())

        data['selVariableType'] = selVariableType
        data['selVariableNull'] = selVariableNull
        data['selVariableDistinctCount'] = selVariableDistinctCount
        data['selVariableDistinctList'] = selVariableDistinctList

    except:
        selected_category_name = None
        print("선택한 범주 정보 출력 중 error 발생")

    # 선택한 추가 변수 Data Type / Empty Cells / Unique Value 
    try:
        # 선택된 추가 컬럼이 있었거나 있는 경우
        if selected_add_category != None:
            # 타입 확인
            selAddVariableType = str(df[selected_add_category].dtype)
            # null 개수 확인
            selAddVariableNull = df[selected_add_category].isnull().sum()
            # unique 개수
            selAddVariableDistinctCount = len(df[selected_add_category].unique())
            # unique 리스트
            try:
                selAddVariableDistinctList = sorted(df[selected_add_category].unique())
            except:
                selAddVariableDistinctList = list(df[selected_add_category].unique())

        data['selAddVariableType'] = selAddVariableType
        data['selAddVariableNull'] = selAddVariableNull
        data['selAddVariableDistinctCount'] = selAddVariableDistinctCount
        data['selAddVariableDistinctList'] = selAddVariableDistinctList

    except:
        selected_add_category = None
        print("선택한 추가 변수 정보 출력 중 error 발생")

    print("데이터 타입, 널, 유니크 : ", time.time() - start)

    # 범주 선택 시 histogram 생성
    try:
        if selected_category_name != None:
            # 범주분포가 저장될 리스트
            category_graphs = []
            
            # Histogram 생성
            category_graphs.append(
                go.Histogram(x=df[selected_category_name], texttemplate="%{x} : %{y}",)
            )
            

            # 레이아웃 설정 (사이즈, 제목 등 추가 설정 가능)
            layout = {
                'title': str(selected_category_name),
                'xaxis_title': 'unique_values',
                'yaxis_title': 'counts',
                # 'barmode': 'stack', 
            }

            # HTML에 전달하기 위한 메소드
            category_hist = plot({'data': category_graphs, 'layout': layout}, 
                            output_type='div')

            data['category_hist'] = category_hist
        else:
            # 기록이 없는 경우 None 전달
            data['selected_category_name'] = None
            data['selected_category_label'] = None
            data['selected_category_data'] = None
            data['selected_category_historgram_data'] = None
    except:
        selected_category_name = None
        selected_category_no = None
        print("범주 히스토그램 생성 중 error 발생")

    print("히스토그램 생성 시간 : ", time.time() - start)

    # 막대그래프, 꺾은선그래프 변수 저장
    try:
        # 선택된 추가 컬럼이 있었거나 있는 경우
        if selected_add_category != None:
            # 꺾은선 그래프가 저장될 리스트
            multi_category_line_graphs = []
            # 막대그래프가 저장될 리스트
            multi_category_bar_graphs = []

            # 그래프가 원활하게 표시되기 위해 unique 리스트를 0의 값을 가진 시리즈로 만든 뒤 추가 선택한 항목과 더하여 그래프 생성
            add_sel_all_index = df[selected_add_category].value_counts().sort_index().index
            add_sel_all = pd.Series(0, index=add_sel_all_index)

            for svdl in selVariableDistinctList:
                # 데이터프레임에서 선택한 범주의 추가 변수 값만 가져와 unique를 sort 시킴
                sel_mul_vc = df[df[selected_category_name]==svdl][selected_add_category].value_counts().sort_index()
                # 미리 만들어둔 모든 unique Series 와 더한 뒤 null 값은 0으로 채우기
                add_sel_all_values = (add_sel_all + sel_mul_vc).fillna(0)
                # 해당되는 전체 값 구하기
                sum = add_sel_all_values.sum()
                # 전체 값이 0이 아니라면 나눠 퍼센트로 만들기
                if sum != 0:
                    add_sel_all_values = add_sel_all_values / add_sel_all_values.sum()
                else:
                    add_sel_all_values = []

                multi_category_line_graphs.append(
                    go.Scatter(x=add_sel_all_index, y=add_sel_all_values, name=str(svdl),)
                )
                multi_category_bar_graphs.append(
                    go.Bar(x=add_sel_all_index, y=add_sel_all_values, texttemplate=str(svdl)+" : %{y}", name=str(svdl),)
                )
    except:
        print("막대 그래프, 꺽은선 그래프 리스트 담는 중 error 발생")

    print("막대, 꺾은선 리스트 담는 시간 : ", time.time() - start)

    # 꺾은선 그래프 생성
    try:
        # 레이아웃 설정 (사이즈, 제목 등 추가 설정 가능)
        line_layout = {
            'title': str(selected_add_category) + " (선택한 예상 범주 : " + str(selected_category_name) + ")",
            'xaxis_title': 'unique_values',
            'yaxis_title': 'counts(pct)',
            'legend_title': "범주 unique list",
            # 'barmode': 'stack', 
        }

        # HTML에 전달하기 위한 메소드
        multi_category_line = plot({'data': multi_category_line_graphs, 'layout': line_layout}, output_type='div')

        data['multi_category_line'] = multi_category_line
    except:
        print("꺾은선 그래프 생성 중 error 발생")

    print("꺾은선 그래프 생성 시간 : ", time.time() - start)

    # 막대 그래프 생성
    try:
        # 레이아웃 설정 (사이즈, 제목 등 추가 설정 가능)
        multi_category_bar_layout = {
            'title': str(selected_add_category) + " (선택한 예상 범주 : " + str(selected_category_name) + ")",
            'xaxis_title': 'unique_values',
            'yaxis_title': 'counts(pct)',
            'legend_title': "범주 unique list",
            'barmode': 'stack', 
        }
        # HTML에 전달하기 위한 메소드
        multi_category_bar = plot({'data': multi_category_bar_graphs, 'layout': multi_category_bar_layout}, output_type='div')

        data['multi_category_bar'] = multi_category_bar
    except:
        print("막대 그래프 생성 중 error 발생")

    print("막대그래프 생성 시간 : ", time.time() - start)

    return render(req, 'category.html', data)

def variable(req):
    # 시간 측정
    start = time.time()

    # 값 불러와 사용
    global sel_val
    global inputfile
    global selected_category_name
    global selected_category_no
    global selected_index
    global selected_add_category
    global selected_one_category
    global df

    # 리턴할 값 모음
    data = {}  

    # 초기 설정
    ip, under_ip, filename, path = firstSetting(req, data)

    # 초기화 버튼, 첨부파일 받아오기, 데이터프레임 만들기
    btnResult = dataButton(req, filename, data, path)
    data['nodata'] = nodata
    if btnResult == 0:
        return render(req, 'variable.html', data)

    # df = makedf(data, path)

    # 선택한 변수의 Null값을 0으로
    try:
        vnz = None
        if 'sel_var_null_zero' in req.POST:
            vnz = req.POST.get('sel_var_null_zero')
        print("변수 null 있는지 확인 시간 :", time.time() - start)
        if vnz == 'sel_var_null_zero':
            print("변수 null if문 들어간 시간 :", time.time() - start)
            df[selected_one_category] = df[selected_one_category].fillna(0)
            # 만약 해당 경로에 같은 이름의 파일이 있는 경우 삭제
            if os.path.isfile(filename):
                os.remove(filename)
            print("기존 파일 삭제 후 시간 :", time.time() - start)
            # 0으로 만든 데이터프레임 저장 (시간 오래 걸린다)
            df.to_csv(filename, index=None)
            print("csv 파일 저장 후 시간 :", time.time() - start)
            # 데이터프레임을 새 데이터프레임으로 덮어씌우기
            df = pd.read_csv(path)
            print("다시 저장한 파일 df로 만든 시간 :", time.time() - start)
    except:
        print("변수 null 값 0 만드는 중 실패")
    
    print("변수 null 시간 : ", time.time() - start)

    # 범주 생성
    try:    
        # 문자열일 경우 or
        # 유일하지 않고, 값을 가지고 있는게 1 이상이고 값 종류는 5개 이하인 것
        objectName = []
        # objeect type이 아닌 것들을 담을 리스트
        nonObjectName = []
        dt = df.dtypes
        for d in range(len(dt)):
            if dt[d] == object:
                objectName.append(dt.index[d])
            else:
                nonObjectName.append(dt.index[d])
                vc = df.iloc[:,d].value_counts()
                if vc.count() > 1 and vc.sort_values().values[0] > 1 and len(vc) <= 5:
                    objectName.append(dt.index[d])                 

        # 범주에 해당되는 값의 범주 이름을 리스트형으로 전달
        data['category'] = objectName    
    except:
        print("범주 생성 중 error 발생")       

    print("범주 생성 시간 : ", time.time() - start)    

    # 변수 생성
    try:
        nonObjectDF = df[nonObjectName]
        lenNO = len(nonObjectDF)

        # 조건 : 문자열이 없는 리스트 + unique value의 count 중 최댓값이 전체 row의 75% 이하인 column
        # nonObjectDFX100Name = []
        # for ln in range(lenNO):
        #     try:
        #         no = nonObjectDF.iloc[:,ln]
        #         if (lenNO*1) > max(no.value_counts()):
        #             nonObjectDFX100Name.append(no.name)
        #     except:
        #         continue

        # 변수 생성
        data['nonObject'] = nonObjectDF
    except:
        print("변수 생성 중 error 발생")

    print("변수 생성 시간 : ", time.time() - start)

    # 선택한 변수 변수로 저장
    try:
        if 'selected_one_category' in req.POST:
            selected_one_category = req.POST.get('selected_one_category')
        if selected_one_category != None:
            data['selected_one_category_name'] = selected_one_category
    except:
        print("선택한 변수 데이터를 가져오는 중 error 발생")

    # 선택한 변수 Data Type / Empty Cells / Unique Value 
    try:
        # 버튼 선택한 기록이 있는 경우
        if selected_one_category != None:
            # 타입 확인
            selOneVariableType = str(df[selected_one_category].dtype)
            # null 개수 확인
            selOneVariableNull = df[selected_one_category].isnull().sum()
            # unique 개수
            selOneVariableDistinctCount = len(df[selected_one_category].unique())
            # unique 리스트
            try:
                selOneVariableDistinctList = sorted(df[selected_one_category].unique())
            except:
                selOneVariableDistinctList = list(df[selected_one_category].unique())

        data['selOneVariableType'] = selOneVariableType
        data['selOneVariableNull'] = selOneVariableNull
        data['selOneVariableDistinctCount'] = selOneVariableDistinctCount
        data['selOneVariableDistinctList'] = selOneVariableDistinctList

    except:
        selected_one_category = None
        print("선택한 변수 정보 출력 중 error 발생")

    # 변수 선택 시 꺾은선그래프 생성
    try:
        if selected_one_category != None:
            # 꺾은선 그래프가 저장될 리스트
            one_category_line_graphs = []

            sel_one_vc = df[selected_one_category].value_counts().sort_index()

            one_category_line_graphs.append(
                go.Scatter(x=sel_one_vc.index, y=sel_one_vc.values, )
            )

            # 레이아웃 설정 (사이즈, 제목 등 추가 설정 가능)
            selected_one_category_layout = {
                'title': str(selected_one_category),
            }

            # HTML에 전달하기 위한 메소드
            one_category_line = plot({'data': one_category_line_graphs, 'layout': selected_one_category_layout}, output_type='div')
            data['one_category_line'] = one_category_line

    except:
        print("선택한 변수 꺾은선 그래프 생성 중 error 발생")

    print("변수 꺾은선 그래프 생성 시간 : ", time.time() - start)

    return render(req, 'variable.html', data)

def makecsv(req):
    # 시간 측정
    start = time.time()

    # 값 불러와 사용
    global sel_val
    global inputfile
    global selected_category_name
    global selected_category_no
    global selected_index
    global selected_add_category
    global selected_one_category
    global df

    # 리턴할 값 모음
    data = {}  

    # 초기 설정
    ip, under_ip, filename, path = firstSetting(req, data)

    # 초기화 버튼, 첨부파일 받아오기, 데이터프레임 만들기
    btnResult = dataButton(req, filename, data, path)
    data['nodata'] = nodata
    if btnResult == 0:
        return render(req, 'makecsv.html', data)

    # df = makedf(data, path)

    # 컬럼명 추출
    try:
        # 컬럼명만 추출
        index = df.columns.tolist()
        # 컬럼 리스트 생성
        data['index'] = index           # 선택한 예상 범주에 영향을 확인할 다른 변수
    except:
        print("컬럼명 추출 중 error 발생")

    # 선택된 컬럼으로 데이터프레임 생성 및 저장
    try:
        # selected_index의 이름을 가진 버튼이 선택된 경우 (컬럼)
        if 'selected_index' in req.POST:          
            # 버튼으로 선택한 것들을 받아오기
            selected_index = req.POST.getlist('selected_index')

        # 선택된 컬럼이 있었거나 있는 경우
        if selected_index != None:
            # 받아온 인자들로만 데이터프레임 만들기
            selectMatch_index = df[selected_index]
            # 선택한 컬럼은 html로 전달
            data['selectMatch_index'] = selected_index

            # 행 번호는 없이 바꾼 이름으로 csv 파일 저장 
            selectMatch_index.to_csv(f'make/{under_ip}.csv', index = False)
            # 데이터프레임 다운 버튼 활성화
            data['download_btn'] = "csv 다운로드"
        else:
            # 컬럼이 선택되지 않은 경우
            data['selectMatch_index'] = None
            data['download_btn'] = None
    except:
        selected_index = None
        print("데이터프레임을 만드는 중 error 발생")

    print("endtime : ", time.time() - start)
    return render(req, 'makecsv.html', data)

# 사용자 ip 얻어오기
def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

# 데이터프레임을 인자값으로 받아서 원하는 퍼센트로 train test set 만들기
def makeTrainTest(df, pct):    
    start = time.time()
    data = df.iloc[:,1:-1]
    target = df.iloc[:,0]
    x_train, x_valid, y_train, y_valid = train_test_split(data, target, test_size=pct, shuffle=True)
    
    people1 = pd.DataFrame({'people':y_train.index, 'set':'Train'})
    people2 = pd.DataFrame({'people':y_valid.index, 'set':'Test'})
    people = pd.concat([people1, people2])
                 
    return x_train, x_valid, y_train, y_valid, people

# 다운로드 버튼 누를경우 작동되는 메소드
def downloadFile(req):
    ip = get_client_ip(req)
    under_ip = str(ip).replace('.', '_')

    filename = f'{under_ip}.csv'
    filepath = "make/" + filename
    # Open the file for reading content
    path = open(filepath, 'r')
    # Set the mime type
    mime_type, _ = mimetypes.guess_type(filepath)
    # Set the return value of the HttpResponse
    response = HttpResponse(path, content_type=mime_type)
    # Set the HTTP header for sending to browser
    response['Content-Disposition'] = "attachment; filename=%s" % filename

    return response

# train data 저장 버튼
def downloadTrainDataFile(req):
    ip = get_client_ip(req)
    under_ip = str(ip).replace('.', '_')

    filename = f'{under_ip}_train_data.csv'
    filepath = "make/" + filename
    # Open the file for reading content
    path = open(filepath, 'r')
    # Set the mime type
    mime_type, _ = mimetypes.guess_type(filepath)
    # Set the return value of the HttpResponse
    response = HttpResponse(path, content_type=mime_type)
    # Set the HTTP header for sending to browser
    response['Content-Disposition'] = "attachment; filename=%s" % filename

    return response

# train target 저장 버튼
def downloadTrainTargetFile(req):
    ip = get_client_ip(req)
    under_ip = str(ip).replace('.', '_')

    filename = f'{under_ip}_train_target.csv'
    filepath = "make/" + filename
    # Open the file for reading content
    path = open(filepath, 'r')
    # Set the mime type
    mime_type, _ = mimetypes.guess_type(filepath)
    # Set the return value of the HttpResponse
    response = HttpResponse(path, content_type=mime_type)
    # Set the HTTP header for sending to browser
    response['Content-Disposition'] = "attachment; filename=%s" % filename

    return response

# train data 저장 버튼
def downloadTestDataFile(req):
    ip = get_client_ip(req)
    under_ip = str(ip).replace('.', '_')

    filename = f'{under_ip}_test_data.csv'
    filepath = "make/" + filename
    # Open the file for reading content
    path = open(filepath, 'r')
    # Set the mime type
    mime_type, _ = mimetypes.guess_type(filepath)
    # Set the return value of the HttpResponse
    response = HttpResponse(path, content_type=mime_type)
    # Set the HTTP header for sending to browser
    response['Content-Disposition'] = "attachment; filename=%s" % filename

    return response

# train target 저장 버튼
def downloadTestTargetFile(req):
    ip = get_client_ip(req)
    under_ip = str(ip).replace('.', '_')

    filename = f'{under_ip}_test_target.csv'
    filepath = "make/" + filename
    # Open the file for reading content
    path = open(filepath, 'r')
    # Set the mime type
    mime_type, _ = mimetypes.guess_type(filepath)
    # Set the return value of the HttpResponse
    response = HttpResponse(path, content_type=mime_type)
    # Set the HTTP header for sending to browser
    response['Content-Disposition'] = "attachment; filename=%s" % filename

    return response

def demo_plot_view(request):
    train_graphs = []
    label = ['Test', 'Train']
    value = [111011, 47576]
    # Adding linear plot of y1 vs. x.
    train_graphs.append(
        go.Pie(labels=label, values=value)
    )


    # Setting layout of the figure.
    layout = {
    }

    # Getting HTML needed to render the plot.
    train_pie = plot({'data': train_graphs, 'layout': layout}, 
                    output_type='div')


    return render(request, 'demo-plot.html', 
                  context={'plot_div': train_pie})

