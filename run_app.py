import streamlit.web.cli as stcli
import os, sys

if "__name__" == "__main__":
    stcli._main_run_clExplicit("app.py", 'streamlit run')