from data_loader import load_stock_almacen_huevo
import pandas as pd

df = load_stock_almacen_huevo()

print('Columnas disponibles:')
existencia_cols = [c for c in df.columns if 'EXISTENCIA' in str(c).upper()]
print(existencia_cols)

print('\nÚltimos valores de cada columna EXISTENCIA:')
for col in existencia_cols:
    last_val = df[col].dropna()
    if len(last_val) > 0:
        print(f'{col}: {last_val.iloc[-1]}')

print('\nSuma total:', sum([df[col].dropna().iloc[-1] if len(df[col].dropna()) > 0 else 0 for col in existencia_cols]))
