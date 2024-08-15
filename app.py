import streamlit as st
import barcode
from barcode.writer import ImageWriter
import random
import csv
import io
import zipfile
import base64
import pandas as pd

def generar_ean13_aleatorio():
    """Genera un número EAN-13 aleatorio válido (12 dígitos + dígito de control)"""
    ean_base = ''.join([str(random.randint(0, 9)) for _ in range(12)])
    return ean_base

def generar_codigos_de_barras(productos):
    # Crear un archivo CSV en memoria
    csv_buffer = io.StringIO()
    csv_writer = csv.writer(csv_buffer)
    csv_writer.writerow(["Nombre del Producto", "Código EAN-13"])

    # Crear un archivo ZIP en memoria
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'a', zipfile.ZIP_DEFLATED, False) as zip_file:
        datos = []
        for producto in productos:
            ean = generar_ean13_aleatorio()

            # Crear el código de barras EAN-13
            ean13 = barcode.get('ean13', ean, writer=ImageWriter())
            
            # Guardar la imagen en memoria
            img_buffer = io.BytesIO()
            ean13.write(img_buffer)
            
            # Añadir la imagen al archivo ZIP
            zip_file.writestr(f"{producto}.png", img_buffer.getvalue())

            # Agregar datos al archivo CSV y a la lista de datos
            csv_writer.writerow([producto, ean])
            datos.append({"Nombre del Producto": producto, "Código EAN-13": ean})

    # Añadir el archivo CSV al ZIP
    zip_buffer.seek(0)
    with zipfile.ZipFile(zip_buffer, 'a', zipfile.ZIP_DEFLATED, False) as zip_file:
        zip_file.writestr("productos_con_codigos_de_barras.csv", csv_buffer.getvalue())

    return zip_buffer.getvalue(), datos

def main():
    st.title("Generador de Códigos de Barras EAN-13")

    # Área de texto para ingresar los nombres de los productos
    productos_input = st.text_area("Ingrese los nombres de los productos (uno por línea):", 
                                   "PASTA DE MANI LB\nMANI 1LB")

    productos = [p.strip() for p in productos_input.split('\n') if p.strip()]

    if st.button("Generar Códigos de Barras"):
        if productos:
            zip_file, datos = generar_codigos_de_barras(productos)
            
            # Crear un enlace de descarga para el archivo ZIP
            b64 = base64.b64encode(zip_file).decode()
            href = f'<a href="data:application/zip;base64,{b64}" download="codigos_de_barras.zip">Descargar Códigos de Barras</a>'
            st.markdown(href, unsafe_allow_html=True)
            
            st.success("Códigos de barras generados exitosamente. Haz clic en el enlace para descargar.")

            # Mostrar la tabla con los datos generados
            df = pd.DataFrame(datos, columns=["Nombre del Producto", "Código EAN-13"])
            st.subheader("Códigos EAN-13 Generados:")
            st.dataframe(df.style.hide(), hide_index=True)

        else:
            st.error("Por favor, ingrese al menos un nombre de producto.")

if __name__ == "__main__":
    main()