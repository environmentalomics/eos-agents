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
        "Returns current status of a given job in vCloud Director"
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

    
            
    