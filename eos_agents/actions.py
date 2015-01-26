"""
ch_agents.actions

A library containing a function for each action which an agent can perform
on the vCloud environment via the vCloud API. This module is exclusively aimed
at interfacing with vCloud.
"""

from eos_agents.vc_client import VCSession
from eos_agents.settings import VCDetails as VCD

def start_vm(vm_id):
    """
    Attempt to start a VM. Returns HTTP status from attempt and job id in
    order to obtain future progress updates.
    """
    session = VCSession(VCD.username, VCD.password, VCD.org, VCD.endpoint)
    session.start_vm(vm_id)
    session.kill()
    return session.last_status, session.last_job_id

def stop_vm(vm_id):
    """
    Attempt to stop a VM. Returns HTTP status from attempt and job_id in
    order to obtain future progress updates
    """
    session = VCSession(VCD.username, VCD.password, VCD.org, VCD.endpoint)
    session.stop_vm(vm_id)
    session.kill()
    return session.last_status, session.last_job_id

def poweroff_vm(vm_id):
    """
    Attempt to stop a VM. Returns HTTP status from attempt and job_id in
    order to obtain future progress updates
    """
    session = VCSession(VCD.username, VCD.password, VCD.org, VCD.endpoint)
    session.poweroff_vm(vm_id)
    session.kill()
    return session.last_status, session.last_job_id

def boost_vm(session_token, vm_id):
    """
    
    """
    pass

def get_status(vm_id):
    """
    
    """
    session = get_session
    pass

    