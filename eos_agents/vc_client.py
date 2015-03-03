"""


"""

import requests
import xml.etree.ElementTree as ET

class VCSession:
    
    def __init__(self, username, password, organisation, endpoint):
        """
        Starts a vCloud session by requesting a session key.
        
        Also saves credentials which will be used regularly into object
        variables.
        """
        self.username = username
        self.password = password
        self.organisation = organisation
        self.endpoint = endpoint
        self.headers = {'Accept':'application/*+xml;version=5.1'}
        
        self.last_status = -1
        self.last_job_id = -1
        r = requests.post(endpoint + 'sessions', 
                          headers = self.headers, 
                          auth=(username + '@' + organisation, password),
                          verify=False)
        self.headers['x-vcloud-authorization'] = r.headers['X-VCLOUD-AUTHORIZATION']
        self.last_status = r.status_code

    def start_vm(self, vm_id):
        """
        Attempts to start a vm given by vm_id.
        """
        r = requests.post(self.endpoint + "/vApp/" + vm_id + "/power/action/powerOn", 
                          data=None, 
                          headers=self.headers,
                          verify=False)
        self.last_status = r.status_code
        root = ET.fromstring(r.content)
        self.last_job_id = root.attrib['id'].split(':')[3]
        return root.attrib['id']
    
    def poweroff_vm(self, vm_id):
        """
        Attempts to start a vm given by vm_id.
        """
        r = requests.post(self.endpoint + "/vApp/" + vm_id + "/power/action/powerOff", 
                          data=None, 
                          headers=self.headers,
                          verify=False)
        self.last_status = r.status_code
        root = ET.fromstring(r.content)
        self.last_job_id = root.attrib['id'].split(':')[3]
        return root.attrib['id']
    
    def shutdown_vm(self, vm_id):
        """
        
        """
        r = requests.post(self.endpoint + "/vApp/" + vm_id + "/power/action/shutdown", 
                          data=None, 
                          headers=self.headers,
                          verify=False)
        self.last_status = r.status_code
        root = ET.fromstring(r.content)
        self.last_job_id = root.attrib['id'].split(':')[3]
        return root.attrib['id']
    
    def stop_vm(self, vm_id):
        """
        
        """
        r = requests.post(self.endpoint + "/vApp/" + vm_id + "/power/action/shutdown", 
                          data=None, 
                          headers=self.headers,
                          verify=False)
        self.last_status = r.status_code
        root = ET.fromstring(r.content)
        self.last_job_id = root.attrib['id'].split(':')[3]
        return root.attrib['id']
    
    def set_system_memory_config(self, vapp_id, ram):
        if ram == 16:
                tree = ET.parse("templates/16gb_memory.xml")
        elif ram == 40:
                tree = ET.parse("templates/40gb_memory.xml")
        elif ram == 140:
                tree = ET.parse("templates/140gb_memory.xml")
        elif ram == 500:
                tree = ET.parse("templates/500gb_memory.xml")
        else:
                tree = ET.parse("templates/16gb_memory.xml")
        root = tree.getroot()
        xmlstring = ET.tostring(root, encoding='utf8', method='xml')
        response = requests.put(self.endpoint + "/vApp/" + vapp_id + "/virtualHardwareSection/memory", data=xmlstring, headers=self.headers, verify=False)
        root = ET.fromstring(response.content)
        self.last_job_id = root.attrib['id'].split(':')[3]
        return root.attrib['id']
    
    def set_system_cpu_config(self, vapp_id, cores):
        if cores == 1:
                tree = ET.parse("templates/1_core.xml")
        elif cores == 2:
                tree = ET.parse("templates/2_cores.xml")
        elif cores == 8:
                tree = ET.parse("templates/8_cores.xml")
        elif cores == 16:
                tree = ET.parse("templates/16_cores.xml")
        else:
                tree = ET.parse("templates/1_core.xml")
        root = tree.getroot()
        xmlstring = ET.tostring(root, encoding='utf8', method='xml')
        response = requests.put(self.endpoint + "/vApp/" + vapp_id + "/virtualHardwareSection/cpu", data=xmlstring, headers=self.headers, verify=False)
        root = ET.fromstring(response.content)
        self.last_job_id = root.attrib['id'].split(':')[3]
        return root.attrib['id']
    
    def boost_vm(self):
        pass
        
    def list_vapps(self):
        payload = {"page": "1", "pageSize":"25", "format":"idrecords"}
        response = requests.get(self.endpoint + '/vApps/query', data=None, headers = self.headers, params=payload,
                          verify=False)
        return response.text   
    
    def get_vapp(self, vapp_id):
        response = requests.get(self.endpoint + "/vApp/" + vapp_id, data=None, headers=self.headers,
                          verify=False)
        return response.text
    
    def get_task_status(self, task_id):
        """Returns current status of a given job in vCloud Director.
        
        This will be one of:
        
            * queued - The task has been queued for execution.
            * preRunning - The task is awaiting preprocessing or, if it is a
              blocking task, administrative action. 
            * running - The task is runnning.
            * success - The task completed with a status of success.
            * error - The task encountered an error while running.
            * canceled - The task was canceled by the owner or an administrator.
            * aborted - The task was aborted by an administrative action.
             
        """
        response = requests.get(self.endpoint + "/task/" + task_id, data=None, headers=self.headers,
                          verify=False)
        root = ET.fromstring(response.content)
        return root.attrib['status']
    
    def poweron_vapp(self, vapp_id):    
        response = requests.post(self.endpoint + "/vApp/" + vapp_id + "/power/action/powerOn", data=None, headers=self.headers,
                          verify=False)
        root = ET.fromstring(response.content)
        return root.attrib['id']
    
    def kill(self):
        """
        Ends the session represented by the current session token self.token.
        """

    
            
    