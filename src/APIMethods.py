# Python 3.9
from typing import Any # Variable importada para hacer uso del tipo de variable "Any"
import requests # Librería para realizar las peticiones a la API de Wazuh
import json # Librería para manejar las respuestas que otorga la API.
from collections import Counter # Módulo importado para realizar cuenta de las repeticiones de vulnerabilidades.
from operator import itemgetter # Módulo empleado para tomar un elemento o su puntero.
from ApiLogger import get_host
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Configuración de la conexión
protocol = 'https'
host =  get_host() # Se coloca la IP si el servidor no está alojado en el local.
port = 55000 # Puerto sugerido por Wazuh
url = f'{protocol}://{host}:{port}'

def vulnerability_by_criticality(severity, request_header: dict):
    """Función que devuelve las vulnerabilidades según su criticidad

    Args:
        severity: Criticidad 
        request_header (dict): Encabezado con el token para hacer correctamente la solicitud

    """
    vulnerabilities = []

    response = requests.get(url + "/agents?limit=20", headers=request_header, verify=False)
    agents = response.json()["data"]["affected_items"]

    for agent in agents:
        agent_id = agent['id']
        params = {"severity": severity}
        response = requests.get(url + f"/vulnerability/{agent_id}", headers=request_header, params=params, verify=False)
        if response.json().get('data'):
            agent_vulnerabilities = response.json()["data"]["affected_items"]
            for vulnerability in agent_vulnerabilities:
                vulnerability["agent_id"] = agent_id
            
            vulnerabilities.extend(agent_vulnerabilities)
    
    return vulnerabilities

def vulnerabilities_by_keyword(keyword, request_header: dict):
    """Función que devuleve las vulnerabilidades por alguna palabra clave

     Args:
        keyword: Palabra clave
        request_header (dict): Encabezado con el token para hacer correctamente la solicitud
    """
    result_vulnerabilities = []

    response = requests.get(url + "/agents?limit=20", headers=request_header, verify=False)
    agents = response.json()["data"]["affected_items"]

    for agent in agents:
        agent_id = agent['id']
        response = requests.get(url + f"/vulnerability/{agent_id}", headers=request_header, verify=False)

        if response.status_code == 200:
            vulnerabilities = response.json()["data"]["affected_items"]
            for vulnerability in vulnerabilities:
                if keyword.lower() in vulnerability['name'].lower():
                    result_vulnerabilities.append(vulnerability)
    return result_vulnerabilities

# Update, Restart & Delete Agents

def upgrade_agents(agents: str, request_header: dict) -> str :

    response = requests.put(url + f'/agents/upgrade?agents_list={agents}', headers=request_header, verify=False)
    
    return response.json()["message"]

def restart_agents(agents: str, request_header: dict) -> str :

    response = requests.put(url + f'/agents/restart?agents_list={agents}', headers=request_header, verify=False)
    
    return response.json()["message"]

def delete_agents(agents: str, request_header: dict) -> str :

    response = requests.delete(url + f'/agents?pretty=true&older_than=0s&status=all&agents_list={agents}', headers=request_header, verify=False)
    
    return response.json()["message"]


# Show agents that share a vulnerability

def get_vulnerabilities_with_agents(request_header: dict) -> dict:

    result : dict[str : [str]] = {}
    band = False

    response_agents = requests.get(url + "/agents?limit=20", headers=request_header, verify=False)
    agents = json.loads(response_agents.text)["data"]["affected_items"]         
    for agent in agents:
        agent_id = agent["id"]
        response_vul = requests.get(url + f"/vulnerability/{agent_id}/summary/cve", headers=request_header, verify=False)
        vulnerabilities_cve : dict = json.loads(response_vul.text)["data"]["cve"]
        for cve in vulnerabilities_cve.keys():
            band = False
            if cve in result:
                result[cve].append(agent_id)
                band = True
            if band == False:
                result[cve] = [agent_id]

    return result

def top_n_vulnerabilities(n: int, request_header: dict) -> list[tuple[Any, int]]:
    """Función que devuelve el top n de vulnerabilidades más comunes.

    Args:
        n (int): Número entero hasta el que se busca obtener el top
        request_header (dict): Encabezado con el token para hacer correctamente la solicitud

    Returns:
        list[tuple[Any, int]]: Lista con elemento tupla donde se indica el elemento y la cantidad de repeticiones que tuvo.
    """
    response = requests.get(url + "/agents?limit=20", headers=request_header, verify=False)
    # Debido a que se buscan los agentes con vulnerabilidades, se filtra por elementos afectados.
    agents = json.loads(response.text)["data"]["affected_items"]
    
    vulnerabilities = []
    for agent in agents:
        agent_id = agent["id"]
        response = requests.get(url + f"/vulnerability/{agent_id}", headers=request_header, verify=False)
        # Se filtra por "data" de acuerdo a la información que se indica en la documentación de la API.
        vulnerabilities = json.loads(response.text)["data"]["affected_items"]
    
    # Counter recibe un iterador, por lo que se tiene que generar filtrando del total de vulnerabilidades.
    # print(vulnerabilities[0])
    vul_count = Counter([vulnerability["cve"] for vulnerability in vulnerabilities])
    
    return vul_count.most_common(n)

def top_n_agents(n: int, request_header: dict) -> list[dict]:
    """Devuelve el top n de agentes con más vulnerabilidades.

    Args:
        n (int): Número entero hasta el que se desea hacer el top
        request_header (dict): Encabezado con el token para hacer correctamente la solicitud

    Returns:
        list[dict]: Lista con los agentes y su total de vulnerabilidades en formato diccionario.
    """
    response = requests.get(url + "/agents?limit=20", headers=request_header, verify=False)
    # Debido a que se buscan los agentes con vulnerabilidades, se filtra por elementos afectados.
    agents = json.loads(response.text)["data"]["affected_items"]
    
    agent_vulnerabilities = []
    for agent in agents:
        agent_id = agent["id"]
        # Acceso a las vulnerabilidades por agente
        vul_response = requests.get(url + f"/vulnerability/{agent_id}", headers=request_header, verify=False)
        vulnerabilities = json.loads(vul_response.text)["data"]["total_affected_items"] # Filtro para visualizar únicamente la información relevante.
        agent_vulnerabilities.append({"agent" : agent_id, "vulnerabilities" : vulnerabilities})
    # Se ordena descendentemente la lista con la llave "vulnerabilities" del diccionario
    return sorted(agent_vulnerabilities, key=itemgetter("vulnerabilities"), reverse=True)[:n]

def get_configuration(request_header: dict)->json:
    """Funcion que devuelve la configuración actual del servidor de Wazuh

    Args:
        request_header (dict): Encabezado con el token para hacer correctamente la solicitud
        
    Returns:
        json: Formato de cadena de json que posee la configuración del servidor
    """
    response = requests.get(url + "/manager/configuration", headers=request_header, verify=False)
    configuration = json.loads(response.text)["data"]
    
    # Se regresa en formato json-string para su próximo manejo
    return json.dumps(configuration, indent=4)

def get_logs(request_header: dict)->json:
    """Función que devuelve los registros del servidor de Wazuh

    Args:
        request_header (dict): Encabezado con el token para hacer correctamente la solicitud
        
    Returns:
        json: Formato de cadena de json que posee los registros del servidor.
    """
    response = requests.get(url + "/manager/logs", headers=request_header, verify=False)
    # El json en "data" contiene los siguientes campos:
    #   total_affected_items
    #   failed_items
    #   total_failed_items
    #   affected_items
    logs = json.loads(response.text)["data"]
    return json.dumps(logs, indent=4)

def get_log_summary(request_header: dict)->json:
    """Función que devuelve un sumario de los registros del servidor de Wazuh

    Args:
        request_header (dict): Encabezado con el token para hacer correctamente la solicitud
    
    Returns:
        json: Formato de cadena de json que posee el sumario de los registros del servidor.
    """
    response = requests.get(url + "/manager/logs/summary",  headers=request_header, verify=False)
    # Son bastantes campos los que devuelve el json, con un máximo de los últimos 2000 registros
    log_summary = json.loads(response.text)["data"]
    
    return json.dumps(log_summary, indent=4)

def get_groups(request_header: dict)->json:
    """Función que devuelve los grupos del servidor de Wazuh

    Args:
        request_header (dict): Encabezado con el token para hacer correctamente la solicitud
    
    Returns:
        json: Formato de cadena de json que posee los grupos del servidor.
    """
    response = requests.get(url + "/groups",  headers=request_header, verify=False)
    groups = json.loads(response.text)["data"]
    
    return json.dumps(groups, indent=4)

def get_task_status(request_header: dict) -> json:

    """

    This function resturns every task status

    Args:

        none

    Returns:

        list: List containing every task and their status
    
    API documentation:

        https://documentation.wazuh.com/current/user-manual/api/reference.html#operation/api.controllers.syscollector_controller.get_processes_info

    """

    response = requests.get(url + "/tasks/status", headers=request_header, verify=False)

    tasks_status = json.loads(response.text)["data"]

    return json.dumps(tasks_status, indent=4)

def get_inv_hardware(request_header: dict) -> json:
    response = requests.get(url + "/agents?limit=20", headers=request_header, verify=False)
    # Debido a que se buscan los agentes con vulnerabilidades, se filtra por elementos afectados.
    agents = json.loads(response.text)["data"]["affected_items"]
    
    hardware = dict()
    for agent in agents:
        agent_id = agent["id"]
        # Acceso a las vulnerabilidades por agente
        vul_response = requests.get(url + f"/syscollector/{agent_id}/hardware", headers=request_header, verify=False)
        hard_agent = json.loads(vul_response.text)["data"] # Filtro para visualizar únicamente la información relevante.
        hardware[agent_id] = hard_agent
    return json.dumps(hardware, indent=4)

def get_inv_hotfixes(request_header: dict) -> json:
    response = requests.get(url + "/agents?limit=20", headers=request_header, verify=False)
    # Debido a que se buscan los agentes con vulnerabilidades, se filtra por elementos afectados.
    agents = json.loads(response.text)["data"]["affected_items"]
    
    hardware = dict()
    for agent in agents:
        agent_id = agent["id"]
        # Acceso a las vulnerabilidades por agente
        vul_response = requests.get(url + f"/syscollector/{agent_id}/hotfixes", headers=request_header, verify=False)
        hard_agent = json.loads(vul_response.text)["data"] # Filtro para visualizar únicamente la información relevante.
        hardware[agent_id] = hard_agent
    return json.dumps(hardware, indent=4)

def get_inv_netaddr(request_header: dict) -> json:
    response = requests.get(url + "/agents?limit=20", headers=request_header, verify=False)
    # Debido a que se buscan los agentes con vulnerabilidades, se filtra por elementos afectados.
    agents = json.loads(response.text)["data"]["affected_items"]
    
    hardware = dict()
    for agent in agents:
        agent_id = agent["id"]
        # Acceso a las vulnerabilidades por agente
        vul_response = requests.get(url + f"/syscollector/{agent_id}/netaddr", headers=request_header, verify=False)
        hard_agent = json.loads(vul_response.text)["data"] # Filtro para visualizar únicamente la información relevante.
        hardware[agent_id] = hard_agent
    return json.dumps(hardware, indent=4)

def get_inv_netiface(request_header: dict) -> json:
    response = requests.get(url + "/agents?limit=20", headers=request_header, verify=False)
    # Debido a que se buscan los agentes con vulnerabilidades, se filtra por elementos afectados.
    agents = json.loads(response.text)["data"]["affected_items"]
    
    hardware = dict()
    for agent in agents:
        agent_id = agent["id"]
        # Acceso a las vulnerabilidades por agente
        vul_response = requests.get(url + f"/syscollector/{agent_id}/netiface", headers=request_header, verify=False)
        hard_agent = json.loads(vul_response.text)["data"] # Filtro para visualizar únicamente la información relevante.
        hardware[agent_id] = hard_agent
    return json.dumps(hardware, indent=4)

def get_inv_netproto(request_header: dict) -> json:
    response = requests.get(url + "/agents?limit=20", headers=request_header, verify=False)
    # Debido a que se buscan los agentes con vulnerabilidades, se filtra por elementos afectados.
    agents = json.loads(response.text)["data"]["affected_items"]
    
    inventory = dict()
    for agent in agents:
        agent_id = agent["id"]
        # Acceso a las vulnerabilidades por agente
        vul_response = requests.get(url + f"/syscollector/{agent_id}/netproto", headers=request_header, verify=False)
        hard_agent = json.loads(vul_response.text)["data"] # Filtro para visualizar únicamente la información relevante.
        inventory[agent_id] = hard_agent
    return json.dumps(inventory, indent=4)

def get_inv_os(request_header: dict) -> json:
    response = requests.get(url + "/agents?limit=20", headers=request_header, verify=False)
    # Debido a que se buscan los agentes con vulnerabilidades, se filtra por elementos afectados.
    agents = json.loads(response.text)["data"]["affected_items"]
    
    hardware = dict()
    for agent in agents:
        agent_id = agent["id"]
        # Acceso a las vulnerabilidades por agente
        vul_response = requests.get(url + f"/syscollector/{agent_id}/os", headers=request_header, verify=False)
        hard_agent = json.loads(vul_response.text)["data"] # Filtro para visualizar únicamente la información relevante.
        hardware[agent_id] = hard_agent
    return json.dumps(hardware, indent=4)

def get_inv_packages(request_header: dict) -> json:
    response = requests.get(url + "/agents?limit=20", headers=request_header, verify=False)
    # Debido a que se buscan los agentes con vulnerabilidades, se filtra por elementos afectados.
    agents = json.loads(response.text)["data"]["affected_items"]
    
    hardware = dict()
    for agent in agents:
        agent_id = agent["id"]
        # Acceso a las vulnerabilidades por agente
        vul_response = requests.get(url + f"/syscollector/{agent_id}/packages", headers=request_header, verify=False)
        hard_agent = json.loads(vul_response.text)["data"] # Filtro para visualizar únicamente la información relevante.
        hardware[agent_id] = hard_agent
    return json.dumps(hardware, indent=4)

def get_inv_ports(request_header: dict) -> json:
    response = requests.get(url + "/agents?limit=20", headers=request_header, verify=False)
    # Debido a que se buscan los agentes con vulnerabilidades, se filtra por elementos afectados.
    agents = json.loads(response.text)["data"]["affected_items"]
    
    hardware = dict()
    for agent in agents:
        agent_id = agent["id"]
        # Acceso a las vulnerabilidades por agente
        vul_response = requests.get(url + f"/syscollector/{agent_id}/ports", headers=request_header, verify=False)
        hard_agent = json.loads(vul_response.text)["data"] # Filtro para visualizar únicamente la información relevante.
        hardware[agent_id] = hard_agent
    return json.dumps(hardware, indent=4)

def get_inv_processes(request_header: dict) -> json:
    response = requests.get(url + "/agents?limit=20", headers=request_header, verify=False)
    # Debido a que se buscan los agentes con vulnerabilidades, se filtra por elementos afectados.
    agents = json.loads(response.text)["data"]["affected_items"]
    
    hardware = dict()
    for agent in agents:
        agent_id = agent["id"]
        # Acceso a las vulnerabilidades por agente
        vul_response = requests.get(url + f"/syscollector/{agent_id}/processes", headers=request_header, verify=False)
        hard_agent = json.loads(vul_response.text)["data"] # Filtro para visualizar únicamente la información relevante.
        hardware[agent_id] = hard_agent
    return json.dumps(hardware, indent=4)

def print_functions(response_list: list, operation: int, n: int = None):
    """Función que permite mostrar el resultado de las operaciones que se hacen con la API

    Args:
        response_list (list): lista procesada con los elementos requeridos de acuerdo a la función que ejecutan
        operation (int): De acuerdo a la operación que se realice se indica el índice
        n (int, optional): Si se desea mostrar un top, es el número n que se buscó. Predeterminado en None.
    """
    # Diccionario de evaluación para el tipo de operación que se pase
    conditions = {
        (operation == 1) : "Vulnerabilidades por criticidad",
        (operation == 2) : "Vulnerabilidades por palabra clave",
        (operation == 4) : "Equipos con vulnerabilidad en común",
        (operation == 5) : f"Top {n} de vulnerabilidades más comunes", 
        (operation == 6) : f"Top {n} de agentes con más vulnerabilidades",
    }
    print(conditions.get(True, "Operación desconocida"))
    if(operation == 5 or operation == 6):
        for idx, (element, count) in enumerate(response_list):
            print(f"{idx+1}. {element} con {count} repeticiones")
    else:
        for item in response_list:
            print(item)
    return None
            
        
