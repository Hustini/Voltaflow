import streamlit as st
import pandas as pd
import plotly.express as px

# Beispiel-Daten
data = {
    'Datum': pd.date_range(start='2023-01-01', periods=100, freq='D'),
    'Einspeisung': pd.Series(range(100)).apply(lambda x: x*0.6),
    'Bezug': pd.Series(range(100)).apply(lambda x: x*0.8)
}

df = pd.DataFrame(data)

# Streamlit Plotly Diagramme
st.title("Stromübersicht")

fig = px.line(df, x='Datum', y=['Einspeisung', 'Bezug'], title='Einspeisung und Bezug')
st.plotly_chart(fig)

# Auswahl der Aggregation
aggregation = st.selectbox("Zeitskala", ["Tage", "Wochen", "Monate"])

if aggregation == "Wochen":
    df_agg = df.resample('W', on='Datum').sum()
elif aggregation == "Monate":
    df_agg = df.resample('M', on='Datum').sum()
else:
    df_agg = df

fig_agg = px.line(df_agg, x=df_agg.index, y=['Einspeisung', 'Bezug'], title=f'Einspeisung und Bezug ({aggregation})')
st.plotly_chart(fig_agg)