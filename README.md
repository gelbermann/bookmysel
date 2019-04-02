# bookmysel
`bookmysel` is a script for automated scheduling of rooms in BookMe, the Technion's Institue of Technology's room reservations system.

The script is written in Python, using Selenium to automate the process.

Using it requires that you have a @campus Technion mail account, and provide it's login information as command line arguments. Of course no data is saved anywhere.

Currently it's hard-coded to try reserving only the CS faculty study rooms, but if necessary modifications can be made to accommodate other rooms around the campus, or using command line arguments to choose which rooms to try.

Reservation success will be mailed to your @campus mail by BookMe. Should a reservation fail (which might happen, taking into account that most of the time all time slots are already taken) , details will be sent to your @campus mail from `bookmysel` Gmail address.

## Command line arguments
* `-h` - help
* `-e/--loginemail` - @campus mail address - required
* `-p/--loginpass` - @campus mail password - required
* `-d/--date` - date of reservation. Default date is two weeks from current date.
* `-H/--hour` - hour of reservation. Default hour is current hour, at 00 minutes.
* `-l/--length` - length of reservation in minutes. Default length is 180 minutes.
