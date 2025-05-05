import polars as pl
import pandas as pd
import os
import numpy as np
from underthesea import text_normalize
import geopandas as gpd
import plotly.express as px 

def read_data():
    # Read data 
    data_index = [dataset for dataset in os.listdir('VHLSS2022')]
    data_dict = {}

    ## Read all .dta file in VHLSS2022 folder
    for file, i in zip(os.scandir('VHLSS2022'), range(0,len(data_index))):
        data_dict[data_index[i]] = pl.DataFrame(pd.read_stata(file.path))

    ## Data cleaning
    ## loại dữ liệu thu nhập và thu bình quân âm
    data_dict['Ho_ThongTinHo.dta'] = data_dict['Ho_ThongTinHo.dta'].filter(
        pl.col('THUNHAP') >= 0, pl.col('THUBQ') >= 0
    )

    vung_mien = pl.read_csv("vung_mien_vn.csv")
    # Left join household survey data with important household member survey data
    data_dict["Ho_ThongTinHo.dta"] = data_dict["Ho_ThongTinHo.dta"].join(
        data_dict["Ho_Muc4B22.dta"][["IDHO", "M4B22_C17"]].group_by("IDHO").agg(pl.sum("M4B22_C17")),
        on = "IDHO",
        how = 'left'
    ).join(
        data_dict["Ho_Muc4B32.dta"][["IDHO", "M4B32_C15"]].group_by("IDHO").agg(pl.sum("M4B32_C15")),
        on = "IDHO",
        how = 'left'
    ).join(
        data_dict["Ho_Muc4B42.dta"][["IDHO", "M4B42_C12"]].group_by("IDHO").agg(pl.sum("M4B42_C12")),
        on = "IDHO",
        how = 'left'
    ).join(
        data_dict["Ho_Muc4B52.dta"][["IDHO", "M4B52_C17"]].group_by("IDHO").agg(pl.sum("M4B52_C17")),
        on = "IDHO",
        how = 'left'
    )

    # Determine area type
    area_type = pl.read_csv("ma_vung.csv")

    # import manipulated weight file
    weight = pl.read_csv('weight.csv').join(
        vung_mien, on = "tentinh"
    ).with_columns(
        pl.col(['MATINH', 'MAHUYEN', 'MAXA', 'MADIABAN']).cast(pl.Utf8) # Chuyển mã thành character
    )

    # Merge marriage status data

    marriage_status_df = data_dict['Ho_ThanhVien.dta'].with_columns(
        marriageStatus = pl.when(
            pl.col('M1A_C2') == 1, 
            pl.col('M1A_C5') >= 20,
            pl.col('M1A_C7') != 2,
            pl.col('M1A_C7') != 5
        ).then(1)\
        .when(
            pl.col('M1A_C2') == 2, 
            pl.col('M1A_C5') >= 18,
            pl.col('M1A_C7') != 2,
            pl.col('M1A_C7') != 5
        ).then(1).otherwise(0)
    ).group_by('IDHO').agg(
        nSingles = pl.sum('marriageStatus')
    )

    data_dict["Ho_ThongTinHo.dta"] = data_dict["Ho_ThongTinHo.dta"].join(
        marriage_status_df, on = "IDHO", how = 'left'
    )

    ## CPI data for uprating
    cpi_data = pl.DataFrame(pd.read_stata("cpi_data.dta")).select(
        pl.col("ReportTerm").cast(pl.Int64),
        pl.col('CPI_growth')
    )
    return(data_dict, cpi_data, weight, area_type)

def get_uprate(simulationYear, baseYear, cpi_data):
    if simulationYear > baseYear:
        uprate = cpi_data.filter(
            (pl.col("ReportTerm") < simulationYear) & (pl.col("ReportTerm") > baseYear)
        )["CPI_growth"].to_numpy().prod()
    elif simulationYear == baseYear:
        uprate = 1
    else:
        print('Inappropriate simulation year')
    return uprate

# Process data
def get_market_income(
    data_dict, cpi_data, weight, area_type,
    tc_that_nghiep=0, tc_thoi_viec=0, luong_bt=0, 
    luong_som=0, tc_mat_suc=0,
    hoc_phi_dt=0, startClass=0, endClass=12,
    hoc_phi_tt=0, dong_phuc=0,
    sgk=0, dung_cu_hoctap=0, hoc_them=0, gd_khac=0,
    tc_giaoduc=0,
    tc_thuong_binh=0, tc_bao_tro_xh=0, tc_thien_tai=0,
    db_trong_trot=0, db_chan_nuoi=0, db_dvnn=0,
    db_trong_rung=0, db_nuoi_thuy_san=0,
    thue_chan_nuoi=0, thue_dvnn=0, thue_lam_nghiep=0, 
    thue_kd_lam_nghiep=0, thue_doc_than=0,
    inc_tax_1=0.05, inc_tax_2=0.1, inc_tax_3=0.15, inc_tax_4=0.2, 
    inc_tax_5=0.25, inc_tax_6=0.3, inc_tax_7=0.35,
    inc_threshold_1=5000, inc_threshold_2=10000, inc_threshold_3=18000, inc_threshold_4=32000,
    inc_threshold_5=52000, inc_threshold_6=80000,
    simulationYear=2025, baseYear=2022
):
    # get uprate
    uprate = get_uprate(simulationYear, baseYear, cpi_data)
            
    tongCaNhan = pl.DataFrame(data_dict["Ho_ThanhVien.dta"]).with_columns(
        tc_thatNghiep = pl.col('M4A_C18A') * (1 + tc_that_nghiep)* uprate,
        tc_thoiViec = pl.col('M4A_C18B') * (1 + tc_thoi_viec)* uprate,
        luongBt = pl.col('M4A_C18C') * (1 + luong_bt)* uprate,
        luongSom = pl.col('M4A_C18D') * (1 + luong_som)* uprate,
        tc_matSucLD = pl.col('M4A_C18E') * (1 + tc_mat_suc)* uprate,

        # Education benefits
        ## Main education fee
        hocPhiDT = pl.when(pl.col('M2_C6').is_in(list(range(startClass, endClass + 1))))\
            .then(pl.col('M2_C8A') * (1 + hoc_phi_dt) * uprate).otherwise(pl.col('M2_C8A')* uprate),
        hocPhiTT = pl.when(pl.col('M2_C6').is_in(list(range(startClass, endClass + 1))))\
            .then(pl.col('M2_C8B') * (1 + hoc_phi_tt)* uprate).otherwise(pl.col('M2_C8B')* uprate),
        dongPhuc = (pl.col('M2_C8E') * (1 + dong_phuc))* uprate,
        SGK = (pl.col('M2_C8F') * (1 + sgk))* uprate,
        dungCu = (pl.col('M2_C8G') * (1 + dung_cu_hoctap))* uprate,
        hocThem = (pl.col('M2_C8H') * (1 + hoc_them))* uprate,
        GDKhac = (pl.col('M2_C8I') * (1 + gd_khac))* uprate,

        ## Benefits
        tongTroCap = pl.sum_horizontal(['M4A_C18A', 'M4A_C18B', 'M4A_C18E'])* uprate,
        luongThang = (pl.sum_horizontal(['M4A_C5', 'M4A_C11', 'M4A_C15'])* uprate) / 12
    ).with_columns(
        tn_tinhThue = pl.when(pl.col('luongThang') > 11000).then(pl.col('luongThang')-11000).otherwise(0)
    ).with_columns(
        M2_C10 = pl.when(pl.col('hocPhiDT') < pl.col('M2_C10')).then(0).otherwise(pl.col('M2_C10')) * uprate,
        thueLuong = pl.when(pl.col('tn_tinhThue') <= inc_threshold_1).then(pl.col('tn_tinhThue') * inc_tax_1)\
        .when(pl.col('tn_tinhThue') <= inc_threshold_2).then(pl.col('tn_tinhThue') * inc_tax_2)\
        .when(pl.col('tn_tinhThue') <= inc_threshold_3).then(pl.col('tn_tinhThue') * inc_tax_3)\
        .when(pl.col('tn_tinhThue') <= inc_threshold_4).then(pl.col('tn_tinhThue') * inc_tax_4)\
        .when(pl.col('tn_tinhThue') <= inc_threshold_5).then(pl.col('tn_tinhThue') * inc_tax_5)\
        .when(pl.col('tn_tinhThue') <= inc_threshold_6).then(pl.col('tn_tinhThue') * inc_tax_6)\
        .when(pl.col('tn_tinhThue') > inc_threshold_6).then(pl.col('tn_tinhThue') * inc_tax_7 ) * 12,
    ).drop(['M4A_C18A', 'M4A_C18B', 'M4A_C18C', 'M4A_C18D', 'M4A_C18E'])\
    .group_by("IDHO", maintain_order = True).agg(
        hocBong = pl.sum('M2_C10') * uprate,
        thueLuong = pl.sum('thueLuong'),
        luong = pl.sum_horizontal([
            pl.sum('M4A_C5') * uprate, pl.sum('M4A_C6A') * uprate, pl.sum('M4A_C6B') * uprate, 
            pl.sum('M4A_C11') * uprate, pl.sum('M4A_C12A') * uprate, pl.sum('M4A_C12B') * uprate,
            pl.sum('M4A_C15') * uprate, pl.sum('tc_thatNghiep'), pl.sum('tc_thoiViec'),
            pl.sum('luongBt'), pl.sum('luongSom'), pl.sum('tc_matSucLD')
        ]),
        troCap = pl.sum('tongTroCap'),
        phiGD_base = pl.sum_horizontal(
            pl.sum('M2_C8A'), pl.sum('M2_C8B'), pl.sum('M2_C8C'),
            pl.sum('M2_C8D'), pl.sum('M2_C8E'), pl.sum('M2_C8G'),
            pl.sum('M2_C8H'), pl.sum('M2_C8I'), pl.sum('M2_C11')
        ) * uprate,
        phiGD_reformed = pl.sum_horizontal(
            pl.sum('hocPhiDT'), pl.sum('hocPhiTT'), pl.sum('M2_C8C') * uprate,
            pl.sum('M2_C8D') * uprate, pl.sum('dongPhuc'), pl.sum('SGK'),
            pl.sum('dungCu'), pl.sum('hocThem'), pl.sum('GDKhac')
        ),
        hocPhiDT = pl.sum('hocPhiDT'),
        hocPhiTT = pl.sum('hocPhiTT') 
    )
    # Ghép data cá nhân với data hộ

    thongTinHo_modified = pl.DataFrame(data_dict['Ho_ThongTinHo.dta']).with_columns(
        # Compensations
        db_trongTrot = pl.col('M4B1T2') * (1 + db_trong_trot) * uprate, 
        db_chanNuoi = pl.col('M4B2T2') * (1 + db_chan_nuoi) * uprate,
        db_DVNN = pl.col('M4B3T2') * (1 + db_dvnn) * uprate,
        db_trongRung = pl.col('M4B4T2') * (1 + db_trong_rung) * uprate,
        db_thuySan = pl.col('M4B5T2') * (1 + db_nuoi_thuy_san) * uprate,
        # Benefits
        tc_giaoDuc = pl.col('M2TN') * (1 + tc_giaoduc) * uprate,
        tc_thuongBinh = pl.col('M4D_04') * (1 + tc_thuong_binh) * uprate,
        tc_xaHoi = pl.col('M4D_05') * (1 + tc_bao_tro_xh) * uprate,
        tc_thienTai = pl.col('M4D_06') * (1 + tc_thien_tai) * uprate,
        # Tax
        t_chanNuoi = pl.col('M4B22_C17') * (1 + thue_chan_nuoi) * uprate, # Thue
        t_DVNN = pl.col('M4B32_C15') * (1 + thue_dvnn) * uprate,
        t_lamNghiep = pl.col('M4B42_C12') * (1 + thue_lam_nghiep) * uprate,
        t_KDLamNghiep = pl.col('M4B52_C17') * (1 + thue_kd_lam_nghiep) * uprate,
        M3TN = pl.col('M3TN') * uprate,
        M2TN = pl.col('M2TN') * uprate, 
        M4B0TN = pl.col('M4B0TN') * uprate, 
        M4B11T = pl.col('M4B11T') * uprate,
        M4B12T = pl.col('M4B12T') * uprate,
        M4B13T = pl.col('M4B13T') * uprate,
        M4B14T = pl.col('M4B14T') * uprate,
        M4B15T = pl.col('M4B15T') * uprate,
        M4B22T = pl.col('M4B22T') * uprate,
        M4B3T = pl.col('M4B3T') * uprate,
        M4B4T = pl.col('M4B4T') * uprate, 
        M4B5T1 = pl.col('M4B5T1') * uprate,
        M4CT = pl.col('M4CT') * uprate,
        M4D_01 = pl.col('M4D_01') * uprate,
        M4D_02 = pl.col('M4D_02') * uprate,
        M4D_03 = pl.col('M4D_03') * uprate,
        M4D_04 = pl.col('M4D_04') * uprate,
        M4D_05 = pl.col('M4D_05') * uprate,
        M4D_06 = pl.col('M4D_06') * uprate,
        M4D_07 = pl.col('M4D_07') * uprate,
        M4D_08 = pl.col('M4D_08') * uprate,
        M4D_09 = pl.col('M4D_09') * uprate,
        M4D_10 = pl.col('M4D_10') * uprate,
        M4D_11 = pl.col('M4D_11') * uprate,
        M4D_12 = pl.col('M4D_12') * uprate,
        M7_C12 = pl.col('M7_C12') * uprate,
        M3A_C10 = pl.col('M3A_C10') * uprate,
        M3A_C11 = pl.col('M3A_C11') * uprate,
        M3CT1 = pl.col('M3CT1') * uprate,
        M3CT2 = pl.col('M3CT2') * uprate,
        M3CT3 = pl.col('M3CT3') * uprate,
        M5A1C4 = pl.col('M5A1C4') * uprate,
        M5A1C5 = pl.col('M5A1C5') * uprate,
        M5A2C6 = pl.col('M5A2C6') * uprate,
        M5A2C7 = pl.col('M5A2C7') * uprate,
        M5A2C8 = pl.col('M5A2C8') * uprate,
        M5B1C6 = pl.col('M5B1C6') * uprate,
        M5B1C7 = pl.col('M5B1C7') * uprate,
        M5B1C8 = pl.col('M5B1C8') * uprate, 
        M5B2C4 = pl.col('M5B2C4') * uprate,
        M5B2C5 = pl.col('M5B2C5') * uprate,
        M5B3CT = pl.col('M5B3CT') * uprate,
        M6A_C7 = pl.col('M6A_C7') * uprate,
        M7_C6 = pl.col('M7_C6') * uprate,
        M7_C9 = pl.col('M7_C9') * uprate,
        M7_C14 = pl.col('M7_C14') * uprate,
        M7_C17 = pl.col('M7_C17') * uprate,
        M7_C19 = pl.col('M7_C19') * uprate
    ).with_columns(
        thuHo = pl.sum_horizontal([
            'M3TN', 'M2TN', 'M4B0TN', 
            'M4B11T', 'M4B12T', 'M4B13T', 'M4B14T', 'M4B15T', 'db_trongTrot', # Tổng thu từ trồng trọt
            'M4B21T', 'db_chanNuoi', # Tổng thu từ chăn nuôi
            'M4B22T', # Thu từ săn bắt
            'M4B3T', 'db_DVNN', # Tổng thu từ dịch vụ nông nghiệp
            'M4B4T', 'db_trongRung', 
            'M4B5T1', 'db_thuySan',
            'M4CT', 
            'M4D_01', 'M4D_02', 'M4D_03', 'M4D_04', 
            'M4D_05', 'M4D_06', 'M4D_07', 'M4D_08', 
            'M4D_09', 'M4D_10', 'M4D_11', 'M4D_12',
            'M7_C12'
        ])
    ).join(
        tongCaNhan,
        on = 'IDHO'
    ).with_columns(
        chiSinhHoat_base = pl.sum_horizontal([
            'phiGD_base',
            'M3A_C10', 'M3A_C11',  'M3CT1', 'M3CT2', 'M3CT3',
            # M4B1C, M4B21C, M4B3C, M4B4C,
            'M5A1C4', 'M5A1C5', 'M5A2C6', 'M5A2C7', 'M5A2C8', 'M5B1C6','M5B1C7', 'M5B1C8', 
            'M5B2C4', 'M5B2C5', 'M5B3CT',
            # M5A1CT, M5A2CT, M5B1CT, M5B2CT, M5B3CT, 
            'M6A_C7',
            'M7_C6', 'M7_C9', 'M7_C14', 'M7_C17', 'M7_C19'
        ]),
        chiSinhHoat_reformed = pl.sum_horizontal([
            'phiGD_reformed',
            'M3A_C10', 'M3A_C11',  'M3CT1', 'M3CT2', 'M3CT3',
            # M4B1C, M4B21C, M4B3C, M4B4C,
            'M5A1C4', 'M5A1C5', 'M5A2C6', 'M5A2C7', 'M5A2C8', 'M5B1C6','M5B1C7', 'M5B1C8', 
            'M5B2C4', 'M5B2C5', 'M5B3CT',
            # M5A1CT, M5A2CT, M5B1CT, M5B2CT, M5B3CT, 
            'M6A_C7',
            'M7_C6', 'M7_C9', 'M7_C14', 'M7_C17', 'M7_C19'
        ]),
        thueDocThan = thue_doc_than * pl.col('nSingles')
    ).with_columns(
        tongThuHo = pl.sum_horizontal(['thuHo','luong']),
        tongChiHo = pl.sum_horizontal([
            'TONGCHI','t_chanNuoi', 't_DVNN', 't_lamNghiep', 't_KDLamNghiep', 'thueLuong', 'thueDocThan'
        ]) - pl.sum_horizontal(['M4B22_C17', 'M4B32_C15', 'M4B42_C12', 'M4B52_C17']) 
    ).join(
        weight,
        on = ['MATINH', 'MAHUYEN', 'MAXA', 'MADIABAN']
    ).with_columns(
        wt_household = pl.col('wt45') * pl.col('SONHANKHAU')
    ).with_columns(
        tongChiTieu = pl.col('TONGCHITIEU').fill_null(0) + 
        (pl.col('chiSinhHoat_reformed') - pl.col('chiSinhHoat_base')),
        weight_percent = pl.col("wt45") / pl.sum(["wt45"])
    ).with_columns(
        # custom_thuBQ = (
        #     (pl.col('tongThuHo') - pl.col('tongChiHo'))/pl.col('SONHANKHAU') - pl.col('tongChiTieu')
        # )/12,
        custom_thuBQ = (pl.col('tongThuHo')/pl.col('SONHANKHAU'))/12,
        custom_chiTieuBQ = (pl.col('tongChiTieu')/pl.col('SONHANKHAU'))/12,
        tongHocPhi = pl.sum_horizontal([pl.col('hocPhiDT'), pl.col('hocPhiTT')])
    )
    # print(sum(thongTinHo_modified["weight_percent"]))

    return(thongTinHo_modified)

def get_poverty_rate(df):
    return(
        df.filter(
            (pl.col('custom_chiTieuBQ')) > 0
        ).with_columns(
            povertyStatus = pl.when(
                (pl.col('custom_chiTieuBQ')/30) <=  16.78637
            ).then(0)\
            .when(
                (pl.col('custom_chiTieuBQ')/30) <=  28.49778 
            ).then(1)\
            .when(
                (pl.col('custom_chiTieuBQ')/30) <=  53.48214 
            ).then(2).otherwise(3)
        # ).group_by('povertyStatus').len(name = 'nPoverty')\
        ).group_by('povertyStatus').agg(nPoverty = pl.sum('wt45'))\
        .with_columns(
            pct = (pl.col('nPoverty') / pl.sum('nPoverty')).round(4)
        ).sort(by='povertyStatus', descending=True).drop('nPoverty')\
        .with_columns(
            povertyStatus = pl.when(pl.col('povertyStatus') == 0).then(pl.lit("IPL"))\
            .when(pl.col('povertyStatus') == 1).then(pl.lit("LMIC"))\
            .when(pl.col('povertyStatus') == 2).then(pl.lit("UMIC"))\
            .otherwise(pl.lit("Normal"))
        )
    )

def get_grouped_poverty(df = pl.DataFrame(), group="lanhtho"):
    grouped_poverty = pl.DataFrame()
    for name, data in df.group_by(group):
        provinceName = name[0]
        data = get_poverty_rate(data).with_columns(
            tentinh = pl.lit(provinceName)
        ).pivot("povertyStatus", index='tentinh')
        grouped_poverty = pl.concat([grouped_poverty, data], how='diagonal')
    return grouped_poverty

def gini(array):
    """Calculate the Gini coefficient of a numpy array."""
    # based on bottom eq: http://www.statsdirect.com/help/content/image/stat0206_wmf.gif
    # from: http://www.statsdirect.com/help/default.htm#nonparametric_methods/gini.htm
    array = array.flatten() #all values are treated equally, arrays must be 1d
    if np.amin(array) < 0:
        array -= np.amin(array) #values cannot be negative
    array += 0.0000001 #values cannot be 0
    array = np.sort(array) #values must be sorted
    index = np.arange(1,array.shape[0]+1) #index per array element
    n = array.shape[0]#number of array elements
    return ((np.sum((2 * index - n  - 1) * array)) / (n * np.sum(array))) #Gini coefficient

def get_grouped_gini(df = pl.DataFrame(), group="lanhtho", type_2="custom_chiTieuBQ"):
    grouped_gini = pl.DataFrame()
    for name, data in df.group_by(group):
        provinceName = name[0]
        G = gini(np.array(
            data.filter(pl.col(type_2) > 0).select(type_2)
        )).round(4)
        data = pl.DataFrame({'tentinh':provinceName, "gini":G})
        grouped_gini = pl.concat([grouped_gini, data])
    return grouped_gini

def calculate(data):
    poverty = get_poverty_rate(data)    
    poverty_ttnt = get_grouped_poverty(data, 'TTNT') 
    poverty_area = get_grouped_poverty(data, 'mien')   
    poverty_prov = get_grouped_poverty(data, 'tentinh')
    return(
        {
            'poverty':poverty,
            'poverty_ttnt': poverty_ttnt,
            'poverty_area':poverty_area,
            'poverty_prov':poverty_prov
        }
    )

def calculate_gini(data, type = "custom_chiTieuBQ"):
    g = gini(
        np.array(data.filter(pl.col(type) > 0).select(type))
    ).round(4)
    gini_ttnt = get_grouped_gini(data, 'TTNT', type_2=type)
    gini_area = get_grouped_gini(data, 'mien', type_2=type)
    gini_prov = get_grouped_gini(data, 'tentinh', type_2=type)
    return(
        {
            'gini':g,
            'gini_ttnt':gini_ttnt,
            'gini_area':gini_area,
            'gini_prov':gini_prov
        }
    )

def pos_neg_value(value):
    return np.where(value < 0, "color: red; value:.2f", np.where(value > 0, "color: green; value:.2f", "color: orange; value:.2f"))

def pos_neg_value_reversed(value):
    return np.where(value > 0, "color: red; value:.2%", np.where(value < 0, "color: green; value:.2%", "color: orange; value:.2%"))

def draw_map(data, variable = 'custom_thuBQ', variable_name = "Thu bình quân (Triệu VND)"):
    URL = 'https://data.opendevelopmentmekong.net/dataset/55bdad36-c476-4be9-a52d-aa839534200a/resource/b8f60493-7564-4707-aa72-a0172ba795d8/download/vn_iso_province.geojson'
    map = gpd.read_file(URL)
    map['Name_VI'] = map['Name_VI'].replace([ 'TP. Hồ Chí Minh',  'Thừa Thiên-Huế'], [ 'Hồ Chí Minh', 'Thừa Thiên Huế']).apply(text_normalize)

    if variable == "povertyRate":
        variable_tinh = pd.DataFrame(data).rename(columns={
                0:'tentinh',
                1:variable
            })
    else:
        variable_tinh = pd.DataFrame(
            data.group_by('tentinh').agg((pl.col(variable).mean())/1000))\
            .rename(columns={
                0:'tentinh',
                1:variable
            })
    variable_tinh['tentinh'] = variable_tinh['tentinh'].apply(text_normalize)

    merged = pd.merge(
        map, variable_tinh, right_on='tentinh', left_on="Name_VI", how='left'
    ).assign(
        var = lambda df: df[variable].astype(float)
    ).set_index('Name_VI').rename(columns={"var":variable_name})
    fig = px.choropleth_map(
        merged, 
        geojson=merged.geometry, 
        locations=merged.index, 
        color=variable_name, 
        color_continuous_scale="blues",
        center = {
            'lat':21.028511,
            'lon':105.804817
        },
        zoom = 6,
        map_style="carto-positron-nolabels",
    )
    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(
        coloraxis_showscale=True,
        # height = 300,
        margin=dict(
            b=0, t=0, l=0, r=0
        ),
        autosize=True
    )
    fig.update_traces(
        marker_line_color='black',
        marker_line_width=0.5
    )
    return(fig)

def style_icon(value, decimal = 4):
    icon = "▲" if value > 0 else "▼" if value < 0 else "●"
    return f"{icon} {round(value, decimal)}"

def record_change(input, init):
    print(f'''
Old value: {init} \n
New value: {input}
''')