#include <stdio.h>

#include <sys/types.h>

#include <sys/stat.h>

#include <fcntl.h>

#include <unistd.h>

 

//       int open(const char *pathname, int flags);

//       int open(const char *pathname, int flags, mode_t mode);

//       int creat(const char *pathname, mode_t mode);

 

#define IOCTL_FUSBI_BUFFERSIZE _IOW('F', 1, unsigned long*);

 

int main(void)

{
int m_fd;
int i=0;
long bytes = 0;
char* data=NULL;
size_t maxSize=0;
unsigned short answer[128];

unsigned short fireq[] = { 0xaaaa,0x0300,0x5256 };
//unsigned short fireq[] = { 0xaaaa,0x2700,0x2e56 };
//unsigned short fireq[] = { 0xaaaa,0x2202,0x0000,0x0010,0x3344 };


m_fd = open("/dev/tmsi0", O_RDWR | O_SYNC);
//  ioctl(m_fd, IOCTL_FUSBI_BUFFERSIZE, &bytes);
/*  maxSize = sizeof(answer);
  answer[0] = answer[01] =answer[02] =0;
while( answer[0] == 0 || i<10)

{
	printf("Send\n");
	write(m_fd, fireq, sizeof(fireq));
	int size;
	printf("Read\n");
	size = read(m_fd, answer, maxSize);
	printf( "%4d answer 0x%x 0x%x 0x%x 0x%x size %d\n", i++, answer[0], answer[1], answer[2], answer[3],size );

}
*/
 

close(m_fd);

 

return 0;

}
