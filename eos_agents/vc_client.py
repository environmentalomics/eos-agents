"""
Yet another VCD client module for Python.

"""

import requests
import xml.etree.ElementTree as ET

#This is almost certainly a Good Idea
from requests.packages import urllib3
urllib3.disable_warnings()

#Handy constant
ns_vc = "http://www.vmware.com/vcloud/v1.5"

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

        print("Connecting to " + endpoint + 'sessions')

        r = requests.post(endpoint + 'sessions',
                          headers=self.headers,
                          auth=(username + '@' + organisation, password),
                          verify=False)
        self.headers['x-vcloud-authorization'] = r.headers['X-VCLOUD-AUTHORIZATION']
        self.last_status = r.status_code

    def start_vm(self, vm_id):
        """
        Attempts to start a vm given by vm_id.
        """
        vm_id = str(vm_id)[3:42] + str("")
        r = requests.post(self.endpoint + "/vApp/" + str(vm_id) + "/power/action/powerOn",
                          data=None,
                          headers=self.headers,
                          verify=False)
        print (vm_id)
        self.last_status = r.status_code
        print (r.status_code)
        print (r.text)
        root = ET.fromstring(r.content)
        if root is not None:
            self.last_job_id = root.attrib['id'].split(':')[3]
            return root.attrib['id']
        else:
            return
        self.last_job_id = root.attrib['id'].split(':')[3]
        return root.attrib['id']

    def restart_vm(self, vm_id):
        """
        Attempts to start a vm given by vm_id.
        """
        vm_id = str(vm_id)[3:42] + str("")
        r = requests.post(self.endpoint + "/vApp/" + vm_id + "/power/action/reboot",
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
        vm_id = str(vm_id)[3:42] + str("")
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
        vm_id = str(vm_id)[3:42] + str("")
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
        vm_id = str(vm_id)[3:42] + str("")
        r = requests.post(self.endpoint + "/vApp/" + vm_id + "/power/action/shutdown",
                          data=None,
                          headers=self.headers,
                          verify=False)
        self.last_status = r.status_code
        root = ET.fromstring(r.content)
        self.last_job_id = root.attrib['id'].split(':')[3]
        return root.attrib['id']

    def set_system_memory_config(self, vapp_id, ram):
        vapp_id = str(vapp_id)[3:42] + str("")
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
        vapp_id = str(vapp_id)[3:42] + str("")
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

    #See http://pubs.vmware.com/vcd-51/topic/com.vmware.vcloud.api.doc_51/GUID-9356B99B-E414-474A-853C-1411692AF84C.html
    def list_vms(self, pagesize=50):
        """Returns an iterable list of VMs in the form of ElementTree
           VMRecord elements.
        """
        page=1
        while True:
            payload = {"page": str(page), "pageSize":str(pagesize), "format":"idrecords"}
            response = requests.get(self.endpoint + '/vms/query', data=None, headers=self.headers, params=payload,
                                    verify=False)
            resp1 = ET.fromstring(response.text)

            vms = resp1.findall(".//{%s}VMRecord" % ns_vc )
            for x in vms:
                yield x

            page += 1
            # Keep fetching pages until we run out.  Note there is a race condition if the list changes
            # in mid query.  We assume you don't care.
            if len(vms) < pagesize:
                break


    def list_vapps(self, pagesize=50):
        """Returns an iterable list of vApps in the form of ElementTree
           VAppRecord elements.
        """
        page = 1
        while True:
            payload = {"page": str(page), "pageSize":str(pagesize), "format":"idrecords"}
            response = requests.get(self.endpoint + '/vApps/query', data=None, headers=self.headers, params=payload,
                                    verify=False)
            resp1 = ET.fromstring(response.text)

            vapps = resp1.findall(".//{%s}VAppRecord" % ns_vc )
            for x in vapps:
                yield x

            page += 1
            # Keep fetching pages until we run out.  Note there is a race condition if the list changes
            # in mid query.  We assume you don't care.
            if len(vapps) < pagesize:
                break

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
        vapp_id = str(vapp_id)[3:42] + str("")
        response = requests.post(self.endpoint + "/vApp/" + vapp_id + "/power/action/powerOn", data=None, headers=self.headers,
                          verify=False)
        root = ET.fromstring(response.content)
        return root.attrib['id']

    def get_all_vms_for_user(self, username):
        """Obtain all VMs for a given user, assuming that each VApp has only one VM
        """
        # Find all VAppRecords where ownerName matches and drill down to find VM IDs
        # We can't use list_vms() because we can't see the owner in the results
        for vapp in self.list_vapps():
            if vapp.attrib.get('ownerName') != username:
                continue

            #I don't get a direct link to the vApp in the response, so here is a heuristic
            #to convert the id into something I can pass to get_vapp.
            vapp_id = 'vapp-' + vapp.attrib.get('id')[16:]
            resp2 = ET.fromstring(self.get_vapp(vapp_id))

            #Assume exactly one VirtualMachineId is going to be mentioned in the XML.
            vm = resp2.find(".//{%s}Vm" % ns_vc)
            vm_id = vm.findtext(".//{%s}VirtualMachineId" % ns_vc)
            #print(vm.attrib.get('name') + ' : vm-' + vm_id)
            yield (vm.attrib.get('name'), 'vm-' + vm_id)

    def get_vm_uid_from_name(self, machine_name):
        """Obtain a VM UUID from a name
        """
        for vm in self.list_vms():
            if vm.attrib.get('name') != machine_name:
                continue

            return 'vm-' + vm.attrib.get('id')[14:]

    def kill(self):
        """
        Ends the session represented by the current session token self.token.
        """
