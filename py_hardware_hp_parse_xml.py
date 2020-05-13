##########################################IMPORTS SECTIONS ################################################
import sys
import datetime
import xml.etree.ElementTree as ET
from itertools import izip
from ordereddict import OrderedDict

##########################################VARIABLES SECTIONS ###############################################
tree = ET.parse(sys.argv[1])
server_name=sys.argv[3]
server_ip=sys.argv[2]
today=sys.argv[4]
iLOversion=sys.argv[5]
root=tree.getroot()
xml_option='VALUE' 
##########################################MAIN XML DOCUMENT SECTION ARRAY###################################
sections = ['./HEALTH_AT_A_GLANCE','./TEMPERATURE/TEMP','./FANS/FAN','./POWER_SUPPLIES','./PROCESSORS/PROCESSOR','./NIC_INFORMATION/NIC','./NIC_INFORMATION/iLO','./VRM/MODULE','./MEMORY/MEMORY_DETAILS','./STORAGE/CONTROLLER']

controller_detail_tag=['LABEL','STATUS', 'CAPACITY','FAULT_TOLERANCE','ENCRYPTION_STATUS','DRIVE_BAY','SERIAL_NUMBER','MODEL','LOCATION VALUE','FW_VERSION','DRIVE_CONFIGURATION','CACHE_MODULE_STATUS','CACHE_MODULE_SERIAL_NUM','CACHE_MODULE_MEMORY','ENCLOSURE_ADDR','PRODUCT_ID','UID_LED']
controller_detail_status =['N/A', 'N/A','N/A','N/A', 'N/A','N/A','N/A','N/A', 'N/A', 'N/A', 'N/A','N/A', 'N/A', 'N/A', 'N/A','N/A','N/A']
 
#Order for MEMORY DETAILS STATUS Report
memory_detail_tag= ['SOCKET','STATUS', 'HP_SMART_MEMORY','PART','TYPE','SIZE','FREQUENCY','MINIMUM_VOLTAGE'	,'RANKS','TECHNOLOGY']	
memory_detail_status =['N/A', 'N/A','N/A','N/A', 'N/A','N/A','N/A','N/A', 'N/A','N/A']

#Order for VRM STATUS Report		 
vrm_tag=['LABEL','STATUS']
vrm_status=['N/A', 'N/A']

#Order for NETWORK INTERFACE CARD STATUS Report	
iLO_nic_tag =['NETWORK_PORT','PORT_DESCRIPTION','LOCATION','MAC_ADDRESS','IP_ADDRESS','STATUS']	
iLO_nic_status=['N/A', 'N/A','N/A','N/A', 'N/A','N/A']

#Order for NETWORK INTERFACE CARD STATUS Report	
nic_tag =['NETWORK_PORT','PORT_DESCRIPTION','LOCATION','MAC_ADDRESS','IP_ADDRESS','STATUS']	
nic_status=['N/A', 'N/A','N/A','N/A', 'N/A','N/A']

#Order for PROCESSOR STATUS Report
#DEFAULT ORDER ['LABEL','NAME','STATUS','SPEED','EXECUTION_TECHNOLOGY','MEMORY_TECHNOLOGY','INTERNAL_L1_CACHE','INTERNAL_L2_CACHE VALUE','INTERNAL_L3_CACHE']
proc_tag =['LABEL','NAME','STATUS','SPEED','EXECUTION_TECHNOLOGY','MEMORY_TECHNOLOGY','INTERNAL_L1_CACHE','INTERNAL_L2_CACHE','INTERNAL_L3_CACHE']
proc_status=['N/A', 'N/A','N/A','N/A', 'N/A','N/A','N/A','N/A','N/A']

#Order for POWER SUMMARY Report#
#DEFAULT ORDER ['PRESENT_POWER_READING','POWER_MANAGEMENT_CONTROLLER_FIRMWARE_VERSION','HIGH_EFFICIENCY_MODE']
power_tag=['LABEL','PRESENT','STATUS','PDS','HOTPLUG_CAPABLE','MODEL','SPARE','SERIAL_NUMBER','CAPACITY','FIRMWARE_VERSION','PRESENT_POWER_READING','POWER_MANAGEMENT_CONTROLLER_FIRMWARE_VERSION','HIGH_EFFICIENCY_MODE']
power_status=['N/A','N/A','N/A','N/A','N/A','N/A','N/A','N/A','N/A','N/A','N/A','N/A','N/A']

#Order for FANS Report#
#DEFAULT ORDER ['STATUS','ZONE','LABEL','SPEED']
fan_tag=['STATUS','ZONE','LABEL','SPEED']
fan_status=['N/A', 'N/A','N/A','N/A']

#Order for TEMPERATURE Report#
#DEFAULT ORDER ['LABEL', 'LOCATION','STATUS','CURRENTREADING', 'CAUTION','CRITICAL']
temp_tag=['LABEL', 'LOCATION','STATUS','CURRENTREADING', 'CAUTION','CRITICAL']
temp_status=['N/A', 'N/A','N/A','N/A', 'N/A','N/A']

#Order for HARDWARE SUMMARY Report#
#DEFAULT ORDER ['BIOS_HARDWARE', 'PROCESSOR','MEMORY','NETWORK', 'STORAGE','FANS','TEMPERATURE','VRM','DRIVE']
hdw_tag=['BIOS_HARDWARE', 'PROCESSOR','MEMORY','NETWORK', 'STORAGE','FANS','TEMPERATURE','VRM','DRIVE']
hdw_status=['N/A', 'N/A','N/A','N/A', 'N/A','N/A','N/A','N/A','N/A']


##########################################FUNCTIONS SECTIONS ###############################################

def genericTreeParser(branch_tag,branch_status,high_level_section):
	################# Using Ordered Dictionary to Maintain the Order of Elements ##################
	branch_status_dict = OrderedDict((key,value) for key,value in izip(branch_tag,branch_status))
	high_level_section_branch=root.findall('./'+high_level_section)
	xml_option='VALUE'
	if high_level_section=='./HEALTH_AT_A_GLANCE' :
		xml_option='STATUS'
	for section in high_level_section_branch : 
		high_level_name=high_level_section[2:].split("/") #Get the high level section name like TEMPERATURE/TEMP and split into two parts ('TEMPERATURE', 'TEMP')
		if high_level_name[0] == 'TEMPERATURE' or  high_level_name[0] == 'PROCESSORS' or high_level_name[0] == 'NIC_INFORMATION' :
			print('\n%s;HARDWARE;%s;%s;%s;') % (today,server_name,server_ip,high_level_name[0]) ,
		elif high_level_name[0] == 'HEALTH_AT_A_GLANCE' :
			print('\n%s;HARDWARE;%s;%s;%s;HARDWARE_SUMMARY;') % (today,server_name,server_ip,high_level_name[0]) ,
		else :
			print('\n%s;HARDWARE;%s;%s;%s;%s;') % (today,server_name,server_ip,high_level_name[0],section.tag) ,
		for item in section:
				branch_status_dict[item.tag]=item.get(xml_option)			
		for item in branch_tag:	 # Use the original order of tags to match the ordered dictionary in printing the values
			print ('%s;') % (branch_status_dict[item]),
		
				
def main (sections):
	for section in sections:
		if section == sections[0] :
			genericTreeParser(hdw_tag,hdw_status,section)
		elif section == sections[1] :
			genericTreeParser(temp_tag,temp_status,section)
		elif section == sections[2] :
			genericTreeParser(fan_tag,fan_status,section)
		elif section == sections[3] :
			for child_section in root.findall(section): #This is for level 3 children not reachable from genericTreeParse e.g ./POWER_SUPPLIES/SUPPLY 
				for child in child_section:
					child_values = root.find(section+'/'+child.tag) 
					genericTreeParser(power_tag,power_status,section+'/'+child_values.tag)		
		elif section == sections[4] :
			genericTreeParser(proc_tag,proc_status,section)
		elif section == sections[5] :
			genericTreeParser(nic_tag,nic_status,section)
		elif section == sections[6] :
			genericTreeParser(nic_tag,nic_status,section)
		elif section == sections[7] :
			genericTreeParser(vrm_tag,vrm_status,section)
		elif section == sections[8] :
			genericTreeParser(memory_detail_tag,memory_detail_status,section+'/'+'CPU')
			genericTreeParser(memory_detail_tag,memory_detail_status,section+'/'+'CPU_1')
			genericTreeParser(memory_detail_tag,memory_detail_status,section+'/'+'CPU_2')
			genericTreeParser(memory_detail_tag,memory_detail_status,section+'/'+'CPU_3')
			genericTreeParser(memory_detail_tag,memory_detail_status,section+'/'+'CPU_4')
		elif section == sections[9] :
			genericTreeParser(controller_detail_tag,controller_detail_status,section)
			genericTreeParser(controller_detail_tag,controller_detail_status,section+'/'+'LOGICAL_DRIVE')
			genericTreeParser(controller_detail_tag,controller_detail_status,section+'/'+'DRIVE_ENCLOSURE')	
			genericTreeParser(controller_detail_tag,controller_detail_status,section+'/'+'LOGICAL_DRIVE'+'/'+'PHYSICAL_DRIVE')						
			

main(sections)
