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

  int m_fd = open("/dev/fusbi0", O_RDWR | O_SYNC);

int i=0;

   long bytes = 0;

char* data=NULL;

size_t maxSize=0;

short answer[128];

short fireq[] = { 0xaaaa,0x300,0x5256 };

 

//  ioctl(m_fd, IOCTL_FUSBI_BUFFERSIZE, &bytes);

 

  maxSize = sizeof(fireq);

printf("Send\n");

  write(m_fd, fireq, maxSize);

 

  maxSize = sizeof(answer);

 

  answer[0] = answer[01] =answer[02] =0;

printf("Read\n");

 

while( answer[0] == 0 )

{

sleep(1);
int size;
  size = read(m_fd, answer, maxSize);

 

printf( "%4d answer 0x%x 0x%x 0x%x size %d\n", i++, answer[0], answer[1], answer[2], size );

}

 

close(m_fd);

 

return 0;

}
