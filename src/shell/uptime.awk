#!/usr/bin/env --split-string=awk --file

{
  sub("hours", "h", $0);
  sub("minutes", "min", $0);
  sub("seconds", "s", $0);
  sub("months", "m", $0);
  sub("years", "y", $0);
  print $2$3" "$4$5
}

# vim:filetype=awk
