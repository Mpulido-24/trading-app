import streamlit as st
import pandas as pd
import talib
import yfinance as yf
import numpy as np

# Configuración de la página
st.set_page_config(page_title="App de Trading", layout="wide", page_icon="📈")
st.title("📈 App de Trading - Señales en Tiempo Real")
st.markdown("<h3 style='color: blue;'>📊 Estrategia basada en patrones de velas, soportes/resistencias e indicadores técnicos</h3>", unsafe_allow_html=True)

# Lista de divisas más comunes
par_divisas = ["EURUSD=X", "GBPUSD=X", "USDJPY=X", "AUDUSD=X", "USDCAD=X", "USDCHF=X", "NZDUSD=X"]

# Función para obtener datos de Yahoo Finance
@st.cache_data
def get_data(ticker):
    try:
        data = yf.download(ticker, period='7d', interval='15m')  # Datos de 15 minutos
        if data.empty:
            return None
        data.dropna(inplace=True)
        return data
    except Exception as e:
        return None

# Función para analizar el mercado
def analyze_market(data):
    close_prices = np.array(data['Close'], dtype=float).ravel()
    high_prices = np.array(data['High'], dtype=float).ravel()
    low_prices = np.array(data['Low'], dtype=float).ravel()
    volume = np.array(data['Volume'], dtype=float).ravel()
    
    data['EMA_20'] = talib.EMA(close_prices, timeperiod=20)
    data['ADX'] = talib.ADX(high_prices, low_prices, close_prices, timeperiod=14)
    macd, macd_signal, _ = talib.MACD(close_prices, fastperiod=12, slowperiod=26, signalperiod=9)
    data['MACD'] = macd
    data['MACD_signal'] = macd_signal
    data['RSI'] = talib.RSI(close_prices, timeperiod=14)
    data['BB_upper'], data['BB_middle'], data['BB_lower'] = talib.BBANDS(close_prices, timeperiod=20)
    data['ATR'] = talib.ATR(high_prices, low_prices, close_prices, timeperiod=14)
    data['Volumen'] = volume
    
    return data

# Generar señal de compra o venta
def generate_signal(data):
    last_row = data.iloc[-1]
    close = float(last_row['Close'])
    ema_20 = float(last_row['EMA_20'])
    macd = float(last_row['MACD'])
    macd_signal = float(last_row['MACD_signal'])
    rsi = float(last_row['RSI'])
    volumen = float(last_row['Volumen'])
    
    tendencia = "Alcista" if close > ema_20 else "Bajista"
    
    if tendencia == "Alcista" and rsi > 40 and macd > macd_signal and volumen > 0.2 * np.mean(data['Volumen']):
        return "✅ Comprar a 1 minuto", "#00FF00"
    elif tendencia == "Alcista" and rsi > 45 and macd > macd_signal and volumen > 0.3 * np.mean(data['Volumen']):
        return "✅ Comprar a 5 minutos", "#32CD32"
    elif tendencia == "Bajista" and rsi < 60 and macd < macd_signal and volumen > 0.2 * np.mean(data['Volumen']):
        return "❌ Vender a 1 minuto", "#FF4500"
    elif tendencia == "Bajista" and rsi < 55 and macd < macd_signal and volumen > 0.3 * np.mean(data['Volumen']):
        return "❌ Vender a 5 minutos", "#FF0000"
    else:
        return "🟡 Esperar", "#FFA500"

# Botón para actualizar manualmente
if st.button("🔄 Actualizar Señales"):
    st.cache_data.clear()
    st.rerun()

# Mostrar señales para todas las divisas
st.subheader("📊 Señales para divisas más comunes")

resultados = []
for ticker in par_divisas:
    data = get_data(ticker)
    if data is not None:
        try:
            data = analyze_market(data)
            signal, color = generate_signal(data)
            resultados.append([ticker, signal, color])
        except Exception as e:
            resultados.append([ticker, f"❌ Error: {e}", "#FF0000"])
    else:
        resultados.append([ticker, "⚠ No hay datos", "#808080"])

# Mostrar los resultados en tarjetas
total_divisas = len(resultados)
col1, col2 = st.columns(2)
for i, (ticker, signal, color) in enumerate(resultados):
    with col1 if i % 2 == 0 else col2:
        st.markdown(
            f"""
            <div style="background-color: {color}; padding: 10px; border-radius: 10px; margin: 10px; text-align: center;">
                <h3 style="color: white;">{ticker}</h3>
                <p style="color: white; font-size: 20px; font-weight: bold;">{signal}</p>
            </div>
            """,
            unsafe_allow_html=True
        )

# Mostrar los valores de los indicadores en pantalla
st.subheader("📌 Últimos valores de los indicadores")
for ticker in par_divisas:
    data = get_data(ticker)
    if data is not None:
        data = analyze_market(data)
        last_row = data.iloc[-1]
        st.write(f"**{ticker}** - RSI: {last_row['RSI']:.2f}, MACD: {last_row['MACD']:.2f}, Volumen: {last_row['Volumen']:.2f}")
