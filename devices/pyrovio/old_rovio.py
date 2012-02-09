    def getMCUReportValue(self):
        # get the MCU report
        report = str(self.getMCUReport());
        # get the string that encodes (in hex) the status
        status = report.split('\n')[1].split(' ')[2];
        # return it
        return status;

    def getMCUReport(self):
        print "getting MCUReport";
        url = '%(prot)s://%(host)s/rev.cgi?Cmd=nav&action=20' % self.url_data
        print "Getting Report";
        return self.getRequestResponse(url);

    def obstacle(self):
        "Returns True if there's an obstacle, False otherwise"
        # get just the status string from the MCU report
        status = self.getMCUReportValue();
        # get the last character, convert it to an integer
        lastByte = int("0x" + status[len(status)-1], 16);
        # the obstacle indicator is on bit 2
        # take bitwise & with 00000100 (4 in base 10)
        return ((lastByte & 4) > 0);

