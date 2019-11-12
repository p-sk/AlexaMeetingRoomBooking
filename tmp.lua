-- FUNCTIONS	    
function split_path(str,car) 
    return split(str,car) 
    end  
    
alerts = alarm.list("subsys","%Disk%")
    if alerts ~= nil then	  
             for k=1,#alerts do
             a=alerts[k]
             if a.a.level >= 4 then
             message = "%TYPE=I %CATEGORY=Software.Corporate.Monitoring %URGENCY=3. 3 days %IMPACT=4. 1 user %GROUP=GSSC Command Centre %DESCRIPTION="..a.message
             subsys=a.subsys
             subject = a.robot.." / "..a.severity.." / "..a.subsys.." /" 
             action.email(ismhelpDeskMail@bureauveritas.com,subject,message)
             end
        end
    end		 