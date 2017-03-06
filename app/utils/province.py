# -*- coding: utf-8 -*-

province_name_dict = {
    '北京市': 1,
    '上海市': 2,
    '天津市': 3,
    '重庆市': 4,
    '河北省': 5,
    '山西省': 6,
    '辽宁省': 7,
    '吉林省': 8,
    '黑龙江省': 9,
    '江苏省': 10,
    '浙江省': 11,
    '安徽省': 12,
    '福建省': 13,
    '江西省': 14,
    '山东省': 15,
    '河南省': 16,
    '湖北省': 17,
    '湖南省': 18,
    '广东省': 19,
    '海南省': 20,
    '四川省': 21,
    '贵州省': 22,
    '云南省': 23,
    '陕西省': 24,
    '甘肃省': 25,
    '青海省': 26,
    '内蒙古自治区': 27,
    '广西壮族自治区': 28,
    '西藏自治区': 29,
    '宁夏回族自治区': 30,
    '新疆维吾尔自治区': 31,
    '台湾': 32,
    '香港': 33,
    '澳门': 34,
}

#id为key
def get_province_id_dict(province_name_dict):
    province_id_dict = {}
    for k, v in province_name_dict.items():
        province_id_dict.update({v: k})
    return province_id_dict
province_id_dict = get_province_id_dict(province_name_dict)


def get_province_by_id(id):
    name = province_id_dict[str(id)]
    return name

def get_province_by_name(name):
    id = province_name_dict[str(name)]
    return id
    # print province['青海省']

def get_region_limit_list(list):
    limit_list = ''
    if list:
        for i in range(0, len(list)):
            list[i] = get_province_by_id(list[i])
        limit_list = ' '.join(list)
    return limit_list


class province(object):
    def __init__(self):
        self.province_name_dict = province_name_dict
        self.province_id_dict = get_province_id_dict(province_name_dict)

    def get_province_by_id(self, id):
        name = province_id_dict[str(id)]
        return name

    def get_province_by_name(self, name):
        id = province_name_dict[str(name)]
        return id
        # print province['青海省']

    def get_region_limit_list(self, list):
        limit_list = ''
        if list:
            for i in range(0, len(list)):
                list[i] = get_province_by_id(list[i])
            limit_list = ' '.join(list)
        return limit_list