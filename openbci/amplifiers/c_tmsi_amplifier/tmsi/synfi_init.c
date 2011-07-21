#include <stdio.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <unistd.h>

int main(int argc, char **argv)
{
	int m_fd;
	int i=0;
	unsigned short fireq[] = { 0xaaaa,0x0300,0x5256 };
	char *name=getenv("KERNEL");
	char dev_path[100];
	FILE * deb;
	sprintf(dev_path,"/dev/%s",argv[1]);
	deb = fopen("/home/mrugacz/deb.txt","w");
	fprintf(deb,"%s\n",dev_path);
	fclose(deb);
	m_fd = open(dev_path, O_RDWR | O_SYNC);
	if (m_fd<0) return -1;
	for (i=0;i<4;i++) 
	{
		write(m_fd, fireq, sizeof(fireq));

	}
	sleep(1);
	close(m_fd);
	return 0;
}
