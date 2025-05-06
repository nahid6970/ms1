//Modify this file to change what commands output to your statusbar, and recompile using the make command.
static const Block blocks[] = {
	/*Icon*/	/*Command*/		/*Update Interval*/	/*Update Signal*/
    {" 🐧 ", "/home/nahid/ms1/archlinux/dwmblock/scripts/kernel",   360, 2},
    {" 🔺 ", "/home/nahid/ms1/archlinux/dwmblock/scripts/upt",      60,  2},
    {" 📦 ", "/home/nahid/ms1/archlinux/dwmblock/scripts/pacupdate",360, 9},
    {" 💻 ", "/home/nahid/ms1/archlinux/dwmblock/scripts/memory",   6,   1},
    {" 🔊 ", "/home/nahid/ms1/archlinux/dwmblock/scripts/volume",   0,   10},
    {" 🕑 ", "/home/nahid/ms1/archlinux/dwmblock/scripts/clock",    60,  0},
};

//sets delimiter between status commands. NULL character ('\0') means no delimiter.
static char delim[] = " | ";
static unsigned int delimLen = 5;
