import streamlit as st
import polars as pl
import pandas as pd
import plotly.express as px
import numpy as np
from functions import pos_neg_value, pos_neg_value_reversed, draw_map, style_icon
from streamlit_elements import dashboard, elements, mui, nivo
from io import StringIO
from time import gmtime, strftime, sleep

st.set_page_config(
    page_title="SciEco Vietnam Microsimulation",
    layout='wide',
    page_icon='https://scontent.fhan14-5.fna.fbcdn.net/v/t39.30808-6/453235411_475775001872764_4435076249897854084_n.jpg?_nc_cat=106&ccb=1-7&_nc_sid=6ee11a&_nc_ohc=0lI8dxcOJHAQ7kNvwHG8dAX&_nc_oc=AdnvOwPvZjZ0fpGYFoemM2di5C0VtXWKg5AAsPEniYetUVsxYpR2KNyV-wgMOivp-GqG3ejyKC5XGBJgpM5SXNli&_nc_zt=23&_nc_ht=scontent.fhan14-5.fna&_nc_gid=GqSTdnmXZh51d3FmFvHNzA&oh=00_AfGh_WsOTU0P-EzgTsxPKHbrdoN81uISXCscQj9xwb33jQ&oe=6811278A',
    menu_items={
        'About':'''Website: http://scienceforeconomics.com \n
Facebook: Science for Economics'''
    }
)

required_data = [
    "init_dat",
    "ref_dat",

    'thuCP',
    'chiCP',
    'thuChiHo',

    "init_gini",
    "ref_gini",
    "init_gini_thu",
    "ref_gini_thu",
    
    "final_poverty",
    "final_poverty_ttnt",
    "final_poverty_area",
    "final_poverty_prov",

    "final_gini_ttnt",
    "final_gini_area",
    "final_gini_prov",

    "final_gini_ttnt_thu",
    "final_gini_area_thu",
    "final_gini_prov_thu"
]

if any(x not in st.session_state for x in required_data):
    print("No initial data, returning to input screen")
    st.switch_page("app.py")

# load Initial data
init_dat = st.session_state.init_dat
ref_dat = st.session_state.ref_dat

thuCP = st.session_state.thuCP
chiCP = st.session_state.chiCP
thuChiHo = st.session_state.thuChiHo

init_gini = st.session_state.init_gini
ref_gini = st.session_state.ref_gini
init_gini_thu = st.session_state.init_gini_thu
ref_gini_thu = st.session_state.ref_gini_thu

final_poverty = st.session_state.final_poverty
final_poverty_ttnt = st.session_state.final_poverty_ttnt
final_poverty_area = st.session_state.final_poverty_area 
final_poverty_prov = st.session_state.final_poverty_prov

final_gini_ttnt = st.session_state.final_gini_ttnt
final_gini_area = st.session_state.final_gini_area
final_gini_prov = st.session_state.final_gini_prov

final_gini_ttnt_thu = st.session_state.final_gini_ttnt_thu
final_gini_area_thu = st.session_state.final_gini_area_thu
final_gini_prov_thu = st.session_state.final_gini_prov_thu

if 'inactiveButton' not in st.session_state:
    st.session_state.inactiveButton = True

upperButton_left, upperButton_right, dummy_column = st.columns([1,1,12])
with upperButton_left:
    if st.button("Quay lại"):
        st.switch_page("app.py")

@st.dialog("Các thay đổi vừa thực hiện")
def logger():
    log = pl.read_json("log.json").rename({
        'var':'Mục', 'init':'Giá trị ban đầu', 'reform':'Giá trị điều chỉnh'
    })
    st.dataframe(log, hide_index=True)
    if st.button("Lưu bản ghi", use_container_width=True):
        log.write_excel(f"input_log\micro_log_{strftime('%Y%m%d%H%M%S', gmtime())}")
        st.success(f"Đã lưu log tại input_log\micro_log_{strftime('%Y%m%d%H%M%S', gmtime())}.xlsx")
        st.rerun()
    if st.button('Return', use_container_width=True):
        st.rerun()

with upperButton_right:
    if 'logger' not in st.session_state:
        if st.button('Log'):
            logger()

st.title("Kết quả mô phỏng")

tab_chart, tab_thuchi, tab_gini, tab_ngheo = st.tabs(
    ["Tổng quan", "Thu, chi", "Bất bình đẳng thu nhập", "Tỷ lệ nghèo"]
)

with tab_chart:

    st.header("Tổng quan")

    reform_toggle = st.toggle("Xem tác động chính sách")

    left_opt, right_opt = st.columns(spec=[0.25,0.75])
    with left_opt:
        overviewMapOptions = {
                    "custom_thuBQ":"Thu bình quân 1 tháng (Triệu VND)",
                    "custom_chiTieuBQ":"Chi tiêu bình quân đầu người 1 tháng (Triệu VND)",
                    'povertyRate':"Tỷ lệ hộ nghèo"
                } 
        mapDataType = st.selectbox(
            "Chọn loại dữ liệu",
            options=('custom_thuBQ', "custom_chiTieuBQ", 'povertyRate'),
            format_func=lambda x: overviewMapOptions.get(x)
        )
       
        if mapDataType == "povertyRate":
            povertyTypes = st.pills(
                'Chọn chỉ tiêu đánh giá nghèo:',
                options=['Normal', "UMIC", 'LMIC', 'IPL'],
                selection_mode='single',
                default='LMIC',
                disabled=False
            )
            # st.session_state.inactiveButton = False
            init_map_dat = final_poverty_prov.select(["tentinh", f"{povertyTypes}"])
            if povertyTypes == "Normal":
                ref_map_dat = init_map_dat
                metric_var = 'Normal'
            else:
                ref_map_dat = final_poverty_prov.select(["tentinh", f"{povertyTypes}_reformed"])
                metric_var = f"{povertyTypes}_reformed"
            metric_data = ref_map_dat.drop_nans().drop_nulls()
        else:
            povertyTypes = st.pills(
                        'Chọn chỉ tiêu đánh giá nghèo:',
                        options=['Normal', "UMIC", 'LMIC', 'IPL'],
                        selection_mode='single',
                        default='LMIC',
                        disabled=True
                    )
            init_map_dat = init_dat
            ref_map_dat = ref_dat
            metric_var = mapDataType
            metric_data = ref_map_dat.select('tentinh',f'{metric_var}').group_by('tentinh')\
                .agg((pl.col(f"{metric_var}").mean())/1000)
        st.metric(
            f'''Tỉnh, thành phố có {overviewMapOptions.get(mapDataType)} \n 
cao nhất:''',
            metric_data.sort(by=metric_var, descending=True).row(index=0)[0]
        )
        st.metric(
            f'''Tỉnh, thành phố có {overviewMapOptions.get(mapDataType)} \n 
thấp nhất:''',
            metric_data.sort(by=metric_var, descending=False).row(index=0)[0]
        )

    init_fig = draw_map(init_map_dat, variable=mapDataType, variable_name=overviewMapOptions.get(mapDataType))
    ref_fig = draw_map(ref_map_dat, variable=mapDataType, variable_name=overviewMapOptions.get(mapDataType))

    if reform_toggle:
        plot_fig = ref_fig
        status = "sau cải cách"
        value = 'pct_reformed'
    else:
        plot_fig = init_fig
        status = "trước cải cách"
        value = 'pct'
    
    with right_opt:
        st.markdown(f"**{overviewMapOptions.get(mapDataType)} {status}**")
        st.plotly_chart(plot_fig, key="init_map")

    poverty_chart = px.pie(
        final_poverty, 
        values='pct', 
        names='povertyStatus', 
        color_discrete_sequence=px.colors.sequential.Blues_r
    )

    secondRow_left, secondRow_right = st.columns([0.6, 0.4])
    with secondRow_left:
        st.markdown(f"**Tỷ lệ hộ nghèo {status}**")
        st.plotly_chart(poverty_chart)
    with secondRow_right:
        st.metric("Chỉ số bất bình đẳng GINI theo chi tiêu", ref_gini, delta= round(init_gini - ref_gini, 4))
        st.metric("Chỉ số bất bình đẳng GINI theo thu nhập", ref_gini_thu, delta= round(init_gini_thu - ref_gini_thu, 4))

with tab_thuchi:
    st.header("Thu, chi hộ gia đình")
    
    st.dataframe(thuChiHo, hide_index=True)

    st.header("Thu, chi vi mô chính phủ")
    st.markdown("Thu chính phủ")
    st.dataframe(thuCP, hide_index=True)

    st.markdown("Chi chính phủ")
    st.dataframe(chiCP,hide_index=True)

with tab_ngheo:
    st.header("Tỷ lệ nghèo (World Bank)")
    ngheo_left, ngheo_right = st.columns([0.35, 0.65])
    with ngheo_right:
        st.markdown("Tỷ lệ nghèo toàn quốc")
        st.dataframe(
            pd.DataFrame(final_poverty).rename(
                columns={
                    0:"Chỉ tiêu",
                    1: "Tỷ lệ gốc",
                    2: "Tỷ lệ sau cải cách",
                    3: "Thay đổi"
                }).style.apply(pos_neg_value_reversed, subset=["Thay đổi"], axis=1).format({
                    "Tỷ lệ gốc":"{:,.2%}",
                    "Tỷ lệ sau cải cách":"{:,.2%}",
                    "Thay đổi":style_icon
                }),
                hide_index=True
        )
    
    with ngheo_left:
        povertyOptions = {
                "UMIC":"Nước thu nhập trung bình cao - UMIC",
                "LMIC":"Nước thu nhập trung bình thấp - LMIC",
                "IPL":"Ngưỡng nghèo quốc tế - IPL"
            } 

        povertyLine = st.radio(
            "Chọn ngưỡng đánh giá nghèo",
            ('UMIC', 'LMIC', 'IPL'),
            format_func= lambda x: povertyOptions.get(x),
            captions = [
                "UMIC (Upper-Middle-Income Countries): Đường tỷ lệ nghèo cho các quốc gia thu nhập trung bình cao, hiện tại là USD 6.85/ngày (PPP 2017).",
                "LMIC (Lower-Middle-Income Countries): Đường tỷ lệ nghèo cho các quốc gia thu nhập trung bình thấp, hiện tại là USD 3.65/ngày (PPP 2017).",
                "IPL (International Poverty Line): Đường nghèo quốc tế, hiện tại là USD 2.15/ngày (theo PPP 2017), dùng để đo lường nghèo đói cực đoan toàn cầu."
            ]
    )

    st.markdown("Tỷ lệ nghèo phân theo thành thị và nông thôn")
    st.dataframe(
        pd.DataFrame(       
            final_poverty_ttnt.select(["tentinh", "Normal", f"{povertyLine}", f"{povertyLine}_reformed", f"thayDoi_{povertyLine}"])
        ).rename(columns={
                0:"Khu vực",
                1: "Normal",
                2: f"{povertyLine}",
                3: f"{povertyLine} sau cải cách",
                4: "Thay đổi"
            }).style.apply(pos_neg_value_reversed, subset=["Thay đổi"], axis=1).format({
                'Normal':"{:,.2%}",
                f"{povertyLine}":"{:,.2%}",
                f"{povertyLine} sau cải cách":"{:,.2%}",
                "Thay đổi":style_icon
            }),
        hide_index = True
    )
    st.markdown("Tỷ lệ nghèo phân theo miền")
    st.dataframe(
        pd.DataFrame(
            final_poverty_area.select(["tentinh", "Normal", f"{povertyLine}", f"{povertyLine}_reformed", f"thayDoi_{povertyLine}"])\
        ).rename(columns={
                0:"Khu vực",
                1: "Normal",
                2: f"{povertyLine}",
                3: f"{povertyLine} sau cải cách",
                4: "Thay đổi"
            }).style.apply(pos_neg_value_reversed, subset=["Thay đổi"], axis=1).format({
                'Normal':"{:,.2%}",
                f"{povertyLine}":"{:,.2%}",
                f"{povertyLine} sau cải cách":"{:,.2%}",
                "Thay đổi":style_icon
                
            }),
        hide_index=True
    )
    st.markdown("Tỷ lệ nghèo phân theo tỉnh, thành phố")
    st.dataframe(
        pd.DataFrame(
            final_poverty_prov.select(["tentinh", "Normal", f"{povertyLine}", f"{povertyLine}_reformed", f"thayDoi_{povertyLine}"])
        ).rename(columns={
                0:"Khu vực",
                1: "Normal",
                2: f"{povertyLine}",
                3: f"{povertyLine} sau cải cách",
                4: "Thay đổi"
            }).style.apply(pos_neg_value_reversed, subset=["Thay đổi"], axis=1).format({
                'Normal':"{:,.2%}",
                f"{povertyLine}":"{:,.2%}",
                f"{povertyLine}":"{:,.2%}",
                f"{povertyLine} sau cải cách":"{:,.2%}",
                "Thay đổi":style_icon
                
            }),
        hide_index=True
    )

with tab_gini:
    st.header("Bất bình đẳng")
    giniOptions = {
            "gini_chi":'Tính theo chi tiêu bình quân hộ', 
            "gini_thu":'Tính theo thu nhập bình quân hộ'
        } 

    gin_opt, gin_left, gin_right = st.columns(3)
    with gin_opt:
        giniVar = st.selectbox(
            "Chọn phương pháp tính GINI",
            ("gini_chi", "gini_thu"),
            format_func= lambda x: giniOptions.get(x)
        )
    if giniVar == "gini_chi":
        init_gini = st.session_state.init_gini
        ref_gini = st.session_state.ref_gini
        final_gini_ttnt = st.session_state.final_gini_ttnt
        final_gini_area = st.session_state.final_gini_area
        final_gini_prov = st.session_state.final_gini_prov

    elif giniVar == "gini_thu":
        init_gini = st.session_state.init_gini_thu
        ref_gini = st.session_state.ref_gini_thu
        final_gini_ttnt = st.session_state.final_gini_ttnt_thu
        final_gini_area = st.session_state.final_gini_area_thu
        final_gini_prov = st.session_state.final_gini_prov_thu
    
    gin_left.metric("Chỉ số GINI toàn quốc gốc", init_gini)
    gin_right.metric("Chỉ số GINI toàn quốc sau cải cách", ref_gini, delta= round(init_gini - ref_gini, 4))
    st.markdown("Chỉ số GINI phân theo thành thị và nông thôn")
    st.dataframe(
        pd.DataFrame(final_gini_ttnt.with_columns(
            tentinh = pl.when(pl.col("tentinh")==1).then(pl.lit("Thành thị")).otherwise(pl.lit("Nông thôn")),
            thayDoi = pl.col('gini_reformed') - pl.col('gini') 
        )).rename(
            columns={
                0:"Khu vực",
                1:'GINI',
                2:"GINI sau cải cách",
                3:"Thay đổi"
            }
        ).style.apply(pos_neg_value, subset=["Thay đổi"], axis=1).format({
                'GINI':"{:,.4f}",
                "GINI sau cải cách":"{:,.4f}",
                "Thay đổi": style_icon 
            }),
        hide_index=True
    )
    st.markdown("Chỉ số GINI phân theo miền")
    st.dataframe(
        pd.DataFrame(
            final_gini_area.with_columns(
                thayDoi = pl.col("gini_reformed") - pl.col("gini") 
            ).rename({
                "tentinh":"Miền",
                "gini":'GINI',
                "gini_reformed":"GINI sau cải cách",
                "thayDoi":"Thay đổi"
            })
        ).rename(
            columns={
                0:"Khu vực",
                1:'GINI',
                2:"GINI sau cải cách",
                3:"Thay đổi"
            }
        ).style.apply(pos_neg_value, subset=["Thay đổi"], axis=1).format({
                'GINI':"{:,.4f}",
                "GINI sau cải cách":"{:,.4f}",
                "Thay đổi": style_icon 
            }),
        hide_index=True
    )
    st.markdown("Chỉ số GINI phân theo tỉnh, thành phố")
    st.dataframe(
        pd.DataFrame(
            final_gini_prov.with_columns(
                thayDoi = pl.col("gini_reformed") - pl.col("gini") 
            ).rename({
                "tentinh":"Tỉnh, thành phố",
                "gini":'GINI',
                "gini_reformed":"GINI sau cải cách",
                "thayDoi":"Thay đổi"
            })
        ).rename(
            columns={
                0:"Khu vực",
                1:'GINI',
                2:"GINI sau cải cách",
                3:"Thay đổi"
            }
        ).style.apply(pos_neg_value, subset=["Thay đổi"], axis=1).format({
                'GINI':"{:,.4f}",
                "GINI sau cải cách":"{:,.4f}",
                "Thay đổi": style_icon 
            }),
        hide_index=True
    )
