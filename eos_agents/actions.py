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

def restart_vm(vm_id):
    """
    Attempt to start a VM. Returns HTTP status from attempt and job id in
    order to obtain future progress updates.
    """
    session = VCSession(VCD.username, VCD.password, VCD.org, VCD.endpoint)
    session.restart_vm(vm_id)
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

def boost_vm_memory(vm_id, ram):
    """
    
    """
    session = VCSession(VCD.username, VCD.password, VCD.org, VCD.endpoint)
    session.set_system_memory_config(vm_id, ram)
    session.kill()
    return session.last_status, session.last_job_id

def boost_vm_cores(vm_id, cores):
    """
    
    """
    session = VCSession(VCD.username, VCD.password, VCD.org, VCD.endpoint)
    session.set_system_cpu_config(vm_id, cores)
    session.kill()
    return session.last_status, session.last_job_id


def get_status(job_id):
    """
    
    """
    session = VCSession(VCD.username, VCD.password, VCD.org, VCD.endpoint)
    job_status = session.get_task_status(job_id)
    session.kill()
    return job_status

    
