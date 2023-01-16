import pandas as pd
import requests
import json

def request_stop_loc(sname, use_types=True, use_city=True):
    kw = {'key':'758a44593643883ec3e0f9accb646aab','keywords':'%s(公交站)'%sname}
    if use_types:
        kw['types'] = '150702'
    if use_city:
        kw['city'] = '010'
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36"}
    response = requests.get("https://restapi.amap.com/v3/place/text?parameters", params = kw, headers = headers).json()
    try:
        poi = response["pois"][0]
        output_name, output_loc = poi["name"], poi["location"]
        print(sname,'->',output_name)
    except:
        output_name, output_loc = "None", "None"
        print("Failed with", sname)
    return output_name, output_loc

def request_stop_information():
    dfext = pd.read_excel("公交站点信息.xlsx")
    dfext = dfext[['线路名称', '方向', '站点序号', '站点名称']]
    dfext = dfext.rename(columns={"线路名称":"route_name", "方向":"direction", "站点序号":"stop_seq", "站点名称":"stop_name"})
    
    stop_names = dfext["stop_name"].to_list()
    sname2sloc, sname2oname = {}, {}
    for sname in stop_names:
        if sname not in sname2sloc:
            output_name, output_loc = request_stop_loc(sname)
            sname2oname[sname] = output_name
            sname2sloc[sname] = output_loc

    stop_onames = [sname2oname[sname] for sname in stop_names]
    stop_locs = [sname2sloc[sname] for sname in stop_names]
    dfext["stop_loc"] = stop_locs
    dfext["stop_oname"] = stop_onames
    dfext.to_csv("transit_bus.csv", index=None)

def request_failed_stop_info():
    df = pd.read_csv("transit_bus.csv")
    new_stop_loc, new_stop_oname = [], []
    sname2sloc, sname2oname = {}, {}
    for row in df.itertuples():
        if row.stop_name+"(公交站)" not in row.stop_oname:
            if row.stop_name not in sname2sloc:
                output_name, output_loc = request_stop_loc(row.stop_name, False, True)
                new_stop_loc.append(output_loc)
                new_stop_oname.append(output_name)
                sname2oname[row.stop_name] = output_name
                sname2sloc[row.stop_name] = output_loc
            else:
                new_stop_loc.append(sname2sloc[row.stop_name])
                new_stop_oname.append(sname2oname[row.stop_name])
        else:
            new_stop_loc.append(row.stop_loc)
            new_stop_oname.append(row.stop_oname)
    df["stop_loc"] = new_stop_loc
    df["stop_oname"] = new_stop_oname
    df.to_csv("BeijingTransit.csv", index=None)

def process_transit_bus_table():
    df = pd.read_csv("BeijingTransit.csv")
    remove_routes = ['专82', '828', '492', '专24', 'H27', '919', '369', '810', 'TZ68', '407', 'H34', '125', '542', 'H63', '345', ' 专66', 'M3', '583', '996', '997', 'H79', '370', '851', '400快外', '887', '912', 'TZ37', '552', '615', '602', ' 专134', '夜间接驳专线1', 'H05', '专110', '951', 'TZ50', '659', '夜38', 'F80内', '专193', '987', 'TZ67', '快速公交3线', 'H23', 'H03', '专50', 'H37', '805快', 'H59', '400内', 'M24', 'F39', '821', 'Y21', '889', '18', '816', '894', '专196', '893', '400外', 'F52', 'TZ38', '485', '专46', '533', '902', '980', '435', '专96', '848', '840', 'TZ40', '645', 'F51', 'H08', '849', '345快', '专101', '专145', 'Y2', '845', '937', '388', 'T119', '557', '930', '918', 'TZ9', '922', '838', '566', '935', '870', 'F23', '专70', '599', '专123', 'F47', '专12', '专56', 'TZ18', 'H54', 'H26', '314', 'C114', '947', '990', 'T114', 'F80外', '418', '882', '365', 'X108', 'TZ7', '专5', '专195', '472', 'F25', '428', 'TZ2', '868', '736', '857', 'Y23', '专31', '384', '336', '344', '957', 'TZ1', '323', '专34', '462', '618', '399', '884', '819', '501', 'TZ52', '921', '专93', '专164', '932', '专173', '586', '942快', '93', '929', '377', 'X104', 'F1内', '专151', '883', '专147', '昌27路', '623', 'F61', '夜19', 'F34', '985', 'H45', '537', '专38', '804', '938', '826', 'H21', '984', '867', 'Y6', '582', 'Y46', '516', '829', 'F5外', '74', '夜18', '441', 'H22', 'T109', 'H52', '668', '676', '962', 'F42', '82', '811', 'H51', '954', '专35', '891', '394', '643', 'C111', '367', '夜34', 'F31', '372', '842', '快速公交4线', '通勤向阳', '587', 'H40', '817', '326', '专53', '955', 'TZ14', '675', '专124', 'TZ43', 'F13', '854', '专102', '专36', 'H33', '571', '463', '477', 'Y5', '专43', '夜16', '820', 'H57', '876', '970快', '夜间接驳专线2', '夜间接驳专线7', '337', '991', '昌25路', '973', '专42', 'TZ28', 'Y33', '878', 'Y49', '980快', '931', '941', '899', '805', '924', '442', 'TZ4', '977', '945', 'H14', '夜间接驳专线6', '871', 'C115', 'TZ49', '519', 'F1外', '803', '专121', '917快', '132', '专132', '970', '400快 内', '822', '专49', '专57', '77', '昌21路', '972', '325', '专148', 'TZ51', 'T108', '139', '昌19路', '833', '119', '852', '943', 'Y20', 'H50', '880', 'X102', '352', 'T118', 'TZ69', 'T102', 'H53', '885', '518', '847', '396', 'H44', 'T101', 'F40', 'TZ44', '890', '12', '949', '430', '905', '494', 'H42', '670', 'F5内', '快速公交2线', '979', '25', '813', '561', '专45', 'H09', 'F30', 'C110', '专80', '专189', '844', '445', 'TZ5', '906', '934', '818', '夜间接驳专线8', 'H71', '680', '128', 'H38']
    save_routes = set(df["route_name"]) - set(remove_routes)
    df = df[df['route_name'].isin(save_routes)]
    stop_locs = df["stop_loc"].to_list()
    temp = [stop_loc.split(",") for stop_loc in stop_locs]
    lonlat = list(zip(*temp))
    df["stop_lon"] = lonlat[0]
    df["stop_lat"] = lonlat[1]
    df = df.rename(columns={"stop_oname":"stop_full_name"})
    df = df[["route_name", "direction", "stop_seq", "stop_lon", "stop_lat", "stop_name","stop_full_name"]]
    print(df)
    df.to_csv("BeijingTransit.csv", index=None, encoding='gbk')

def further_process():
    df = pd.read_csv("BeijingTransit.csv", encoding='gbk')
    remove_routes = df[df["stop_name"] == '永安路']["route_name"]
    save_routes = set(df["route_name"]) - set(remove_routes)
    df = df[df['route_name'].isin(save_routes)]
    df.to_csv("BeijingTransit.csv", index=None, encoding='gbk')


if __name__ == "__main__":
    # request_stop_information()
    # request_failed_stop_info()
    # process_transit_bus_table()
    further_process()


