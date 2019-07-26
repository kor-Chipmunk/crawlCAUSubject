import requests, json
from bs4 import BeautifulSoup

from openpyxl import load_workbook
from openpyxl import Workbook

year = "2019"
campfgs = ["1", "2"]

for campfg in campfgs:
    URL = "https://mportal.cau.ac.kr/std/usk/sUskSif001/selectParam.ajax"
    params = {'year': year, 'campfg': campfg, 'course': "3", 'gb': "3"}
    headers = {'Content-Type': 'application/json; charset=utf-8'}

    res = requests.post(URL, headers=headers, data=json.dumps(params))

    resToJson = res.json()
    
    # 교양 / 융합전공 / 연계전공 / --- / 대학들...
    colgList = []
    
    for menu in resToJson['selectColg']:
        if menu['deptcd'] == None:
            continue

        insertDict = {'name': menu['deptkornm'], 'code': menu['deptcd'], 'campcode': menu['campfg']}

        colgList.append(insertDict)
    
    
    # 대학들 마다 세부 전공 탐색
    for idx, colg in enumerate(colgList):
        URL = "https://mportal.cau.ac.kr/std/usk/sUskSif001/selectSust.ajax"
        params = {'year': year, 'campfg': campfg, 'course': "3", 'gb': "3", 'colgcd': colg['code'], 'shtm': "2"}
        headers = {'Content-Type': 'application/json; charset=utf-8'}

        res = requests.post(URL, headers=headers, data=json.dumps(params))
        resToJson = res.json()
        
        # 세부 전공들
        susts = []
        
        exportTable = []
        exportTable.append(['전공', '학년', '이수구분', '과목번호-분반', '과목명', '담당교수', '학점', '시간', '강의실/강의시간', '개설학과', '유의사항'])
        
        write_wb = Workbook()
        write_ws = write_wb.active
        
        for detailSust in resToJson['selectSust']:
            insertSust = {'campcode': detailSust['camp'], 'name': detailSust['nm'], 'code': detailSust['deptcd']}

            susts.append(insertSust)
        
        if idx < 3:
            search_gb = colg['code']
        else:
            search_gb = "ELSE"
        
        for sust in susts:
            URL = "https://mportal.cau.ac.kr/std/usk/sUskSif001/selectSbjt.ajax"
            params = {"year":year,"campfg":campfg,"course":"3","gb":"3","colgcd":colg['code'], "shtm":"2", "sust":sust['code'], "search_gb": search_gb, "kornm":""}
            headers = {'Content-Type': 'application/json; charset=utf-8'}

            res = requests.post(URL, headers=headers, data=json.dumps(params))
            resToJson = res.json()

            for subject in resToJson['selectSust']:
                exportTable.append([sust['name'] \
                                    , subject['shyr'] \
                                    , subject['pobtnm'] \
                                    , subject['sbjtclss'] \
                                    , subject['clssnm'] \
                                    , subject['profnm'] \
                                    , subject['pnt'].split('-')[0] \
                                    , subject['pnt'].split('-')[1] \
                                    , subject['ltbdrm'] \
                                    , '' if subject['sustnm'] == None else subject['sustnm'] \
                                    , subject['remk']])

        for row in exportTable:
            write_ws.append(row)

        write_wb.save('{} - {}.csv'.format("서울캠퍼스" if campfg == "1" else "안성캠퍼스",colg['name']))
        
        print('{} - {} 파일 완료'.format("서울캠퍼스" if campfg == "1" else "안성캠퍼스",colg['name']))