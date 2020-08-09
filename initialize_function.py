from FWUtils import FWUtils
from CommonUtils import CommonUtils
from Pulse_Desktop_Linux_Data import *
import os
import admin.ProcsSA as pcsAdmin
import admin.RestApiSA as pcsRest
import time
import ast
import sys
import copy
from DesktopUtils import DesktopUtils
from Initialize import Initialize
import datetime
from sshUtils import sshUtils
import threading

objFwUtils = FWUtils()
log = objFwUtils.get_logger(__name__, 1)
objCommonUtils = CommonUtils()
objInitialize = Initialize()
obj_ssh_utils = sshUtils()

pisa_home = objFwUtils.request_desktop('get_env_var', {'env_var_name': 'PISA_HOME'})['env_var_value']
objDesktopUtils = DesktopUtils()

def INITIALIZE():

    tc_id = sys._getframe().f_code.co_name
    log.info('-' * 50)
    log.info(tc_id + ' [START]')

    try:

        step_text = "Initializing the test bed"
        log.info(step_text)
        return_dict = objInitialize.initialize()
        if return_dict["status"] == 1:
            log.info("Initializing the test bed successful")

        assert return_dict["status"] == 1, f"Failed to intialize the test bed\nOutput: {return_dict}"

        step_text = "Checking whether the network card connected to the external interface is available or not"
        log.info(step_text)
        return_dict = objFwUtils.request_desktop("get_network_interface_config", nw_interface_info)
        
        if return_dict["status"] == 1:
            log.info("Getting network interface configuration successful")

        assert return_dict["status"] == 1, f"Failed to get network interface configuration\nOutput: {return_dict}"

        external_interface_connected = False
        
        interface_configs = return_dict['interface_configs']
        for config in interface_configs.items():
            if "Non-Corp Network" in config[1]:
                external_interface_connected = True
                break
                
        assert external_interface_connected == True, f"No interface connected to external network found on the machine, not continuing with automation"
        if external_interface_connected:
            log.info("Interface connected to external network found, and connected")
        
        step_text = "Checking whether Pulse Client is installed or not. If installed, un-installing the client"
        log.info(step_text)
        
        pulse_find_cmd = "apt list --installed | grep pulsesecure"
        
        pulse_find_cmd_dict ={
            'command' : pulse_find_cmd
        }

        return_dict = objFwUtils.request_desktop('exec_cmd', pulse_find_cmd_dict)
        assert return_dict['status'] == 1, f"Checking whether pulse client is installed failed\nOutput: {return_dict}"

        if (return_dict['status'] == 1):
            if "pulsesecure" in return_dict['value']:
                log.info("A previous version of Pulse Client is installed, un-installing it")
                
                return_dict = objFwUtils.request_desktop("uninstall_pulse_using_command", uninstall_info)
                assert return_dict['status'] == 1, f"Un-installation of pulse client through command line failed"
                if return_dict['status'] == 1:
                    log.info("Un-installation of Pulse Client successful")

                log.info("Un-installing dependencies")
                return_dict = objFwUtils.request_desktop("cleanup_pulse_packages", uninstall_info)
                assert return_dict['status'] == 1, f"Un-installation of dependencies failed"
                if return_dict['status'] == 1:
                    log.info("Un-installation of dependencies successful")
                

        pulse_package_remove_cmd = "rm -f /pisa/temp/*.deb"
        
        pulse_package_remove_cmd_dict ={
            'command' : pulse_package_remove_cmd
        }

        return_dict = objFwUtils.request_desktop('exec_cmd', pulse_package_remove_cmd_dict)
        assert return_dict['status'] == 1, f"Removing previously present Pulse Client DEB package files from /pisa/temp failed\nOutput: {return_dict}"

        if (return_dict['status'] == 1):
            log.info("Removing Pulse Client DEB package files from /pisa/temp successful")

        pulse_package_remove_cmd = "rm -f /pisa/temp/*.rpm"
        
        pulse_package_remove_cmd_dict ={
            'command' : pulse_package_remove_cmd
        }

        return_dict = objFwUtils.request_desktop('exec_cmd', pulse_package_remove_cmd_dict)
        assert return_dict['status'] == 1, f"Removing previously present Pulse Client RPM package files from /pisa/temp failed\nOutput: {return_dict}"

        if (return_dict['status'] == 1):
            log.info("Removing Pulse Client RPM package files from /pisa/temp successful")
            
        step_text = "Logging into PCS as admin"
        log.info(step_text)
        return_val = pcsAdmin.loginSA()
        assert return_val['status'] == 1, "Failed to login into PCS as admin"
        
        if return_val['status'] == 1:
            log.info("Logging in to PCS server as admin successful")

        step_text = "Importing the base xml for IP based Split Tunneling Test suite"
        log.info(step_text)
        log.info("PISA_HOME: " + pisa_home)
        basexml = pisa_home + '/config/ive-import-base-ipv6st.xml'
        basexml_loc = objCommonUtils.convert_file_path(basexml)
        log.info("Converted xml file path: " + basexml_loc)
        return_val = pcsAdmin.importBaseXml(basexml_loc)
        assert return_val['status'] == 1, "Failed to import the base xml"
        
        if return_val['status'] == 1:
            log.info("Importing base XML successful")

        step_text = "Logging out PCS as admin"
        log.info(step_text)
        return_val = pcsAdmin.logoutSA()
        assert return_val['status'] == 1, "Failed to logout PCS as admin"
        
        if return_val['status'] == 1:
            log.info("Logging out of PCS as admin successful")
            
        step_text = "Closing the browser"
        log.info(step_text)
        return_val = pcsAdmin.closeBrowser()
        assert return_val['status'] == 1, "Failed to close the browser"
        
        if return_val['status'] == 1:
            log.info("Closing browser successful")

        # log.info("Downloading Pulse Client build from bamboo website")
        # return_dict = objCommonUtils.download_build_from_bamboo()
        # if return_dict['status'] == 1:
            # log.info("Downloading Pulse Client Build from Bamboo website successful")
        # assert return_dict['status'] == 1, f"Failed to download Pulse Client build from Bamboo website"

        #
        # Note: This is a temporary step. It will be removed before checking in the automation to Git
        #
        pulse_package_copy_cmd = "cp /automation/builds/*.deb /pisa/temp/"
        
        pulse_package_copy_cmd_dict ={
            'command' : pulse_package_copy_cmd
        }

        return_dict = objFwUtils.request_desktop('exec_cmd', pulse_package_copy_cmd_dict)
        assert return_dict['status'] == 1, f"Copying Pulse Client installer from /automation/builds to /pisa/temp failed\nOutput: {return_dict}"

        if (return_dict['status'] == 1):
            log.info("Copying Pulse Client installer from /automation/builds to /pisa/temp successful")
        
        
        # log.info("Installing Pulse Client")
        # return_dict = objFwUtils.request_desktop("install_pulse_using_command", )
        # if return_dict['status'] == 1:
            # log.info("Installing Pulse Client successful")
        # assert return_dict['status'] == 1, f"Failed to install Pulse Client"        
        
        step_text = "Launching Pulse Secure App"
        log.info(step_text)
        return_dict = objFwUtils.request_desktop('launch_pulse_app', app_info)
        if return_dict['status'] == 1:
            log.info("Launching Pulse Client successful")
        assert return_dict['status'] == 1, f"Failed to launch the App\nOutput: {return_dict}"
        
        log.info(tc-id + " [PASSED]")
        eresult = True
        
    except AssertionError as e:
        log.error(e)
        log.info(tc_id + ' [FAILED]')
        if objCommonUtils.get_screenshot(file_name=tc_id) is None:
            log.error('Failed to get the screenshot')
        eresult = False

    log.info(tc_id + ' [END]')
    log.info('-' * 50)

    return eresult
