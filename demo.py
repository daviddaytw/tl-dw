import folium
import numpy as np
import pandas as pd
import streamlit as st
from sklearn.linear_model import LinearRegression

from streamlit_folium import st_folium

# Some global variables
current_time = (pd.Timestamp('now') - pd.Timestamp('now').normalize()) / pd.Timedelta('1 hour')
ZIPCODES = {'94114': [37.7585841, -122.4496457], '94612': [37.8044871,-122.2706511]}

"""
Function to load and convert hospital's data.

"""
def loadData(hospitalId, filename='hospital_data_sampleee.csv'):
    df = pd.read_csv(filename)
    df = df.loc[df['HospitalID'] == hospitalId]
    df["Check-in Time"] = (pd.to_datetime(df["Check-in Time"]) - pd.Timestamp('today').normalize()) / pd.Timedelta('1 hour')
    df["Entry Time"] = (pd.to_datetime(df["Entry Time"]) - pd.Timestamp('today').normalize()) / pd.Timedelta('1 hour')
    df["Completion Time"] = (pd.to_datetime(df["Completion Time"]) - pd.Timestamp('today').normalize()) / pd.Timedelta('1 hour')
    df['Waiting Time'] = (df['Entry Time'] - df['Check-in Time']) * 60
    df = df[['Check-in Time', 'Entry Time', 'Completion Time', 'Waiting Time']]
    return df

"""
Calculate numbers of patients waiting in line.
"""
def calculatePatients(df):
    history = []
    for i in range(80, 240): # 8 am to 12 am
        t = i / 10
        history.append(len(df.loc[df['Check-in Time'] <= t].loc[t <= df['Entry Time']]))
    return pd.DataFrame({ 'Entry Time': np.array(range(80, 240)) / 10, 'Patient in line': history })

"""
Estimate the real-time waiting time.
"""
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

"""
Callee function to render the demo page.
"""
def render():
    zipcode = st.selectbox(
        'Please enter your ZIP Code (Currently only available in San Francisco and Oakland.)',
        [''] + list(ZIPCODES.keys())
    )

    if zipcode != '':
        hospitals = pd.read_csv('hospital_list.csv')

        # For each hospital estimate wait time.
        waitingTime = []
        inLine = []
        for i, h in hospitals.iterrows():
            df = loadData(h['ID'])
            waitingTime.append(estimateWaitTime(df))
            l = calculatePatients(df)
            inLine.append(l[l['Entry Time'] <= current_time].iloc[-1]['Patient in line'])
        hospitals['Waiting Time'] = waitingTime
        hospitals['Patient In Line'] = inLine
        hospitals = hospitals.sort_values(by='Waiting Time')

        col1, col2 = st.columns(2)

        # Left column shows the map.
        with col1:
            # center on Liberty Bell, add marker
            m = folium.Map(location=ZIPCODES[zipcode], zoom_start=12)
            
            for i, h in hospitals.iterrows():
                info = f"{h['Name']} ({round(h['Waiting Time'])} min)"
                folium.Marker(
                    [h['latitude'], h['longitude']], popup=info, tooltip=info
                ).add_to(m)

            # call to render Folium map in Streamlit
            st_folium(m, width=725)


        # Right column shows the list of hospitals.
        with col2:

            # Create a data card for each hospital.
            for i, h in hospitals.iterrows():
                # Ignore if too far.
                if abs(h['latitude'] - ZIPCODES[zipcode][0]) + abs(h['longitude'] - ZIPCODES[zipcode][1]) > 0.1:
                    continue

                with st.container():
                    st.subheader(h['Name'])
                    st.markdown(f"{h['Address']} [Open in map]({h['google_map']})")
                    st.markdown(f"[Call {h['Phone']}](tel:{h['Phone']})")

                    
                    st.write(f"**⏳Current wait time: <span style=\"font-size:x-large;\">{round(h['Waiting Time'])}</span> minutes**", unsafe_allow_html=True)
                    st.write(f"**👥Number of patients waiting now: <span style=\"font-size:x-large;\">{round(h['Patient In Line'])}</span> people**", unsafe_allow_html=True)
                    st.divider()
