# Clear cache
sudo sync && echo 1 > /proc/sys/vm/drop_caches

#To Clear PageCache, dentries and inodes
sudo sh -c 'echo 3 >  /proc/sys/vm/drop_caches'  