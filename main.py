import streamlit as st
import pandas as pd
import plotly.express as px
from ESLData import esl_data
from SDATData import sdat_data
import datetime as dt

st.set_page_config(layout="wide")
CURRENT_THEME = "light"


# Function to process the ESL data
def process_esl_data():
    # Parse the ESL files and convert them to two DataFrames: cumulative and monthly
    cumulative_data, monthly_data = esl_data()

    # Convert both lists to DataFrames
    df_cumulative = pd.DataFrame(cumulative_data)
    df_monthly = pd.DataFrame(monthly_data)

    # Convert 'TimePeriod' to datetime for easier resampling
    df_cumulative['TimePeriod'] = pd.to_datetime(df_cumulative['TimePeriod'], format='%Y-%m')
    df_monthly['TimePeriod'] = pd.to_datetime(df_monthly['TimePeriod'], format='%Y-%m')

    return df_cumulative, df_monthly


# Function to process the SDAT data
def process_sdat_data(directory='SDAT-Files'):
    # Call the sdat_data function to get cumulative and daily data
    cumulative_data, daily_data = sdat_data(directory)

    # Convert both lists to DataFrames
    df_cumulative = pd.DataFrame(cumulative_data, columns=['Label', 'Timestamp', 'CumulativeVolume'])
    df_daily = pd.DataFrame(daily_data, columns=['Label', 'Timestamp', 'DailyVolume'])

    # Convert 'Timestamp' to datetime for easier resampling
    df_cumulative['Timestamp'] = pd.to_datetime(df_cumulative['Timestamp'])
    df_daily['Timestamp'] = pd.to_datetime(df_daily['Timestamp'])

    return df_cumulative, df_daily


def daily_data():
    data = sdat_data()
    sequences_cumulative = data[0]
    sequences_daily = data[1]

    # Convert to DataFrame for easier manipulation
    df_cumulative = pd.DataFrame(sequences_cumulative, columns=['Label', 'Date', 'Cumulative'])
    df_daily = pd.DataFrame(sequences_daily, columns=['Label', 'Date', 'Daily'])

    # Display cumulative data
    st.subheader("Cumulative Data")
    st.write(df_cumulative)

    # Display daily data
    st.subheader("Daily Data")
    st.write(df_daily)

    # Plotting Cumulative Data
    st.subheader("Cumulative Data Visualization")
    fig_cumulative = px.bar(df_cumulative,
                            x='Date',
                            y='Cumulative',
                            color='Label',
                            title='Cumulative Data Over Time',
                            labels={'Cumulative': 'Cumulative Value'},
                            text='Cumulative')
    fig_cumulative.update_traces(texttemplate='%{text:.2f}', textposition='outside')
    fig_cumulative.update_layout(xaxis_title='Date', yaxis_title='Cumulative Value', barmode='stack')
    st.plotly_chart(fig_cumulative)

    # Plotting Daily Data
    st.subheader("Daily Data Visualization")
    fig_daily = px.bar(df_daily,
                       x='Date',
                       y='Daily',
                       color='Label',
                       title='Daily Data Over Time',
                       labels={'Daily': 'Daily Value'},
                       text='Daily')
    fig_daily.update_traces(texttemplate='%{text:.2f}', textposition='outside')
    fig_daily.update_layout(xaxis_title='Date', yaxis_title='Daily Value', barmode='stack')
    st.plotly_chart(fig_daily)


def monthly_data():
    pass


def yearly_data():
    pass


# Streamlit app
def main():
    st.title('Voltaflow Energie Visualizer')

    # Parse data
    df_cumulative, df_monthly = process_esl_data()
    df_cumulative_sdat, df_daily = process_sdat_data()

    if not df_cumulative.empty and not df_monthly.empty:
        # User selection for time granularity
        time_granularity = st.selectbox('Wählen Sie eine Zeitspanne aus', ('Monatlich', 'Jährlich', 'Täglich'))

        # Resample data based on user selection (yearly or monthly)
        if time_granularity == 'Jährlich':
            # Resample cumulative data to yearly
            df_cumulative_resampled = df_cumulative.resample('Y', on='TimePeriod').sum()
            df_cumulative_resampled['TimePeriod'] = df_cumulative_resampled.index

            # Resample monthly data to yearly
            df_monthly_resampled = df_monthly.resample('Y', on='TimePeriod').sum()
            df_monthly_resampled['TimePeriod'] = df_monthly_resampled.index

            # Set title for yearly
            cumulative_title = 'Kumulativer jährlicher Energiebezug und Einspeisung'
            monthly_title = 'Jährlicher Energiebezug und Einspeisung'
            xaxis_format = "%Y"  # Yearly format
        if time_granularity == 'Monatlich':
            # No resampling needed for monthly data
            df_cumulative_resampled = df_cumulative
            df_monthly_resampled = df_monthly

            # Set title for monthly
            cumulative_title = 'Kumulativer monatlicher Energiebezug und Einspeisung'
            monthly_title = 'Monatlicher Energiebezug und Einspeisung'
            xaxis_format = "%b %Y"  # Monthly format
        if time_granularity == 'Täglich':
            daily_data()

        # Visualization for cumulative data
        st.subheader('Cumulative Energy Data (Bezug and Einspeisung)')
        st.dataframe(df_cumulative_resampled)

        fig_cumulative = px.line(df_cumulative_resampled, x='TimePeriod', y=['Bezug', 'Einspeisung'],
                                 labels={'value': 'Energie (kWh)', 'TimePeriod': 'Zeitspanne'},
                                 title=cumulative_title,
                                 color_discrete_sequence=["#ff0000", "#00ff00"]
                                 )

        # Customize x-axis for cumulative data
        fig_cumulative.update_layout(
            autosize=False,
            margin=dict(l=40, r=40, b=100, t=80),
            xaxis=dict(
                tickmode='linear',
                dtick="M12" if time_granularity == 'Jährlich' else "D1" if time_granularity == 'Täglich' else "M1",
                tickformat=xaxis_format,
                tickangle=-45,
                title_font=dict(size=14),
                tickfont=dict(size=12),
            ),
            yaxis=dict(
                title_font=dict(size=14),
                tickfont=dict(size=12)
            )
        )

        # Display the cumulative plot
        st.plotly_chart(fig_cumulative, use_container_width=False)

        # Visualization for monthly data using a bar chart (beam diagram)
        st.subheader('Monatliche/Jährliche Energiestatistik (Bezug and Einspeisung)')
        st.dataframe(df_monthly_resampled)
        # Bar chart for monthly energy consumption
        fig_monthly = px.bar(df_monthly_resampled, x='TimePeriod', y=['Bezug', 'Einspeisung'],
                             barmode='group',
                             labels={'value': 'Energie (kWh)', 'TimePeriod': 'Monat'},
                             title=monthly_title,
                             color_discrete_sequence=["#ff0000", "#00ff00"]
                             )

        # Customize x-axis for monthly data
        fig_monthly.update_layout(
            autosize=False,
            width=1500,
            height=400,
            margin=dict(l=40, r=40, b=100, t=80),
            xaxis=dict(
                tickmode='linear',
                dtick="M12" if time_granularity == 'Jährlich' else "M1",  # Adjust tick based on granularity
                tickformat=xaxis_format,  # Dynamic format for month/year
                tickangle=-45,
                title_font=dict(size=14),
                tickfont=dict(size=12)
            ),
            yaxis=dict(
                title_font=dict(size=14),
                tickfont=dict(size=12)
            ),
            overwrite=True
        )

        # Display the monthly bar chart
        st.plotly_chart(fig_monthly, use_container_width=False)

    else:
        st.warning('Keine Daten zum Visualisieren')


if __name__ == '__main__':
    main()
