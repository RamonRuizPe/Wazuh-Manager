import json
from datetime import date
from lxml import etree

def json_to_xtm(json_str, file_name: str = f"{date.today()}"):
    # Generación del elemento json para ser modificado
    json_obj = json.loads(json_str)

    # Creación del elemento padre con la relación a XTM
    root = etree.Element("topicMap", xmlns="http://www.topicmaps.org/xtm/1.0/")
    
    # Falta analizar de qué forma se puede hacer correctamente la traducción.
    # Preliminar
    for key, value in json_obj.items():
        # Crear un tema con el nombre de la clave
        theme_elem = etree.SubElement(root, "topic")
        name_elem = etree.SubElement(theme_elem, "baseName")
        name_elem.text = key

        if isinstance(value, dict):
            # Agregar las propiedades como un conjunto de temas relacionados
            for subkey, subvalue in value.items():
                value_elem = etree.SubElement(theme_elem, "occurrence")
                value_elem.set("resourceRef", subkey)
                value_elem.text = str(subvalue)
        else:
            # Agregar el valor como una propiedad del tema
            value_elem = etree.SubElement(theme_elem, "occurrence")
            value_elem.set("resourceRef", "value")
            value_elem.text = str(value)
            
    # Se devuelve el árbol XTM creado.
    et = etree.ElementTree(root)
    file_name = file_name + f"_{date.today()}" if file_name in str(date.today()) else file_name
    et.write(f'{file_name}.xtm', pretty_print=True, xml_declaration=True,   encoding="utf-8")
    return None

json_str = '''
{
    "person": {
        "name": "John Smith",
        "age": 35,
        "address": {
            "street": "123 Main St",
            "city": "Anytown",
            "state": "CA",
            "zip": "12345"
        }
    },
    "company": {
        "name": "Acme Corp",
        "industry": "Manufacturing",
        "employees": 1000
    }
}
'''
# print(json.loads(json_str))
# print(json.loads(json.dumps(json_str)))
# json_to_xtm(json_str)


