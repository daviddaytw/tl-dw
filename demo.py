import folium
import numpy as np
import pandas as pd
import streamlit as st
from sklearn.linear_model import LinearRegression

from streamlit_folium import st_folium
from streamlit_option_menu import option_menu

current_time = (pd.Timestamp('now') - pd.Timestamp('now').normalize()) / pd.Timedelta('1 hour')

def loadData(hospitalId, filename='hospital_data_sampleee.csv'):
    df = pd.read_csv(filename)
    df = df.loc[df['HospitalID'] == hospitalId]
    df["Check-in Time"] = (pd.to_datetime(df["Check-in Time"]) - pd.Timestamp('today').normalize()) / pd.Timedelta('1 hour')
    df["Entry Time"] = (pd.to_datetime(df["Entry Time"]) - pd.Timestamp('today').normalize()) / pd.Timedelta('1 hour')
    df["Completion Time"] = (pd.to_datetime(df["Completion Time"]) - pd.Timestamp('today').normalize()) / pd.Timedelta('1 hour')
    df['Waiting Time'] = (df['Entry Time'] - df['Check-in Time']) * 60
    df = df[['Check-in Time', 'Entry Time', 'Completion Time', 'Waiting Time']]
    return df

def calculatePatients(df):
    history = []
    for i in range(80, 240):
        t = i / 10
        history.append(len(df.loc[df['Check-in Time'] <= t].loc[t <= df['Entry Time']]))
    return pd.DataFrame({ 'Entry Time': np.array(range(80, 240)) / 10, 'Patient in line': history })

def estimateWaitTime(df):
    patientsInLine = calculatePatients(df)
    df = df[['Entry Time', 'Waiting Time']]
    df['Entry Time'] = df['Entry Time'].round(decimals=1)
    df = df.groupby('Entry Time').mean().reset_index()

    # Calculate the number of patient
    df = df.join(patientsInLine.set_index('Entry Time'), on='Entry Time', how='inner')
    Y = df.pop('Waiting Time').to_numpy().reshape(-1, 1)
    X = df.to_numpy()

    regr = LinearRegression()
    regr.fit(X, Y)

    return regr.predict(df.loc[df['Entry Time'] < current_time].to_numpy())[0][-1]

def render():
    zipcode = st.selectbox('Please enter your zipcode', ('94114',))

    hospitals = pd.read_csv('hospital_list.csv')

    col1, col2 = st.columns(2)

    with col1:
        # center on Liberty Bell, add marker
        m = folium.Map(location=[37.7585841, -122.4496457], zoom_start=12)
        
        for i, h in hospitals.iterrows():
            folium.Marker(
                [h['latitude'], h['longitude']], popup=h['Name'], tooltip=h['Name']
            ).add_to(m)

        # call to render Folium map in Streamlit
        st_data = st_folium(m, width=725)


    with col2:
        for i, h in hospitals.iterrows():
            with st.container():
                st.subheader(h['Name'])
                st.markdown(f"{h['Address']} [Open in map]({h['google_map']})")
                st.markdown(f"[Call {h['Phone']}](tel:{h['Phone']})")

                df = loadData(h['ID'])
                patientsInLine = calculatePatients(df)
                patientsInLine = patientsInLine[patientsInLine['Entry Time'] <= current_time].iloc[-1]['Patient in line']

                waitTime = estimateWaitTime(df)
                st.write(f"**⏳Current wait time: <span style=\"font-size:x-large;\">{round(waitTime)}</span> min**", unsafe_allow_html=True)
                st.write(f"**👥Number of patients waiting: <span style=\"font-size:x-large;\">{round(patientsInLine)}</span> ppl**", unsafe_allow_html=True)
                st.divider()
