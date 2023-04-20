import json
from datetime import date
from lxml import etree

def json_to_xtm(json_str, file_name: str = f"Prueba.hytm"):
    # Generación del elemento json para ser modificado
    json_obj = json.loads(json_str)

    # Creación del elemento padre con la relación a XTM
    NSMP = {
        "xlink" : "http://www.w3.org/1999/xlink"
    }
    root = etree.Element("topicMap", xmlns="http://www.topicmaps.org/xtm/1.0/",nsmap=NSMP)
    root.set("id", f"Prueba.hytm")
    
    # Falta analizar de qué forma se puede hacer correctamente la traducción.
    # Preliminar
    for key, value in json_obj.items():
        # Crear un tema con el nombre de la clave
        theme_elem = etree.SubElement(root, "topic")
        theme_elem.set("id", f"t_{key}")
        name_elem = etree.SubElement(theme_elem, "baseName")
        str_name_elem = etree.SubElement(name_elem, "baseNameString")
        str_name_elem.text = key
        parent_key = key
        
        if isinstance(value, dict) or isinstance(value, list):
            if len(value) > 1:
                check_inner_dict(value, root, parent_key)
            else:
                print(value)
        else:
            # Agregar el valor como una propiedad del tema
            value_elem = etree.SubElement(root, "topic")
            if len(str(value).split()) > 1:
                value_elem.set("id", f"t_{value.split()[0]}")
            else:
                value_elem.set("id", f"t_{str(value)}")
            instance_elem = etree.SubElement(value_elem, "instanceOf")
            topic_ref_elem = etree.SubElement(instance_elem, "topicRef")
            topic_ref_elem.set("{http://www.w3.org/1999/xlink}href", f"#t_{key}")
            name_elem = etree.SubElement(value_elem, "baseName")
            str_name_elem = etree.SubElement(name_elem, "baseNameString")
            str_name_elem.text = str(value)
            
    # Se devuelve el árbol XTM creado.
    et = etree.ElementTree(root)
    file_name = file_name + f"_{date.today()}" if file_name in str(date.today()) else file_name
    et.write(f'{file_name}.xtm', pretty_print=True, xml_declaration=True,   encoding="utf-8")
    return None

def check_inner_dict(inner_dict, parent, parent_key = None):
    if isinstance(inner_dict, list):
        if isinstance(inner_dict[0], dict):
            for item in inner_dict:
                for key, value in item.items():
                    if isinstance(value, dict):
                        value_elem = etree.SubElement(parent, "topic")
                        value_elem.set("id", f"t_{key}")
                        name_elem = etree.SubElement(value_elem, "baseName")
                        str_name_elem = etree.SubElement(name_elem, "baseNameString")
                        str_name_elem.text = key
                        check_inner_dict(value, parent, key)
                    else:
                        key_elem = etree.SubElement(parent, "topic")
                        if len(key.split()) > 1:
                            key_elem.set("id", f"t_{key.split()[0]}")
                        else:
                            key_elem.set("id", f"t_{key}")
                        if parent_key is not None:
                            instance_elem = etree.SubElement(key_elem, "instanceOf")
                            topic_ref_elem = etree.SubElement(instance_elem, "topicRef")
                            topic_ref_elem.set("{http://www.w3.org/1999/xlink}href", f"#t_{parent_key}")
                        name_elem = etree.SubElement(key_elem, "baseName")
                        str_name_elem = etree.SubElement(name_elem, "baseNameString")
                        str_name_elem.text = str(key)
                        
                        value_elem = etree.SubElement(parent, "topic")
                        if len(str(value).split()) > 1:
                            value_elem.set("id", f"t_{value.split()[0]}")
                        else:
                            value_elem.set("id", f"t_{str(value)}")
                        instance_elem = etree.SubElement(value_elem, "instanceOf")
                        topic_ref_elem = etree.SubElement(instance_elem, "topicRef")
                        topic_ref_elem.set("{http://www.w3.org/1999/xlink}href", f"#t_{key}")
                        name_elem = etree.SubElement(value_elem, "baseName")
                        str_name_elem = etree.SubElement(name_elem, "baseNameString")
                        str_name_elem.text = str(value)
    else:
        for key, value in inner_dict.items():
            if isinstance(value, dict):
                value_elem = etree.SubElement(parent, "topic")
                value_elem.set("id", f"t_{key}")
                name_elem = etree.SubElement(value_elem, "baseName")
                str_name_elem = etree.SubElement(name_elem, "baseNameString")
                str_name_elem.text = key
                check_inner_dict(value, parent, key)
            else:
                key_elem = etree.SubElement(parent, "topic")
                if len(key.split()) > 1:
                    key_elem.set("id", f"t_{key.split()[0]}")
                else:
                    key_elem.set("id", f"t_{key}")
                if parent_key is not None:
                    instance_elem = etree.SubElement(key_elem, "instanceOf")
                    topic_ref_elem = etree.SubElement(instance_elem, "topicRef")
                    topic_ref_elem.set("{http://www.w3.org/1999/xlink}href", f"#t_{parent_key}")
                name_elem = etree.SubElement(key_elem, "baseName")
                str_name_elem = etree.SubElement(name_elem, "baseNameString")
                str_name_elem.text = str(key)
                
                value_elem = etree.SubElement(parent, "topic")
                if len(str(value).split()) > 1:
                    value_elem.set("id", f"t_{value.split()[0]}")
                else:
                    value_elem.set("id", f"t_{str(value)}")
                instance_elem = etree.SubElement(value_elem, "instanceOf")
                topic_ref_elem = etree.SubElement(instance_elem, "topicRef")
                topic_ref_elem.set("{http://www.w3.org/1999/xlink}href", f"#t_{key}")
                name_elem = etree.SubElement(value_elem, "baseName")
                str_name_elem = etree.SubElement(name_elem, "baseNameString")
                str_name_elem.text = str(value)
        

# json_str = '''
# {
#     "person": {
#         "name": "John Smith",
#         "age": 35,
#         "address": {
#             "street": "123 Main St",
#             "city": "Anytown",
#             "state": "CA",
#             "zip": "12345"
#         }
#     },
#     "company": {
#         "name": "Acme Corp",
#         "industry": "Manufacturing",
#         "employees": 1000
#     }
# }
# '''
# colors= '''
# {
#     "_id": "5973782bdb9a930533b05cb2",
#     "isActive": true,
#     "balance": "$1,446.35",
#     "age": 32,
#     "eyeColor": "green",
#     "name": "Logan Keller",
#     "gender": "male",
#     "company": "ARTIQ",
#     "email": "logankeller@artiq.com",
#     "phone": "+1 (952) 533-2258",
#     "friends": [
#       {
#         "id": 0,
#         "name": "Colon Salazar"
#       },
#       {
#         "id": 1,
#         "name": "French Mcneil"
#       },
#       {
#         "id": 2,
#         "name": "Carol Martin"
#       }
#     ],
#     "favoriteFruit": "banana"
#   }
# '''
# print(json.loads(json_str))
# print(json.loads(json.dumps(json_str)))
# json_to_xtm(json_str, "prueba")
# json_to_xtm(colors, "colors")


