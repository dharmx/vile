#!/usr/bin/env bash

## Files and cmd
FILE="$XDG_CACHE_HOME/launch_main.eww"
CONFIG="$XDG_CONFIG_HOME/eww/structs/main-utils"

run_eww() {
  eww -c "$CONFIG" open-many "background"					\
  				"time" 	                          \
			     "user"		                          \
		  	   "system" 		                      \
			     "calendar"        	                  \
			     "directories"   	                  \
			     "wshutdown"     	                  \
	         "wreboot"       	                  \
			     "wlogout"       	                  \
			     "wlock"	     	                    \
			     "wsuspend"      	                  \
			     "mpd"		                          \
			     "quicklinks"	                      \
			     "audiocontrol"
}

close_eww() {
  eww -c "$CONFIG" close "background"			\
  				"time" 	                      \
	    		 "user"			                    \
	    	   "system" 	                    \
			     "calendar"        	                  \
	    		 "directories"       	          \
	    		 "wshutdown"         	          \
	    		 "wreboot"           	          \
	    		 "wlogout"           	          \
	    		 "wlock"	     	                \
	    		 "wsuspend"       	            \
	    		 "mpd"			                    \
	    		 "quicklinks"		                \
	    		 "audiocontrol"
}

## Launch or close widgets accordingly
if [[ ! -f "$FILE" ]]; then
  run_eww
  touch "$FILE"
else
  close_eww
  rm "$FILE"
fi

# vim:ft=bash:nowrap
