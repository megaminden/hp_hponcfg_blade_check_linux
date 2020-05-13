#!/bin/bash
cd `dirname $0`
##################################################Environment Variables ##################################
defaultBladeUsername='"XXXXXX"'  #default blade username where all blades in a chest are using same username
defaultBladePassword='"XXXXXX"'    #default blade password where all blades in a chest are using same password
deactivateLoader="N"                  #{"Y" / "N" }Sometimes we want to test script so we set value to N to stop loading in db            

wd=/home/BASIC_CHECK/scripts/checks/automatic/hardware  #The home of the hardware check scripts
loader_dir=/home/BASIC_CHECK/checkdata/            #The db loader directory
python2_exe=/usr/bin/python                             #Python2 executable
##################################################Other Variables ##################################
hour=`date +'%Y%m%d%H'`
log_time=`date +'%Y%m%d%H%M%S'`
outputfile=outputfile_hdwtests_$hour
inputfile=$wd/server_list
log_file=$wd/log/hardware_check.log
hp_check_list_file=get_blade_status_no_delete.xml
hp_check_list_file_full=$wd/${hp_check_list_file}

if [ ! -f $inputfile ]; then echo file $inputfile not found; exit; fi

cd output
rm -f $outputfile

cat $inputfile | grep -v "#" | grep -v ^$ | while read mydata
do
	serverName=`echo $mydata | cut -d "|" -f1`
	serverIP=`echo $mydata | cut -d "|" -f2`
	serverDir=`echo $mydata | cut -d "|" -f3`
	serverUser=`echo $mydata | cut -d "|" -f4`
	bladeUsername=`echo $mydata | cut -d "|" -f5`   
	bladePassword=`echo $mydata | cut -d "|" -f6` 
	
	if [[  -z "${bladeUsername}" ||   -z "${bladePassword}" || ${bladeUsername} == "N/A" || ${bladePassword} == "N/A" ]];
	then
		bladeUsername=${defaultBladeUsername}
		bladePassword=${defaultBladePassword}
	fi
		
	# create the xml file required by hponcfg on the server # dyamically pass the name and password 
	echo '<RIBCL VERSION="2.0">
			<LOGIN USER_LOGIN='${bladeUsername}' PASSWORD='${bladePassword}'>
				<SERVER_INFO MODE="read"> 
					<GET_EMBEDDED_HEALTH> 
						<GET_ALL_FANS/> 
						<GET_ALL_TEMPERATURES/>	
						<GET_ALL_POWER_SUPPLIES/>
						<GET_ALL_VRM/>
						<GET_ALL_PROCESSORS/>
						<GET_ALL_MEMORY/>
						<GET_ALL_NICS/>
						<GET_ALL_STORAGE/> 
						<GET_ALL_HEALTH_STATUS/>
					</GET_EMBEDDED_HEALTH> 
				</SERVER_INFO>
			</LOGIN>
		</RIBCL>' > ${hp_check_list_file_full}
	echo ${hp_check_list_file_full}
	tmpfileName=outputfile_hdw_${serverName}_$hour.txt
	echo ${log_time} "Started" ${serverName} >> ${log_file}
	scp ${hp_check_list_file_full} $serverIP:/  
	
	ssh $serverIP << EOF 
		cd /
		hponcfg -f ${hp_check_list_file} > $tmpfileName 
		#rm ${hp_check_list_file} 
EOF
     scp $serverIP:/$tmpfileName $wd/output/
	 
	 	ssh $serverIP << EOF 
		cd /
		rm $tmpfileName
EOF
	 #attempt to parse files giving errors on python version on oml report
	 cd $wd/output/
	 iLOversion=`head -n 3 $tmpfileName | grep iLO | awk '{print $9}'`
	 head -n -1 $tmpfileName | sed 's/PART NUMBER /PART VALUE/g' > $tmpfileName.xml
	 tail -n +4 $tmpfileName.xml > $tmpfileName
	 
	 #fix other version issues specific to other servers with iLO4 type output but named iLO3
	 if [[ $serverName == "msc1_uip10" || $serverName == "msc1_uip11" || $serverName == dr-vasdb* || $serverName == dro* || $serverName == drdb* || $serverName == drpcrf*   ]];then 
	 #These have a version of iLO matching v4 but named v3
		iLOversion=4
	 fi
	 
	 #format files to fix version issues between iLO3 and iLO4
	 
	if [[ $iLOversion -eq 3 ]] ; then  
		cat $tmpfileName |  sed 's/MEMORY_COMPONENTS/MEMORY_DETAILS/g'| sed 's/MEMORY_COMPONENT/CPU/g' |sed 's/MEMORY_LOCATION/SOCKET/g' | sed 's/MEMORY_SIZE/SIZE/g' | sed 's/MEMORY_SPEED/FREQUENCY/g' | sed 's/DRIVES/STORAGE/g' | sed 's/BACKPLANE/CONTROLLER/g' | sed 's/FIRMWARE_VERSION/FW_VERSION/g' | sed 's/.*<DRIVE_BAY/<DRIVE_ENCLOSURE>&/' |  awk '1;/<UID_LED/{print "</DRIVE_ENCLOSURE>"}' >  $tmpfileName.xml
		cp $tmpfileName.xml $tmpfileName
	 fi
	echo ${log_time} "File Formatting Completed" ${serverName} >> ${log_file}
	
	 #run python script to format xml into csv
	 ${python2_exe} $wd/py_hardware_hp_parse_xml.py $tmpfileName ${serverIP} ${serverName} ${hour} ${iLOversion} > $tmpfileName.csv
	
	#check server fiber ports for servers that connects to the fiber switch. e.g OCS,DB etc
	port_array=$(ssh -n $serverIP "cat /sys/class/fc_host/host*/port_state")
	echo ${hour}";HARDWARE;"${serverName}";"${serverIP}";STORAGE;FIBER_PORT;" `echo $port_array | awk '{print $1}'`";"`echo $port_array | awk '{print $2}'`";" >> $tmpfileName.csv

	#deleting temporary files
	rm $tmpfileName.xml
	rm $tmpfileName
	
	#loading into the database
	if [[ ${deactivateLoader} == "N" || ${deactivateLoader} == "n"  ]];
	then
		mv $tmpfileName.csv ${loader_dir}
	fi
	
	echo ${log_time} "Completed" ${serverName} >> ${log_file}
	rm /home/BASIC_CHECK/backup/output*hdw*csv
	echo ${log_time} "Old Backup File Deleted" ${serverName} >> ${log_file}
done


