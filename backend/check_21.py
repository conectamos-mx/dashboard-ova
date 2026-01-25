import pandas as pd
from data_loader import load_excel_sheet

df = load_excel_sheet('ventas', 'EGRESOS EN EFECTIVO', header=8)
df = df.rename(columns={
    'ID': 'id',
    'FECHA': 'fecha',
    'IMPORTE': 'importe',
    'CONCEPTO': 'concepto'
})

df['fecha'] = pd.to_datetime(df['fecha'], errors='coerce')
df_21 = df[df['fecha'] == '2026-01-21']
df_21_valid = df_21[(df_21['importe'].notna()) & (df_21['importe'] > 0)]

print('Registros del 21/01:')
print(f'Total: {len(df_21_valid)}')
print(f'Suma: ${df_21_valid["importe"].sum():,.2f}')
print('\nDetalle:')
for _, row in df_21_valid.iterrows():
    id_val = row['id'] if pd.notna(row['id']) else 'Sin ID'
    print(f'{id_val}: ${row["importe"]:,.2f} - {row["concepto"]}')
