#!/usr/bin/env --split-string=awk --file

{
  if ($0 ~ "hours") sub("hours", "h", $0)
  if ($0 ~ "hour") sub("hour", "h", $0)

  if ($0 ~ "minutes") sub("minutes", "m", $0)
  if ($0 ~ "minute") sub("minute", "m", $0)

  if ($0 ~ "seconds") sub("seconds", "s", $0)
  if ($0 ~ "second") sub("second", "s", $0)

  if ($0 ~ "days") sub("days", "d", $0)
  if ($0 ~ "day") sub("day", "d", $0)

  if ($0 ~ "weeks") sub("weeks", "w", $0)
  if ($0 ~ "week") sub("week", "w", $0)
  
  gsub(",", "", $0)
  print $2$3" "$4$5" "$6$7
}

# vim:filetype=awk
