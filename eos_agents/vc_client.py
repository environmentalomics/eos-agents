"""
Yet another VCD client module for Python.

"""

import requests
import xml.etree.ElementTree as ET

import logging
log = logging.getLogger(__name__)

#This is almost certainly a Good Idea
from requests.packages import urllib3
urllib3.disable_warnings()

# FIXME - we should import and trust the certificate for our SSL endpoint

#Handy constant
ns_vc = "http://www.vmware.com/vcloud/v1.5"

class BadRequestException(Exception):
    """Specific exception raised for '400 BAD_REQUEST'
    """
    pass

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

        log.debug("Connecting to " + endpoint + 'sessions')

        r = requests.post(endpoint + 'sessions',
                          headers=self.headers,
                          auth=(username + '@' + organisation, password),
                          verify=False)
        self.headers['x-vcloud-authorization'] = r.headers['X-VCLOUD-AUTHORIZATION']
        self.last_status = r.status_code

    def _vm_power_action(self, vm_id, action):
        """ Attempts to apply an action (powerOn, powerOff, reboot, shutdown) to a VM
            and capture the job ID for polling.
        """
        #This looks dicey...
        #vm_id = str(vm_id)[3:42] + str("")
        self.last_job_id = None

        log.debug("Action: " + self.endpoint + "/vApp/" + vm_id + "/power/action/" + action)
        r = requests.post(self.endpoint + "/vApp/" + vm_id + "/power/action/" + action,
                          data=None,
                          headers=self.headers,
                          verify=False)

        return self._process_vc_response(r)

    def _process_vc_response(self, content):
        self.last_status = "%i %s" % (r.status_code, r.reason)
        log.debug(r.status_code)
        log.debug(r.text)

        #Convert to XML.  If that fails, just let the exception propogate.
        root = ET.fromstring(content)

        #So we know root must at least be valid XML
        if 'id' in root.attrib:
            self.last_job_id = root.attrib['id'].split(':')[3]
            return root.attrib['id']
        elif root.attrib.get('minorErrorCode') == 'BAD_REQUEST':
            #Trying to, eg., power off a machine which is already off,
            #produces minorErrorCode="BAD_REQUEST"
            raise BadRequestException(root.attrib.get('message', 'Unknown'))

        #Failing that, I'm out of ideas.  Caller should examine self.last_status
        raise ValueError("Unrecognised response from VCloud.")

    def start_vm(self, vm_id):
        """
        Attempts to start a vm given by vm_id.
        """
        return self._vm_power_action(vm_id, 'powerOn')

    def restart_vm(self, vm_id):
        """
        Attempts to reboot a vm given by vm_id.
        """
        return self._vm_power_action(vm_id, 'reboot')

    def poweroff_vm(self, vm_id):
        """
        Attempts to stop (uncleanly) a vm given by vm_id.
        """
        return self._vm_power_action(vm_id, 'powerOff')

    def shutdown_vm(self, vm_id):
        """
        Attempts a clean shutdown of the given VM.
        """
        return self._vm_power_action(vm_id, 'shutdown')

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
        response = requests.put(self.endpoint + "/vApp/" + vapp_id + "/virtualHardwareSection/memory",
                                data=xmlstring, headers=self.headers, verify=False)

        return self._process_vc_response(r)

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
        response = requests.put(self.endpoint + "/vApp/" + vapp_id + "/virtualHardwareSection/cpu",
                                data=xmlstring, headers=self.headers, verify=False)

        return self._process_vc_response(r)

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
        response = requests.delete(self.endpoint + '/session',
                                   data=None, headers=self.headers,
                                   verify=False)
        self.headers = None
