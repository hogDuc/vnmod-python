import streamlit as st
import polars as pl
import numpy as np
from functions import *
from streamlit_desktop_app import start_desktop_app
from underthesea import text_normalize
import geopandas as gpd
import plotly.express as px 


st.logo(
    image='https://scontent.fhan14-5.fna.fbcdn.net/v/t39.30808-6/453235411_475775001872764_4435076249897854084_n.jpg?_nc_cat=106&ccb=1-7&_nc_sid=6ee11a&_nc_ohc=0lI8dxcOJHAQ7kNvwHG8dAX&_nc_oc=AdnvOwPvZjZ0fpGYFoemM2di5C0VtXWKg5AAsPEniYetUVsxYpR2KNyV-wgMOivp-GqG3ejyKC5XGBJgpM5SXNli&_nc_zt=23&_nc_ht=scontent.fhan14-5.fna&_nc_gid=GqSTdnmXZh51d3FmFvHNzA&oh=00_AfGh_WsOTU0P-EzgTsxPKHbrdoN81uISXCscQj9xwb33jQ&oe=6811278A',
    icon_image='https://scontent.fhan14-5.fna.fbcdn.net/v/t39.30808-6/453235411_475775001872764_4435076249897854084_n.jpg?_nc_cat=106&ccb=1-7&_nc_sid=6ee11a&_nc_ohc=0lI8dxcOJHAQ7kNvwHG8dAX&_nc_oc=AdnvOwPvZjZ0fpGYFoemM2di5C0VtXWKg5AAsPEniYetUVsxYpR2KNyV-wgMOivp-GqG3ejyKC5XGBJgpM5SXNli&_nc_zt=23&_nc_ht=scontent.fhan14-5.fna&_nc_gid=GqSTdnmXZh51d3FmFvHNzA&oh=00_AfGh_WsOTU0P-EzgTsxPKHbrdoN81uISXCscQj9xwb33jQ&oe=6811278A',
    link='http://scienceforeconomics.com',
    size='large'
)

st.set_page_config(
    page_title="SciEco Vietnam Microsimulation",
    layout='wide',
    page_icon='https://scontent.fhan14-5.fna.fbcdn.net/v/t39.30808-6/453235411_475775001872764_4435076249897854084_n.jpg?_nc_cat=106&ccb=1-7&_nc_sid=6ee11a&_nc_ohc=0lI8dxcOJHAQ7kNvwHG8dAX&_nc_oc=AdnvOwPvZjZ0fpGYFoemM2di5C0VtXWKg5AAsPEniYetUVsxYpR2KNyV-wgMOivp-GqG3ejyKC5XGBJgpM5SXNli&_nc_zt=23&_nc_ht=scontent.fhan14-5.fna&_nc_gid=GqSTdnmXZh51d3FmFvHNzA&oh=00_AfGh_WsOTU0P-EzgTsxPKHbrdoN81uISXCscQj9xwb33jQ&oe=6811278A',
    menu_items={
        'About':'''Website: http://scienceforeconomics.com \n
Facebook: Science for Economics'''
    }
)

datasets = ["data_dict", "cpi_data", "weight", "area_type"]
# Prevent re-reading files
if any(x not in st.session_state for x in datasets):
    data_dict, cpi_data, weight, area_type = read_data()
    st.session_state.data_dict = data_dict
    st.session_state.cpi_data = cpi_data
    st.session_state.weight = weight
    st.session_state.area_type = area_type
else:
    data_dict =  st.session_state.data_dict
    cpi_data = st.session_state.cpi_data
    weight = st.session_state.weight
    area_type = st.session_state.area_type

if 'tc_that_nghiep' not in st.session_state:
    st.session_state.tc_that_nghiep = 0
if 'tc_thoi_viec' not in st.session_state:
    st.session_state.tc_thoi_viec = 0     
if 'luong_bt' not in st.session_state:
    st.session_state.luong_bt = 0     
if 'luong_som' not in st.session_state:
    st.session_state.luong_som = 0     
if 'tc_mat_suc' not in st.session_state:
    st.session_state.tc_mat_suc = 0
if 'hoc_phi_dt' not in st.session_state:
    st.session_state.hoc_phi_dt = 0
if 'hoc_phi_tt' not in st.session_state:
    st.session_state.hoc_phi_tt = 0
if 'startClass' not in st.session_state:
    st.session_state.startClass = 0
if 'endClass' not in st.session_state:
    st.session_state.endClass = 12
if 'dong_phuc' not in st.session_state:
    st.session_state.dong_phuc = 0
if 'sgk' not in st.session_state:
    st.session_state.sgk = 0
if 'dung_cu_hoctap' not in st.session_state:
    st.session_state.dung_cu_hoctap = 0
if 'hoc_them' not in st.session_state:
    st.session_state.hoc_them = 0
if 'gd_khac' not in st.session_state:
    st.session_state.gd_khac = 0
if 'tc_giaoduc' not in st.session_state:
    st.session_state.tc_giaoduc = 0
if 'tc_thuong_binh' not in st.session_state:
    st.session_state.tc_thuong_binh = 0
if 'tc_bao_tro_xh' not in st.session_state:
    st.session_state.tc_bao_tro_xh = 0
if 'tc_thien_tai' not in st.session_state:
    st.session_state.tc_thien_tai = 0
if 'db_trong_trot' not in st.session_state:
    st.session_state.db_trong_trot = 0
if 'db_chan_nuoi' not in st.session_state:
    st.session_state.db_chan_nuoi = 0
if 'db_dvnn' not in st.session_state:
    st.session_state.db_dvnn = 0
if 'db_trong_rung' not in st.session_state:
    st.session_state.db_trong_rung = 0
if 'db_nuoi_thuy_san' not in st.session_state:
    st.session_state.db_nuoi_thuy_san = 0
if 'thue_chan_nuoi' not in st.session_state:
    st.session_state.thue_chan_nuoi = 0
if 'thue_dvnn' not in st.session_state:
    st.session_state.thue_dvnn = 0
if 'thue_lam_nghiep' not in st.session_state:
    st.session_state.thue_lam_nghiep = 0 
if 'thue_kd_lam_nghiep' not in st.session_state:
    st.session_state.thue_kd_lam_nghiep = 0 
if 'thue_doc_than' not in st.session_state:
    st.session_state.thue_doc_than = 0 
if 'inc_tax_1' not in st.session_state:
    st.session_state.inc_tax_1 = 0.05 
if 'inc_tax_2' not in st.session_state:
    st.session_state.inc_tax_2 = 0.1 
if 'inc_tax_3' not in st.session_state:
    st.session_state.inc_tax_3 = 0.15 
if 'inc_tax_4' not in st.session_state:
    st.session_state.inc_tax_4 = 0.2 
if 'inc_tax_5' not in st.session_state:
    st.session_state.inc_tax_5 = 0.25 
if 'inc_tax_6' not in st.session_state:
    st.session_state.inc_tax_6 = 0.3
if 'inc_tax_7' not in st.session_state:
    st.session_state.inc_tax_7 = 0.35 
if 'inc_threshold_1' not in st.session_state:
    st.session_state.inc_threshold_1 = 5000 
if 'inc_threshold_2' not in st.session_state:
    st.session_state.inc_threshold_2 = 10000 
if 'inc_threshold_3' not in st.session_state:
    st.session_state.inc_threshold_3 = 18000 
if 'inc_threshold_4' not in st.session_state:
    st.session_state.inc_threshold_4 = 32000 
if 'inc_threshold_5' not in st.session_state:
    st.session_state.inc_threshold_5 = 52000 
if 'inc_threshold_6' not in st.session_state:
    st.session_state.inc_threshold_6 = 80000 

def reset_number_input():
    st.session_state.tc_that_nghiep = 0
    st.session_state.tc_thoi_viec = 0     
    st.session_state.luong_bt = 0     
    st.session_state.luong_som = 0     
    st.session_state.tc_mat_suc = 0
    st.session_state.hoc_phi_dt = 0
    st.session_state.hoc_phi_tt = 0
    st.session_state.startClass = 0
    st.session_state.endClass = 12
    st.session_state.dong_phuc = 0
    st.session_state.sgk = 0
    st.session_state.dung_cu_hoctap = 0
    st.session_state.hoc_them = 0
    st.session_state.gd_khac = 0
    st.session_state.tc_giaoduc = 0
    st.session_state.tc_thuong_binh = 0
    st.session_state.tc_bao_tro_xh = 0
    st.session_state.tc_thien_tai = 0
    st.session_state.db_trong_trot = 0
    st.session_state.db_chan_nuoi = 0
    st.session_state.db_dvnn = 0
    st.session_state.db_trong_rung = 0
    st.session_state.db_nuoi_thuy_san = 0
    st.session_state.thue_chan_nuoi = 0
    st.session_state.thue_dvnn = 0
    st.session_state.thue_lam_nghiep = 0 
    st.session_state.thue_kd_lam_nghiep = 0 
    st.session_state.thue_doc_than = 0 
    st.session_state.inc_tax_1 = 0.05 
    st.session_state.inc_tax_2 = 0.1 
    st.session_state.inc_tax_3 = 0.15 
    st.session_state.inc_tax_4 = 0.2 
    st.session_state.inc_tax_5 = 0.25 
    st.session_state.inc_tax_6 = 0.3
    st.session_state.inc_tax_7 = 0.35 
    st.session_state.inc_threshold_1 = 5000 
    st.session_state.inc_threshold_2 = 10000 
    st.session_state.inc_threshold_3 = 18000 
    st.session_state.inc_threshold_4 = 32000 
    st.session_state.inc_threshold_5 = 52000 
    st.session_state.inc_threshold_6 = 80000

st.title("Mô phỏng kinh tế vi mô - Vietnam Microsimulation")

clearInput = st.toggle("Xóa input sau mỗi lần chạy")
st.button(
    "Reset", 
    use_container_width=False, 
    key="reset_button", 
    on_click=reset_number_input, 
    icon=":material/refresh:"
)
    
with st.form("VNMicro", clear_on_submit=clearInput):
    
    submitButton = st.form_submit_button("Chạy mô phỏng", use_container_width=True, icon=":material/sprint:")

    troCap, luong, thue, thuNghiem  = st.tabs(["Trợ cấp", "Lương", "Thuế", "Thử nghiệm"])

    with troCap:
        troCap_left, troCap_right = st.columns(2)
        with troCap_left:
            tc_that_nghiep = st.number_input(
                "Tỷ lệ thay đổi các khoản trợ cấp thất nghiệp",
                step=0.1,

                key='tc_that_nghiep'
            )
            tc_thoi_viec = st.number_input(
                "Tỷ lệ thay đổi các khoản trợ cấp thôi việc 1 lần",
                step=0.1,

                key='tc_thoi_viec'
            )
            tc_mat_suc = st.number_input(
                "Tỷ lệ thay đổi các khoản trợ cấp mất sức lao động",
                step=0.1,

                key='tc_mat_suc'
            )
            tc_bao_tro_xh = st.number_input(
                "Tỷ lệ thay đổi các khoản trợ cấp các đối tượng bảo trợ xã hội",
                step=0.1,

                key= 'tc_bao_tro_xh'
            )
            tc_thuong_binh = st.number_input(
                "Tỷ lệ thay đổi các khoản trợ cấp thương binh, liệt sỹ",
                step=0.1,

                key='tc_thuong_binh'
            )
            tc_thien_tai = st.number_input(
                "Tỷ lệ thay đổi các khoản trợ cấp khắc phục thiên tai, dịch bệnh",
                step=0.1,

                key='tc_thien_tai'
            )
        with troCap_right:
            db_trong_trot = st.number_input(
                "Tỷ lệ thay đổi các khoản đền bù trồng trọt",
                step=0.1,

                key='db_trong_trot'
            )
            db_chan_nuoi = st.number_input(
                "Tỷ lệ thay đổi các khoản đền bù chăn nuôi",
                step=0.1,

                key='db_chan_nuoi'
            )
            db_dvnn = st.number_input(
                "Tỷ lệ thay đổi các khoản đền bù dịch vụ nông nghiệp",
                step=0.1,

                key='db_dvnn'
            )
            db_trong_rung = st.number_input(
                "Tỷ lệ thay đổi các khoản đền bù trồng rừng, lâm nghiệp",
                step=0.1,

                key='db_trong_rung'
            )
            db_nuoi_thuy_san = st.number_input(
                "Tỷ lệ thay đổi các khoản đền bù về nuôi trồng thủy sản",
                step=0.1,

                key='db_nuoi_thuy_san'
            )
    with luong:
        luong_left, luong_right = st.columns(2)
        with luong_left:
            luong_bt = st.number_input(
                'Tỷ lệ thay đổi lương nghỉ hưu thông thường',
                step=0.1,

                key='luong_bt'
            )
        with luong_right:
            luong_som = st.number_input(
                "Tỷ lệ thay đổi lương nghỉ hưu sớm",
                step=0.1,

                key='luong_som'
            )
    with thue:
        thue_left, thue_mid, thue_right = st.columns(3)
        with thue_left:
            thue_chan_nuoi = st.number_input(
                "Tỷ lệ thay đổi về thuế chăn nuôi",
                step=0.1,

                key='thue_chan_nuoi'
            )
            thue_dvnn = st.number_input(
                "Tỷ lệ thay đổi về thuế kinh doanh dịch vụ nông nghiệp",
                step=0.1,

                key='thue_dvnn'
            )
            thue_lam_nghiep = st.number_input(
                "Tỷ lệ thay đổi về thuế lâm nghiệp",
                step=0.1,

                key='thue_lam_nghiep'
            )
            thue_kd_lam_nghiep = st.number_input(
                "Tỷ lệ thay đổi về thuế kinh doanh lâm nghiệp",
                step=0.1,

                key='thue_kd_lam_nghiep'
            )
        with thue_mid:
            inc_tax_1 = st.number_input(
                "% thuế TNCN mức 1",
                step=0.1,
                # value = 0.05,
                key='inc_tax_1'
            )
            inc_tax_2 = st.number_input(
                "% thuế TNCN mức 2",
                step=0.1,
                # value = 0.1,
                key='inc_tax_2'
            )
            inc_tax_3 = st.number_input(
                "% thuế TNCN mức 3",
                step=0.1,
                # value = 0.15,
                key='inc_tax_3'
            )
            inc_tax_4 = st.number_input(
                "% thuế TNCN mức 4",
                step=0.1,
                # value = 0.2,
                key='inc_tax_4'
            )
            inc_tax_5 = st.number_input(
                "% thuế TNCN mức 5",
                step=0.1,
                # value = 0.25,
                key='inc_tax_5'
            )
            inc_tax_6 = st.number_input(
                "% thuế TNCN mức 6",
                step=0.1,
                # value = 0.3,
                key='inc_tax_6'
            )
            inc_tax_7 = st.number_input(
                "% thuế TNCN mức 7",
                step=0.1,
                # value = 0.35,
                key='inc_tax_7'
            )
        with thue_right:
            inc_threshold_1 = st.number_input(
                "Mức thu nhập chịu thuế 1 (nghìn đồng / tháng)",
                step=0.1,
                # value = 5000,
                key='inc_threshold_1'
            )
            inc_threshold_2 = st.number_input(
                "Mức thu nhập chịu thuế 2 (nghìn đồng / tháng)",
                step=0.1,
                # value = 10000,
                key='inc_threshold_2'
            )
            inc_threshold_3 = st.number_input(
                "Mức thu nhập chịu thuế 3 (nghìn đồng / tháng)",
                # value = 18000,
                step=0.1,
                key='inc_threshold_3'
            )
            inc_threshold_4 = st.number_input(
                "Mức thu nhập chịu thuế 4 (nghìn đồng / tháng)",
                step=0.1,
                # value = 32000,
                key='inc_threshold_4'
            )
            inc_threshold_5 = st.number_input(
                "Mức thu nhập chịu thuế 5 (nghìn đồng / tháng)",
                # value = 52000,
                step=0.1,
                key='inc_threshold_5'
            )
            inc_threshold_6 = st.number_input(
                "Mức thu nhập chịu thuế 6 (nghìn đồng / tháng)",
                step=0.1,
                # value = 80000,
                key='inc_threshold_6'
            )

    with thuNghiem:
        startClass, endClass = st.select_slider(
            "Áp dụng chính sách cho học sinh trong khoảng lớp",
            options=range(0,13),
            value=(0, 12)
        )
        hoc_phi_dt = st.number_input(
            label = 'Tỷ lệ Thay đổi mức học phí đúng tuyến'
        )
        hoc_phi_tt = st.number_input(
            label = 'Tỷ lệ Thay đổi mức học phí trái tuyến'
        )
        dong_phuc = st.number_input(
            label = 'Tỷ lệ Thay đổi phí đồng phục'
        )
        sgk = st.number_input(
            label = 'Tỷ lệ Thay đổi giá sách giáo khoa'
        )
        dung_cu_hoctap = st.number_input(
            label = 'Tỷ lệ Thay đổi giá dụng cụ học tập'
        )
        hoc_them = st.number_input(
            label = '% Thay đổi phí học thêm'
        )
        thue_doc_than = st.number_input(
            label = "Thuế độc thân (nghìn đồng / năm)"
        )

# Initial data

initial_input = {
    'tc_that_nghiep':st.session_state.tc_that_nghiep, 'tc_thoi_viec':st.session_state.tc_thoi_viec, 
    'luong_bt':st.session_state.luong_bt, 'luong_som':st.session_state.luong_som,
    'tc_mat_suc':st.session_state.tc_mat_suc, 'hoc_phi_dt':st.session_state.hoc_phi_dt,
    'hoc_phi_tt':st.session_state.hoc_phi_tt, 'startClass':st.session_state.startClass,
    'endClass':st.session_state.endClass, 'dong_phuc':st.session_state.dong_phuc,
    'sgk':st.session_state.sgk, 'dung_cu_hoctap':st.session_state.dung_cu_hoctap,
    'hoc_them':st.session_state.hoc_them, 'gd_khac':st.session_state.gd_khac, 
    'tc_giaoduc':st.session_state.tc_giaoduc, 'tc_thuong_binh':st.session_state.tc_thuong_binh, 
    'tc_bao_tro_xh':st.session_state.tc_bao_tro_xh, 'tc_thien_tai':st.session_state.tc_thien_tai,
    'db_trong_trot':st.session_state.db_trong_trot, 'db_chan_nuoi':st.session_state.db_chan_nuoi, 
    'db_dvnn':st.session_state.db_dvnn, 'db_trong_rung':st.session_state.db_trong_rung,
    'db_nuoi_thuy_san':st.session_state.db_nuoi_thuy_san, 'thue_chan_nuoi':st.session_state.thue_chan_nuoi,
    'thue_dvnn':st.session_state.thue_dvnn, 'thue_lam_nghiep':st.session_state.thue_lam_nghiep, 
    'thue_kd_lam_nghiep':st.session_state.thue_kd_lam_nghiep, 'thue_doc_than':st.session_state.thue_doc_than, 
    'inc_tax_1':st.session_state.inc_tax_1, 'inc_tax_2':st.session_state.inc_tax_2,
    'inc_tax_3':st.session_state.inc_tax_3, 'inc_tax_4':st.session_state.inc_tax_4, 'inc_tax_5':st.session_state.inc_tax_5, 
    'inc_tax_6':st.session_state.inc_tax_6, 'inc_tax_7':st.session_state.inc_tax_7, 'inc_threshold_1':st.session_state.inc_threshold_1, 
    'inc_threshold_2':st.session_state.inc_threshold_2, 'inc_threshold_3':st.session_state.inc_threshold_3, 
    'inc_threshold_4':st.session_state.inc_threshold_4, 'inc_threshold_5':st.session_state.inc_threshold_5, 
    'inc_threshold_6':st.session_state.inc_threshold_6
}

init_dat = get_market_income(data_dict, cpi_data, weight, area_type)
initial_data = calculate(init_dat)
gini_data_chi = calculate_gini(init_dat)
gini_data_thu = calculate_gini(init_dat, type = 'custom_thuBQ')

init_poverty = initial_data["poverty"]    
init_poverty_ttnt = initial_data["poverty_ttnt"] 
init_poverty_area = initial_data["poverty_area"]   
init_poverty_prov = initial_data["poverty_prov"]

init_gini = gini_data_chi['gini']
init_gini_ttnt = gini_data_chi["gini_ttnt"]
init_gini_area = gini_data_chi['gini_area']
init_gini_prov = gini_data_chi['gini_prov']

init_gini_thu = gini_data_thu['gini']
init_gini_ttnt_thu = gini_data_thu["gini_ttnt"]
init_gini_area_thu = gini_data_thu['gini_area']
init_gini_prov_thu = gini_data_thu['gini_prov']

if submitButton:

    reform_input = {
        'tc_that_nghiep' : 0, 'tc_thoi_viec' : 0, 'luong_bt' : 0, 
        'luong_som' : 0, 'tc_mat_suc' : 0, 'hoc_phi_dt' : 0,
        'hoc_phi_tt' : 0, 'startClass' : 0, 'endClass' : 12,
        'dong_phuc' : 0, 'sgk' : 0, 'dung_cu_hoctap' : 0,
        'hoc_them' : 0, 'gd_khac' : 0, 'tc_giaoduc' : 0,
        'tc_thuong_binh' : 0, 'tc_bao_tro_xh' : 0, 'tc_thien_tai' : 0,
        'db_trong_trot' : 0, 'db_chan_nuoi' : 0, 'db_dvnn' : 0,
        'db_trong_rung' : 0, 'db_nuoi_thuy_san' : 0, 'thue_chan_nuoi' : 0,
        'thue_dvnn' : 0, 'thue_lam_nghiep' : 0, 'thue_kd_lam_nghiep' : 0, 
        'thue_doc_than' : 0, 'inc_tax_1' : 0.05, 'inc_tax_2' : 0.1,
        'inc_tax_3' : 0.15, 'inc_tax_4' : 0.2, 'inc_tax_5' : 0.25, 
        'inc_tax_6' : 0.3, 'inc_tax_7' : 0.35, 'inc_threshold_1' : 5000, 
        'inc_threshold_2' : 10000, 'inc_threshold_3' : 18000, 'inc_threshold_4' : 32000, 
        'inc_threshold_5' : 52000, 'inc_threshold_6' : 80000
    }

    log = pl.DataFrame({'var':initial_input.keys(), 'init':initial_input.values()}, strict=False)\
    .join(
        pl.DataFrame({'var':reform_input.keys(), 'reform':reform_input.values()}, strict=False), on='var'
    ).filter(pl.col('reform')!=pl.col('init'))
    log.write_json('input_log\log.json')

    ref_dat = get_market_income(
        data_dict, cpi_data, weight, area_type,
        tc_that_nghiep= tc_that_nghiep, tc_thoi_viec=tc_thoi_viec, luong_bt=luong_bt, 
        luong_som=luong_som, tc_mat_suc=tc_mat_suc,
        hoc_phi_dt=hoc_phi_dt, startClass=startClass, endClass=endClass,
        hoc_phi_tt=hoc_phi_tt, dong_phuc=dong_phuc,
        sgk=sgk, dung_cu_hoctap=dung_cu_hoctap, hoc_them=hoc_them, gd_khac=0,
        tc_giaoduc=0,
        tc_thuong_binh=tc_thuong_binh, tc_bao_tro_xh=tc_bao_tro_xh, tc_thien_tai=tc_thien_tai,
        db_trong_trot=db_trong_trot, db_chan_nuoi=db_chan_nuoi, db_dvnn=db_dvnn,
        db_trong_rung=db_trong_rung, db_nuoi_thuy_san=db_nuoi_thuy_san,
        thue_chan_nuoi=thue_chan_nuoi, thue_dvnn=thue_dvnn, thue_lam_nghiep=thue_lam_nghiep, 
        thue_kd_lam_nghiep=thue_kd_lam_nghiep, thue_doc_than=thue_doc_than,
        inc_tax_1=inc_tax_1, inc_tax_2=inc_tax_2, inc_tax_3=inc_tax_3, inc_tax_4=inc_tax_4, 
        inc_tax_5=inc_tax_5, inc_tax_6=inc_tax_6, inc_tax_7=inc_tax_7,
        inc_threshold_1=inc_threshold_1, inc_threshold_2=inc_threshold_2, inc_threshold_3=inc_threshold_3, 
        inc_threshold_4=inc_threshold_4, inc_threshold_5=inc_threshold_5, inc_threshold_6=inc_threshold_6,
        simulationYear=2025, baseYear=2022
    )

    reformed_data = calculate(ref_dat)
    reformed_gini_chi = calculate_gini(ref_dat, type = "custom_chiTieuBQ")
    reformed_gini_thu = calculate_gini(ref_dat, type='custom_thuBQ')
    
    ref_poverty = reformed_data["poverty"]    
    ref_poverty_ttnt = reformed_data["poverty_ttnt"] 
    ref_poverty_area = reformed_data["poverty_area"]   
    ref_poverty_prov = reformed_data["poverty_prov"]

    ref_gini = reformed_gini_chi['gini']
    ref_gini_ttnt = reformed_gini_chi["gini_ttnt"]
    ref_gini_area = reformed_gini_chi['gini_area']
    ref_gini_prov = reformed_gini_chi['gini_prov']
    
    ref_gini_thu = reformed_gini_thu['gini']
    ref_gini_ttnt_thu = reformed_gini_thu["gini_ttnt"]
    ref_gini_area_thu = reformed_gini_thu['gini_area']
    ref_gini_prov_thu = reformed_gini_thu['gini_prov']

    final_poverty = init_poverty.join(ref_poverty, on="povertyStatus", suffix="_reformed")
    final_poverty_ttnt = init_poverty_ttnt.join(ref_poverty_ttnt, on="tentinh", suffix="_reformed")
    final_poverty_area = init_poverty_area.join(ref_poverty_area, on='tentinh', suffix="_reformed")
    final_poverty_prov = init_poverty_prov.join(ref_poverty_prov, on='tentinh', suffix="_reformed")
   
    final_gini_ttnt = init_gini_ttnt.join(ref_gini_ttnt, on='tentinh', suffix="_reformed")
    final_gini_area = init_gini_area.join(ref_gini_area, on='tentinh', suffix="_reformed")
    final_gini_prov = init_gini_prov.join(ref_gini_prov, on='tentinh', suffix="_reformed")
    
    final_gini_ttnt_thu = init_gini_ttnt_thu.join(ref_gini_ttnt_thu, on='tentinh', suffix="_reformed")
    final_gini_area_thu = init_gini_area_thu.join(ref_gini_area_thu, on='tentinh', suffix="_reformed")
    final_gini_prov_thu = init_gini_prov_thu.join(ref_gini_prov_thu, on='tentinh', suffix="_reformed")

    thuCP = pd.DataFrame({
        "Mục":[
            "Tổng thu nhập chính phủ từ thuế và giáo dục BQDN", 
            "Thuế TNCN từ lương BQDN", 
            "Thuế kinh doanh chăn nuôi BQDN",
            "Thuế dịch vụ nông nghiệp BQDN", 
            "Thuế lâm nghiệp BQDN", 
            "Thuế kinh doanh lâm nghiệp BQDN",
            'Thu từ giáo dục công lập BQDN',
            "Thuế độc thân BQDN"
        ],
        "Gốc (Triệu VND)": [
            np.average(
                pd.DataFrame(init_dat[[
                    "thueLuong", 't_chanNuoi', "t_DVNN",
                    "t_lamNghiep", "t_KDLamNghiep", "thueDocThan",
                    "tongHocPhi",
                ]]).sum(axis=1),
                weights = init_dat['wt45']
            )/1000,
            np.nansum((init_dat["thueLuong"] * init_dat["wt45"]))/np.nansum(init_dat["wt45"])/1000,
            np.nansum((init_dat["t_chanNuoi"] * init_dat["wt45"]))/np.nansum(init_dat['wt45'])/1000,
            np.nansum((init_dat["t_DVNN"] * init_dat["wt45"]))/np.nansum(init_dat['wt45'])/1000, 
            np.nansum((init_dat["t_lamNghiep"] * init_dat["wt45"]))/np.nansum(init_dat['wt45'])/1000, 
            np.nansum((init_dat["t_KDLamNghiep"] * init_dat["wt45"]))/np.nansum(init_dat['wt45'])/1000, 
            np.nansum((init_dat["tongHocPhi"] * init_dat["wt45"]))/np.nansum(init_dat['wt45'])/1000,
            np.nansum((init_dat["thueDocThan"] * init_dat["wt45"]))/np.nansum(init_dat['wt45'])/1000
        ],
        "Cải cách (Triệu VND)": [
            sum([
                np.nansum((ref_dat["thueLuong"] * ref_dat["wt45"]))/sum(ref_dat["wt45"]), 
                np.nansum((ref_dat["t_chanNuoi"] * ref_dat["wt45"]))/sum(ref_dat['wt45']), 
                np.nansum((ref_dat["t_DVNN"] * ref_dat["wt45"]))/sum(ref_dat['wt45']), 
                np.nansum((ref_dat["t_lamNghiep"] * ref_dat["wt45"]))/sum(ref_dat['wt45']), 
                np.nansum((ref_dat["t_KDLamNghiep"] * ref_dat["wt45"]))/sum(ref_dat['wt45']), 
                np.nansum((ref_dat["tongHocPhi"] * ref_dat["wt45"]))/sum(ref_dat['wt45']),
                np.nansum((ref_dat["thueDocThan"] * ref_dat["wt45"]))/sum(ref_dat['wt45']) 
            ]) / 1000,

            (np.nansum((ref_dat["thueLuong"] * ref_dat["wt45"]))/sum(ref_dat["wt45"]))/1000, 
            (np.nansum((ref_dat["t_chanNuoi"] * ref_dat["wt45"]))/sum(ref_dat['wt45']))/1000, 
            (np.nansum((ref_dat["t_DVNN"] * ref_dat["wt45"]))/sum(ref_dat['wt45']))/1000, 
            (np.nansum((ref_dat["t_lamNghiep"] * ref_dat["wt45"]))/sum(ref_dat['wt45']))/1000, 
            (np.nansum((ref_dat["t_KDLamNghiep"] * ref_dat["wt45"]))/sum(ref_dat['wt45']))/1000, 
            (np.nansum((ref_dat["tongHocPhi"] * ref_dat["wt45"]))/sum(ref_dat['wt45']))/1000,
            (np.nansum((ref_dat["thueDocThan"] * ref_dat["wt45"]))/sum(ref_dat['wt45']))/1000 
        ]
    }).assign(
            thayDoi = lambda df: df["Cải cách (Triệu VND)"] - df["Gốc (Triệu VND)"] 
        ).rename(
            columns={
                0:"Mục",
                1:'Gốc (Triệu VND)',
                2:"Cải cách (Triệu VND)",
                'thayDoi':"Thay đổi (Triệu VND)"
            }
        ).style.apply(pos_neg_value, subset=["Thay đổi (Triệu VND)"], axis=1).format({
                'Gốc (Triệu VND)':"{:,.4f}",
                "Cải cách (Triệu VND)":"{:,.4f}",
                "Thay đổi (Triệu VND)": style_icon 
            })
    
    chiCP = pd.DataFrame({
        "Mục":[
            "Tổng chi trợ cấp, đền bù BQDN",
            "Trợ cấp thất nghiệp, thôi việc, mất sức lao động BQDN",
            "Đền bù trồng trọt BQDN",
            "Đền bù hoạt động chăn nuôi BQDN",
            "Đền bù dịch vụ nông nghiệp BQDN",
            "Đền bù hoạt động trồng rừng BQDN",
            "Đền bù hoạt động nuôi, trồng thủy sản BQDN",
            "Trợ cấp thương binh, liệt sỹ BQDN",
            "Trợ cấp các đối tượng bảo trợ xã hội BQDN",
            "Trợ cấp khắc phục thiên tai, dịch bệnh BQDN",
            'Trợ cấp giáo dục BQDN'
        ],
        "Gốc (Triệu VND)": [
            np.average(
                pd.DataFrame(init_dat[[
                    "troCap", "db_trongTrot", "db_chanNuoi",
                    "db_DVNN", 'db_trongRung', "db_thuySan",
                    "tc_giaoDuc", "tc_thuongBinh", "tc_xaHoi",
                    "tc_thienTai"
                ]]).sum(axis=1),
                weights = init_dat['wt_household']
            )/1000,
            np.nansum((init_dat["troCap"] * init_dat["wt_household"]))/np.nansum(init_dat["wt_household"])/1000,
            np.nansum((init_dat["db_trongTrot"] * init_dat["wt_household"]))/np.nansum(init_dat['wt_household'])/1000,
            np.nansum((init_dat["db_chanNuoi"] * init_dat["wt_household"]))/np.nansum(init_dat['wt_household'])/1000, 
            np.nansum((init_dat["db_DVNN"] * init_dat["wt_household"]))/np.nansum(init_dat['wt_household'])/1000, 
            np.nansum((init_dat["db_trongRung"] * init_dat["wt_household"]))/np.nansum(init_dat['wt_household'])/1000, 
            np.nansum((init_dat["db_thuySan"] * init_dat["wt_household"]))/np.nansum(init_dat['wt_household'])/1000,
            np.nansum((init_dat["tc_giaoDuc"] * init_dat["wt_household"]))/np.nansum(init_dat['wt_household'])/1000,
            np.nansum((init_dat["tc_thuongBinh"] * init_dat["wt_household"]))/np.nansum(init_dat['wt_household'])/1000,
            np.nansum((init_dat["tc_xaHoi"] * init_dat["wt_household"]))/np.nansum(init_dat['wt_household'])/1000,
            np.nansum((init_dat["tc_thienTai"] * init_dat["wt_household"]))/np.nansum(init_dat['wt_household'])/1000
        ],
        "Cải cách (Triệu VND)": [
            np.average(
                pd.DataFrame(ref_dat[[
                    "troCap", "db_trongTrot", "db_chanNuoi",
                    "db_DVNN", 'db_trongRung', "db_thuySan",
                    "tc_giaoDuc", "tc_thuongBinh", "tc_xaHoi",
                    "tc_thienTai"
                ]]).sum(axis=1),
                weights = ref_dat['wt_household']
            )/1000,
            np.nansum((ref_dat["troCap"] * ref_dat["wt_household"]))/np.nansum(ref_dat["wt_household"])/1000,
            np.nansum((ref_dat["db_trongTrot"] * ref_dat["wt_household"]))/np.nansum(ref_dat['wt_household'])/1000,
            np.nansum((ref_dat["db_chanNuoi"] * ref_dat["wt_household"]))/np.nansum(ref_dat['wt_household'])/1000, 
            np.nansum((ref_dat["db_DVNN"] * ref_dat["wt_household"]))/np.nansum(ref_dat['wt_household'])/1000, 
            np.nansum((ref_dat["db_trongRung"] * ref_dat["wt_household"]))/np.nansum(ref_dat['wt_household'])/1000, 
            np.nansum((ref_dat["db_thuySan"] * ref_dat["wt_household"]))/np.nansum(ref_dat['wt_household'])/1000,
            np.nansum((ref_dat["tc_giaoDuc"] * ref_dat["wt_household"]))/np.nansum(ref_dat['wt_household'])/1000,
            np.nansum((ref_dat["tc_thuongBinh"] * ref_dat["wt_household"]))/np.nansum(ref_dat['wt_household'])/1000,
            np.nansum((ref_dat["tc_xaHoi"] * ref_dat["wt_household"]))/np.nansum(ref_dat['wt_household'])/1000,
            np.nansum((ref_dat["tc_thienTai"] * ref_dat["wt_household"]))/np.nansum(ref_dat['wt_household'])/1000
        ]
    }).assign(
            thayDoi = lambda df: df["Cải cách (Triệu VND)"] - df["Gốc (Triệu VND)"] 
        ).rename(
            columns={
                0:"Mục",
                1:'Gốc (Triệu VND)',
                2:"Cải cách (Triệu VND)",
                'thayDoi':"Thay đổi (Triệu VND)"
            }
        ).style.apply(pos_neg_value, subset=["Thay đổi (Triệu VND)"], axis=1).format({
                'Gốc (Triệu VND)':"{:,.4f}",
                "Cải cách (Triệu VND)":"{:,.4f}",
                "Thay đổi (Triệu VND)": style_icon 
            })
    thuChiHo = pd.DataFrame({
            "Mục": [
                "Tổng thu nhập từ lương, kinh doanh hộ BQDN",
                "Chi phí kinh doanh hộ BQDN",
                "Lợi nhuận kinh doanh hộ BQDN",
                "Chi tiêu sinh hoạt BQDN"
            ],
            "Gốc (Triệu VND)": [
                np.average((init_dat["tongThuHo"] / init_dat['SONHANKHAU']), weights = init_dat["wt_household"]) / 1000,
                np.average((init_dat["tongChiHo"] / init_dat['SONHANKHAU']), weights = init_dat["wt_household"]) / 1000,
                np.average(
                    (init_dat["tongThuHo"] - init_dat["tongChiHo"]) / init_dat['SONHANKHAU'],
                    weights = init_dat["wt_household"]
                ) / 1000,
                np.average(
                    np.array(
                        init_dat.filter(
                            pl.col('custom_chiTieuBQ') > 0
                        ).select("custom_chiTieuBQ")
                    ),
                    weights=np.array(
                        init_dat.filter(
                            pl.col('custom_chiTieuBQ') > 0
                        ).select("wt_household")
                    )
                ) * 12 / 1000
            ],
            "Cải cách (Triệu VND)": [
                np.average((ref_dat["tongThuHo"] / ref_dat['SONHANKHAU']), weights = ref_dat["wt_household"]) / 1000,
                np.average((ref_dat["tongChiHo"] / ref_dat['SONHANKHAU']), weights = ref_dat["wt_household"]) / 1000,
                np.average(
                    (ref_dat["tongThuHo"] - ref_dat["tongChiHo"]) / ref_dat['SONHANKHAU'],
                    weights = ref_dat["wt_household"]
                ) / 1000,
                np.average(
                    np.array(
                        ref_dat.filter(
                            pl.col('custom_chiTieuBQ') > 0
                        ).select("custom_chiTieuBQ")
                    ),
                    weights=np.array(
                        ref_dat.filter(
                            pl.col('custom_chiTieuBQ') > 0
                        ).select("wt_household")
                    )
                ) * 12 / 1000
            ]
        }).assign(
            thayDoi = lambda df: df["Cải cách (Triệu VND)"] - df["Gốc (Triệu VND)"] 
        ).rename(
            columns={
                0:"Mục",
                1:'Gốc (Triệu VND)',
                2:"Cải cách (Triệu VND)",
                'thayDoi':"Thay đổi (Triệu VND)"
            }
        ).style.format(
            {
                'Gốc (Triệu VND)':"{:,.4f}",
                "Cải cách (Triệu VND)":"{:,.4f}",
                "Thay đổi (Triệu VND)": style_icon 
            }
        ).map(pos_neg_value, subset = "Thay đổi (Triệu VND)")

    # Save to session state
    st.session_state.init_dat = init_dat
    st.session_state.ref_dat = ref_dat

    st.session_state.thuCP = thuCP
    st.session_state.chiCP = chiCP
    st.session_state.thuChiHo = thuChiHo

    st.session_state.init_gini = init_gini
    st.session_state.init_gini_thu = init_gini_thu
    st.session_state.ref_gini = ref_gini
    st.session_state.ref_gini_thu = ref_gini_thu
    
    st.session_state.final_poverty = final_poverty.with_columns(
                    thayDoi = pl.col("pct_reformed") - pl.col("pct")
                )
    st.session_state.final_poverty_ttnt = final_poverty_ttnt.with_columns(
                tentinh = pl.when(pl.col("tentinh") == 1).then(pl.lit("Thành thị")).otherwise(pl.lit("Nông thôn")),
                thayDoi_UMIC = pl.col("UMIC_reformed") - pl.col("UMIC"),
                thayDoi_LMIC = pl.col("LMIC_reformed") - pl.col("LMIC"),
                thayDoi_IPL = pl.col("IPL_reformed") - pl.col("IPL")
            )
    
    st.session_state.final_poverty_area = final_poverty_area.with_columns(
        thayDoi_UMIC = pl.col("UMIC_reformed") - pl.col("UMIC"),
        thayDoi_LMIC = pl.col("LMIC_reformed") - pl.col("LMIC"),
        thayDoi_IPL = pl.col("IPL_reformed") - pl.col("IPL")
    )
    st.session_state.final_poverty_prov = final_poverty_prov.with_columns(
        thayDoi_UMIC = pl.col("UMIC_reformed") - pl.col("UMIC"),
        thayDoi_LMIC = pl.col("LMIC_reformed") - pl.col("LMIC"),
        thayDoi_IPL = pl.col("IPL_reformed") - pl.col("IPL")
    )
 
    st.session_state.final_gini_ttnt = final_gini_ttnt
    st.session_state.final_gini_area = final_gini_area
    st.session_state.final_gini_prov = final_gini_prov
 
    st.session_state.final_gini_ttnt_thu = final_gini_ttnt_thu
    st.session_state.final_gini_area_thu = final_gini_area_thu
    st.session_state.final_gini_prov_thu = final_gini_prov_thu

    st.switch_page("pages\\output.py")
        
